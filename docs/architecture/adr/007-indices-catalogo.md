# ADR-007: Optimizar consultas del catálogo sin abandonar el monolito modular

- Estado: Propuesto para ratificación por el equipo
- Fecha: 2026-10-31
- Iteración ADD: 2 (E4)
- Escenario: QA-08-02

## Contexto

La incorporación de todas las facultades y biblioteca virtual aumenta la concurrencia. Se toma una hipótesis de 24 consultas por segundo, cuatro workers y presupuesto p95 <=1500 ms en el único VPS.

## Alternativas

1. Microservicios y orquestación: infraestructura desproporcionada para 3 personas en 1 mes; rechazada.
2. Caché Redis del catálogo: reduce lecturas, pero necesita invalidez precisa de disponibilidad; aplazada.
3. Índices PostgreSQL sobre filtros reales, revisión EXPLAIN ANALYZE y queries optimizadas: **elegida**.
4. Aumentar workers: puede agotar CPU/RAM antes de resolver la consulta.

## Decisión

Mantener Catálogo dentro de la aplicación Django; diseñar índices a partir de consultas reales, no crear microservicio nuevo. Medir el p95 en un entorno de ensayo antes de aceptar el índice de producción.

## Evidencia

Simulación de colas fitness/catalogo.py, 5000 solicitudes a 24 rps y cuatro workers: sin índice (230 ms supuestos por consulta), p95=76155,4 ms; con índice (80 ms supuestos), p95=253,5 ms. Esto verifica la hipótesis de capacidad **del modelo**, no el rendimiento de PostgreSQL real.

## Trade-off

Escrituras ligeramente más lentas y ocupación adicional de disco; seguridad de consistencia de stock sin caché volátil. Si EXPLAIN ANALYZE no valida la mejora, reconsiderar índices y parametrización.

## Relación

ADR-001, docs/architecture/add/iteracion-2.md.
