"""Chequeo AST local complementario a import-linter, sin dependencias externas."""

from __future__ import annotations

import ast
from pathlib import Path

REGLAS = {
    "FF-01": {
        "origenes": {"dominio", "estados"},
        "destinos": {"externos", "validadores", "servicio"},
    },
    "FF-02": {
        "origenes": {"validadores", "decoradores"},
        "destinos": {"servicio"},
    },
}


def detectar_infracciones(nombre: str, texto: str, regla: str) -> list[str]:
    if nombre not in REGLAS[regla]["origenes"]:
        return []
    arbol = ast.parse(texto)
    fallos = []
    for nodo in ast.walk(arbol):
        modulos = []
        if isinstance(nodo, ast.Import):
            modulos = [alias.name for alias in nodo.names]
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            modulos = [nodo.module]
        for modulo in modulos:
            for prohibido in REGLAS[regla]["destinos"]:
                if modulo == f"reservas.{prohibido}" or modulo.startswith(f"reservas.{prohibido}."):
                    fallos.append(f"{nombre}.py:{nodo.lineno} importa {modulo}")
    return fallos


def comprobar_regla(raiz: Path, regla: str) -> list[str]:
    return [
        fallo
        for nombre in REGLAS[regla]["origenes"]
        for fallo in detectar_infracciones(
            nombre, (raiz / "src" / "reservas" / f"{nombre}.py").read_text(encoding="utf-8"), regla
        )
    ]
