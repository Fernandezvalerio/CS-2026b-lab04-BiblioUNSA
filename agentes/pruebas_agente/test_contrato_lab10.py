import json
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).parents[1]))
from agente.contrato import validar_decision
from agente.nucleo import Agente
from agente.herramientas import Herramientas
from agente.politica import Politica


@pytest.mark.parametrize("decision", [
    {"pensamiento":"leo", "accion":"leer_archivo", "args":{}, "extra":True},
    {"pensamiento":"leo", "accion":"leer_archivo", "args":"ruta"},
    {"pensamiento":"leo", "accion":"", "args":{}},
    {"pensamiento":"leo", "accion":[], "args":{}},
    {"pensamiento":"fin", "final":"listo", "extra":True},
    {"pensamiento":"fin", "final":" "},
])
def test_invalidas(decision):
    assert not validar_decision(decision, {"leer_archivo"})[0]


def test_limite_incluso_si_todas_las_decisiones_son_invalidas(tmp_path):
    class ModeloInvalido:
        def decidir(self, historial):
            return "texto libre"
    a = Agente("ejecutor", ModeloInvalido(), Herramientas(tmp_path), Politica(max_pasos=2), "prueba", tmp_path/"traza.jsonl")
    assert a.ejecutar() == "(sin respuesta final)"
    ev = [json.loads(l) for l in (tmp_path/"traza.jsonl").read_text().splitlines()]
    assert sum(e["estado"] == "CONTRATO_INVALIDO" for e in ev) == 2
    assert any(e["estado"] == "LIMITE_ALCANZADO" for e in ev)
    assert ev[-1]["pasos"] == 2


def test_no_permite_comando_encadenado():
    assert not Politica().evaluar("ejecutar_comando", {"comando":"python -m pytest -q; echo prohibido"}, 1).permitido


def test_no_permite_editar_pruebas_por_ruta_alternativa():
    assert not Politica().evaluar("editar_archivo", {"ruta":"src/../tests/test_issue_01.py"}, 1).permitido
