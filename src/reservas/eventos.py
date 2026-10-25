"""Lab 07, E4: Observer para eventos del módulo de reservas.

Los mensajes son simulados en memoria: no se conectan servicios de correo,
WhatsApp ni otras integraciones reales durante las pruebas.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class EventoReserva:
    tipo: str
    prestamo_id: UUID


class ObservadorEventos(Protocol):
    def actualizar(self, evento: EventoReserva) -> None: ...


class PublicadorEventos:
    def __init__(self) -> None:
        self._suscriptores: list[ObservadorEventos] = []

    def suscribir(self, observador: ObservadorEventos) -> None:
        if observador not in self._suscriptores:
            self._suscriptores.append(observador)

    def desuscribir(self, observador: ObservadorEventos) -> None:
        if observador in self._suscriptores:
            self._suscriptores.remove(observador)

    def publicar(self, evento: EventoReserva) -> None:
        for observador in tuple(self._suscriptores):
            observador.actualizar(evento)


class ObservadorHistorial:
    """Primer suscriptor: mantiene el historial observable de E1-E3."""

    def __init__(self) -> None:
        self.eventos: list[str] = []

    def actualizar(self, evento: EventoReserva) -> None:
        self.eventos.append(f"{evento.tipo}:{evento.prestamo_id}")


class ObservadorAvisos:
    """Segundo suscriptor: prepara avisos para la biblioteca en memoria."""

    def __init__(self) -> None:
        self.avisos: list[str] = []

    def actualizar(self, evento: EventoReserva) -> None:
        if evento.tipo == "reserva_creada":
            self.avisos.append(f"biblioteca:reserva:{evento.prestamo_id}")
        elif evento.tipo == "reverificacion_programada":
            self.avisos.append(f"biblioteca:reverificar:{evento.prestamo_id}")
