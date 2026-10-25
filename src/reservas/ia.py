"""E5: recomendaciones de libros con LLM intercambiable y guardrails.

No usa Internet ni claves de API. El modelo solamente propone ISBN;
los resultados finales siempre se obtienen del catálogo local.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Mapping

from reservas.dominio import Libro
from reservas.externos import MotorTextoSimulado


class ProveedorLLM(ABC):
    """Strategy pequeña para cambiar de proveedor sin tocar el dominio."""

    @abstractmethod
    def generar(self, prompt: str) -> str: ...


class AdaptadorMotorSimulado(ProveedorLLM):
    """Adapter: convierte completar(...) en generar(...)."""

    def __init__(self, motor: MotorTextoSimulado) -> None:
        self.motor = motor

    def generar(self, prompt: str) -> str:
        return self.motor.completar(prompt)


class ConCacheLLM(ProveedorLLM):
    """Decorator: evita repetir llamadas para prompts idénticos."""

    def __init__(self, interno: ProveedorLLM) -> None:
        self.interno = interno
        self.cache: dict[str, str] = {}
        self.aciertos = 0

    def generar(self, prompt: str) -> str:
        if prompt in self.cache:
            self.aciertos += 1
            return self.cache[prompt]
        respuesta = self.interno.generar(prompt)
        self.cache[prompt] = respuesta
        return respuesta


class RespuestaLLMInvalida(ValueError):
    """La sugerencia de IA no cumple el formato o las reglas del catálogo."""


@dataclass
class ContextoGuardrails:
    respuesta: str
    isbn_origen: str
    catalogo: Mapping[str, Libro]
    isbns_sugeridos: tuple[str, ...] = field(default_factory=tuple)


class Guardrail(ABC):
    """Eslabón base de Chain of Responsibility."""

    def __init__(self, siguiente: Guardrail | None = None) -> None:
        self.siguiente = siguiente

    def procesar(self, contexto: ContextoGuardrails) -> ContextoGuardrails:
        self.validar(contexto)
        if self.siguiente is not None:
            return self.siguiente.procesar(contexto)
        return contexto

    @abstractmethod
    def validar(self, contexto: ContextoGuardrails) -> None: ...


class GuardrailFormato(Guardrail):
    """Solo acepta JSON {'isbns': [1 a 3 cadenas]} sin campos extra."""

    def validar(self, contexto: ContextoGuardrails) -> None:
        try:
            datos = json.loads(contexto.respuesta)
        except (ValueError, TypeError) as error:
            raise RespuestaLLMInvalida("La IA no devolvió JSON válido") from error

        if not isinstance(datos, dict) or set(datos) != {"isbns"}:
            raise RespuestaLLMInvalida("La respuesta debe contener solo 'isbns'")
        sugeridos = datos["isbns"]
        if (
            not isinstance(sugeridos, list)
            or not (1 <= len(sugeridos) <= 3)
            or not all(isinstance(isbn, str) and isbn.strip() for isbn in sugeridos)
        ):
            raise RespuestaLLMInvalida("Se requieren entre 1 y 3 ISBN válidos")
        contexto.isbns_sugeridos = tuple(sugeridos)


class GuardrailCatalogo(Guardrail):
    """Bloquea libros inventados, duplicados y el mismo libro de origen."""

    def validar(self, contexto: ContextoGuardrails) -> None:
        sugeridos = contexto.isbns_sugeridos
        if not sugeridos:
            raise RespuestaLLMInvalida("No hay ISBN para validar contra el catálogo")
        if len(set(sugeridos)) != len(sugeridos):
            raise RespuestaLLMInvalida("La IA repitió un ISBN")
        if contexto.isbn_origen in sugeridos:
            raise RespuestaLLMInvalida("La IA recomendó el mismo libro de origen")
        if any(isbn not in contexto.catalogo for isbn in sugeridos):
            raise RespuestaLLMInvalida("La IA inventó libros fuera del catálogo")


class RecomendadorLibros:
    """Función de IA de BiblioUNSA: recomendar libros reales del catálogo."""

    def __init__(
        self,
        catalogo: list[Libro],
        proveedor: ProveedorLLM,
        cadena: Guardrail | None = None,
    ) -> None:
        self.catalogo = {libro.isbn: libro for libro in catalogo}
        self.proveedor = proveedor
        self.cadena = cadena if cadena is not None else GuardrailFormato(GuardrailCatalogo())

    def recomendar(self, isbn_origen: str) -> list[Libro]:
        if isbn_origen not in self.catalogo:
            raise ValueError("El libro de origen no existe en el catálogo")

        origen = self.catalogo[isbn_origen]
        opciones = [
            {"isbn": libro.isbn, "titulo": libro.titulo, "autor": libro.autor}
            for libro in sorted(self.catalogo.values(), key=lambda item: item.isbn)
            if libro.isbn != isbn_origen
        ]
        if not opciones:
            return []
        prompt = (
            f"Recomienda entre 1 y 3 libros parecidos a '{origen.titulo}' "
            "usando exclusivamente los ISBN del catálogo siguiente. "
            'Responde solo JSON con la clave "isbns". Catálogo: '
            + json.dumps(opciones, ensure_ascii=False, sort_keys=True)
        )
        respuesta = self.proveedor.generar(prompt)
        contexto = ContextoGuardrails(respuesta, isbn_origen, self.catalogo)
        validado = self.cadena.procesar(contexto)

        # Nunca construimos títulos ni libros a partir de texto del LLM.
        return [self.catalogo[isbn] for isbn in validado.isbns_sugeridos]
