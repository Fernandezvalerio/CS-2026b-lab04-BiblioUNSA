"""Vista de despliegue de BiblioUNSA (E6).

Requisitos: pip install diagrams  +  Graphviz instalado en el sistema.
Ejecución:  python despliegue.py   ->  genera img/despliegue.png
"""
import os

from diagrams import Cluster, Diagram, Edge
from diagrams.generic.device import Mobile
from diagrams.onprem.client import Client, Users
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.monitoring import Grafana, Prometheus
from diagrams.onprem.network import Internet, Nginx
from diagrams.onprem.queue import Celery
from diagrams.programming.framework import Django

AQUI = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(AQUI, "img")
os.makedirs(IMG, exist_ok=True)

graph_attr = {"fontsize": "20", "bgcolor": "white", "pad": "0.3"}

with Diagram(
    "BiblioUNSA - Vista de despliegue",
    filename=os.path.join(IMG, "despliegue"),
    show=False,
    direction="LR",
    graph_attr=graph_attr,
    outformat="png",
):
    estudiantes = Users("Estudiantes")
    celular = Mobile("Celular\n(web responsive)")
    biblio = Client("Bibliotecario\n(PC + lector QR)")

    with Cluster("Servidor en la nube (VPS)"):
        proxy = Nginx("Nginx\n(HTTPS)")
        with Cluster("Monolito modular"):
            app = Django("Django API\n(6 módulos)")
            worker = Celery("Reverificación\nde matrícula")
        cache = Redis("Redis\n(caché de matrícula\n+ cola)")
        db = PostgreSQL("PostgreSQL\n(esquema por módulo)")
        with Cluster("Monitoreo"):
            prom = Prometheus("Prometheus")
            graf = Grafana("Grafana")

    idp = Internet("Proveedor de identidad\n(correo institucional)")
    sa = Internet("Sistema académico UNSA\n(API)")

    estudiantes >> celular >> Edge(label="HTTPS") >> proxy
    biblio >> Edge(label="HTTPS") >> proxy
    proxy >> app
    app >> Edge(label="SQL") >> db
    app >> Edge(label="caché ≤ 24 h") >> cache
    app >> Edge(label="OIDC", style="dashed") >> idp
    app >> Edge(label="API, timeout 3 s", style="dashed") >> sa
    cache >> Edge(label="encola") >> worker
    worker >> Edge(label="reverifica ≤ 30 min", style="dashed") >> sa
    app >> Edge(style="dotted") >> prom >> graf
