import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
from agente.herramientas import Herramientas
from agente.nucleo import Agente
from agente.politica import Politica, aprobar_en_consola


def test_valida_entrada(monkeypatch):
    entradas = iter(["tal vez","S","n"])
    monkeypatch.setattr("builtins.input",lambda _:next(entradas))
    assert aprobar_en_consola({"ruta":"src/a.py","antes":"a","despues":"b"}) is False


def test_humano_rechaza_y_luego_aprueba(tmp_path):
    src=tmp_path/"src"; src.mkdir(); archivo=src/"a.py"; archivo.write_text("a=1",encoding="utf-8")
    d={"pensamiento":"editar","accion":"editar_archivo","args":{"ruta":"src/a.py","antes":"a=1","despues":"a=2"}}
    class Modelo:
        decisiones=iter([d,d,{"pensamiento":"fin","final":"listo"}])
        def decidir(self,historial): return next(self.decisiones)
    respuestas=iter([False,True]); registro=[]
    def aprobar(args):
        registro.append(archivo.read_text(encoding="utf-8"))
        return next(respuestas)
    a=Agente("ejecutor",Modelo(),Herramientas(tmp_path),Politica(aprobar_edicion=aprobar),"prueba",tmp_path/"traza.jsonl")
    a.ejecutar()
    assert registro == ["a=1","a=1"]
    assert archivo.read_text(encoding="utf-8") == "a=2"
    ev=[json.loads(l) for l in (tmp_path/"traza.jsonl").read_text().splitlines()]
    assert [e["permitida"] for e in ev if e["tipo"]=="aprobacion"] == [False,True]


def test_diagrama_registra_aprobaciones():
    from agente.traza import a_mermaid
    eventos = [{"tipo": "aprobacion", "agente": "ejecutor", "permitida": x} for x in (False, True)]
    diagrama = a_mermaid(eventos)
    assert "Rechazada (n)" in diagrama
    assert "Aprobada (s)" in diagrama
