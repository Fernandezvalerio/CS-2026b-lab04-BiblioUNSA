# ADR-006: Persistir validaciones académicas recientes y reverificación pendiente

- Estado: Propuesto para ratificación por el equipo
- Fecha: 2026-10-31
- Iteración ADD: 1 (E2)
- Escenario: QA-08-01 y QA-08-06

## Contexto

BiblioUNSA se extiende a todas las facultades. Durante matrícula, la API académica puede fallar y el flujo de préstamos no debe bloquearse si existe una validación reciente y vigente. Se conserva el monolito modular, un VPS y acceso exclusivo vía API.

## Alternativas

1. Consulta síncrona sin caché: falla junto con el servicio externo.
2. Solo caché/cola Redis: simple, pero sin garantía de durabilidad tras reiniciar el servidor.
3. Guardar en PostgreSQL el mínimo estado académico (resultado y fecha) y un outbox de reverificación dentro de la misma transacción: más escrituras, pero recuperable. **Elegida**.

## Decisión

Proponer PostgreSQL como fuente durable del estado académico mínimo por un máximo de 24 h y de las tareas pendientes. Mantener el adaptador existente, timeout de 3 s, política fail-closed si no hay caché reciente y worker que reprograme dentro de 30 min. Redis puede acelerar, pero no ser la única copia.

## Evidencia

Simulación de 1000 solicitudes (fitness/academica.py): ante 327 fallos, las reservas bloqueadas pasan de 327 a 53; las **274** fallidas con validación reciente pudieron continuar y quedaron pendientes de reverificación a 15 min. Las 53 sin caché se bloquean deliberadamente.

## Trade-off

Se reduce interrupción del servicio a costa de consistencia temporal (hasta 24 h) y escrituras extra en la BD local. Mitigar con caducidad y reverificación. El prototipo no demuestra aún durabilidad real ni transacciones en PostgreSQL; queda implementación posterior.

## Relación

ADR-001, ADR-003, ADR-005, docs/architecture/add/iteracion-1.md.
