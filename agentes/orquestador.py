"""Gestor, ejecutor y crítico de solo lectura; máximo dos rondas."""
import argparse
from pathlib import Path
from agente.politica import Politica, LECTURA, aprobar_en_consola
from agente.traza import generar
from ejecutar import A, R, preparar, crear_agente, limpiar_trazas

MAX_RONDAS = 2


def orquestar(issue, modo="interactivo", origen=R, nombre=None, aprobar=True):
    nombre = nombre or f"issue{issue}-multi"
    h = preparar(origen,nombre,issue); limpiar_trazas(nombre)
    p = crear_agente("planificador",h,Politica(herramientas_permitidas={"leer_archivo"},max_pasos=4),
                     f"Lee issues/ISSUE-{issue}.md y propone un plan breve para resolverlo y verificarlo. No edites ni ejecutes comandos.",nombre,modo)
    plan = p.ejecutar()
    retro = ""
    veredicto = "SIN REVISION"
    for ronda in range(1,MAX_RONDAS+1):
        ejecutor = crear_agente("ejecutor",h,Politica(max_pasos=12, aprobar_edicion=aprobar_en_consola if aprobar else None),
                     f"Resuelve issues/ISSUE-{issue}.md siguiendo el plan {plan}. {retro} Reproduce y verifica con pruebas.",nombre,modo,ronda)
        resumen = ejecutor.ejecutar()
        revisor = crear_agente("revisor",h,Politica(herramientas_permitidas=set(LECTURA),max_pasos=8),
                     f"Revisa de forma independiente el cambio del ISSUE-{issue}. Lee el issue, comprueba el diff, las pruebas y el código relacionado; considera casos de borde y si se cumplen todos los requisitos. No edites ni solicites cambios innecesarios. Responde APROBADO o CAMBIOS SOLICITADOS con razones concretas. Resumen: {resumen}",nombre,modo,ronda)
        veredicto = revisor.ejecutar()
        print(f"Ronda {ronda}: {resumen}\nRevisor: {veredicto}")
        if veredicto.startswith("APROBADO"):
            break
        retro = "Revisión anterior: " + veredicto
    print("Veredicto del crítico:",veredicto,". Integración únicamente por decisión humana.")
    print("Métricas:",generar(A/"trazas"/nombre))
    print(h.ver_cambios())

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("issue",choices=["01","02","03"],default="02",nargs="?"); p.add_argument("--modo",choices=["interactivo","grabado"],default="interactivo"); p.add_argument("--origen",type=Path,default=R); p.add_argument("--nombre"); p.add_argument("--sin-aprobacion",action="store_true",help="Solo para reproducir E5 en copias locales"); args=p.parse_args()
    orquestar(args.issue,args.modo,args.origen,args.nombre,not args.sin_aprobacion)
