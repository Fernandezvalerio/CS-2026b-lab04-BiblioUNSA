"""Caracterización de HU-03: estos casos se conservarán en E2-E4.

El fixture ejecuta cada prueba contra E1 y E2 para comprobar que el
comportamiento observable no cambió al introducir los patrones.
"""

import importlib
from datetime import datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest

from reservas.dominio import Ejemplar, EstadoPrestamo, Estudiante, ResultadoMatricula
from reservas.externos import (
    RepositorioEjemplaresMemoria,
    RepositorioPrestamosMemoria,
    SistemaAcademicoCodigos,
    SistemaAcademicoJSON,
)


HOY = datetime(2026, 10, 25, 12, 0, 0)


@pytest.fixture(
    params=["reservas.antes.servicio", "reservas.servicio"],
    ids=["antes", "despues"],
)
def m(request):
    """La misma red de seguridad protege ambas implementaciones."""
    return importlib.import_module(request.param)


def escenario(
    m,
    proveedor="JSON",
    vigente=True,
    disponible=True,
    fallas_json=0,
    fallas_codigos=0,
    cache=None,
    codigo_http=200,
):
    estudiante = Estudiante(correo_institucional="estudiante@unsa.edu.pe")
    ejemplar = Ejemplar(codigo_inventario="B-001", biblioteca="Central", disponible=disponible)
    json = SistemaAcademicoJSON(
        matriculas={estudiante.id: vigente}, fecha_consulta=HOY, fallas=fallas_json
    )
    codigos = SistemaAcademicoCodigos(
        matriculas={str(estudiante.id): vigente},
        fecha_consulta=HOY,
        fallas=fallas_codigos,
        codigo_http=codigo_http,
    )
    ejemplares = RepositorioEjemplaresMemoria([ejemplar])
    prestamos = RepositorioPrestamosMemoria()
    servicio = m.ServicioReservas(
        estudiantes={estudiante.id: estudiante},
        repo_ejemplares=ejemplares,
        repo_prestamos=prestamos,
        academico_json=json,
        academico_codigos=codigos,
        proveedor=proveedor,
        cache={estudiante.id: cache} if cache is not None else None,
        ahora=HOY,
    )
    return SimpleNamespace(
        estudiante=estudiante,
        ejemplar=ejemplar,
        json=json,
        codigos=codigos,
        ejemplares=ejemplares,
        prestamos=prestamos,
        servicio=servicio,
    )


def reservar(s):
    return s.servicio.reservar_libro(s.estudiante.id, s.ejemplar.id)


def test_json_vigente_crea_reserva_y_ocupa_ejemplar(m):
    s = escenario(m)
    prestamo = reservar(s)
    assert prestamo.estado == EstadoPrestamo.RESERVADO
    assert prestamo.estudiante.id == s.estudiante.id
    assert not s.ejemplar.esta_disponible()
    assert s.prestamos.prestamos == [prestamo]
    assert s.servicio.eventos == [f"reserva_creada:{prestamo.id}"]


def test_api_codigos_vigente_tambien_permite_reservar(m):
    s = escenario(m, proveedor="CODIGOS")
    prestamo = reservar(s)
    assert prestamo.estado == EstadoPrestamo.RESERVADO
    assert s.prestamos.prestamos == [prestamo]
    assert not prestamo.requiere_reverificacion


def test_matricula_no_vigente_rechaza_sin_modificar_ejemplar(m):
    s = escenario(m, vigente=False)
    with pytest.raises(m.MatriculaNoVigente, match="Matrícula no vigente"):
        reservar(s)
    assert s.ejemplar.esta_disponible()
    assert s.prestamos.prestamos == []
    assert s.servicio.eventos == []


def test_ejemplar_no_disponible_rechaza_sin_crear_prestamo(m):
    s = escenario(m, disponible=False)
    with pytest.raises(m.EjemplarNoDisponible, match="Ejemplar no disponible"):
        reservar(s)
    assert s.prestamos.prestamos == []
    assert s.servicio.eventos == []


def test_dos_timeouts_json_y_luego_exito_no_duplica_reserva(m):
    s = escenario(m, fallas_json=2)
    prestamo = reservar(s)
    assert prestamo.estado == EstadoPrestamo.RESERVADO
    assert s.json.llamadas == 3
    assert len(s.prestamos.prestamos) == 1


def test_timeout_codigos_y_luego_exito(m):
    s = escenario(m, proveedor="CODIGOS", fallas_codigos=1)
    prestamo = reservar(s)
    assert prestamo.estado == EstadoPrestamo.RESERVADO
    assert s.codigos.llamadas == 2


def test_timeout_total_con_cache_reciente_reserva_y_programa_reverificacion(m):
    cache = ResultadoMatricula(vigente=True, fecha_consulta=HOY - timedelta(hours=2))
    s = escenario(m, fallas_json=3, cache=cache)
    prestamo = reservar(s)
    assert prestamo.estado == EstadoPrestamo.RESERVADO
    assert prestamo.requiere_reverificacion is True
    assert s.servicio.programaciones == [(prestamo.id, HOY + timedelta(minutes=30))]
    assert s.servicio.eventos == [
        f"reverificacion_programada:{prestamo.id}",
        f"reserva_creada:{prestamo.id}",
    ]
    assert s.json.llamadas == 3


def test_cache_de_exactamente_24_horas_es_valida(m):
    cache = ResultadoMatricula(vigente=True, fecha_consulta=HOY - timedelta(hours=24))
    s = escenario(m, fallas_json=3, cache=cache)
    assert reservar(s).requiere_reverificacion is True


def test_cache_mayor_de_24_horas_no_se_acepta(m):
    cache = ResultadoMatricula(
        vigente=True, fecha_consulta=HOY - timedelta(hours=24, seconds=1)
    )
    s = escenario(m, fallas_json=3, cache=cache)
    with pytest.raises(m.IntegracionException, match="Intente nuevamente"):
        reservar(s)
    assert s.prestamos.prestamos == []
    assert s.ejemplar.esta_disponible()


def test_timeout_total_sin_cache_rechaza_reserva(m):
    s = escenario(m, fallas_json=3)
    with pytest.raises(m.IntegracionException, match="Intente nuevamente"):
        reservar(s)
    assert s.prestamos.prestamos == []
    assert s.servicio.eventos == []


def test_cache_reciente_pero_matricula_no_vigente_no_autoriza(m):
    cache = ResultadoMatricula(vigente=False, fecha_consulta=HOY - timedelta(hours=1))
    s = escenario(m, fallas_json=3, cache=cache)
    with pytest.raises(m.MatriculaNoVigente):
        reservar(s)
    assert s.ejemplar.esta_disponible()
    assert s.prestamos.prestamos == []


def test_proveedor_desconocido_se_rechaza_sin_efectos(m):
    s = escenario(m, proveedor="OTRO")
    with pytest.raises(ValueError, match="Proveedor no soportado"):
        reservar(s)
    assert s.ejemplar.esta_disponible()
    assert s.prestamos.prestamos == []


def test_doble_reserva_del_mismo_ejemplar_no_crea_dos_prestamos(m):
    s = escenario(m)
    primero = reservar(s)
    with pytest.raises(m.EjemplarNoDisponible):
        reservar(s)
    assert s.prestamos.prestamos == [primero]
    assert s.servicio.eventos == [f"reserva_creada:{primero.id}"]


def test_respuesta_http_erronea_no_crea_reserva(m):
    s = escenario(m, proveedor="CODIGOS", codigo_http=503)
    with pytest.raises(m.IntegracionException, match="Error del sistema académico"):
        reservar(s)
    assert s.ejemplar.esta_disponible()
    assert s.prestamos.prestamos == []


def test_cache_con_fecha_futura_no_se_usa(m):
    cache = ResultadoMatricula(vigente=True, fecha_consulta=HOY + timedelta(seconds=1))
    s = escenario(m, fallas_json=3, cache=cache)
    with pytest.raises(m.IntegracionException):
        reservar(s)
    assert s.prestamos.prestamos == []
