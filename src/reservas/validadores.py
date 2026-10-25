"""E2: Strategy, Adapter y Factory para validar matrículas.

Los adaptadores conocen los contratos externos, pero no toman decisiones
sobre si se puede reservar un ejemplar.
"""

from __future__ import annotations

from collections.abc import Callable
from uuid import UUID

from reservas.dominio import ResultadoMatricula, ValidadorMatricula
from reservas.externos import SistemaAcademicoCodigos, SistemaAcademicoJSON


class IntegracionException(ConnectionError):
    """La integración no puede devolver una validación confiable."""


class AdaptadorMatriculaJSON(ValidadorMatricula):
    """Adapter: convierte el diccionario JSON al objeto del dominio."""

    def __init__(self, cliente: SistemaAcademicoJSON) -> None:
        self.cliente = cliente

    def validar(self, estudiante_id: UUID) -> ResultadoMatricula:
        respuesta = self.cliente.consultar_matricula(
            estudiante_id, timeout_segundos=1
        )
        return ResultadoMatricula(
            vigente=respuesta["vigente"],
            fecha_consulta=respuesta["consultado_en"],
            desde_cache=False,
        )


class AdaptadorMatriculaCodigos(ValidadorMatricula):
    """Adapter: convierte (HTTP, estado, fecha) al objeto del dominio."""

    def __init__(self, cliente: SistemaAcademicoCodigos) -> None:
        self.cliente = cliente

    def validar(self, estudiante_id: UUID) -> ResultadoMatricula:
        codigo, estado, consultado = self.cliente.obtener_estado_alumno(
            str(estudiante_id), tiempo_maximo_ms=1000
        )
        if codigo != 200:
            raise IntegracionException("Error del sistema académico")
        return ResultadoMatricula(
            vigente=estado == 1,
            fecha_consulta=consultado,
            desde_cache=False,
        )


class FabricaValidadores:
    """Factory por registro: puede ampliarse sin editar ServicioReservas."""

    def __init__(self) -> None:
        self._creadores: dict[str, Callable[[], ValidadorMatricula]] = {}

    def registrar(self, nombre: str, creador: Callable[[], ValidadorMatricula]) -> None:
        self._creadores[nombre] = creador

    def crear(self, nombre: str) -> ValidadorMatricula:
        if nombre not in self._creadores:
            raise ValueError(f"Proveedor no soportado: {nombre}")
        return self._creadores[nombre]()
