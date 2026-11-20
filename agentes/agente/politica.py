"""Permisos y presupuesto. No se ejecutan comandos arbitrarios de shell."""
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Callable

LECTURA = {"listar_archivos", "leer_archivo", "buscar", "ejecutar_pruebas", "ver_cambios", "mapa_repo", "leer_notas"}

@dataclass
class Decision:
    permitido: bool
    motivo: str = ""


@dataclass
class Politica:
    herramientas_permitidas: set = field(default_factory=lambda: LECTURA | {"editar_archivo", "ejecutar_comando", "anotar"})
    max_pasos: int = 12
    aprobar_edicion: Callable[[dict], bool] | None = None

    def evaluar(self, accion, args, paso):
        if paso > self.max_pasos:
            return Decision(False, "Se alcanzó el máximo de pasos")
        if accion not in self.herramientas_permitidas:
            return Decision(False, f"Herramienta no permitida: {accion}")
        if accion == "ejecutar_comando" and args.get("comando") != "python -m pytest -q":
            return Decision(False, "Comando fuera de la lista permitida")
        if accion == "editar_archivo":
            ruta = args.get("ruta", "")
            if not isinstance(ruta, str) or "\\" in ruta:
                return Decision(False, "Ruta protegida")
            p = PurePosixPath(ruta)
            if p.is_absolute() or ".." in p.parts or not p.parts or p.parts[0] != "src" or p.suffix != ".py":
                return Decision(False, "Ruta protegida: solo código Python en src/")
        return Decision(True)

    def autorizacion_humana(self, args):
        if self.aprobar_edicion is not None and not self.aprobar_edicion(args):
            return Decision(False, "El revisor humano rechazó la edición")
        return Decision(True)


def aprobar_en_consola(args):
    print("\n=== EDICIÓN SOLICITADA ===")
    print("Ruta:", args.get("ruta"))
    print("Antes:\n", args.get("antes"), "\nDespués:\n", args.get("despues"))
    while True:
        respuesta = input("¿Aprueba esta edición? [s/n]: ").strip()
        if respuesta in ("s", "n"):
            return respuesta == "s"
        print("Respuesta inválida. Escriba exactamente s o n.")
