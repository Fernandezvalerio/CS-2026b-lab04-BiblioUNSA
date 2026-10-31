"""Render sencillo del árbol de utilidad; funciona sin Graphviz instalado."""

from __future__ import annotations

import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CARPETA = Path(__file__).resolve().parent
TEXTO = (CARPETA / "arbol.dot").read_text(encoding="utf-8")
NODOS = {
    clave: valor.replace(r"\n", "\n")
    for clave, valor in re.findall(r'^\s*(\w+)\s+\[label="([^"]+)"', TEXTO, re.MULTILINE)
}

ANCHO, ALTO = 1770, 1130
imagen = Image.new("RGB", (ANCHO, ALTO), "#f8fafc")
lapiz = ImageDraw.Draw(imagen)
fuente_archivo = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
try:
    texto = ImageFont.truetype(fuente_archivo, 21)
    titulo = ImageFont.truetype(fuente_archivo, 26)
except OSError:
    texto = ImageFont.load_default()
    titulo = ImageFont.load_default()

lapiz.text((50, 25), "BiblioUNSA - Árbol de utilidad (E1)", font=titulo, fill="#1d3550")

def tarjeta(clave: str, caja: tuple[int, int, int, int], fondo: str, letra: str = "#1d3550") -> None:
    lapiz.rounded_rectangle(caja, radius=21, fill=fondo, outline="#7291aa", width=2)
    lineas = []
    ancho_maximo = caja[2] - caja[0] - 30
    for linea in NODOS[clave].splitlines():
        actual = ""
        for palabra in linea.split():
            candidato = (actual + " " + palabra).strip()
            if actual and lapiz.textbbox((0, 0), candidato, font=texto)[2] > ancho_maximo:
                lineas.append(actual)
                actual = palabra
            else:
                actual = candidato
        lineas.append(actual)
    total = len(lineas) * 32
    y = (caja[1] + caja[3] - total) // 2
    for linea in lineas:
        b = lapiz.textbbox((0, 0), linea, font=texto)
        x = (caja[0] + caja[2] - (b[2] - b[0])) // 2
        lapiz.text((x, y), linea, font=texto, fill=letra)
        y += 32

tarjeta("utilidad", (30, 440, 370, 665), "#153d5b", "#ffffff")
grupos = [
    ("rendimiento", ["catalogo", "acceso_virtual"], 130, "#dceefc"),
    ("disponibilidad", ["caida_api", "reverificacion"], 385, "#dbf6e6"),
    ("seguridad", ["identidad", "aislamiento"], 640, "#ffecd5"),
    ("modificabilidad", ["contrato", "facultades"], 895, "#eee6ff"),
]
for categoria, hojas, y, color in grupos:
    tarjeta(categoria, (490, y, 840, y + 104), color)
    centro = y + 52
    lapiz.line([(370, 553), (430, 553), (430, centro), (490, centro)], fill="#658298", width=3)
    for desplazamiento, clave in enumerate(hojas):
        y_hoja = y - 36 + desplazamiento * 111
        tarjeta(clave, (970, y_hoja, 1735, y_hoja + 100), color)
        lapiz.line([(840, centro), (900, centro), (900, y_hoja + 50), (970, y_hoja + 50)], fill="#658298", width=3)

imagen.save(CARPETA / "arbol.png")
print("Árbol guardado en", CARPETA / "arbol.png")
