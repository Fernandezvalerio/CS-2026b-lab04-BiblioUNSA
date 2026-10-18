# Comparaciones — BiblioUNSA (Laboratorio 06)

## 1. Secuencia UML frente a vista dinámica C4 (E4)

La vista dinámica `ReservarLibro` toma el mismo flujo que [`secuencia-reservar-libro.puml`](../../design/secuencia-reservar-libro.puml) del Lab 05 (HU-03), pero solo muestra 6 pasos entre componentes, contenedores y sistemas externos. La secuencia UML conserva lo que la vista omite: las bifurcaciones (timeout de 3 s, caché de ≤ 24 h, matrícula no vigente, ejemplar no disponible), los códigos de respuesta (201, 403, 409, 503), los mensajes de vuelta, la creación del `Prestamo` y las operaciones de cada clase (`estaDisponible()`, `marcarReservado()`, `marcarParaReverificacion()`). La vista dinámica sirve al equipo técnico y a quien debe entender la colaboración entre módulos sin leer clases; la secuencia UML sirve a quien implementa o prueba el caso y necesita cada camino y cada operación. La vista dinámica muestra solo el camino con respuesta a tiempo, porque una vista C4 no representa ramas alternativas.

## 2. Modelado (Structurizr DSL) frente a diagramación manual (C4-PlantUML) (E6)

| Aspecto | Escrito a mano (`contexto-manual.puml`) | Modelo exportado (`workspace.dsl`) |
|---------|------------------------------------------|-------------------------------------|
| Alcance | 1 vista (contexto), 18 líneas | 5 vistas, 156 líneas de modelo; 263 líneas de `.puml` generadas |
| Tiempo invertido | Una escritura corta, pero cada vista nueva hay que dibujarla desde cero | Escribir el modelo llevó más tiempo; exportar las 5 vistas a `.puml` y `.mmd` y generar los PNG tarda unos 5 s con un solo comando |
| Errores encontrados | Al escribirlo se coló un carácter invisible dentro de `@enduml`; PlantUML no lo marca de forma clara y solo se vio al revisar el archivo. Nada impide que el nombre o el protocolo de una flecha difieran de otra vista | `validate` detecta identificadores inexistentes (se probó con un destino falso y falló con código 1). Primer problema: el export a PlantUML no llevó colores ni formas hasta activar la propiedad `c4plantuml.tags` |
| Si mañana cambia un nombre | Hay que buscar y corregir el nombre en cada archivo y recordar volver a generar el PNG | Se cambia en **una** línea del DSL (hoy "Sistema académico UNSA" aparece una sola vez); al re-exportar se actualizan las 4 vistas que lo muestran (en los `.puml` generados son 5 líneas) |
| Coherencia entre niveles | Depende de la disciplina del equipo | Garantizada: el contenedor y el componente son el mismo elemento en todas las vistas |
| Aspecto | Control total de la apariencia (leyenda con "external system" automática) | Más legible con `autolayout`, aunque en la vista de componentes algunas flechas se cruzan |
| Uso recomendado | Un diagrama único y estable (por ejemplo, una diapositiva) | Documentación que evoluciona con el código |

**Conclusión:** para el nivel 1 solo, escribir a mano es más rápido; en cuanto hay más de una vista, el modelo único evita contradicciones y se paga solo.
