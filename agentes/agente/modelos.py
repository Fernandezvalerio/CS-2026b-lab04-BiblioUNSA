"""Strategy: decisiones grabadas o interactivas, sin API ni credenciales."""
import json
from pathlib import Path


class ModeloGrabado:
    def __init__(self, archivo):
        self.decisiones = iter(json.loads(Path(archivo).read_text(encoding="utf-8")))

    def decidir(self, historial):
        try:
            return next(self.decisiones)
        except StopIteration:
            return {"pensamiento": "Fin de la grabación", "final": "SIN DECISIÓN GRABADA"}


class ModeloInteractivo:
    def __init__(self, grabar_en):
        self.archivo = Path(grabar_en)
        self.decisiones = []

    def decidir(self, historial):
        print("\n===== COPIE AL ASISTENTE (historial completo) =====")
        print(json.dumps(historial, ensure_ascii=False, indent=2))
        print("===== PEGUE UNA RESPUESTA JSON EN UNA SOLA LÍNEA =====")
        bruto = input("> ")
        try:
            d = json.loads(bruto)
        except json.JSONDecodeError:
            d = bruto  # El contrato rechaza texto libre y devuelve observación.
        self.decisiones.append(d)
        self.archivo.write_text(json.dumps(self.decisiones, ensure_ascii=False, indent=2), encoding="utf-8")
        return d
