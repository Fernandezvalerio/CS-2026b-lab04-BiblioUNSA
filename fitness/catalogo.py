"""Simulación de colas para una búsqueda de catálogo (no es una prueba HTTP real)."""

from __future__ import annotations

from heapq import heapreplace, heapify
from random import Random


def simular_catalogo(
    carga_rps: float = 24,
    consultas: int = 5000,
    workers: int = 4,
    indice: bool = True,
    semilla: int = 2026,
) -> dict[str, float | int]:
    if carga_rps <= 0 or consultas <= 0 or workers <= 0:
        raise ValueError("La carga, consultas y workers deben ser positivos")
    aleatorio = Random(semilla)
    fin_workers = [0.0] * workers
    heapify(fin_workers)
    instante = 0.0
    latencias_ms: list[float] = []

    # El índice reduce la búsqueda media supuesta de 230 a 80 ms.
    # El algoritmo compara las mismas llegadas y variables aleatorias.
    media_servicio = 0.080 if indice else 0.230
    for _ in range(consultas):
        instante += aleatorio.expovariate(carga_rps)
        duracion = aleatorio.expovariate(1.0 / media_servicio)
        libre = fin_workers[0]
        inicio = max(instante, libre)
        termino = inicio + duracion
        heapreplace(fin_workers, termino)
        latencias_ms.append((termino - instante) * 1000.0)

    ordenadas = sorted(latencias_ms)
    return {
        "consultas": consultas,
        "carga_rps": carga_rps,
        "workers": workers,
        "p95_ms": round(ordenadas[max(0, int(0.95 * consultas) - 1)], 1),
        "promedio_ms": round(sum(latencias_ms) / consultas, 1),
        "maximo_ms": round(max(latencias_ms), 1),
    }


if __name__ == "__main__":
    for con_indice in (False, True):
        print("con_indice=" + str(con_indice), simular_catalogo(indice=con_indice))
