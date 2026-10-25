"""E1 - versión inicial de HU-03, deliberadamente sin patrones GoF.

El método reservar_libro sigue el diagrama de secuencia del Lab 05.
Conservamos los condicionales y las responsabilidades mezcladas para
caracterizar primero el comportamiento y refactorizarlo en E2-E4.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID

from reservas.dominio import (
    Estudiante,
    Prestamo,
    ResultadoMatricula,
)
from reservas.externos import (
    RepositorioEjemplaresMemoria,
    RepositorioPrestamosMemoria,
    SistemaAcademicoCodigos,
    SistemaAcademicoJSON,
)


class IntegracionException(ConnectionError):
    """El sistema académico no respondió y no hay caché vigente."""


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
    ) -> None:
        self.estudiantes = estudiantes
        self.repo_ejemplares = repo_ejemplares
        self.repo_prestamos = repo_prestamos
        self.academico_json = academico_json
        self.academico_codigos = academico_codigos
        self.proveedor = proveedor
        self.cache = dict(cache or {})
        self.ahora = ahora or datetime.now()
        self.eventos: list[str] = []
        self.programaciones: list[tuple[UUID, datetime]] = []

    def reservar_libro(self, estudiante_id: UUID, ejemplar_id: UUID) -> Prestamo:
        if self.proveedor not in ("JSON", "CODIGOS"):
            raise ValueError(f"Proveedor no soportado: {self.proveedor}")

        resultado = None
        # Tres intentos de hasta 1 s cada uno: presupuesto total de 3 s (ADR-003).
        for intento in range(3):
            try:
                if self.proveedor == "JSON":
                    respuesta = self.academico_json.consultar_matricula(
                        estudiante_id, timeout_segundos=1
                    )
                    resultado = ResultadoMatricula(
                        vigente=respuesta["vigente"],
                        fecha_consulta=respuesta["consultado_en"],
                        desde_cache=False,
                    )
                elif self.proveedor == "CODIGOS":
                    codigo, estado, consultado = (
                        self.academico_codigos.obtener_estado_alumno(
                            str(estudiante_id), tiempo_maximo_ms=1000
                        )
                    )
                    if codigo != 200:
                        raise IntegracionException("Error del sistema académico")
                    resultado = ResultadoMatricula(
                        vigente=estado == 1,
                        fecha_consulta=consultado,
                        desde_cache=False,
                    )
                self.cache[estudiante_id] = resultado
                break
            except TimeoutError:
                if intento == 2:
                    resultado = None

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
            self.eventos.append(f"reverificacion_programada:{prestamo.id}")

        self.repo_prestamos.guardar(prestamo)
        self.eventos.append(f"reserva_creada:{prestamo.id}")
        return prestamo
