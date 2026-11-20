"""Permisos y presupuesto. No se ejecutan comandos arbitrarios de shell."""
from dataclasses import dataclass, field
from pathlib import PurePosixPath

LECTURA = {"listar_archivos", "leer_archivo", "buscar", "ejecutar_pruebas", "ver_cambios"}

@dataclass
class Decision:
    permitido: bool
    motivo: str = ""


@dataclass
class Politica:
    herramientas_permitidas: set = field(default_factory=lambda: LECTURA | {"editar_archivo", "ejecutar_comando"})
    max_pasos: int = 12
    aprobar_edicion = None

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
