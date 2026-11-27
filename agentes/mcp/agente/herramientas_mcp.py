"""Adapter del Lab 07: presenta MCP al núcleo síncrono del agente del Lab 10."""
import asyncio
import json
import re
import threading
from concurrent.futures import TimeoutError

from mcp import Client, StdioServerParameters
from mcp.types import Implementation


class HerramientasMCP:
    def __init__(self, servidor: StdioServerParameters, exponer_recursos=True):
        self._loop = asyncio.new_event_loop()
        self._hilo = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._listo = threading.Event()
        self._cerrar = None
        self._exponer_recursos = exponer_recursos
        self._hilo.start()
        self._sesion = asyncio.run_coroutine_threadsafe(self._conectar(servidor), self._loop)
        self._sesion.add_done_callback(lambda _: self._listo.set())
        try:
            if not self._listo.wait(30):
                raise TimeoutError('El servidor MCP no respondió en 30 segundos')
            if self._sesion.done():
                self._sesion.result()
                raise RuntimeError('La conexión MCP se cerró durante el arranque')
        except BaseException:
            self.cerrar()
            raise

    async def _conectar(self, servidor):
        self._cerrar = asyncio.Event()
        async with Client(servidor, client_info=Implementation(name='agente-bibliounsa-lab10', version='1.1')) as c:
            self._cliente = c
            self._tools = {t.name: t for t in (await c.list_tools()).tools}
            self._listo.set()
            await self._cerrar.wait()

    def _llamar(self, coro):
        futuro = asyncio.run_coroutine_threadsafe(coro, self._loop)
        try:
            return futuro.result(timeout=60)
        except TimeoutError:
            futuro.cancel()
            raise

    def catalogo(self):
        cat = {n: f'{(t.description or "").strip()} Esquema: {json.dumps(t.input_schema, ensure_ascii=False)}'
               for n, t in self._tools.items()}
        if self._exponer_recursos:
            cat['leer_recurso'] = 'Lee reglas o ADR del proyecto. uri: bibliounsa://prestamos/reglas o bibliounsa://adr/001 (tres dígitos).'
        return cat

    def herramientas_de_escritura(self):
        # Las anotaciones son pistas; el host también fija la única escritura esperada.
        return {n for n, t in self._tools.items() if not (t.annotations and t.annotations.read_only_hint)}

    def leer_recurso(self, uri: str):
        if not self._exponer_recursos:
            raise ValueError('Lectura de recursos deshabilitada por el host')
        if not isinstance(uri, str) or not re.fullmatch(r'bibliounsa://(?:prestamos/reglas|adr/[0-9]{3})', uri):
            raise ValueError('URI fuera del catálogo de recursos permitido')
        r = self._llamar(self._cliente.read_resource(uri))
        return '\n'.join(getattr(c, 'text', '') for c in r.contents)

    def __getattr__(self, nombre):
        if nombre.startswith('_') or nombre not in self.__dict__.get('_tools', {}):
            raise AttributeError(nombre)

        def invocar(**args):
            r = self._llamar(self._cliente.call_tool(nombre, args))
            cuerpo = (json.dumps(r.structured_content, ensure_ascii=False)
                      if r.structured_content is not None else ' '.join(getattr(c, 'text', '') for c in r.content))
            return ('ERROR: ' if r.is_error else '') + cuerpo
        return invocar

    def cerrar(self):
        if self._loop.is_closed():
            return
        try:
            if self._cerrar is not None and not self._sesion.done():
                self._loop.call_soon_threadsafe(self._cerrar.set)
            try:
                self._sesion.result(timeout=10)
            except TimeoutError:
                self._sesion.cancel()
                # Dejar que el contexto del cliente cierre el subproceso.
                async def drenar():
                    tareas = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
                    for t in tareas:
                        t.cancel()
                    await asyncio.gather(*tareas, return_exceptions=True)
                asyncio.run_coroutine_threadsafe(drenar(), self._loop).result(timeout=5)
            except Exception:
                pass  # El error de conexión se informa al iniciar o invocar.
        finally:
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._hilo.join(timeout=5)
            if not self._hilo.is_alive():
                self._loop.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.cerrar()
