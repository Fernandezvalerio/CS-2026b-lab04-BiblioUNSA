"""Pruebas de Observer y Decorator (Lab 07, E4)."""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from reservas.decoradores import ConReintentos
from reservas.dominio import Ejemplar, Estudiante, ResultadoMatricula, ValidadorMatricula
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
from reservas.servicio import ServicioReservas
from reservas.validadores import IntegracionException


HOY = datetime(2026, 10, 25, 12, 0)


def escenario_servicio(*, fallas=0, cache=None):
    estudiante = Estudiante(correo_institucional="alumno@unsa.edu.pe")
    ejemplar = Ejemplar(codigo_inventario="OBS-01", biblioteca="Central")
    servicio = ServicioReservas(
        estudiantes={estudiante.id: estudiante},
        repo_ejemplares=RepositorioEjemplaresMemoria([ejemplar]),
        repo_prestamos=RepositorioPrestamosMemoria(),
        academico_json=SistemaAcademicoJSON(
            matriculas={estudiante.id: True}, fecha_consulta=HOY, fallas=fallas
        ),
        academico_codigos=SistemaAcademicoCodigos(),
        cache={estudiante.id: cache} if cache is not None else None,
        ahora=HOY,
    )
    return servicio, estudiante, ejemplar


def test_observer_publica_un_evento_a_dos_suscriptores():
    publicador = PublicadorEventos()
    historial = ObservadorHistorial()
    avisos = ObservadorAvisos()
    publicador.suscribir(historial)
    publicador.suscribir(avisos)
    prestamo_id = uuid4()

    publicador.publicar(EventoReserva("reserva_creada", prestamo_id))

    assert historial.eventos == [f"reserva_creada:{prestamo_id}"]
    assert avisos.avisos == [f"biblioteca:reserva:{prestamo_id}"]


def test_observer_permite_desuscribir_sin_afectar_a_los_demas():
    publicador = PublicadorEventos()
    historial = ObservadorHistorial()
    avisos = ObservadorAvisos()
    publicador.suscribir(historial)
    publicador.suscribir(avisos)
    publicador.desuscribir(avisos)
    identificador = uuid4()

    publicador.publicar(EventoReserva("reserva_creada", identificador))

    assert historial.eventos == [f"reserva_creada:{identificador}"]
    assert avisos.avisos == []


def test_servicio_avisa_al_crear_reserva_sin_mensajes_manual_en_el_metodo():
    servicio, estudiante, ejemplar = escenario_servicio()

    prestamo = servicio.reservar_libro(estudiante.id, ejemplar.id)

    assert servicio.eventos == [f"reserva_creada:{prestamo.id}"]
    assert servicio.notificaciones == [f"biblioteca:reserva:{prestamo.id}"]


def test_servicio_avisa_cuando_usa_cache_y_programa_reverificacion():
    cache = ResultadoMatricula(
        vigente=True, fecha_consulta=HOY - timedelta(hours=2)
    )
    servicio, estudiante, ejemplar = escenario_servicio(fallas=3, cache=cache)

    prestamo = servicio.reservar_libro(estudiante.id, ejemplar.id)

    assert prestamo.requiere_reverificacion
    assert servicio.eventos == [
        f"reverificacion_programada:{prestamo.id}",
        f"reserva_creada:{prestamo.id}",
    ]
    assert servicio.notificaciones == [
        f"biblioteca:reverificar:{prestamo.id}",
        f"biblioteca:reserva:{prestamo.id}",
    ]


def test_decorator_reintenta_dos_timeouts_y_luego_devuelve_respuesta():
    class ValidadorLento(ValidadorMatricula):
        def __init__(self):
            self.llamadas = 0

        def validar(self, estudiante_id):
            self.llamadas += 1
            if self.llamadas <= 2:
                raise TimeoutError("API sin respuesta")
            return ResultadoMatricula(vigente=True, fecha_consulta=HOY)

    lento = ValidadorLento()
    decorado = ConReintentos(lento, intentos=3)

    resultado = decorado.validar(uuid4())

    assert resultado.es_vigente()
    assert lento.llamadas == 3


def test_decorator_no_reintenta_fallos_distintos_de_timeout():
    class ValidadorConError(ValidadorMatricula):
        def __init__(self):
            self.llamadas = 0

        def validar(self, estudiante_id):
            self.llamadas += 1
            raise IntegracionException("HTTP 503")

    fallido = ValidadorConError()
    with pytest.raises(IntegracionException, match="HTTP 503"):
        ConReintentos(fallido).validar(uuid4())
    assert fallido.llamadas == 1


def test_decorator_propaga_timeout_tras_agotar_intentos():
    class ValidadorSinRespuesta(ValidadorMatricula):
        def __init__(self):
            self.llamadas = 0

        def validar(self, estudiante_id):
            self.llamadas += 1
            raise TimeoutError("Sigue sin responder")

    fallido = ValidadorSinRespuesta()
    with pytest.raises(TimeoutError, match="Sigue sin responder"):
        ConReintentos(fallido, intentos=3).validar(uuid4())
    assert fallido.llamadas == 3


def test_decorator_rechaza_configuracion_sin_intentos():
    class ValidadorFijo(ValidadorMatricula):
        def validar(self, estudiante_id):
            return ResultadoMatricula(vigente=True, fecha_consulta=HOY)

    with pytest.raises(ValueError, match="cantidad de intentos"):
        ConReintentos(ValidadorFijo(), intentos=0)
