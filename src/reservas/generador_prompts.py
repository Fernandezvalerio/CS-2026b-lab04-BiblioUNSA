"""Integración de los prompts del Lab 09 con el puerto ProveedorLLM (Lab 07).

Solo genera y valida respuestas: no ejecuta consultas SQL.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

from jsonschema import ValidationError
from jsonschema.validators import validator_for

from reservas.ia import ProveedorLLM

RAIZ_PROMPTS = Path(__file__).resolve().parents[2] / "prompts"
VERSION = re.compile(r"v[1-9]\d*\Z")
TABLAS = frozenset({"libros", "ejemplares", "prestamos", "multas"})
PALABRAS_PROHIBIDAS = re.compile(
    r"\b(?:INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|COPY|GRANT|"
    r"REVOKE|EXEC|CALL|WITH|MERGE|REPLACE|INTO|UNION)\b|\bFOR\s+UPDATE\b",
    re.IGNORECASE,
)


class SalidaPromptInvalida(ValueError):
    """La respuesta no respeta el contrato o las reglas de la tarea."""


class _GeneradorBase:
    tarea: str

    def __init__(self, proveedor: ProveedorLLM, version: str = "v3") -> None:
        if not VERSION.fullmatch(version):
            raise ValueError("Versión de prompt inválida")

        carpeta = RAIZ_PROMPTS / self.tarea
        self.plantilla = (carpeta / f"{version}.txt").read_text(encoding="utf-8")
        esquema = json.loads((carpeta / "esquema.json").read_text(encoding="utf-8"))
        clase_validadora = validator_for(esquema)  # Respeta el draft del esquema.
        clase_validadora.check_schema(esquema)
        self.validador = clase_validadora(esquema)
        self.proveedor = proveedor

    def _consultar(self, identificador: str, dato: str, variable: str) -> dict:
        # Evita que el texto insertado cierre etiquetas <historia> o <pregunta>.
        dato_seguro = html.escape(dato, quote=True)
        prompt = self.plantilla.replace("{{id}}", identificador).replace(
            "{{" + variable + "}}", dato_seguro
        )
        respuesta = self.proveedor.generar(prompt)
        try:
            objeto = json.loads(respuesta)
            self.validador.validate(objeto)
        except (json.JSONDecodeError, ValidationError, TypeError) as error:
            raise SalidaPromptInvalida("La respuesta no cumple el esquema JSON") from error
        return objeto


class GeneradorCriterios(_GeneradorBase):
    tarea = "criterios"

    def generar(self, historia_id: str, historia: str) -> dict:
        if not re.fullmatch(r"H[1-8]", historia_id):
            raise ValueError("ID de historia inválido")
        salida = self._consultar(historia_id, historia, "historia")
        if salida["historia_id"] != historia_id:
            raise SalidaPromptInvalida("La respuesta corresponde a otra historia")

        preguntas, escenarios = salida["preguntas"], salida["escenarios"]
        if salida["invest_ok"]:
            tipos = {escenario["tipo"] for escenario in escenarios}
            if preguntas or not (2 <= len(escenarios) <= 4):
                raise SalidaPromptInvalida("Cantidad de preguntas o escenarios incorrecta")
            if "exito" not in tipos or not tipos.intersection({"error", "borde"}):
                raise SalidaPromptInvalida("Falta un escenario de éxito o alternativa")
        elif not (1 <= len(preguntas) <= 3) or escenarios:
            raise SalidaPromptInvalida("Una historia ambigua debe pedir aclaraciones sin escenarios")
        return salida


class GeneradorSQL(_GeneradorBase):
    tarea = "sql"

    def generar(self, pregunta_id: str, pregunta: str) -> dict:
        if not re.fullmatch(r"Q[1-8]", pregunta_id):
            raise ValueError("ID de pregunta inválido")
        salida = self._consultar(pregunta_id, pregunta, "pregunta")
        if salida["pregunta_id"] != pregunta_id:
            raise SalidaPromptInvalida("La respuesta corresponde a otra pregunta")

        preguntas = salida["preguntas"]
        sql = salida["consulta_sql"]
        if salida["necesita_aclaracion"]:
            if sql is not None or not (1 <= len(preguntas) <= 3):
                raise SalidaPromptInvalida("La aclaración debe tener preguntas y SQL nulo")
            return salida
        if preguntas or not isinstance(sql, str):
            raise SalidaPromptInvalida("Una pregunta clara debe devolver SQL sin aclaraciones")

        # Admitimos un único punto y coma AL FINAL, como el generado en E4.
        consulta = sql.strip()
        if consulta.endswith(";"):
            consulta = consulta[:-1].rstrip()
        if (
            not re.match(r"\ASELECT\s+", consulta, re.IGNORECASE)
            or ";" in consulta
            or any(c in consulta for c in ("--", "/*", "*/"))
            or PALABRAS_PROHIBIDAS.search(consulta)
        ):
            raise SalidaPromptInvalida("Solo se permite una consulta SELECT de lectura")

        tablas = re.findall(
            r"\b(?:FROM|JOIN)\s+([a-z_][a-z_0-9]*)", consulta, re.IGNORECASE
        )
        if not tablas or any(nombre.lower() not in TABLAS for nombre in tablas):
            raise SalidaPromptInvalida("La consulta usa tablas fuera del esquema")
        return salida
