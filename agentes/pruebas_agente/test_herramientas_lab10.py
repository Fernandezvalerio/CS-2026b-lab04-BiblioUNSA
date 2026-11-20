import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).parents[1]))
from agente.herramientas import Herramientas
from agente.politica import Politica


def test_mapa_repo_no_ejecuta_codigo(tmp_path):
    src = tmp_path/"src"; src.mkdir()
    (src/"libros.py").write_text("raise RuntimeError('no ejecutar')\nclass Libro:\n    def buscar(self, titulo: str): pass\n", encoding="utf-8")
    mapa = Herramientas(tmp_path).mapa_repo()
    assert "src/libros.py" in mapa and "buscar(self, titulo: str)" in mapa


def test_memoria_persiste_y_es_local(tmp_path):
    h = Herramientas(tmp_path)
    assert h.leer_notas() == "(sin notas)"
    h.anotar("Revisar externos.py")
    h.anotar("Filtrar fecha_devolucion")
    assert Herramientas(tmp_path).leer_notas() == "- Revisar externos.py\n- Filtrar fecha_devolucion\n"
    assert (tmp_path/"notas.md").exists()


def test_nota_invalida(tmp_path):
    with pytest.raises(ValueError):
        Herramientas(tmp_path).anotar("x"*1001)


def test_revisor_no_puede_anotar():
    from agente.politica import LECTURA
    assert not Politica(herramientas_permitidas=LECTURA).evaluar("anotar", {"texto":"x"}, 1).permitido
