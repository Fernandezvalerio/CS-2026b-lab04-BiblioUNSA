# Revisión de consistencia — BiblioUNSA (Lab 05, E7)

Se aplicó el **Prompt IA 3 (auditor de consistencia)** a los cinco diagramas UML del laboratorio (ver el prompt completo en el anexo de [`bitacora-ia.md`](bitacora-ia.md)). La IA solo reporta hallazgos; no reescribe los diagramas. Cada hallazgo se verificó contra los archivos, y las reglas C1, C2 y C5 se comprobaron además con un script que compara los nombres de operaciones y estados.

| Diagrama revisado | Archivo |
|-------------------|---------|
| Clases | [`clases.puml`](clases.puml) |
| Secuencia | [`secuencia-reservar-libro.puml`](secuencia-reservar-libro.puml) |
| Estados | [`estados-prestamo.mmd`](estados-prestamo.mmd) |
| Actividades | [`actividades-devolucion-multa.puml`](actividades-devolucion-multa.puml) |
| Paquetes | [`paquetes.puml`](paquetes.puml) |

Reglas: **C1** cada mensaje de secuencia es una operación de la clase receptora · **C2** cada transición de estados corresponde a una operación · **C3** las multiplicidades reflejan el negocio · **C4** paquetes sin ciclos y coherentes con el ADR-001 · **C5** nombres del dominio iguales en todos los diagramas.

## Hallazgos

| # | Regla | Elemento (archivo) | Hallazgo de la IA | Verificación del equipo | Corrección |
|---|-------|--------------------|-------------------|-------------------------|------------|
| 1 | C2 | `estados-prestamo.mmd` vs `actividades-devolucion-multa.puml` | La actividad aplica la multa cuando `fecha > fechaVencimiento` sin pasar por `marcarVencido()`, pero en el diagrama de estados `CON_MULTA` solo se alcanza desde `VENCIDO`. Un préstamo `PRESTADO` devuelto tarde antes de que se ejecute `marcarVencido()` no tiene transición. | **Confirmado.** En `dominio.py`, `registrar_devolucion()` sobre un préstamo `PRESTADO` lo deja en `DEVUELTO` aunque sea tardío, y la multa se pierde. | Agregar en la actividad el paso `marcarVencido()` antes de `registrarDevolucion(fecha)` cuando la devolución es tardía, o agregar la transición `PRESTADO → CON_MULTA` en E3. Decidir con el equipo. |
| 2 | C2 | `estados-prestamo.mmd`, transición `CON_MULTA --> [*] : multa pagada` | La transición no corresponde a ninguna operación de `Prestamo`. | **Confirmado.** Es un evento del módulo Multas, que `clases.puml` dejó fuera de alcance. | Agregar `registrarPagoMulta()` a `Prestamo` en `clases.puml` y usarlo como etiqueta. |
| 3 | C2 | `estados-prestamo.mmd`, transición `[*] --> RESERVADO : Prestamo()` | `Prestamo()` no es una operación declarada en `clases.puml`. | **Falso positivo.** Es el constructor: la creación del objeto en `RESERVADO` es el evento inicial, y `secuencia-reservar-libro.puml` la modela con `<<create>>`. Los constructores no se listan como operaciones. | Ninguna. |
| 4 | C1 | `secuencia-reservar-libro.puml`, mensaje `POST /reservas` hacia `ReservaController` | `ReservaController` no existe en `clases.puml`, así que el mensaje no corresponde a una operación. | **Falso positivo.** El controlador y la interfaz web pertenecen a la capa de presentación del Lab 04 (API REST + web responsive), que no forma parte del diagrama de clases del dominio. Los 12 mensajes dirigidos a clases del dominio sí existen en `clases.puml` (verificado con script). | Ninguna. |
| 5 | C1 / C5 | `secuencia-reservar-libro.puml`, retornos `IntegracionException`, `MatriculaNoVigente` y `EjemplarNoDisponible` | Las tres excepciones aparecen en la secuencia y no están en `clases.puml`. Además mezclan estilos de nombre (una lleva el sufijo `Exception`, las otras no). | **Confirmado.** | Declarar las tres como excepciones del dominio en `clases.puml` (o en un comentario) y unificar el nombre, por ejemplo `IntegracionException`, `MatriculaNoVigenteException` y `EjemplarNoDisponibleException`. |
| 6 | C4 / C5 | `paquetes.puml` vs ADR-001 | Los nombres de los paquetes no son iguales a los módulos del ADR-001: `integracion` (ADR: "Integración académica"), `prestamos` ("Préstamos y devoluciones") y `autenticacion` ("Autenticación y acceso"). | **Confirmado (menor).** Los nombres de paquete se abreviaron y se escribieron sin tildes. | Renombrar los paquetes con los nombres del ADR-001 o dejar una nota en `paquetes.puml` con la equivalencia. |
| 7 | C4 | `paquetes.puml` vs `arquitectura.mmd` (Lab 04) | `prestamos` no depende de `integracion`, pero el diagrama de arquitectura del Lab 04 dibuja Reservas **y** Préstamos hacia Integración académica. | **Falso positivo.** El diagrama de arquitectura es una vista gruesa. Aquí solo `reservas` usa el puerto `ValidadorMatricula`, porque la reverificación (`reverificarPendientes`) está en `ServicioReservas`. Ni el ADR-001 ni el ADR-003 exigen esa dependencia. Está documentado en los comentarios de `paquetes.puml`. | Ninguna. |
| 8 | C3 | `clases.puml`, asociación `Prestamo "0..*" --> "1" Ejemplar` | La multiplicidad permite varios préstamos por ejemplar, pero el criterio 4 de la historia dice que un ejemplar ya reservado o prestado no se puede reservar de nuevo. | **Confirmado (menor).** La multiplicidad `0..*` es correcta para el historial de préstamos; la regla "un solo préstamo activo por ejemplar" se hace cumplir con `Ejemplar.disponible`, pero el diagrama no lo dice. | Agregar una nota en `clases.puml`: "Un ejemplar tiene a lo sumo un préstamo activo (RESERVADO, PRESTADO o VENCIDO)". |

**Resumen:** 8 hallazgos de la IA, de los cuales 5 se confirmaron y 3 fueron falsos positivos (#3, #4 y #7).

## Verificaciones sin hallazgos

- **C1:** las 12 operaciones distintas que reciben mensajes en la secuencia (`validar`, `consultarApi`, `leerCache`, `cacheVigente`, `esVigente`, `buscar`, `estaDisponible`, `marcarReservado`, `guardar`, `marcarParaReverificacion`, `reverificarPendientes` y `reservarLibro`) existen en `clases.puml`.
- **C2:** las 5 operaciones de las transiciones de E3 (`entregar`, `marcarVencido`, `registrarDevolucion`, `aplicarMulta`, `marcarParaReverificacion`) existen en `Prestamo`. Los 5 estados del diagrama coinciden con la enumeración `EstadoPrestamo`.
- **C3:** `Estudiante 1 — 0..* Prestamo` y `Libro 1 *— 1..* Ejemplar` reflejan el negocio.
- **C4:** el diagrama de paquetes tiene 13 dependencias y no forma ciclos (verificado con script).
- **C5:** `Prestamo`, `Ejemplar`, `Estudiante`, `ResultadoMatricula` y los 5 estados usan el mismo nombre en clases, secuencia, estados, actividades y en la historia de usuario.

## Cambios pendientes

Los hallazgos confirmados (#1, #2, #5, #6 y #8) quedan como cambios pendientes de los diagramas, igual que `aceptarPreparacion()` en el modelo de la guía. No se corrigieron en este archivo, porque la IA solo reporta; el equipo decide cuáles aplicar antes de la entrega.
