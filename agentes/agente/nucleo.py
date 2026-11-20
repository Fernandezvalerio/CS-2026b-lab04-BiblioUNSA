"""Bucle ReAct: las decisiones, guardias y transiciones quedan en JSONL."""
import json
import time
from pathlib import Path
from agente.contrato import validar_decision


class Agente:
    def __init__(self, nombre, modelo, herramientas, politica, objetivo, traza_archivo, ronda=1):
        self.nombre, self.modelo, self.h, self.politica = nombre, modelo, herramientas, politica
        self.historial = [{"role": "user", "content": objetivo}]
        self.traza_archivo = Path(traza_archivo)
        self.eventos, self.ronda = [], ronda

    def _registrar(self, **evento):
        self.eventos.append(dict(evento,t=round(time.perf_counter()-self._t0,3),agente=self.nombre,ronda=self.ronda))

    def _estado(self, estado, paso):
        self._registrar(tipo="estado", estado=estado, paso=paso)

    def ejecutar(self):
        self._t0 = time.perf_counter()
        self._registrar(tipo="objetivo",estado="INICIO",texto=self.historial[0]["content"])
        final = "(sin respuesta final)"
        for paso in range(1,self.politica.max_pasos+1):
            self._estado("DECIDIENDO",paso)
            d = self.modelo.decidir(self.historial)
            self.historial.append({"role":"assistant","content":json.dumps(d,ensure_ascii=False)})
            self._estado("VALIDANDO_CONTRATO",paso)
            ok,motivo = validar_decision(d,set(self.h.catalogo()))
            if not ok:
                obs = f"ERROR DE CONTRATO: {motivo}"
                self._registrar(tipo="accion",estado="CONTRATO_INVALIDO",paso=paso,accion="(ninguna)",args={},observacion=obs,bloqueada=True)
            elif "final" in d:
                final = d["final"]
                self._registrar(tipo="final",estado="FINALIZADO",paso=paso,pensamiento=d["pensamiento"],texto=final)
                break
            else:
                acc,args = d["accion"],d["args"]
                self._estado("EVALUANDO_POLITICA",paso)
                veredicto = self.politica.evaluar(acc,args,paso)
                if veredicto.permitido:
                    self._estado("EJECUTANDO",paso)
                    try:
                        obs = getattr(self.h,acc)(**args)
                    except Exception as e:
                        obs = f"ERROR: {type(e).__name__}: {e}"
                    estado = "OBSERVANDO"
                else:
                    obs = f"BLOQUEADO: {veredicto.motivo}"
                    estado = "BLOQUEADO"
                self._registrar(tipo="accion",estado=estado,paso=paso,pensamiento=d["pensamiento"],accion=acc,args=args,observacion=obs,bloqueada=not veredicto.permitido)
            self.historial.append({"role":"user","content":f"Observación: {obs}"})
        else:
            self._estado("LIMITE_ALCANZADO",self.politica.max_pasos)
        self._registrar(tipo="resumen",estado="TERMINADO",contexto_final=len(json.dumps(self.historial,ensure_ascii=False)),pasos=paso)
        self.traza_archivo.parent.mkdir(parents=True,exist_ok=True)
        with self.traza_archivo.open("w",encoding="utf-8") as f:
            for e in self.eventos:
                f.write(json.dumps(e,ensure_ascii=False)+"\n")
        return final
