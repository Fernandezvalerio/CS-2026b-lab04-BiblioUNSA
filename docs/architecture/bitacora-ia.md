# Bitácora de uso de IA — BiblioUNSA

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | 02/10 | Claude | Prompt 1 adaptado: 3 alternativas de estilo para BiblioUNSA (plazo de 1 mes, 3 developers, un VPS) | Monolito en capas, monolito modular y microservicios; recomendó microservicios "por separación de la integración" | Excede R-01 (1 mes), R-02 (3 developers) y R-03 (presupuesto). La separación de la integración académica se logra con un adaptador dentro del monolito | Rechazada (la recomendación) |
| 2 | 02/10 | Claude | Prompt 2: crítica adversarial ("abogado del diablo") contra su propia recomendación | 5 riesgos: complejidad operativa, consistencia de datos, latencia entre servicios, costo de infraestructura y seguridad entre servicios | Los riesgos confirman que los microservicios no encajan con nuestras restricciones. Se anotó la mitigación con adaptador y caché para el monolito modular | Aceptada |
| 3 | 02/10 | Claude | Prompt 3: borrador de `drivers.md` (requisitos, atributos, restricciones y 3 escenarios de calidad) a partir del caso 4 | 7 requisitos funcionales, 5 atributos de calidad, 6 restricciones y 3 escenarios con medidas numéricas | Se ajustó R-02 a las tecnologías reales del equipo. R-06 (proveedor de identidad OAuth/OIDC) no estaba confirmado, así que se marcó para verificar con la oficina responsable | Corregida |
| 4 | 03/10 | Claude | Prompt 4: puntuar las 3 alternativas con 5 criterios ponderados | Matriz con totales A = 4,05, B = 4,20 y C = 2,80 | Se recalculó a mano cada total (Σ peso × puntaje) y coincidió. Se revisó que la diferencia entre A y B es pequeña y se justificó el desempate con QA-03 (cambio del adaptador académico) | Aceptada |
| 5 | 03/10 | Claude | Prompt 5: afirmación sobre la API del sistema académico | Afirmó que el sistema académico de la UNSA expone una API REST pública y documentada lista para consumir | No hay evidencia de ello. Se consultó a la oficina responsable. Por eso se aisló la integración en un adaptador reemplazable y se usó caché (QA-02) | Rechazada |
| 6 | 03/10 | Claude | Prompt 6: generar el diagrama Mermaid de la alternativa elegida a partir de `matriz-decision.md` | Código Mermaid con 2 actores, 6 módulos, PostgreSQL y 2 servicios externos | Se validó en mermaid.live y en GitHub, y se revisó línea por línea. Se comprobó que cada módulo corresponde a un requisito (RF-01 a RF-07) y que las dependencias van de arriba hacia abajo | Aceptada |

> Los prompts completos están en el anexo. Nunca se incluyeron datos personales ni información confidencial.

## Anexo: prompts

### Prompt 1 — Generación de alternativas
```
Actúa como arquitecto de software senior con experiencia en sistemas universitarios.
Contexto: plataforma "BiblioUNSA" para préstamo y reserva de libros de las
bibliotecas de la UNSA. Actores: estudiante, bibliotecario y sistema académico.
Funciones: catálogo en línea, reserva, préstamo con carné QR, multas y validación
de matrícula vigente. Atributo crítico: seguridad e interoperabilidad (acceso con
correo institucional; consulta al sistema académico solo mediante API).
Restricciones: 3 developers con experiencia en Python/Django, presupuesto bajo
(un VPS), MVP en 1 mes.
Tarea: propón 3 alternativas de estilo arquitectónico. Para cada una indica
fortalezas, debilidades, riesgos y qué atributos de calidad favorece o penaliza.
Formato: tabla comparativa en Markdown y, al final, tu recomendación justificada.
No inventes APIs ni capacidades de servicios; si no estás seguro, indícalo.
```

### Prompt 2 — Crítica adversarial
```
Ahora actúa como "abogado del diablo". Critica duramente la alternativa que
recomendaste: ¿qué supuestos no se cumplen con nuestras restricciones?, ¿qué podría
fallar en producción?, ¿qué costo oculto tiene? Enumera los 5 riesgos más graves y,
para cada uno, una táctica arquitectónica de mitigación.
```

### Prompt 3 — Drivers y escenarios de calidad
```
Rol: actúa como arquitecto de software senior con experiencia en sistemas universitarios.
Contexto: "BiblioUNSA" es una plataforma para el préstamo y la reserva de libros de las
bibliotecas de la UNSA. Actores: estudiante, bibliotecario y sistema académico.
Funciones: catálogo en línea, reserva de libros, préstamo con carné QR, control de multas
y validación de matrícula vigente. Atributo crítico: seguridad e interoperabilidad (acceso
con el correo institucional; consulta al sistema académico solo mediante API, sin acceso
directo a su base de datos).
Restricciones: MVP en 1 mes, equipo de 3 developers, presupuesto bajo (un servidor).
Tarea: redacta el contenido de drivers.md con (1) mínimo 5 requisitos funcionales con su
actor y prioridad, (2) mínimo 4 atributos de calidad ordenados por prioridad, con una
línea de justificación cada uno, (3) mínimo 4 restricciones con ID (R-01, R-02...) y
(4) 3 escenarios de calidad de atributos distintos, con las seis partes y una medida numérica.
Formato: tablas en Markdown con IDs (RF-01, QA-01, R-01).
No inventes capacidades de servicios de la UNSA; si no estás seguro, indícalo.
```

### Prompt 4 — Matriz de decisión
```
Rol: actúa como arquitecto de software senior.
Contexto: los drivers de BiblioUNSA están en el mensaje anterior (RF-01 a RF-07, QA-01
a QA-03, R-01 a R-06). Las alternativas son: A. monolito en capas, B. monolito modular
y C. microservicios.
Restricciones: MVP en 1 mes, equipo de 3 developers, un solo servidor.
Tarea: define 5 criterios derivados de los drivers con pesos que sumen 100 % y justifica
cada peso citando un driver. Puntúa cada alternativa de 1 a 5 en cada criterio, calcula
el total ponderado mostrando la operación (Σ peso × puntaje) y justifica los puntajes
más discutibles.
Formato: tablas en Markdown y una conclusión breve.
```

### Prompt 5 — Integración con el sistema académico
```
Rol: actúa como arquitecto de software senior.
Contexto: BiblioUNSA debe validar la matrícula vigente de cada estudiante consultando el
sistema académico de la UNSA solo mediante API.
Restricciones: no se puede acceder directamente a su base de datos; el equipo es de
3 developers y el plazo es de 1 mes.
Tarea: explica cómo conviene integrar BiblioUNSA con ese sistema (qué componente se
encarga, qué pasa si el sistema académico no responde) e indica qué datos necesitaríamos
confirmar con la oficina responsable.
Formato: lista breve de pasos y de preguntas pendientes.
No inventes APIs ni capacidades de servicios; si no estás seguro, indícalo.
```

### Prompt 6 — Diagrama Mermaid de la alternativa elegida
```
Rol: actúa como arquitecto de software con experiencia en Diagram as Code.
Contexto: elegimos el monolito modular para BiblioUNSA (ver matriz-decision.md). Módulos:
Autenticación y acceso, Catálogo, Reservas, Préstamos y devoluciones (QR), Multas e
Integración académica. Actores: estudiante y bibliotecario. Datos en PostgreSQL con un
esquema por módulo. Servicios externos: proveedor de identidad (correo institucional)
y sistema académico (API).
Restricciones: la sintaxis debe renderizar en mermaid.live y en GitHub.
Tarea: escribe el código Mermaid (flowchart TB) con mínimo 2 actores, todos los módulos,
el almacenamiento de datos, mínimo 1 servicio externo, un subgraph que agrupe el
monolito y la dirección de las dependencias.
Formato: solo el bloque de código Mermaid.
```
