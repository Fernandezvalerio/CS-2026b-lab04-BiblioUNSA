"""Dominio de BiblioUNSA (HU-03: reservar un libro).

Generado con IA a partir de docs/diagram/clases.puml (ingeniería directa, Lab 05 - E6)
y revisado por el equipo. Convenciones:
- Clases y enumeraciones con los mismos nombres que el diagrama (C5).
- Operaciones y atributos en snake_case (convención de Python).
- `Prestamo` delega sus transiciones en objetos State (Lab 07, E3).
- Los puertos y el servicio esquelético del Lab 05 se conservan como referencia.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from reservas.estados import EstadoPrestamoBase, crear_estado


class EstadoPrestamo(Enum):
    RESERVADO = "RESERVADO"
    PRESTADO = "PRESTADO"
    VENCIDO = "VENCIDO"
    DEVUELTO = "DEVUELTO"
    CON_MULTA = "CON_MULTA"


@dataclass
class Estudiante:
    correo_institucional: str
    id: UUID = field(default_factory=uuid4)


@dataclass
class Libro:
    titulo: str
    autor: str
    isbn: str
    ejemplares: list[Ejemplar] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)


@dataclass
class Ejemplar:
    codigo_inventario: str
    biblioteca: str
    disponible: bool = True
    id: UUID = field(default_factory=uuid4)

    def esta_disponible(self) -> bool:
        return self.disponible

    def marcar_reservado(self) -> None:
        if not self.disponible:
            raise ValueError("El ejemplar no está disponible")
        self.disponible = False

    def marcar_disponible(self) -> None:
        self.disponible = True


@dataclass
class Prestamo:
    estudiante: Estudiante
    ejemplar: Ejemplar
    fecha_reserva: datetime = field(default_factory=datetime.now)
    fecha_vencimiento: date | None = None
    fecha_devolucion: date | None = None
    estado: EstadoPrestamo = EstadoPrestamo.RESERVADO
    requiere_reverificacion: bool = False
    monto_multa: Decimal = Decimal("0")
    id: UUID = field(default_factory=uuid4)
    _estado_objeto: EstadoPrestamoBase = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        self._estado_objeto = crear_estado(self.estado.value)

    def _cambiar_a(self, nombre: str) -> None:
        """Mantiene sincronizados el enum persistible y el objeto State."""
        nuevo_estado = EstadoPrestamo(nombre)
        nuevo_objeto = crear_estado(nuevo_estado.value)
        self.estado = nuevo_estado
        self._estado_objeto = nuevo_objeto

    def entregar(self) -> None:
        self._estado_objeto.entregar(self)

    def marcar_vencido(self, hoy: date | None = None) -> None:
        self._estado_objeto.marcar_vencido(self, hoy or date.today())

    def registrar_devolucion(self, fecha: date) -> None:
        self._estado_objeto.registrar_devolucion(self, fecha)

    def aplicar_multa(self, monto: Decimal) -> None:
        self._estado_objeto.aplicar_multa(self, monto)

    def marcar_para_reverificacion(self) -> None:
        self._estado_objeto.marcar_para_reverificacion(self)


@dataclass
class ResultadoMatricula:
    vigente: bool
    fecha_consulta: datetime
    desde_cache: bool = False

    def es_vigente(self) -> bool:
        return self.vigente

    def cache_vigente(self, ahora: datetime) -> bool:
        raise NotImplementedError("Aplicar la ventana de caché de 24 h (ADR-003)")


class ValidadorMatricula(ABC):
    """Puerto hacia el sistema académico (ADR-001, ADR-003)."""

    @abstractmethod
    def validar(self, estudiante_id: UUID) -> ResultadoMatricula: ...


class AdaptadorSistemaAcademico(ValidadorMatricula):
    def __init__(self, timeout_segundos: int = 3, horas_cache: int = 24) -> None:
        self.timeout_segundos = timeout_segundos
        self.horas_cache = horas_cache

    def validar(self, estudiante_id: UUID) -> ResultadoMatricula:
        raise NotImplementedError("Integrar con la API del sistema académico")

    def _consultar_api(self, estudiante_id: UUID) -> ResultadoMatricula:
        raise NotImplementedError("Integrar con la API del sistema académico")

    def _leer_cache(self, estudiante_id: UUID) -> ResultadoMatricula:
        raise NotImplementedError("Leer la última validación en caché")


class RepositorioPrestamos(ABC):
    @abstractmethod
    def guardar(self, p: Prestamo) -> None: ...

    @abstractmethod
    def buscar_pendientes_reverificacion(self) -> list[Prestamo]: ...


class RepositorioEjemplares(ABC):
    @abstractmethod
    def buscar(self, id: UUID) -> Ejemplar: ...

    @abstractmethod
    def guardar(self, e: Ejemplar) -> None: ...


class ServicioReservas:
    def __init__(
        self,
        validador: ValidadorMatricula,
        repo_prestamos: RepositorioPrestamos,
        repo_ejemplares: RepositorioEjemplares,
    ) -> None:
        self.validador = validador
        self.repo_prestamos = repo_prestamos
        self.repo_ejemplares = repo_ejemplares

    def reservar_libro(self, estudiante_id: UUID, ejemplar_id: UUID) -> Prestamo:
        raise NotImplementedError("Implementar el flujo de secuencia-reservar-libro.puml")

    def reverificar_pendientes(self) -> None:
        raise NotImplementedError("Reverificar préstamos marcados (≤ 30 min, ADR-003)")
