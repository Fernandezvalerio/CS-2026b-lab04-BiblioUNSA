"""Pruebas del patrón State y del diagrama estados-prestamo.mmd (E3)."""

from datetime import date
from decimal import Decimal

import pytest

from reservas.dominio import Ejemplar, EstadoPrestamo, Estudiante, Prestamo
from reservas.estados import ConMulta, Devuelto, Prestado, Reservado, Vencido


FECHA_LIMITE = date(2026, 10, 24)


def prestamo(estado=EstadoPrestamo.RESERVADO):
    return Prestamo(
        estudiante=Estudiante(correo_institucional="alumno@unsa.edu.pe"),
        ejemplar=Ejemplar(codigo_inventario="EST-01", biblioteca="Central"),
        fecha_vencimiento=FECHA_LIMITE,
        estado=estado,
    )


def test_se_crea_reservado_con_objeto_state():
    p = prestamo()
    assert p.estado == EstadoPrestamo.RESERVADO
    assert isinstance(p._estado_objeto, Reservado)


def test_reservado_pasa_a_prestado_al_entregar():
    p = prestamo()
    p.entregar()
    assert p.estado == EstadoPrestamo.PRESTADO
    assert isinstance(p._estado_objeto, Prestado)


def test_reservado_puede_marcar_reverificacion_sin_cambiar_estado():
    p = prestamo()
    p.marcar_para_reverificacion()
    assert p.requiere_reverificacion is True
    assert p.estado == EstadoPrestamo.RESERVADO


def test_prestado_devuelto_a_tiempo_queda_finalizado():
    p = prestamo()
    p.entregar()
    p.registrar_devolucion(FECHA_LIMITE)
    assert p.estado == EstadoPrestamo.DEVUELTO
    assert isinstance(p._estado_objeto, Devuelto)
    assert p.fecha_devolucion == FECHA_LIMITE


def test_prestado_vencido_devuelto_con_multa():
    p = prestamo()
    p.entregar()
    p.marcar_vencido(hoy=date(2026, 10, 25))
    assert p.estado == EstadoPrestamo.VENCIDO
    assert isinstance(p._estado_objeto, Vencido)

    p.registrar_devolucion(date(2026, 10, 26))
    assert p.estado == EstadoPrestamo.VENCIDO
    p.aplicar_multa(Decimal("4.50"))
    assert p.estado == EstadoPrestamo.CON_MULTA
    assert isinstance(p._estado_objeto, ConMulta)
    assert p.monto_multa == Decimal("4.50")


def test_transicion_invalida_no_permite_devolver_reservado():
    p = prestamo()
    with pytest.raises(ValueError, match="Transición inválida desde RESERVADO"):
        p.registrar_devolucion(FECHA_LIMITE)
    assert p.estado == EstadoPrestamo.RESERVADO
    assert p.fecha_devolucion is None


def test_no_puede_entregar_dos_veces():
    p = prestamo()
    p.entregar()
    with pytest.raises(ValueError, match="Transición inválida desde PRESTADO"):
        p.entregar()
    assert p.estado == EstadoPrestamo.PRESTADO


def test_no_puede_marcar_vencido_si_no_ha_pasado_la_fecha():
    p = prestamo()
    p.entregar()
    with pytest.raises(ValueError, match="todavía no ha vencido"):
        p.marcar_vencido(hoy=FECHA_LIMITE)
    assert p.estado == EstadoPrestamo.PRESTADO


def test_devolucion_tardia_exige_pasar_primero_por_vencido():
    p = prestamo()
    p.entregar()
    with pytest.raises(ValueError, match="Debe marcar vencido"):
        p.registrar_devolucion(date(2026, 10, 25))
    assert p.estado == EstadoPrestamo.PRESTADO
    assert p.fecha_devolucion is None


def test_multa_requiere_devolucion_y_monto_positivo():
    p = prestamo()
    p.entregar()
    p.marcar_vencido(hoy=date(2026, 10, 25))
    with pytest.raises(ValueError, match="La multa requiere devolución"):
        p.aplicar_multa(Decimal("4.50"))
    p.registrar_devolucion(date(2026, 10, 26))
    with pytest.raises(ValueError, match="monto > 0"):
        p.aplicar_multa(Decimal("0"))
    assert p.estado == EstadoPrestamo.VENCIDO


def test_devuelto_y_con_multa_son_estados_finales():
    devuelto = prestamo(EstadoPrestamo.DEVUELTO)
    con_multa = prestamo(EstadoPrestamo.CON_MULTA)
    with pytest.raises(ValueError, match="Transición inválida desde DEVUELTO"):
        devuelto.entregar()
    with pytest.raises(ValueError, match="Transición inválida desde CON_MULTA"):
        con_multa.marcar_para_reverificacion()


def test_reconstruye_objeto_state_desde_estado_guardado():
    p = prestamo(EstadoPrestamo.PRESTADO)
    assert isinstance(p._estado_objeto, Prestado)
    p.registrar_devolucion(FECHA_LIMITE)
    assert p.estado == EstadoPrestamo.DEVUELTO


def test_no_permita_reverificar_cuando_ya_esta_prestado():
    p = prestamo()
    p.entregar()
    with pytest.raises(ValueError, match="Transición inválida desde PRESTADO"):
        p.marcar_para_reverificacion()
    assert p.requiere_reverificacion is False
