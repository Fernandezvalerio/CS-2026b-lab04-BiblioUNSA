# Bitácora de uso de IA — BiblioUNSA (Laboratorio 05)

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | 07/10 | Claude | Prompt 1 adaptado (Prompt IA 1 del Lab 05): diagrama de clases en PlantUML para HU-03 (reservar un libro validando la matrícula vigente), según ADR-001 y ADR-003 | 7 clases, 3 interfaces (puertos), la enumeración `EstadoPrestamo`, un adaptador académico con caché y la composición Libro–Ejemplar | Se revisó con la lista de verificación de E1: multiplicidad en ambos extremos de cada asociación, atributos sin datos sensibles (Estudiante solo guarda `id` y correo institucional) y nombres del dominio (C5). Se dejaron fuera Multa, Notificador y Autenticación porque no se derivan de la historia. Los estados de la enumeración coinciden con los de E3 | Aceptada (con revisión del equipo) |
| 2 | 07/10 | Claude | Prompt 2 (Lab 05): diagrama de secuencia en PlantUML de HU-03 (reservar un libro validando la matrícula vigente), a partir de `historia.md` y `clases.puml` | Una primera versión con `Reserva`, `Notificador` y `CacheMatricula`, y operaciones que no existen en el diagrama de clases (por ejemplo `Libro.reservarEjemplar`) | Se aplicó la regla C1: esas clases y operaciones no están en `clases.puml` ni se derivan de la historia. Se rehízo usando `Prestamo` en estado RESERVADO, `ValidadorMatricula`, `Ejemplar` y los repositorios. Se comprobó que cada mensaje es una operación de su clase y que se cubren los 4 criterios de aceptación | Corregida |
| 3 | 10/10 | Claude | Prompt 3 (Lab 05): diagrama de actividades en PlantUML del proceso "devolución con cálculo de multa" (E4), a partir de `clases.puml` y `estados-prestamo.mmd` | Diagrama con 3 particiones (Estudiante, Bibliotecario, Sistema), 3 decisiones (¿existe préstamo activo?, ¿fecha > fechaVencimiento?, ¿ejemplar en buen estado?) y un fork/join (`marcarDisponible()` y comprobante en paralelo). Asumió una tarifa de multa por día de retraso y una rama "reporta el daño" que no figuran en el caso | Se renderizó con PlantUML y se comprobó que cumple lo mínimo de E4 (≥ 3 particiones, ≥ 2 decisiones, fork/join). Se verificó que las acciones usan operaciones existentes en `clases.puml` (`registrarDevolucion`, `aplicarMulta`, `marcarDisponible`) y que los estados `DEVUELTO` y `CON_MULTA` coinciden con E3 (C2, C5). La tarifa por día y la rama de daño son supuestos del equipo, marcados en un comentario del `.puml`. Pendiente: validar el flujo con un compañero que actúe como usuario | Aceptada (con supuestos documentados) |
| 4 | 10/10 | Claude | Prompt 4 (Lab 05, Prompt IA 2 adaptado): esqueleto en Python 3.10+ (dataclasses, type hints, ABC) de `clases.puml` en `src/reservas/` (E6) | `dominio.py` con las 11 clases, la enumeración `EstadoPrestamo` y los puertos como clases abstractas (ABC). Lógica solo en `Ejemplar` y `Prestamo` (transiciones de E3); el adaptador y el servicio lanzan `NotImplementedError` | Se revisaron nombres y operaciones contra `clases.puml` (C5) y las transiciones contra `estados-prestamo.mmd` (C2). Se probó con un script el flujo RESERVADO → PRESTADO → VENCIDO → CON_MULTA, el flujo a DEVUELTO, el rechazo de una transición inválida y que el puerto no se instancia. Se ejecutó `pyreverse` y se compararon ambos diagramas: 10 diferencias en `round-trip.md` (sin multiplicidades, composición Libro–Ejemplar perdida, puertos como clases, agregación en lugar de dependencia, enum sin valores, visibilidad perdida, entre otras), cada una con su causa y acción | Aceptada (con revisión del equipo) |

> Los prompts completos están en el anexo. Nunca se incluyeron datos personales ni información confidencial.

## Anexo: prompts

### Prompt 1 — Diagrama de clases (historia HU-03)
```
Rol: actúa como diseñador de software orientado a objetos con experiencia en
monolitos modulares y arquitectura de puertos y adaptadores.
Contexto: "BiblioUNSA" es una plataforma para el préstamo y la reserva de libros de
las bibliotecas de la UNSA. Elegimos un monolito modular (ADR-001) con los módulos
Autenticación y acceso, Catálogo, Reservas, Préstamos y devoluciones, Multas e
Integración académica. El sistema académico se consulta solo por API mediante un
adaptador con timeout de 3 s y caché de la última validación por un máximo de 24 h;
cuando se usa la caché, el préstamo se marca para reverificación en ≤ 30 min (ADR-003).
Historia y criterios de aceptación: [pegar historia.md]
Restricciones: MVP en 1 mes, equipo de 3 developers, Ley 29733 (del estudiante solo
guardar id y correo institucional), nombres en español del dominio de la biblioteca.
Tarea: genera un diagrama de clases en PlantUML con (1) mínimo 6 clases, (2) 1 interfaz
(puerto) para la validación de matrícula, con su adaptador que la realice, (3) 1
enumeración para el estado del préstamo (RESERVADO, PRESTADO, VENCIDO, DEVUELTO,
CON_MULTA), (4) atributos con tipo y visibilidad, (5) operaciones, incluyendo una por
cada transición de estados del préstamo, y (6) multiplicidad en ambos extremos de cada
asociación.
Formato: solo el código PlantUML. No agregues clases que no se deriven de la historia;
si asumes algo, indícalo en un comentario. No inventes capacidades del sistema
académico de la UNSA; si no estás seguro, indícalo.
```

### Prompt 2 — Diagrama de secuencia (historia HU-03)
```
Rol: actúa como diseñador de software orientado a objetos con experiencia en
monolitos modulares y arquitectura de puertos y adaptadores.
Contexto: "BiblioUNSA" (monolito modular, ADR-001). Adjunto la historia HU-03
con sus 4 criterios de aceptación [pegar historia.md] y el diagrama de clases
ya revisado [pegar clases.puml]. El sistema académico se consulta con timeout de
3 s y caché de 24 h; si se usa la caché, el préstamo se marca para reverificación
en ≤ 30 min (ADR-003).
Tarea: genera un diagrama de secuencia en PlantUML del escenario principal de
HU-03 con (1) mínimo 5 líneas de vida (actor, interfaz, controlador, servicio,
entidades y puertos), (2) un fragmento alt para el éxito y los errores y un opt
o loop, (3) al menos un mensaje asíncrono (->>) y los mensajes de retorno, y
(4) que cubra los 4 criterios de aceptación.
Restricciones: cada mensaje debe ser una operación de la clase receptora
definida en clases.puml (regla C1). No agregues clases ni operaciones que no
estén en el diagrama de clases; si asumes algo, indícalo en un comentario.
Formato: solo el código PlantUML.
```

### Prompt 3 — Diagrama de actividades (devolución con cálculo de multa)
```
Rol: actúa como diseñador de software orientado a objetos con experiencia en
modelado de procesos de negocio.
Contexto: "BiblioUNSA" (monolito modular, ADR-001). Adjunto el diagrama de clases
ya revisado [pegar clases.puml] y la máquina de estados del préstamo
[pegar estados-prestamo.mmd]. El bibliotecario registra la devolución con el
carné QR del estudiante; si el libro se devuelve después de fechaVencimiento, se
aplica una multa.
Tarea: genera un diagrama de actividades en PlantUML del proceso "devolución con
cálculo de multa" con (1) mínimo 3 particiones (|Partición|), (2) mínimo 2
decisiones (if / else) y (3) una ejecución paralela (fork / end fork).
Restricciones: las acciones del sistema deben usar operaciones que existan en
clases.puml, y los estados nombrados deben coincidir con la enumeración
EstadoPrestamo (reglas C2 y C5). No agregues reglas de negocio que no estén en el
caso; si asumes algo (por ejemplo, la tarifa de la multa), indícalo en un comentario.
Formato: solo el código PlantUML.
```

### Prompt 4 — Ingeniería directa (clases a código Python)
```
Rol: actúa como desarrollador Python senior con experiencia en arquitectura de
puertos y adaptadores.
Contexto: "BiblioUNSA" (monolito modular, ADR-001). Adjunto el diagrama de clases
ya revisado [pegar clases.puml] y la máquina de estados del préstamo
[pegar estados-prestamo.mmd].
Tarea: genera el esqueleto en Python 3.10+ (dataclasses y type hints) en
src/reservas/dominio.py. Respeta exactamente los nombres de clases, atributos y
operaciones (en snake_case), la enumeración EstadoPrestamo, los puertos como clases
abstractas (ABC) y las multiplicidades cuando sea posible. Implementa solo la lógica
mínima de las operaciones de Prestamo y Ejemplar (transiciones de estado válidas);
el adaptador del sistema académico y el servicio deben lanzar NotImplementedError.
Restricciones: no agregues clases ni operaciones que no estén en el diagrama; si
asumes algo, indícalo en un comentario o docstring.
Formato: solo el código Python.
```
