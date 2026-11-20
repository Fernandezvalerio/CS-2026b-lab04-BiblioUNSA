"""Convierte la evidencia real JSONL en secuencia Mermaid y métricas."""
import argparse
import collections
import json
from pathlib import Path


def cargar(carpeta):
    fs = sorted(Path(carpeta).glob("*.jsonl"))
    def orden(f):
        r = int(f.stem.split("_r")[-1]) if "_r" in f.stem else 1
        return (r, {"planificador":0,"ejecutor":1,"revisor":2}.get(f.stem.split("_r")[0],1),f.name)
    return [json.loads(l) for f in sorted(fs,key=orden) for l in f.read_text(encoding="utf-8").splitlines()]


def metricas(eventos):
    acciones = [e for e in eventos if e["tipo"]=="accion" and e["estado"]!="CONTRATO_INVALIDO"]
    resumenes = [e for e in eventos if e["tipo"]=="resumen"]
    return {"pasos":sum(e["pasos"] for e in resumenes),"rondas":max((e["ronda"] for e in eventos),default=0),
            "acciones":len(acciones),"bloqueadas":sum(e["bloqueada"] for e in acciones),
            "contrato":sum(e["estado"]=="CONTRATO_INVALIDO" for e in eventos),
            "herramientas":dict(collections.Counter(e["accion"] for e in acciones)),
            "contexto_final":sum(e["contexto_final"] for e in resumenes),
            "contextos_por_agente":{f"{e['agente']}_r{e['ronda']}":e["contexto_final"] for e in resumenes}}


def a_mermaid(eventos):
    l=["sequenceDiagram","    autonumber","    actor U as Humano","    participant PL as Planificador","    participant EJ as Ejecutor","    participant RV as Revisor","    participant C as Contrato","    participant P as Política","    participant H as Herramientas"]
    alias={"planificador":"PL","ejecutor":"EJ","revisor":"RV"}
    for e in eventos:
        a=alias.get(e["agente"],"EJ")
        if e["tipo"]=="objetivo":
            l.append(f"    U->>{a}: Objetivo ronda {e['ronda']}")
        elif e["tipo"]=="accion":
            if e["estado"]=="CONTRATO_INVALIDO":
                l.extend([f"    {a}->>C: Decisión",f"    C--x{a}: Contrato inválido"])
            elif e["bloqueada"]:
                l.extend([f"    {a}->>P: {e['accion']}",f"    P--x{a}: Bloqueada"])
            else:
                obs=e["observacion"].splitlines()[0] if e["observacion"] else "(vacío)"
                obs=obs.replace(";",",").replace("#","N.").replace("<","[").replace(">","]")[:65]
                l.extend([f"    {a}->>H: {e['accion']}",f"    H-->>{a}: {obs}"])
        elif e["tipo"]=="final":
            l.append(f"    {a}-->>U: Respuesta final (revisión humana pendiente)")
    return "\n".join(l)+"\n"


def generar(carpeta):
    p=Path(carpeta); ev=cargar(p)
    (p/"trayectoria.mmd").write_text(a_mermaid(ev),encoding="utf-8")
    m=metricas(ev)
    (p/"metricas.json").write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding="utf-8")
    return m

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("carpeta"); args=p.parse_args()
    print(json.dumps(generar(args.carpeta),ensure_ascii=False,indent=2))
