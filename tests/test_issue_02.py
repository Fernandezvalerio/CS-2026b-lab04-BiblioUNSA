from datetime import datetime
import pytest
from reservas.dominio import Estudiante, Ejemplar
from reservas.externos import (RepositorioEjemplaresMemoria, RepositorioPrestamosMemoria,
                               SistemaAcademicoJSON, SistemaAcademicoCodigos)
from reservas.servicio import ServicioReservas, MatriculaNoVigente
from reservas.validadores import IntegracionException


def test_matricula_textual_no_autoriza():
    estudiante = Estudiante("prueba@unsa.edu.pe")
    ejemplar = Ejemplar("LAB10-01", "Central")
    prestamos = RepositorioPrestamosMemoria()
    cliente = SistemaAcademicoJSON({estudiante.id: "false"})
    servicio = ServicioReservas({estudiante.id: estudiante}, RepositorioEjemplaresMemoria([ejemplar]),
                               prestamos, cliente, SistemaAcademicoCodigos(), ahora=datetime(2026, 11, 20))
    with pytest.raises((MatriculaNoVigente, IntegracionException)):
        servicio.reservar_libro(estudiante.id, ejemplar.id)
    assert ejemplar.esta_disponible()
    assert not prestamos.prestamos
