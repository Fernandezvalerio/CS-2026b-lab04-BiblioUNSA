"""E2-E4: reservas con Strategy/Adapter/Factory, Decorator y Observer.

Los reintentos y los avisos se delegan a colaboradores. La política de caché
permanece en el servicio para conservar el comportamiento de E1-E3.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID

from reservas.decoradores import ConReintentos
from reservas.dominio import Estudiante, Prestamo, ResultadoMatricula
from reservas.eventos import (
    EventoReserva,
    ObservadorAvisos,
    ObservadorHistorial,
    PublicadorEventos,
)
from reservas.externos import (
    RepositorioEjemplaresMemoria,
    RepositorioPrestamosMemoria,
    SistemaAcademicoCodigos,
    SistemaAcademicoJSON,
)
from reservas.validadores import (
    AdaptadorMatriculaCodigos,
    AdaptadorMatriculaJSON,
    FabricaValidadores,
    IntegracionException,
)


class MatriculaNoVigente(ValueError):
    """El estudiante no tiene matrícula vigente."""


class EjemplarNoDisponible(ValueError):
    """El ejemplar ya está reservado o prestado."""


class ServicioReservas:
    def __init__(
        self,
        estudiantes: dict[UUID, Estudiante],
        repo_ejemplares: RepositorioEjemplaresMemoria,
        repo_prestamos: RepositorioPrestamosMemoria,
        academico_json: SistemaAcademicoJSON,
        academico_codigos: SistemaAcademicoCodigos,
        proveedor: str = "JSON",
        cache: dict[UUID, ResultadoMatricula] | None = None,
        ahora: datetime | None = None,
        fabrica: FabricaValidadores | None = None,
        publicador: PublicadorEventos | None = None,
    ) -> None:
        self.estudiantes = estudiantes
        self.repo_ejemplares = repo_ejemplares
        self.repo_prestamos = repo_prestamos
        self.proveedor = proveedor
        self.cache = dict(cache or {})
        self.ahora = ahora or datetime.now()
        self.programaciones: list[tuple[UUID, datetime]] = []

        # Observer: un mismo evento llega al historial y a los avisos.
        self.publicador = publicador if publicador is not None else PublicadorEventos()
        historial = ObservadorHistorial()
        avisos = ObservadorAvisos()
        self.publicador.suscribir(historial)
        self.publicador.suscribir(avisos)
        self.eventos = historial.eventos  # Compatibilidad con la red de E1-E3.
        self.notificaciones = avisos.avisos

        # La Factory por defecto se ensambla una vez. Para agregar otra
        # estrategia, el cliente puede inyectar una Factory ya registrada.
        self.fabrica = fabrica if fabrica is not None else FabricaValidadores()
        if fabrica is None:
            self.fabrica.registrar(
                "JSON", lambda: AdaptadorMatriculaJSON(academico_json)
            )
            self.fabrica.registrar(
                "CODIGOS", lambda: AdaptadorMatriculaCodigos(academico_codigos)
            )

    def reservar_libro(self, estudiante_id: UUID, ejemplar_id: UUID) -> Prestamo:
        # Decorator: el flujo no administra los reintentos del SDK.
        validador = ConReintentos(self.fabrica.crear(self.proveedor), intentos=3)

        resultado = None
        try:
            resultado = validador.validar(estudiante_id)
            self.cache[estudiante_id] = resultado
        except TimeoutError:
            # El último timeout habilita la recuperación por caché (ADR-003).
            pass

        if resultado is None:
            guardado = self.cache.get(estudiante_id)
            if guardado is not None:
                antiguedad = self.ahora - guardado.fecha_consulta
                if timedelta(0) <= antiguedad <= timedelta(hours=24):
                    resultado = ResultadoMatricula(
                        vigente=guardado.vigente,
                        fecha_consulta=guardado.fecha_consulta,
                        desde_cache=True,
                    )
            if resultado is None:
                raise IntegracionException("Intente nuevamente en unos minutos")

        if not resultado.es_vigente():
            raise MatriculaNoVigente("Matrícula no vigente")

        ejemplar = self.repo_ejemplares.buscar(ejemplar_id)
        if not ejemplar.esta_disponible():
            raise EjemplarNoDisponible("Ejemplar no disponible")

        ejemplar.marcar_reservado()
        self.repo_ejemplares.guardar(ejemplar)
        prestamo = Prestamo(
            estudiante=self.estudiantes[estudiante_id],
            ejemplar=ejemplar,
            fecha_reserva=self.ahora,
        )
        if resultado.desde_cache:
            prestamo.marcar_para_reverificacion()
            fecha_programada = self.ahora + timedelta(minutes=30)
            self.programaciones.append((prestamo.id, fecha_programada))
            self.publicador.publicar(EventoReserva("reverificacion_programada", prestamo.id))

        self.repo_prestamos.guardar(prestamo)
        self.publicador.publicar(EventoReserva("reserva_creada", prestamo.id))
        return prestamo
