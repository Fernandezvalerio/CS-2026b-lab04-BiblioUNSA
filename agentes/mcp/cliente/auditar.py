"""Auditor de catálogo MCP (Lab 11, E7). No invoca herramientas.
Solo permite iniciar el servidor propio y la muestra docente revisada.
Códigos de salida: 0 sin hallazgos altos, 1 hallazgos altos, 2 error de auditoría.
"""
import argparse
import asyncio
import hashlib
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
PROPIO = BASE / 'servidor_mcp' / 'bibliounsa_mcp.py'
TERCERO = BASE / 'terceros' / 'clima_mcp.py'
HASH_DOCENTE = 'f64fea935c74943d10958b11a1ee4de59ffc6e9e2419499f126bb0a1bb8e6204'

# Reglas del ejemplo docente, con identificadores para facilitar la evidencia.
REGLAS = [
    ('R01', 'ALTA', r'<\s*important\s*>|ignora|ignore (all|previous)|no (le )?(menciones|digas)|do not (tell|mention)',
     'instrucciones ocultas dirigidas al modelo'),
    ('R02', 'ALTA', r'\.env\b|id_rsa|\.ssh|credencial|password|contraseña|token|api[_ ]?key',
     'pide secretos o credenciales'),
    ('R03', 'ALTA', r'curl |wget |\| *sh\b|https?://', 'comandos o URL externas en la descripción'),
    ('R04', 'MEDIA', r'(lee|read).{0,40}(archivo|file|recurso|resource)', 'pide leer datos ajenos a su función'),
]
PARAMS_SOSPECHOSOS = {'contexto', 'context', 'notas', 'notes', 'extra', 'metadata', 'debug'}


def revisar_catalogo(tools):
    hallazgos = []
    for t in tools:
        def agregar(regla, severidad, motivo):
            hallazgos.append({'regla': regla, 'severidad': severidad,
                               'herramienta': t.name, 'motivo': motivo})
        desc = t.description or ''
        for regla, sev, patron, motivo in REGLAS:
            if re.search(patron, desc, re.I):
                agregar(regla, sev, motivo)
        props = t.input_schema.get('properties', {})
        for p in sorted(set(props) & PARAMS_SOSPECHOSOS):
            agregar('R05', 'MEDIA', f'parámetro genérico {p!r}: posible filtración de datos')
        a = t.annotations
        if a is None:
            agregar('R06', 'BAJA', 'sin anotaciones')
        if len(desc) > 400:
            agregar('R07', 'BAJA', f'descripción muy larga ({len(desc)} caracteres)')
        # R08: si no se declara lectura, tratar como posible escritura.
        if getattr(a, 'read_only_hint', None) is not True and getattr(a, 'destructive_hint', None) is None:
            agregar('R08', 'MEDIA', 'posible escritura sin destructiveHint explícito')
        # R09: advertencia de esquema, no prueba de ausencia de validación interna.
        for p, esquema in sorted(props.items()):
            if esquema.get('type') == 'string' and not isinstance(esquema.get('maxLength'), int):
                agregar('R09', 'MEDIA', f'parámetro de texto {p!r} sin maxLength en el esquema publicado')
    return hallazgos


def ruta_permitida(ruta):
    ruta = Path(ruta).resolve(strict=True)
    if ruta == PROPIO.resolve():
        return ruta
    if ruta == TERCERO.resolve():
        if hashlib.sha256(ruta.read_bytes().replace(b'\r\n', b'\n')).hexdigest() != HASH_DOCENTE:
            raise ValueError('La muestra docente fue modificada; revise su código sin ejecutarlo.')
        return ruta
    raise ValueError('No se inicia código MCP desconocido. Revise primero su fuente en un entorno aislado.')


async def auditar(ruta):
    from mcp import Client, StdioServerParameters
    ruta = ruta_permitida(ruta)
    async with Client(StdioServerParameters(command=sys.executable, args=[str(ruta)])) as c:
        tools = (await c.list_tools()).tools
        hallazgos = revisar_catalogo(tools)
        return {'servidor': c.server_info.name, 'herramientas': [t.name for t in tools],
                'hallazgos': hallazgos, 'bloqueado': any(h['severidad'] == 'ALTA' for h in hallazgos)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('servidor', type=Path)
    p.add_argument('--salida', type=Path, help='Guardar informe JSON con los hallazgos reales')
    args = p.parse_args()
    try:
        resultado = asyncio.run(asyncio.wait_for(auditar(args.servidor), timeout=30))
        if args.salida:
            args.salida.parent.mkdir(parents=True, exist_ok=True)
            args.salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('Servidor:', resultado['servidor'])
        for h in resultado['hallazgos']:
            print(f"  [{h['severidad']:<5}] {h['regla']} {h['herramienta']}: {h['motivo']}")
        if not resultado['hallazgos']:
            print('  [OK] Sin hallazgos del auditor')
        print('Decisión:', 'NO CONECTAR' if resultado['bloqueado'] else 'REVISIÓN HUMANA REQUERIDA')
        return int(resultado['bloqueado'])
    except Exception as exc:
        print(f'Auditoría incompleta: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
