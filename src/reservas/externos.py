"""Dobles locales de los servicios externos usados por HU-03.

No realizan peticiones HTTP ni utilizan credenciales. Las dos versiones
simulan contratos posibles de la API académica (ADR-003), con interfaces
intencionalmente diferentes para el ejercicio de refactorización.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from reservas.dominio import Ejemplar, Prestamo


class SistemaAcademicoJSON:
    """Simula una API que responde con un diccionario de Python."""

    def __init__(
        self,
        matriculas: dict[UUID, bool] | None = None,
        fecha_consulta: datetime | None = None,
        fallas: int = 0,
    ) -> None:
        self.matriculas = matriculas or {}
        self.fecha_consulta = fecha_consulta
        self.fallas = fallas
        self.llamadas = 0

    def consultar_matricula(
        self, estudiante_id: UUID, timeout_segundos: int = 3
    ) -> dict[str, object]:
        self.llamadas += 1
        if self.llamadas <= self.fallas:
            raise TimeoutError("La API académica JSON no responde")
        return {
            "vigente": self.matriculas.get(estudiante_id, False),
            "consultado_en": self.fecha_consulta or datetime.now(),
        }


class SistemaAcademicoCodigos:
    """Simula otra versión HTTP que devuelve (status, estado, fecha)."""

    def __init__(
        self,
        matriculas: dict[str, bool] | None = None,
        fecha_consulta: datetime | None = None,
        fallas: int = 0,
        codigo_http: int = 200,
    ) -> None:
        self.matriculas = matriculas or {}
        self.fecha_consulta = fecha_consulta
        self.fallas = fallas
        self.codigo_http = codigo_http
        self.llamadas = 0

    def obtener_estado_alumno(
        self, codigo_alumno: str, tiempo_maximo_ms: int = 3000
    ) -> tuple[int, int, datetime]:
        self.llamadas += 1
        if self.llamadas <= self.fallas:
            raise TimeoutError("La API académica de códigos no responde")
        vigente = self.matriculas.get(codigo_alumno, False)
        return (
            self.codigo_http,
            1 if vigente else 0,
            self.fecha_consulta or datetime.now(),
        )


class RepositorioEjemplaresMemoria:
    """Repositorio en memoria; no necesita PostgreSQL para las pruebas."""

    def __init__(self, ejemplares: list[Ejemplar] | None = None) -> None:
        self.ejemplares = {e.id: e for e in (ejemplares or [])}

    def buscar(self, ejemplar_id: UUID) -> Ejemplar:
        return self.ejemplares[ejemplar_id]

    def guardar(self, ejemplar: Ejemplar) -> None:
        self.ejemplares[ejemplar.id] = ejemplar


class RepositorioPrestamosMemoria:
    def __init__(self) -> None:
        self.prestamos: list[Prestamo] = []

    def guardar(self, prestamo: Prestamo) -> None:
        if not any(p.id == prestamo.id for p in self.prestamos):
            self.prestamos.append(prestamo)

    def buscar_pendientes_reverificacion(self) -> list[Prestamo]:
        return [p for p in self.prestamos if p.requiere_reverificacion]
