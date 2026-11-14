# Product Backlog inicial — BiblioUNSA

Este backlog reúne las funcionalidades principales de BiblioUNSA: consultar el catálogo, reservar libros, registrar préstamos y devoluciones y revisar los movimientos pendientes. Lo armamos a partir de los requisitos que ya se habían definido para el proyecto en los laboratorios anteriores. No existía un backlog formal en el repositorio, así que este documento sirve como punto de partida para el Laboratorio 09.

Las historias H1–H6 son las mismas que usamos en `prompts/criterios/casos.yaml`. La prioridad se tomó de los requisitos originales y el orden es una propuesta para organizar el trabajo; todavía puede cambiar cuando el equipo lo revise.

## Historias priorizadas

| Orden sugerido | ID | Historia resumida | Prioridad | Requisitos de referencia | Estado |
| --- | --- | --- | --- | --- | --- |
| 1 | H3 | Inicio de sesión con correo institucional | Alta | RF-01, QA-01 | Aprobado |
| 2 | H2 | Búsqueda de libros en el catálogo | Alta | RF-02 | Aprobado |
| 3 | H1 | Reserva de ejemplares disponibles | Alta | RF-03, RF-05; HU-03 del Lab 05 | Aprobado |
| 4 | H4 | Registro de préstamos con carné QR | Alta | RF-04 | Aprobado |
| 5 | H5 | Registro de devoluciones | Alta | RF-04, RF-06 | Aprobado |
| 6 | H6 | Consulta de préstamos, reservas y multas | Media | RF-07 | Aprobado |

## H3 — Inicio de sesión institucional

**Historia:** Como estudiante, quiero iniciar sesión con mi correo institucional UNSA para acceder a mis servicios de biblioteca.

**Criterios de aceptación iniciales:**

- Un estudiante que usa una identidad institucional válida puede acceder a los servicios que le corresponden.
- Una persona que intenta ingresar con un correo no institucional no obtiene acceso.
- Si el inicio de sesión falla, la persona recibe un mensaje comprensible y no queda autenticada.

**Referencia:** RF-01 y QA-01. La integración con un proveedor de identidad concreto sigue pendiente de confirmación; esta historia no presupone uno.

## H2 — Búsqueda en el catálogo

**Historia:** Como estudiante, quiero buscar libros por título, autor o biblioteca para encontrar el material que necesito.

**Criterios de aceptación iniciales:**

- Al buscar un título o autor con coincidencias, aparecen los libros correspondientes.
- El estudiante puede acotar la búsqueda por biblioteca.
- Cuando no hay coincidencias, el sistema lo comunica sin mostrar resultados incorrectos.

**Referencia:** RF-02.

## H1 — Reserva de un ejemplar

**Historia:** Como estudiante de la UNSA, quiero reservar un ejemplar disponible para tenerlo apartado hasta recogerlo.

**Criterios de aceptación iniciales:**

- Si la matrícula está vigente y el ejemplar está disponible, se confirma la reserva y deja de figurar como disponible.
- Si el ejemplar ya está reservado o prestado, la reserva se rechaza y se informa al estudiante.
- Si la matrícula no está vigente, no se concreta la reserva y se muestra el motivo.

**Referencia:** RF-03, RF-05 y la historia **HU-03** documentada en `docs/design/historia.md`. Esa historia también contempla la indisponibilidad temporal del sistema académico, con reglas de caché y reverificación; no se repiten aquí porque ya están detalladas allí.

## H4 — Registro de préstamos con carné QR

**Historia:** Como bibliotecario, quiero registrar la entrega de un libro usando el carné QR para llevar el control del préstamo.

**Criterios de aceptación iniciales:**

- Cuando el estudiante recoge un ejemplar reservado y se valida la operación con su carné QR, el préstamo queda registrado como entregado.
- Un ejemplar que no está disponible no puede entregarse como si estuviera libre.
- El bibliotecario puede identificar si la operación se completó o fue rechazada.

**Referencia:** RF-04 y el flujo de estados del préstamo del Lab 05.

## H5 — Registro de devoluciones

**Historia:** Como bibliotecario, quiero registrar la devolución de un ejemplar para actualizar el préstamo y su disponibilidad.

**Criterios de aceptación iniciales:**

- Al registrar la devolución de un préstamo activo dentro del plazo, el movimiento queda cerrado y el ejemplar vuelve a estar disponible.
- Si el ejemplar se devuelve después del vencimiento, el sistema identifica la devolución tardía y refleja que corresponde evaluar una multa.
- No se registra una segunda devolución de un préstamo que ya estaba cerrado.

**Referencia:** RF-04, RF-06 y el flujo de devolución del Lab 05. El importe y la forma de cálculo de las multas necesitan una regla de negocio acordada; no se fijan montos en este backlog.

## H6 — Consulta de préstamos, reservas y multas

**Historia:** Como estudiante, quiero consultar mis reservas, préstamos y multas para saber qué tengo pendiente.

**Criterios de aceptación iniciales:**

- Un estudiante con movimientos puede ver sus reservas, préstamos y multas asociados.
- La consulta permite distinguir los movimientos pendientes de los ya finalizados.
- Si no tiene registros, ve un estado vacío claro en lugar de información de otras personas.

**Referencia:** RF-07.

## Casos de evaluación del Laboratorio 09

Los ocho casos de `prompts/criterios/casos.yaml` se forman con estas **seis historias** y dos entradas adicionales que no deben tratarse como funcionalidades del producto:

| Caso | Para qué se usa |
| --- | --- |
| H1–H6 | Evaluar la generación de criterios para historias del proyecto |
| H7 | Comprobar que el prompt detecta una historia demasiado ambigua y pide aclaraciones (no INVEST) |
| H8 | Comprobar que el prompt ignora una instrucción maliciosa incluida dentro de una historia |

**H7 y H8 no forman parte del Product Backlog**: son casos de prueba diseñados para la evaluación del prompt.

## Documentos utilizados

- `docs/architecture/drivers.md`: RF-01 a RF-07 y prioridades.
- `docs/design/historia.md`: HU-03 y sus criterios de aceptación.
- `README.md`: descripción general del caso BiblioUNSA.
- `prompts/criterios/casos.yaml`: historias H1–H6 usadas en el Laboratorio 09.
