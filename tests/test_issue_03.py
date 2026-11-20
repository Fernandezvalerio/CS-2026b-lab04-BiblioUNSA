from datetime import date
from reservas.dominio import Estudiante, Ejemplar, Prestamo, EstadoPrestamo
from reservas.externos import RepositorioPrestamosMemoria


def test_devuelto_no_figura_como_vencido():
    hoy = date(2026, 11, 20)
    estudiante = Estudiante("prueba@unsa.edu.pe")
    activo = Prestamo(estudiante, Ejemplar("LAB10-A", "Central"), fecha_vencimiento=date(2026, 11, 18), estado=EstadoPrestamo.VENCIDO)
    devuelto = Prestamo(estudiante, Ejemplar("LAB10-B", "Central"), fecha_vencimiento=date(2026, 11, 18), estado=EstadoPrestamo.VENCIDO)
    devuelto.registrar_devolucion(date(2026, 11, 19))
    en_plazo = Prestamo(estudiante, Ejemplar("LAB10-C", "Central"), fecha_vencimiento=hoy, estado=EstadoPrestamo.PRESTADO)
    repo = RepositorioPrestamosMemoria()
    for p in (activo, devuelto, en_plazo):
        repo.guardar(p)
    assert repo.buscar_vencidos(hoy) == [activo]
