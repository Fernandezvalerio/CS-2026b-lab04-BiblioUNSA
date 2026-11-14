"""Proveedor offline para promptfoo: lee los archivos de grabaciones tal como están.

Este módulo NO llama a ningún LLM; permite repetir una evaluación sin API.
"""
from pathlib import Path
import re

BASE = Path(__file__).resolve().parent


def call_api(prompt, options, context):
    etiqueta = str(context.get("prompt", {}).get("label", ""))
    encontrado = re.search(r"(?:^|[/\\])(v\d+(?:\.\d+)?)\.txt", etiqueta)
    if not encontrado:
        return {"error": f"No se pudo identificar la versión en: {etiqueta}"}

    variables = context.get("vars", {})
    tarea = str(variables.get("tarea", "criterios"))
    caso = str(variables.get("id", ""))
    version = encontrado.group(1)
    if tarea not in {"criterios", "sql"} or not re.fullmatch(r"[HQ]\d{1,2}", caso):
        return {"error": "Tarea o caso inválido"}

    archivo = BASE / tarea / "grabaciones" / version / f"{caso}.txt"
    if not archivo.is_file():
        return {"error": f"Falta la grabación de {tarea}/{version}/{caso}"}
    return {"output": archivo.read_text(encoding="utf-8").strip()}
