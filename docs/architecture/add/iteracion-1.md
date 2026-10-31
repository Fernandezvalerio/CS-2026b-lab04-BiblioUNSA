# E2 - ADD iteración 1: continuidad de reservas durante matrícula

## 1. Revisar entradas

- Escenario: QA-08-01 (H,H); disponibilidad e interoperabilidad.
- Restricciones: equipo de tres personas, un mes, un VPS, sin acceso a BD académica y conservando el monolito modular (ADR-001).
- Base: ADR-003 ya usa un adaptador con timeout de 3 s, caché de hasta 24 h y reverificación en 30 min; el simulador del Lab 07 usa caché en memoria.

## 2. Objetivo y elemento refinado

Con 35 % de consultas fallidas a la API académica, lograr 0 reservas bloqueadas **entre estudiantes que tienen validación vigente en caché de menos de 24 h**. Refinamos el módulo Integración académica y la programación de reverificación. No pretendemos autorizar estudiantes sin validación previa.

## 3. Conceptos y trade-offs

| Alternativa | Ventaja | Costo o riesgo | Decisión |
|---|---|---|---|
| Consulta síncrona sin respaldo | Simplicidad, dato reciente | Bloquea préstamos al fallar la API | Rechazada |
| Caché solo en memoria/Redis y tarea no duradera | Respuesta rápida | Pérdida del estado ante reinicio; reverificación incierta | Insuficiente |
| Última validación mínima en PostgreSQL + outbox transaccional de reverificación | Soporta reinicios y permite reintentar | Más escrituras y limpieza de datos vencidos | Seleccionada |
| Microservicio de integración separado | Escala de manera aislada | Segundo despliegue y operación fuera de presupuesto | Rechazada |

## 4. Evidencia experimental reproducible

Prototipo: fitness/academica.py. Simula 1000 reservas, semilla 2026, 35 % de fallas independientes, 80 % de estudiantes con verificación de matrícula previa y reciente. Se repite el mismo patrón aleatorio antes y después.

Ejecución: python -m fitness.academica

| Medida | Antes (sin respaldo) | Después (caché válida + outbox) | Objetivo |
|---|---:|---:|---|
| Reservas bloqueadas con caché reciente | 274 | 0 | 0 |
| Total de reservas bloqueadas (incluye estudiantes sin caché) | 327 | 53 | Informativa |
| Espera máxima por fallo API | 3 s | 3 s | <= 3 s |
| Pendientes programados para reverificación | 0 | 274 (a los 15 min) | Todos <= 30 min |

Se simularon 327 fallas de la API y 812 usuarios con caché reciente. El prototipo redujo de 327 a 53 las reservas bloqueadas, pero **las 53 restantes no tenían caché** y se bloquean correctamente. La simulación representa políticas, no mide PostgreSQL, Redis ni la latencia de un endpoint real. El outbox transaccional queda como decisión de diseño para implementar en Django.

## 5. Elementos instanciados

Integración académica mantiene la interfaz ValidadorMatricula del ADR-005; persistirá una instantánea mínima (estudiante, estado verificado, fecha), con caducidad máxima de 24 h, y generará una fila pendiente de reverificación en la misma transacción de reserva. El worker intentará procesarla dentro de 30 min.

## 6. Vistas y responsabilidades

La API mantiene su límite con el sistema académico; la BD local sirve de caché y outbox. Los módulos Reservas y Préstamos consumen un contrato propio, no los formatos del servicio externo. La vista C4 será actualizada en E6.

## 7. Verificación

Los tests automatizados se agregan en E5. Un estudiante sin validación previa deberá esperar a que la API vuelva; es una restricción de seguridad deliberada. Se conserva un riesgo de carga de escritura sobre PostgreSQL.
