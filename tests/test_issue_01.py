from datetime import date
from decimal import Decimal
from reservas.multas import calcular_multa


def test_no_cobra_domingo():
    assert calcular_multa(date(2026, 11, 14), date(2026, 11, 16), Decimal("2")) == Decimal("2")


def test_sin_retraso():
    assert calcular_multa(date(2026, 11, 14), date(2026, 11, 14), Decimal("2")) == 0
