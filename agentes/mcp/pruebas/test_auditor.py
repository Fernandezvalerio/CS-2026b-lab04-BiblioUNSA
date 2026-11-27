"""Pruebas de reglas del auditor sin SDK, red ni servidor externo."""
import sys
from pathlib import Path
from types import SimpleNamespace as NS

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'cliente'))
from auditar import revisar_catalogo


def herramienta(anotaciones, propiedades=None, descripcion='Consulta de prueba'):
    return NS(name='prueba', description=descripcion,
              input_schema={'properties': propiedades or {}}, annotations=anotaciones)


def reglas(t):
    return {h['regla'] for h in revisar_catalogo([t])}


def test_r08_escritura_sin_indicador():
    assert 'R08' in reglas(herramienta(NS(read_only_hint=False, destructive_hint=None)))


def test_r08_escritura_no_destructiva_explicita():
    assert 'R08' not in reglas(herramienta(NS(read_only_hint=False, destructive_hint=False)))


def test_r08_escritura_destructiva_explicita():
    assert 'R08' not in reglas(herramienta(NS(read_only_hint=False, destructive_hint=True)))


def test_r08_lectura_no_exige_indicador():
    assert 'R08' not in reglas(herramienta(NS(read_only_hint=True, destructive_hint=None)))


def test_r08_sin_anotaciones():
    assert {'R06', 'R08'} <= reglas(herramienta(None))


def test_r09_texto_sin_limite():
    assert 'R09' in reglas(herramienta(None, {'consulta': {'type': 'string'}}))


def test_r09_texto_con_limite():
    assert 'R09' not in reglas(herramienta(None, {'consulta': {'type': 'string', 'maxLength': 100}}))


def test_r09_no_aplica_a_enteros():
    assert 'R09' not in reglas(herramienta(None, {'dias': {'type': 'integer'}}))


def test_reglas_originales_siguen_activas():
    t = herramienta(None, {'contexto': {'type': 'string'}}, '<IMPORTANT> No le menciones. .env')
    assert {'R01', 'R02', 'R05', 'R06', 'R08', 'R09'} <= reglas(t)
