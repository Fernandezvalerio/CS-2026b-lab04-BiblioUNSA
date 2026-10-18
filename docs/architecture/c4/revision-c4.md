# Revisión de las vistas con la lista oficial de c4model.com (E7)

Lista aplicada: [c4model.com/diagrams/checklist](https://c4model.com/diagrams/checklist), grupos General, Elementos y Relaciones (Tabla 3 de la guía). Estado **después** de aplicar las correcciones de la sección 2.

## 1. Lista aplicada a las cinco vistas

| Pregunta de la lista | Contexto | Contenedores | Componentes | Dinámica | Despliegue |
|----------------------|:--------:|:------------:|:-----------:|:--------:|:----------:|
| General: ¿tiene título y se entiende el tipo y el alcance? | Sí | Sí | Sí | Sí | Sí |
| General: ¿tiene leyenda? | Sí | Sí | Sí | Sí | Sí |
| Elementos: ¿nombre, tipo y descripción? | Sí | Sí | Sí | Sí | Sí |
| Elementos: ¿tecnología (si corresponde)? | n. a. | Sí | Sí | Sí | Sí |
| Elementos: ¿se entienden colores y formas? | Sí | Sí | Sí | Sí | Sí |
| Elementos: ¿se entienden los acrónimos? | Sí (UNSA, QR) | Parcial (REST, SQL, TCP) | Parcial | Parcial | Parcial (VPS, MVP) |
| Relaciones: ¿etiqueta con la intención? | Sí | Sí | Sí | Sí | Sí |
| Relaciones: ¿etiqueta coherente con la dirección? | Sí | Sí | Sí | Sí | Sí |
| Relaciones: ¿tecnología o protocolo? | Sí | Sí | Sí | Sí | Sí |
| Legibilidad: ¿las flechas y etiquetas se leen sin cruces confusos? | Sí | Sí | **No** | Sí | Sí |

**Evidencia:** títulos, leyendas y descripciones en `img/structurizr-*.png`; las tecnologías en `export/structurizr-*.puml`. Hallazgo abierto: en la vista de **Componentes** hay 22 relaciones y varias curvas largas (las flechas a la base de datos y a Redis) cruzan el borde del contenedor; la vista cumple el contenido, pero es densa. Se deja como mejora pendiente (dividirla por módulo o agrupar las flechas a la base de datos en una nota).

## 2. Hallazgos del revisor de IA y verificación del equipo

El revisor aplicó el Prompt IA 2 (ver `bitacora-ia.md`, interacción 3) sobre los `.puml` y las imágenes. Verificación de cada hallazgo contra los archivos:

| # | Vista | Hallazgo de la IA | Verificación | Resultado |
|---|-------|-------------------|--------------|-----------|
| 1 | Contexto, Contenedores | Los sistemas externos tienen el mismo color que BiblioUNSA y las formas (base de datos, cola) no están en la leyenda | Cierto: `$tags=""` en el `.puml` exportado. Se activó la propiedad `c4plantuml.tags` | **Corregido** |
| 2 | Contexto | Jerga para no técnicos: "su API" en la descripción del sistema académico | Cierto; se cambió por una descripción sin tecnología | **Corregido** |
| 3 | Contexto | Las flechas muestran `[HTTPS/JSON]` y `[OpenID Connect]` y eso es jerga en el nivel 1 | **Falso positivo.** La lista oficial pide indicar el protocolo en las relaciones, y la propia guía lo muestra en el nivel 1 (Fig. 5); las relaciones de las personas no lo llevan | Rechazado |
| 4 | Contexto | "UNSA" no está desarrollada | **Falso positivo.** Es el nombre propio de la institución para la que se construye el sistema; los lectores del nivel 1 la conocen | Rechazado |
| 5 | Componentes y Dinámica | 7 flechas entre módulos sin tecnología | Cierto (`$techn=""`). Se agregó "Llamada interna (Python)" | **Corregido** |
| 6 | Dinámica | Los pasos 3 y 4 (sin caché) y el paso 7 (con caché) son ramas excluyentes numeradas como una sola secuencia | Cierto. Se quitó el paso 7 y el título dice "camino con respuesta a tiempo"; las ramas están en la secuencia UML | **Corregido** |
| 7 | Dinámica | Falta un paso final de respuesta a la interfaz | **Falso positivo.** Una vista dinámica solo muestra relaciones del modelo, y la respuesta HTTP es la misma relación de ida | Rechazado |
| 8 | Despliegue | Faltan el sistema académico, el proveedor de identidad y un proxy HTTPS | **Falso positivo.** Los sistemas externos no se despliegan nosotros (guía, Fig. 9) y el proxy no está en ningún ADR | Rechazado |
| 9 | Dinámica | Las declaraciones duplicadas dentro y fuera de `System_Boundary` en el `.puml` | **Falso positivo.** Es el formato del exportador de Structurizr, no un error del modelo | Rechazado |
| 10 | Contenedores | "Redis [Redis]" repite el nombre y no aporta | Cierto; el contenedor se renombró "Caché y cola de tareas" | **Corregido** |
| 11 | Varias | "HU-03", "R-03" y "MVP" sin explicar | Parcial: se quitó "R-03" y "HU-03" de las descripciones de los elementos; "HU-03" queda en el título de la vista dinámica con "historia de usuario" | **Corregido** |
| 12 | Todas | El título del `.puml` sale en inglés ("System Context View") | Cierto, pero lo genera el exportador; se acepta | Aceptado sin cambio |
| 13 | Todas | El tipo no está explícito en las cajas (`hide stereotypes`) | Parcial: las cajas llevan la tecnología entre corchetes y la leyenda explica el color; el tipo se infiere del nivel | Aceptado sin cambio |
| 14 | Componentes | Etiquetas sobre los bordes y curvas largas | Cierto; ver "hallazgo abierto" arriba | Pendiente |

**Resumen:** 14 hallazgos, 6 corregidos, 5 falsos positivos (3, 4, 7, 8, 9), 2 aceptados sin cambio y 1 pendiente. Los falsos positivos cumplen la condición de E7 (al menos 1).
