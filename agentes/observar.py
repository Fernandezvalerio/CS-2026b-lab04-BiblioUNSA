"""E7: calcula las métricas directamente a partir de las trazas JSONL."""
import argparse
from pathlib import Path

from agente.traza import cargar, metricas

RAIZ = Path(__file__).resolve().parent
PRINCIPALES = ["issue01-unico", "issue02-multi", "issue03-unico"]
COMPLEMENTARIAS = ["issue02-unico", "issue02-aprobacion"]


def tabla(casos):
    lineas = [
        "| Ejecución | Pasos | Rondas | Acciones | Herramientas (llamadas) | Contrato rechazado | Bloqueadas | Contexto final (caracteres) |",
        "|---|---:|---:|---:|---|---:|---:|---:|",
    ]
    for caso in casos:
        eventos = cargar(RAIZ / "trazas" / caso)
        if not eventos:
            raise ValueError(f"No hay trazas JSONL para {caso}")
        m = metricas(eventos)
        herramientas = ", ".join(f"{k} ({v})" for k, v in m["herramientas"].items())
        lineas.append(
            f"| {caso} | {m['pasos']} | {m['rondas']} | {m['acciones']} | "
            f"{herramientas} | {m['contrato']} | {m['bloqueadas']} | {m['contexto_final']} |"
        )
    return "\n".join(lineas)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("casos", nargs="*", help="Nombres de carpetas en agentes/trazas")
    args = parser.parse_args()
    if args.casos:
        print(tabla(args.casos))
    else:
        print("## Métricas de los tres issues\n")
        print(tabla(PRINCIPALES))
        print("\n## Ejecuciones complementarias\n")
        print(tabla(COMPLEMENTARIAS))
