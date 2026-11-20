# ADR-010: Arquitectura del sistema agéntico de BiblioUNSA

- Estado: Propuesto para ratificación por el equipo
- Fecha: 2026-11-20
- Decisores: Equipo BiblioUNSA (Grupo 04)

## Contexto

BiblioUNSA debe corregir errores en las reglas de multas, la integración académica y la consulta de préstamos vencidos. Aunque las reglas de negocio son deterministas, localizar el código responsable, reproducir un fallo y ajustar una solución según las observaciones requiere explorar el repositorio. Queremos incorporar agentes sin comprometer la arquitectura del proyecto, las pruebas existentes ni los datos institucionales. El laboratorio también requiere trabajar sin claves de API, poder repetir las ejecuciones y preservar el control humano de las modificaciones.

## Alternativas consideradas

| Alternativa | Evaluación |
|---|---|
| Flujo fijo para corregir todos los errores | Útil para cálculos y verificaciones conocidas, pero poco flexible al explorar fallos cuya causa no se conoce de antemano. |
| Un solo agente ReAct | Menor coordinación y contexto; adecuado para errores acotados. Es la opción inicial elegida. |
| Planificador, ejecutor y revisor actor-crítico | Permite una revisión independiente y especialización por permisos; requiere más pasos y contexto. Se elige para cambios que lo justifiquen. |
| Agente con shell libre o acceso directo a `main` | Aumenta el alcance de las acciones y el riesgo de modificar pruebas, credenciales o archivos no autorizados. Se descarta. |
| Memoria global persistente o base vectorial | Agrega complejidad y almacenamiento innecesarios para tareas breves. Se descarta en esta etapa. |

## Decisión

Usaremos un agente ReAct como punto de partida. Cada decisión contiene una breve intención y una acción con argumentos, o una respuesta final. El programa valida el contrato JSON y evalúa la política antes de ejecutar herramientas; devuelve el resultado como observación y registra la trayectoria en JSONL. `ModeloInteractivo` permite obtener decisiones desde el navegador y `ModeloGrabado` permite reproducir decisiones ya registradas. Este diseño conserva el modelo como componente intercambiable.

Cuando el riesgo justifique una segunda revisión, utilizaremos coordinación por gestor y actor-crítico: un planificador que solo lee el issue, un ejecutor que puede editar código en la copia y un revisor que puede leer, buscar, consultar el mapa y las notas, ejecutar las pruebas del issue e inspeccionar los cambios, pero no editar archivos ni escribir notas. El orquestador limita la coordinación a dos rondas y deja la integración al equipo.

Para actuar sobre el proyecto mantenemos un conjunto reducido de herramientas: listado, lectura, búsqueda, pruebas, diff, edición de fragmentos, mapa AST y notas. `ejecutar_comando` solo admite `python -m pytest -q`. Las ediciones se restringen a archivos Python en `src/` dentro de la copia y no se permite modificar pruebas mediante el agente. La memoria consiste en el historial de trabajo actual y `notas.md` por ejecución; no se comparten notas entre tareas.

El presupuesto es de 4 pasos para el planificador, 12 para el ejecutor y 8 para el revisor por ronda. Los estados del bucle y las decisiones rechazadas o bloqueadas se registran para su revisión. Desde E6, `ejecutar.py` y `orquestador.py` solicitan por defecto la aprobación humana de cada edición; la consola acepta únicamente `s` o `n`. La opción `--sin-aprobacion` se reserva para reproducir experimentos anteriores en copias de trabajo. El nivel de delegación actual es **revisor**: ninguna modificación se integra sin revisión humana del diff y las pruebas. La aprobación del crítico no equivale a la autorización para fusionar un Pull Request.

## Consecuencias

- **Positivas:** los cambios pueden comprobarse con pruebas y trazas, la separación de roles reduce los permisos innecesarios y la aprobación humana permite detener modificaciones no deseadas. La reproducción grabada facilita revisar un experimento sin depender de una nueva respuesta del modelo.
- **Costos:** en ISSUE-02 el agente único necesitó 10 pasos, 9 acciones y 18362 caracteres de contexto; el sistema multiagente necesitó 22 pasos, 20 acciones y 51616 caracteres en una ronda. El ejecutor multiagente añadió la validación de que la respuesta completa fuera un diccionario, omitida por el agente único. El revisor confirmó la solución y no solicitó una segunda ronda. Es una mejora comprobable en el diff, no un error descubierto por el crítico durante una ronda de corrección.
- **Costos de memoria:** ISSUE-03 empleó mapa y notas, con 12 pasos y 24432 caracteres frente a 8 pasos y 8027 caracteres de ISSUE-01. Los issues son distintos; no es posible aislar el efecto de las herramientas a partir de esa comparación. En futuras tareas conviene limitar la extensión del mapa y de las observaciones.
- **Control humano:** E6 registró 11 pasos, una acción bloqueada y dos solicitudes de edición: rechazamos la primera y aceptamos la segunda. Además, el programa rechazó una entrada inválida en consola. Fue una reproducción controlada de decisiones previas, no una nueva ejecución interactiva del LLM.
- **Riesgos y límites:** la copia es un aislamiento lógico, no una frontera de seguridad del sistema operativo. Las pruebas pueden ejecutar el código modificado, por lo que no se deben usar secretos ni código no confiable. Las grabaciones no prueban la consistencia de respuestas futuras y el contexto final no representa por sí solo el costo o consumo de tokens. Los permisos y el presupuesto deben revisarse antes de ampliar la autonomía.

## Evidencias y relación

- [Lienzo de diseño](../../../agentes/diseno/lienzo.md) y [máquina de estados](../../../agentes/diseno/estados.puml).
- [Comparación E2/E4](../../../agentes/trazas/issue03-unico/comparacion-e4.md) y [comparación E5](../../../agentes/comparacion-e5.md).
- [Delegación progresiva](../../../agentes/delegacion.md) y [traza de aprobación humana](../../../agentes/trazas/issue02-aprobacion/ejecutor.jsonl).
- [Observación](../../../agentes/observacion.md) y [bitácora](../../../agentes/bitacora-ia.md).
- ADR-003, ADR-005 y ADR-006, por la integración académica, los patrones de diseño y la resiliencia de matrícula.
- Guía de Laboratorio 10 de Construcción de Software, UNSA (2026B), secciones 1.3–1.8 y ejercicios E1–E8.
