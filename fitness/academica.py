"""Simulación de una interrupción de la API académica; no conecta con la UNSA."""

from __future__ import annotations

from random import Random


def simular_caida(
    cantidad: int = 1000,
    prob_fallo: float = 0.35,
    fraccion_cache: float = 0.8,
    estrategia: str = "respaldo",
    semilla: int = 2026,
) -> dict[str, float | int]:
    """Compara solicitudes idénticas con y sin respaldo de validación reciente.

    Se supone que todas las matrículas del experimento están vigentes; la
    fracción con caché tiene una validación previa de no más de 24 h.
    """
    if cantidad <= 0 or not 0 <= prob_fallo <= 1 or not 0 <= fraccion_cache <= 1:
        raise ValueError("Parámetros fuera de rango")
    if estrategia not in {"sin_respaldo", "respaldo"}:
        raise ValueError("Estrategia no reconocida")

    aleatorio = Random(semilla)
    fallos = bloqueadas = bloqueadas_con_cache = 0
    usuarios_con_cache = pendientes = 0
    peor_espera_s = 0.0
    for _ in range(cantidad):
        tiene_cache = aleatorio.random() < fraccion_cache
        falla = aleatorio.random() < prob_fallo
        usuarios_con_cache += int(tiene_cache)
        fallos += int(falla)
        peor_espera_s = max(peor_espera_s, 3.0 if falla else 0.12)
        puede_continuar = not falla or (estrategia == "respaldo" and tiene_cache)
        if not puede_continuar:
            bloqueadas += 1
            bloqueadas_con_cache += int(tiene_cache)
        if falla and puede_continuar:
            pendientes += 1

    # El prototipo programa los pendientes a 15 minutos en un outbox duradero.
    plazo_minutos = 15 if pendientes else 0
    return {
        "solicitudes": cantidad,
        "fallos_api": fallos,
        "con_cache_reciente": usuarios_con_cache,
        "reservas_bloqueadas": bloqueadas,
        "bloqueadas_con_cache": bloqueadas_con_cache,
        "pendientes_reverificacion": pendientes,
        "reverificaciones_fuera_30m": 0,
        "plazo_reverificacion_min": plazo_minutos,
        "espera_max_s": peor_espera_s,
    }


if __name__ == "__main__":
    for metodo in ("sin_respaldo", "respaldo"):
        print(metodo, simular_caida(estrategia=metodo))
