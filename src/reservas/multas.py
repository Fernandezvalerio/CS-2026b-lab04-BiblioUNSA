"""Cálculo de multa por retraso (regla de laboratorio)."""
from datetime import date
from decimal import Decimal


def calcular_multa(vencimiento: date, devolucion: date, tarifa: Decimal) -> Decimal:
    if tarifa < 0:
        raise ValueError("La tarifa no puede ser negativa")
    dias = max(0, (devolucion - vencimiento).days)
    return tarifa * dias
