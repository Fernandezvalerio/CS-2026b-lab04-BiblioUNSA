# Bitácora de uso de IA — BiblioUNSA (Laboratorio 06: modelo C4)

> **Nota de autoría.** Los prompts de esta bitácora los redactó Claude (asistente de IA) a pedido del equipo, a partir del Prompt IA 1, 2 y 3 de la guía del Lab 06 y de las necesidades de cada entregable. Las respuestas descritas son las que se obtuvieron realmente al ejecutarlos el 17/10/2026. Antes de entregar, cada integrante debe repetir la verificación de su columna y firmar la decisión.

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | 17/10 | Claude | Prompt 1 (Prompt IA 1 de la guía adaptado): inventario de elementos C4 a partir de `drivers.md`, los tres ADR, `despliegue.py`, `paquetes.puml` y `secuencia-reservar-libro.puml` (E1) | `inventario.md` con 2 personas, 3 sistemas, 5 contenedores, 6 componentes y la vista dinámica, cada uno con su origen | Se contrastó cada fila con el archivo citado. Se **descartó el paquete `compartido`** como componente (solo agregaría 6 flechas), se **excluyeron Nginx, Prometheus y Grafana** (aparecen en `despliegue.py` pero ningún ADR los fija) y no se copió "PostgreSQL 16" de la guía porque el ADR-001 no fija versión | Corregida |
| 2 | 17/10 | Claude | Prompt 2: borrador de `workspace.dsl` con restricciones (solo tecnologías de los ADR, contenedor ≠ Docker, `!identifiers hierarchical`, protocolo en cada relación, etiqueta "Externo") (E1–E5) | Un workspace con 5 contenedores, 6 componentes, 5 vistas (contexto, contenedores, componentes, dinámica y despliegue) y estilos | `structurizr.sh validate` sin errores; además se probó que falla con un destino inexistente (código de salida 1). Se verificó con un script que las 7 dependencias entre componentes **coinciden exactamente** con `paquetes.puml` y que no hay ciclos. Se decidió que el worker llegue al sistema académico solo a través del componente Integración académica (ADR-003: único punto de contacto). Docker Compose quedó solo como nodo de despliegue | Aceptada (con revisión del equipo) |
| 3 | 17/10 | Claude (agente revisor independiente que no vio el modelo) | Prompt 3 (Prompt IA 2 de la guía): auditar las cinco vistas con la lista de c4model.com y responder en una tabla, sin inventar problemas | Tabla de 14 hallazgos: colores y formas poco claros, jerga en el nivel 1, 7 flechas internas sin tecnología, ramas excluyentes numeradas juntas en la vista dinámica, "Redis [Redis]" redundante, vista de componentes densa, entre otros | Se verificó cada hallazgo contra los `.puml` y las imágenes: 6 corregidos (colores y formas con `c4plantuml.tags`, "su API" fuera del nivel 1, "Llamada interna (Python)", vista dinámica solo con el camino a tiempo, Redis renombrado, siglas internas), **5 falsos positivos** (protocolo en el nivel 1, "UNSA" sin desarrollar, falta de respuesta en la vista dinámica, sistemas externos fuera del despliegue, declaraciones duplicadas del exportador), 2 aceptados y 1 pendiente (densidad de la vista de componentes). Detalle en `revision-c4.md` | Aceptada (6 corregidos, 5 rechazados) |
| 4 | 17/10 | Claude | Prompt 4 (Prompt IA 3 de la guía): explicar el contexto al presidente de una cooperativa no técnico en ≤ 120 palabras (E7) | `explicacion.md` de 93 palabras sin jerga | Se contrastó con el ADR-002 y el ADR-003 (caché de hasta 24 h, reverificación pronto, identidad externa). Se cambió "servicio de identidad de la universidad" por "servicio de identidad externo" porque aún no está confirmado que lo opere la UNSA (R-06). Se contó con `wc -w` | Corregida |
| 5 | 17/10 | Claude | Prompt 5: comparar `contexto-manual.puml` frente al modelo exportado y la secuencia UML frente a la vista dinámica (E4 y E6) | `comparacion.md` con tabla de tiempo, errores y cambio de nombre | Se reemplazaron las cifras supuestas por mediciones: el nombre "Sistema académico UNSA" aparece en 1 línea del DSL y en 4 archivos generados; exportar y renderizar las 5 vistas tarda ≈ 5 s; el archivo manual tuvo un carácter invisible en `@enduml` que se corrigió. Se quitó una afirmación sobre "horas invertidas" porque no se midió | Corregida |
| 6 | 17/10 | Claude | Prompt 6: sección "Arquitectura C4 (Lab 06)" del README con el contexto en Mermaid copiado de `export/`, enlaces a las vistas y comandos para regenerar (E8) | Sección con el Mermaid, tablas de vistas y entregables, y una GitHub Action opcional | Se renderizó el Mermaid exportado con `mermaid-cli` (válido) y se comprobaron los enlaces. La GitHub Action pasó el análisis YAML pero **no se ha ejecutado en GitHub**; queda por probar con el primer push | Aceptada (Action pendiente de probar) |

> Los prompts completos están en el anexo. No se incluyeron datos personales ni información confidencial.

## Anexo: prompts

### Prompt 1 — Inventario de elementos
```
Rol: actúa como arquitecto de software experto en el modelo C4 de Simon Brown.
Contexto: "BiblioUNSA" (Lab 04 y 05). Adjunto drivers.md, los ADR-001/002/003,
despliegue.py, paquetes.puml y secuencia-reservar-libro.puml: [pegar archivos].
Tarea: construye inventario.md con una tabla (Elemento | Tipo C4 | Origen) que
cubra personas, sistemas, sistemas externos, contenedores, componentes del
contenedor principal y el flujo crítico. Cada fila debe citar el archivo del que sale.
Restricciones: "contenedor" de C4 no es contenedor Docker; no incluyas
tecnologías que no figuren en los ADR ni en despliegue.py; si algo de
despliegue.py no está en un ADR, márcalo como duda en vez de incluirlo en silencio.
Formato: solo Markdown, en español.
```

### Prompt 2 — Borrador de workspace.dsl
```
Actúa como arquitecto experto en el modelo C4 y en Structurizr DSL.
Contexto: [pegar inventario.md, los ADR y despliegue.py de BiblioUNSA].
Tarea: escribe un workspace con 2 personas, el sistema, 5 contenedores con
tecnología, los componentes del monolito modular (los mismos nombres de paquetes.puml),
2 sistemas externos (etiqueta "Externo") y relaciones con descripción y protocolo.
Incluye las vistas systemContext, container, component, dynamic (reservar un
libro, HU-03, 4 o más pasos que ya existan como relaciones) y deployment (entorno "Producción").
Restricciones: usa solo las tecnologías de los ADR; no confundas contenedor C4 con
contenedor Docker; usa !identifiers hierarchical; las dependencias entre
componentes no deben formar ciclos; si un dato no está en los documentos, dilo.
Formato: solo el código DSL, con un comentario por cada suposición.
```

### Prompt 3 — Auditor C4
```
Actúa como revisor de diagramas de arquitectura. Evalúa estas vistas exportadas de
un modelo C4 con la lista de revisión de c4model.com/diagrams/checklist
(generales, elementos y relaciones): [archivos .puml e imágenes].
Responde en una tabla (vista, pregunta de la lista, cumple sí/no, evidencia
concreta, corrección sugerida). No inventes problemas: si algo cumple, indícalo.
No modifiques archivos. Al final, resume en dos líneas los 3 hallazgos más importantes.
```

### Prompt 4 — Explicación para público no técnico
```
Explica el siguiente diagrama de contexto al presidente de una cooperativa que no
es técnico, en máximo 120 palabras: qué hace el sistema, quién lo usa y de qué
servicios externos depende. Evita la jerga técnica y no afirmes nada que no esté en
el diagrama ni en los ADR: [pegar vista de contexto y ADR-002/003].
```

### Prompt 5 — Comparaciones
```
Compara con datos medidos (no estimados) dos formas de producir el diagrama de
contexto de BiblioUNSA: contexto-manual.puml (C4-PlantUML a mano) y workspace.dsl
exportado. Criterios: tiempo de generación, errores encontrados, esfuerzo si cambia
el nombre de un elemento y coherencia entre vistas. Después explica en 3 a 5 líneas
qué detalle de secuencia-reservar-libro.puml omite la vista dinámica y para qué
público sirve cada una. Si no tienes una medición, dilo en vez de inventar una cifra.
```

### Prompt 6 — README
```
Agrega al README.md existente la sección "Arquitectura C4 (Lab 06)": el diagrama de
contexto en Mermaid copiado tal cual de export/, enlaces a las imágenes y fuentes de
las cinco vistas, una tabla de entregables y los comandos para regenerar todo.
No cambies las secciones de los Laboratorios 04 y 05. No incluyas enlaces a archivos
que no existan.
```
