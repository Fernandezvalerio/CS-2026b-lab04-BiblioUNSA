"""Patrón State para el ciclo de vida del préstamo (Lab 07, E3).

Cada estado redefine solamente las operaciones permitidas por la máquina de
estados de docs/design/estados-prestamo.mmd. Las demás se rechazan en la base.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from reservas.dominio import Prestamo


class EstadoPrestamoBase:
    nombre = "?"

    def _prohibir(self) -> None:
        raise ValueError(f"Transición inválida desde {self.nombre}")

    def entregar(self, prestamo: Prestamo) -> None:
        self._prohibir()

    def marcar_vencido(self, prestamo: Prestamo, hoy: date) -> None:
        self._prohibir()

    def registrar_devolucion(self, prestamo: Prestamo, fecha: date) -> None:
        self._prohibir()

    def aplicar_multa(self, prestamo: Prestamo, monto: Decimal) -> None:
        self._prohibir()

    def marcar_para_reverificacion(self, prestamo: Prestamo) -> None:
        self._prohibir()


class Reservado(EstadoPrestamoBase):
    nombre = "RESERVADO"

    def entregar(self, prestamo: Prestamo) -> None:
        prestamo._cambiar_a("PRESTADO")

    def marcar_para_reverificacion(self, prestamo: Prestamo) -> None:
        prestamo.requiere_reverificacion = True


class Prestado(EstadoPrestamoBase):
    nombre = "PRESTADO"

    def marcar_vencido(self, prestamo: Prestamo, hoy: date) -> None:
        if prestamo.fecha_vencimiento is not None and hoy <= prestamo.fecha_vencimiento:
            raise ValueError("El préstamo todavía no ha vencido")
        prestamo._cambiar_a("VENCIDO")

    def registrar_devolucion(self, prestamo: Prestamo, fecha: date) -> None:
        if (
            prestamo.fecha_vencimiento is not None
            and fecha > prestamo.fecha_vencimiento
        ):
            raise ValueError("Debe marcar vencido antes de devolver fuera de plazo")
        prestamo.fecha_devolucion = fecha
        prestamo._cambiar_a("DEVUELTO")


class Vencido(EstadoPrestamoBase):
    nombre = "VENCIDO"

    def registrar_devolucion(self, prestamo: Prestamo, fecha: date) -> None:
        if (
            prestamo.fecha_vencimiento is not None
            and fecha <= prestamo.fecha_vencimiento
        ):
            raise ValueError("La devolución de un préstamo vencido es posterior al plazo")
        prestamo.fecha_devolucion = fecha

    def aplicar_multa(self, prestamo: Prestamo, monto: Decimal) -> None:
        if prestamo.fecha_devolucion is None or monto <= 0:
            raise ValueError("La multa requiere devolución registrada y monto > 0")
        prestamo.monto_multa = monto
        prestamo._cambiar_a("CON_MULTA")


class Devuelto(EstadoPrestamoBase):
    nombre = "DEVUELTO"


class ConMulta(EstadoPrestamoBase):
    nombre = "CON_MULTA"


_CLASES_ESTADO = {
    "RESERVADO": Reservado,
    "PRESTADO": Prestado,
    "VENCIDO": Vencido,
    "DEVUELTO": Devuelto,
    "CON_MULTA": ConMulta,
}


def crear_estado(nombre: str) -> EstadoPrestamoBase:
    """Reconstruye el objeto State a partir del valor persistido del enum."""
    try:
        return _CLASES_ESTADO[nombre]()
    except KeyError as error:
        raise ValueError(f"Estado de préstamo desconocido: {nombre}") from error
