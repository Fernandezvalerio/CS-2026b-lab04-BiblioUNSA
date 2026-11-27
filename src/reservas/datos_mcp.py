"""Datos ficticios y consulta de catálogo para la demostración del Lab 11.

Cada instancia tiene sus propios repositorios. No hay persistencia ni red.
"""
from datetime import date
from uuid import UUID

from reservas.dominio import Ejemplar, Estudiante, Libro, Prestamo, EstadoPrestamo
from reservas.externos import (
    RepositorioEjemplaresMemoria, RepositorioPrestamosMemoria,
    SistemaAcademicoJSON, SistemaAcademicoCodigos,
)
from reservas.servicio import ServicioReservas


def _id(n: int) -> UUID:
    return UUID(f"00000000-0000-4000-8000-{n:012d}")


class DatosMCP:
    def __init__(self) -> None:
        self.estudiantes = {
            _id(1): Estudiante("alumno1@example.invalid", id=_id(1)),
            _id(2): Estudiante("alumno2@example.invalid", id=_id(2)),
        }
        e1 = Ejemplar("LAB11-101", "Central", id=_id(101))
        e2 = Ejemplar("LAB11-102", "Central", False, _id(102))
        e3 = Ejemplar("LAB11-103", "Ingeniería", False, _id(103))
        e4 = Ejemplar("LAB11-104", "Ingeniería", id=_id(104))
        e5 = Ejemplar("LAB11-105", "Central", False, _id(105))
        e6 = Ejemplar("LAB11-106", "Central", id=_id(106))
        self.libros = [
            Libro("Redes de computadoras", "Autor de prueba A", "9780000000019", [e1, e2], _id(201)),
            Libro("Sistemas operativos", "Autor de prueba B", "9780000000026", [e3, e4], _id(202)),
            Libro("Bases de datos", "Autor de prueba C", "9780000000033", [e5, e6], _id(203)),
        ]
        self.repo_ejemplares = RepositorioEjemplaresMemoria([e1, e2, e3, e4, e5, e6])
        self.repo_prestamos = RepositorioPrestamosMemoria()
        alumno = self.estudiantes[_id(1)]
        for prestamo in (
            Prestamo(alumno, e2, fecha_vencimiento=date(2026, 11, 20), estado=EstadoPrestamo.PRESTADO, id=_id(301)),
            Prestamo(alumno, e3, fecha_vencimiento=date(2026, 11, 23), estado=EstadoPrestamo.VENCIDO, id=_id(302)),
            Prestamo(alumno, e5, fecha_vencimiento=date(2026, 11, 27), estado=EstadoPrestamo.PRESTADO, id=_id(303)),
            Prestamo(alumno, e6, fecha_vencimiento=date(2026, 11, 18), fecha_devolucion=date(2026, 11, 19), estado=EstadoPrestamo.DEVUELTO, id=_id(304)),
        ):
            self.repo_prestamos.guardar(prestamo)
        self.servicio = ServicioReservas(
            self.estudiantes, self.repo_ejemplares, self.repo_prestamos,
            SistemaAcademicoJSON({_id(1): True, _id(2): False}),
            SistemaAcademicoCodigos(),
        )

    def buscar_libros(self, consulta: str, biblioteca: str = "") -> list[tuple[Libro, list[Ejemplar]]]:
        """Coincidencia parcial de título/autor y filtro opcional de biblioteca."""
        consulta, biblioteca = consulta.casefold(), biblioteca.casefold()
        resultado = []
        for libro in self.libros:
            if consulta not in libro.titulo.casefold() and consulta not in libro.autor.casefold():
                continue
            ejemplares = [e for e in libro.ejemplares if biblioteca in e.biblioteca.casefold()]
            if ejemplares or not biblioteca:
                resultado.append((libro, ejemplares))
        return resultado
