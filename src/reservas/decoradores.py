"""Lab 07, E4: responsabilidades transversales con Decorator."""

from __future__ import annotations

from uuid import UUID

from reservas.dominio import ResultadoMatricula, ValidadorMatricula


class ConReintentos(ValidadorMatricula):
    """Reintenta solo ante TimeoutError, sin alterar la respuesta del validador.

    Cada adaptador conserva un timeout de 1 s; tres intentos suman como
    máximo 3 s de espera por timeouts, como señala el ADR-003.
    """

    def __init__(self, interno: ValidadorMatricula, intentos: int = 3) -> None:
        if intentos < 1:
            raise ValueError("La cantidad de intentos debe ser positiva")
        self.interno = interno
        self.intentos = intentos

    def validar(self, estudiante_id: UUID) -> ResultadoMatricula:
        for intento in range(self.intentos):
            try:
                return self.interno.validar(estudiante_id)
            except TimeoutError:
                if intento == self.intentos - 1:
                    raise
        raise AssertionError("Bucle de reintentos agotado inesperadamente")
