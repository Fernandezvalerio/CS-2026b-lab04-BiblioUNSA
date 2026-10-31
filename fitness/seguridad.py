"""Prototipo de reglas de acceso tras validación criptográfica OIDC externa."""

from __future__ import annotations

EMISOR_PERMITIDO = "https://idp.unsa.edu.pe"
DOMINIO_PERMITIDO = "@unsa.edu.pe"


def identidad_autorizada(
    correo: str,
    emisor: str,
    correo_verificado: bool,
    token_verificado: bool,
) -> bool:
    """No valida una firma: token_verificado debe provenir del middleware OIDC."""
    return (
        token_verificado
        and correo_verificado
        and emisor == EMISOR_PERMITIDO
        and correo.lower().strip().endswith(DOMINIO_PERMITIDO)
    )


def simular_intentos_externos() -> dict[str, int]:
    # Mezcla de correos externos, emisores falsos y claims no verificados.
    casos = []
    for numero in range(10):
        casos.append((f"externo{numero}@gmail.com", EMISOR_PERMITIDO, True, True))
        casos.append((f"alumno{numero}@unsa.edu.pe", "https://sitio-invalido.test", True, True))
        casos.append((f"alumno{numero}@unsa.edu.pe", EMISOR_PERMITIDO, True, False))
    rechazados = sum(not identidad_autorizada(*caso) for caso in casos)
    return {"intentos": len(casos), "rechazados": rechazados, "autorizados": len(casos) - rechazados}


if __name__ == "__main__":
    print(simular_intentos_externos())
