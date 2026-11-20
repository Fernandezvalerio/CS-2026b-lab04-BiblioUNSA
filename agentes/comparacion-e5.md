# E5. Comparación entre agente único y actor-crítico

## Objetivo

Resolver el ISSUE-02 de BiblioUNSA, relacionado con la interpretación incorrecta del campo `vigente` del sistema académico, y comparar las dos formas de coordinación desde la misma versión base del E4.

## Resultados de las ejecuciones

| Métrica | Agente único | Actor-crítico |
|---|---:|---:|
| Rondas | 1 | 1 |
| Pasos | 10 | 22 |
| Acciones | 9 | 20 |
| Acciones bloqueadas | 0 | 0 |
| Decisiones rechazadas por el contrato | 0 | 0 |
| Contexto final (caracteres) | 18 362 | 51 616 |
| Veredicto del revisor | No aplica | APROBADO |

El contexto final del sistema multiagente se distribuyó entre el planificador (2489 caracteres), el ejecutor (31 745) y el revisor (17 382). La comparación utiliza la suma de los contextos finales de los agentes reportada por el framework; no representa tokens consumidos ni costo monetario.

## Revisión del cambio

El revisor aprobó la solución en la primera ronda. El cambio en `src/reservas/validadores.py` exige que `vigente` sea un booleano y genera `IntegracionException` ante valores inválidos. De acuerdo con la revisión, el comportamiento de `True` y `False` se conserva y una respuesta mal formada no permite ocupar el ejemplar ni crear un préstamo. La prueba específica ejecutada por el revisor pasó y el ejecutor reportó 91 pruebas aprobadas en la suite completa. Los demás casos límite fueron revisados mediante inspección estática, no mediante pruebas independientes adicionales.

El diff entre ambas soluciones muestra que el agente único valida el campo `vigente` mediante `isinstance(vigente, bool)`, pero llama a `respuesta.get()` sin comprobar primero el tipo de la respuesta. El ejecutor multiagente añade `isinstance(respuesta, dict)` antes de acceder al campo. Así, una respuesta que no sea un diccionario se rechaza mediante `IntegracionException`, en vez de arriesgar un `AttributeError` al acceder a `.get()`. Ambas soluciones rechazan valores no booleanos de `vigente` dentro de un diccionario.

El revisor no solicitó cambios ni reportó defectos bloqueantes en la solución multiagente. La protección adicional fue incorporada por el ejecutor multiagente y posteriormente aprobada por el revisor; no hay evidencia de que el crítico la haya descubierto o solicitado. Se seleccionó la versión multiagente por su validación más completa. El caso de una respuesta que no sea un diccionario se comprueba por inspección del diff; no se cuenta como una prueba adicional ejecutada.

## Conclusión

El agente único necesitó 10 pasos y 9 acciones, frente a los 22 pasos y 20 acciones del sistema multiagente.  
El actor-crítico también utilizó más contexto, pasando de 18 362 a 51 616 caracteres.  
Ninguna de las dos ejecuciones registró acciones bloqueadas ni decisiones inválidas.  
El revisor aprobó el cambio en la primera ronda, sin solicitar nuevas correcciones.  
La variante multiagente añadió una validación del tipo de respuesta, que el agente único había omitido; el revisor la aprobó.  
Para correcciones pequeñas, conviene comenzar con un agente único y evitar una coordinación innecesaria.  
En cambios que afectan reglas de negocio sensibles, una revisión adicional puede justificar el mayor esfuerzo.

## Evidencias

- [Métricas del agente único](trazas/issue02-unico/metricas.json).
- [Métricas del sistema multiagente](trazas/issue02-multi/metricas.json).
- [Trazas del agente único](trazas/issue02-unico/).
- [Trazas del sistema multiagente](trazas/issue02-multi/).
