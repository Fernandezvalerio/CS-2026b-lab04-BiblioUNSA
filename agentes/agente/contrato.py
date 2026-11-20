"""Contrato estructurado: exactamente una acción o una respuesta final."""
def validar_decision(d, herramientas_conocidas) -> tuple[bool, str]:
    if not isinstance(d, dict):
        return False, "la decisión debe ser un objeto JSON"
    if not isinstance(d.get("pensamiento"), str) or not d["pensamiento"].strip():
        return False, "falta pensamiento no vacío"
    if ("final" in d) == ("accion" in d):
        return False, "se requiere accion o final, no ambos"
    if "final" in d:
        if set(d) != {"pensamiento", "final"} or not isinstance(d["final"], str) or not d["final"].strip():
            return False, "final debe ser texto no vacío y sin campos adicionales"
        return True, ""
    if not isinstance(d["accion"], str) or d["accion"] not in herramientas_conocidas:
        return False, "herramienta desconocida"
    if set(d) != {"pensamiento", "accion", "args"} or not isinstance(d["args"], dict):
        return False, "args debe ser objeto JSON; no se permiten campos adicionales"
    return True, ""
