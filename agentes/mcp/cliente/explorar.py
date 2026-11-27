"""Exploración por stdio de las primitivas de BiblioUNSA (sin LLM ni red).
La reserva opcional exige confirmación explícita; los datos se pierden al cerrar.
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path
from mcp import Client, StdioServerParameters
from mcp.types import Implementation

RAIZ = Path(__file__).resolve().parents[1]
SERVIDOR = StdioServerParameters(command=sys.executable,
                                 args=[str(RAIZ / "servidor_mcp/bibliounsa_mcp.py")])


def texto(resultado):
    return " ".join(getattr(c, "text", "") for c in resultado.content)


def comprobar(resultado, nombre):
    if resultado.is_error:
        raise RuntimeError(f"{nombre}: {texto(resultado)}")
    if resultado.structured_content is None:
        raise RuntimeError(f"{nombre}: falta salida estructurada")
    print(f"  {nombre} ->", json.dumps(resultado.structured_content, ensure_ascii=False))
    return resultado.structured_content


async def main(reservar=False):
    async with Client(SERVIDOR, client_info=Implementation(name="explorador-bibliounsa", version="1.0")) as c:
        print(f"Servidor: {c.server_info.name} | protocolo {c.protocol_version}")
        print("\nHERRAMIENTAS:")
        for h in (await c.list_tools()).tools:
            tipo = "solo lectura" if h.annotations and h.annotations.read_only_hint else "ESCRITURA"
            print(f"  - {h.name}({', '.join(h.input_schema.get('properties', {}))}) [{tipo}]")
        print("\nRECURSOS:")
        for r in (await c.list_resources()).resources:
            print(f"  - {r.uri} {r.title}")
        for t in (await c.list_resource_templates()).resource_templates:
            print(f"  - {t.uri_template} {t.title} (plantilla)")
        print("\nPROMPTS:")
        for p in (await c.list_prompts()).prompts:
            print(f"  - {p.name}({', '.join(a.name for a in p.arguments or [])})")
        print("\nPRUEBAS DE USO:")
        args = {"consulta": "redes", "biblioteca": "Central"}
        libros = comprobar(await c.call_tool("buscar_libro", args), "buscar_libro")
        comprobar(await c.call_tool("prestamos_vencidos", {"hoy": "2026-11-27"}), "prestamos_vencidos")
        r = await c.call_tool("prestamos_vencidos", {"hoy": "27/11/2026"})
        print(f"  fecha inválida -> is_error = {r.is_error} | {texto(r)}")
        if not r.is_error:
            raise RuntimeError("Se aceptó una fecha inválida")
        for uri in ("bibliounsa://prestamos/reglas", "bibliounsa://adr/001"):
            r = await c.read_resource(uri)
            print(f"  {uri} -> {r.contents[0].text.splitlines()[0]}")
        for nombre, parametros in (
            ("aviso_vencimiento", {"titulo": "Redes de computadoras", "fecha_vencimiento": "2026-11-20"}),
            ("generar_criterios", {"id": "HU-03", "historia": "Como estudiante quiero reservar un libro disponible."}),
        ):
            r = await c.get_prompt(nombre, parametros)
            print(f"  {nombre} -> {r.messages[0].content.text[:100]} ...")
        if reservar:
            ejemplar = next(e for l in libros["libros"] for e in l["ejemplares"] if e["disponible"])
            print(f"\nReserva ficticia de {ejemplar['codigo_inventario']} (estudiante de prueba 001).")
            if input("¿Aprueba la creación? [s/N]: ").strip().lower() == "s":
                comprobar(await c.call_tool("crear_reserva", {
                    "estudiante_id": "00000000-0000-4000-8000-000000000001",
                    "ejemplar_id": ejemplar["ejemplar_id"],
                }), "crear_reserva")
                comprobar(await c.call_tool("buscar_libro", args), "buscar_libro después de reservar")
            else:
                print("Reserva no ejecutada.")
        print("\nExploración finalizada.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reservar", action="store_true", help="Ofrece crear una reserva previa aprobación")
    asyncio.run(main(parser.parse_args().reservar))
