# E7 — Bitácora de IA

Se registran interacciones del trabajo realizado con el asistente y el mini framework de BiblioUNSA. Las entradas describen las acciones y observaciones comprobables en las trayectorias; no pretenden ser una transcripción literal de cada conversación. La reproducción de E6 y la comprobación posterior de E7 se distinguen de las interacciones originales.

| N.º | Ejercicio e interacción | Resultado observado | Evaluación |
|---:|---|---|---|
| 1 | E2: se pidió al asistente leer el ISSUE-01 y ejecutar las pruebas antes de editar. | Una prueba falló y otra pasó. El cálculo cobraba S/ 4 en lugar de S/ 2. | Se reprodujo el problema de la multa incluyendo el domingo. |
| 2 | E2: se solicitó revisar `multas.py` y corregir el cálculo. | Se excluyeron los domingos y las dos pruebas específicas pasaron. | La modificación respetó el alcance y las pruebas existentes. |
| 3 | E2: el asistente ejecutó la suite completa y revisó el diff. | 89 pruebas pasaron y 2 fallaron, correspondientes a los issues 02 y 03 pendientes. | Se comprobó que el agente no debía corregir esos problemas todavía. |
| 4 | E4: se pidió usar `mapa_repo()`, `anotar()` y `leer_notas()` para el ISSUE-03. | Las tres herramientas se utilizaron una vez; quedó una nota con la hipótesis sobre `fecha_devolucion`. | La memoria permitió conservar la causa identificada, aunque aumentó el contexto final. |
| 5 | E4: el asistente añadió el filtro `p.fecha_devolucion is None` a `buscar_vencidos()`. | Se observó el cambio en el diff; la prueba específica pasó después de la corrección. | Se excluyeron los préstamos devueltos sin cambiar la máquina de estados del dominio. |
| 6 | E5: el agente único propuso validar el campo `vigente` mediante `isinstance(vigente, bool)`. | La corrección cumplió el caso original del ISSUE-02, pero accedía a `respuesta.get()` sin validar primero el tipo de la respuesta. | Al comparar las soluciones se identificó una limitación: una respuesta `None` o una lista produciría `AttributeError` en lugar de `IntegracionException`. |
| 7 | E5: el planificador, el ejecutor y el revisor colaboraron sobre el mismo issue. | El ejecutor multiagente añadió la comprobación de que la respuesta fuera un diccionario. El revisor inspeccionó el diff y obtuvo 1 prueba específica aprobada; terminó con `APROBADO` en la primera ronda. | Se conservó la solución multiagente, más robusta frente a respuestas mal formadas. El revisor no solicitó una segunda ronda. |
| 8 | E6: se reprodujo una decisión de edición del agente único con aprobación humana. | La entrada `tal vez` fue rechazada; en el paso 6 el integrante respondió `n` y en el paso 7 respondió `s`. La traza registró una edición bloqueada y otra permitida. | El humano conserva el control de las ediciones. Fue una reproducción controlada de decisiones existentes, no una nueva conversación con el modelo. |

## Error del agente y verificación posterior

El error de la solución del agente único de E5 consiste en suponer que la respuesta académica siempre es un diccionario. El caso original no cubría una respuesta completa de tipo incorrecto, por lo que haber superado esa prueba no garantizaba que el adaptador manejara todas las entradas mal formadas. El ejecutor multiagente sí añadió la verificación del tipo de la respuesta, y el revisor aprobó el cambio. El problema del agente único se identificó al comparar los archivos de ambas ejecuciones, no por una solicitud de cambios del revisor.

Para comprobarlo de forma objetiva se incorporan en E7 dos casos de regresión en `tests/test_issue_02_respuesta.py`, usando `None` y una lista como respuesta simulada. Ambos deben producir `IntegracionException`. Se espera que fallen sobre la solución del agente único y pasen sobre la solución definitiva. Son pruebas posteriores al experimento original; no modifican sus trayectorias ni sus métricas.

Evidencias de la comprobación local, una vez ejecutada:

- [Pruebas contra la solución del agente único](trazas/regresion-e5-unico.txt).
- [Pruebas contra la solución definitiva](trazas/regresion-e5-final.txt).

## Evidencias de las interacciones

- [E2 — ISSUE-01](trazas/issue01-unico/ejecutor.jsonl)
- [E4 — ISSUE-03](trazas/issue03-unico/ejecutor.jsonl) y [notas](trazas/issue03-unico/notas.md)
- [E5 — Agente único](trazas/issue02-unico/ejecutor.jsonl)
- [E5 — Revisor multiagente](trazas/issue02-multi/revisor.jsonl)
- [E6 — Aprobación humana](trazas/issue02-aprobacion/ejecutor.jsonl)
