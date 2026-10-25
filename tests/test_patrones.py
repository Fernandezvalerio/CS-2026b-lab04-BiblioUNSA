"""Pruebas estructurales de Strategy, Adapter y Factory (Lab 07, E2)."""

from datetime import datetime
from uuid import uuid4

import pytest

from reservas.dominio import (
    Ejemplar,
    EstadoPrestamo,
    Estudiante,
    ResultadoMatricula,
    ValidadorMatricula,
)
from reservas.externos import (
    RepositorioEjemplaresMemoria,
    RepositorioPrestamosMemoria,
    SistemaAcademicoCodigos,
    SistemaAcademicoJSON,
)
from reservas.servicio import ServicioReservas
from reservas.validadores import (
    AdaptadorMatriculaCodigos,
    AdaptadorMatriculaJSON,
    FabricaValidadores,
)


AHORA = datetime(2026, 10, 25, 12, 0)


def test_adapter_json_devuelve_el_contrato_comun():
    estudiante_id = uuid4()
    cliente = SistemaAcademicoJSON(
        matriculas={estudiante_id: True}, fecha_consulta=AHORA
    )
    validador = AdaptadorMatriculaJSON(cliente)

    resultado = validador.validar(estudiante_id)

    assert isinstance(validador, ValidadorMatricula)
    assert isinstance(resultado, ResultadoMatricula)
    assert resultado.es_vigente()
    assert resultado.fecha_consulta == AHORA
    assert not resultado.desde_cache


def test_adapter_codigos_traduce_un_resultado_no_vigente():
    estudiante_id = uuid4()
    cliente = SistemaAcademicoCodigos(
        matriculas={str(estudiante_id): False}, fecha_consulta=AHORA
    )
    validador = AdaptadorMatriculaCodigos(cliente)

    resultado = validador.validar(estudiante_id)

    assert isinstance(validador, ValidadorMatricula)
    assert isinstance(resultado, ResultadoMatricula)
    assert not resultado.es_vigente()
    assert resultado.fecha_consulta == AHORA


def test_factory_crea_la_estrategia_registrada_y_rechaza_desconocida():
    fabrica = FabricaValidadores()
    fabrica.registrar("JSON", lambda: AdaptadorMatriculaJSON(SistemaAcademicoJSON()))

    assert isinstance(fabrica.crear("JSON"), ValidadorMatricula)
    assert fabrica.crear("JSON") is not fabrica.crear("JSON")
    with pytest.raises(ValueError, match="Proveedor no soportado: OTRO"):
        fabrica.crear("OTRO")


def test_open_closed_nuevo_proveedor_sin_modificar_servicio():
    """Una tercera Strategy se añade solo registrándola en la Factory."""

    class ValidadorLocal(ValidadorMatricula):
        def validar(self, estudiante_id):
            return ResultadoMatricula(vigente=True, fecha_consulta=AHORA)

    fabrica = FabricaValidadores()
    fabrica.registrar("LOCAL", ValidadorLocal)

    estudiante = Estudiante(correo_institucional="nuevo@unsa.edu.pe")
    ejemplar = Ejemplar(codigo_inventario="E2-001", biblioteca="Central")
    prestamos = RepositorioPrestamosMemoria()
    servicio = ServicioReservas(
        estudiantes={estudiante.id: estudiante},
        repo_ejemplares=RepositorioEjemplaresMemoria([ejemplar]),
        repo_prestamos=prestamos,
        academico_json=SistemaAcademicoJSON(),
        academico_codigos=SistemaAcademicoCodigos(),
        proveedor="LOCAL",
        fabrica=fabrica,
        ahora=AHORA,
    )

    prestamo = servicio.reservar_libro(estudiante.id, ejemplar.id)

    assert prestamo.estado == EstadoPrestamo.RESERVADO
    assert prestamos.prestamos == [prestamo]
    assert not ejemplar.esta_disponible()
    assert servicio.eventos == [f"reserva_creada:{prestamo.id}"]
