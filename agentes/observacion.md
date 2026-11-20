# E7 — Observación del sistema agéntico

El análisis se basa en las ejecuciones realizadas por el equipo durante E2, E4, E5 y E6. Se trabajó sobre copias del repositorio y se ejecutaron pruebas antes y después de las modificaciones. Los pasos corresponden a las decisiones registradas; las acciones incluyen las solicitudes de herramientas bloqueadas, pero no los rechazos de contrato. El contexto final se expresa en caracteres y, en el caso multiagente, corresponde a la suma de los historiales finales de los agentes, no a la cantidad de tokens consumidos.

## Métricas de los tres issues

| Ejecución | Pasos | Rondas | Acciones | Herramientas (llamadas) | Contrato rechazado | Bloqueadas | Contexto final (caracteres) |
|---|---:|---:|---:|---|---:|---:|---:|
| ISSUE-01 (`issue01-unico`) | 8 | 1 | 7 | leer_archivo (2), ejecutar_pruebas (2), editar_archivo (1), ejecutar_comando (1), ver_cambios (1) | 0 | 0 | 8027 |
| ISSUE-02 (`issue02-multi`) | 22 | 1 | 20 | leer_archivo (11), ejecutar_pruebas (3), mapa_repo (1), editar_archivo (1), ejecutar_comando (1), ver_cambios (2), listar_archivos (1) | 0 | 0 | 51616 |
| ISSUE-03 (`issue03-unico`) | 12 | 1 | 11 | mapa_repo (1), leer_archivo (3), ejecutar_pruebas (2), anotar (1), leer_notas (1), editar_archivo (1), ejecutar_comando (1), ver_cambios (1) | 0 | 0 | 24432 |

## Ejecuciones complementarias

| Ejecución | Pasos | Rondas | Acciones | Herramientas (llamadas) | Contrato rechazado | Bloqueadas | Contexto final (caracteres) |
|---|---:|---:|---:|---|---:|---:|---:|
| Agente único (`issue02-unico`) | 10 | 1 | 9 | leer_archivo (3), ejecutar_pruebas (2), buscar (1), editar_archivo (1), ejecutar_comando (1), ver_cambios (1) | 0 | 0 | 18362 |
| Aprobación humana (`issue02-aprobacion`) | 11 | 1 | 10 | leer_archivo (3), ejecutar_pruebas (2), buscar (1), editar_archivo (2), ejecutar_comando (1), ver_cambios (1) | 0 | 1 | 19401 |

## Análisis

En el ISSUE-01 el agente corrigió el cálculo de multas y consiguió que las dos pruebas específicas pasaran. Fue la ejecución con menos pasos y contexto. Para el ISSUE-03 se incorporaron el mapa del repositorio y la memoria de notas, que ayudaron a localizar el método y conservar la hipótesis de trabajo. Sin embargo, se necesitaron más pasos y caracteres que en E2; como los issues eran distintos, no se puede atribuir todo el incremento únicamente a las nuevas herramientas.

El ISSUE-02 se resolvió con las dos variantes del sistema. El orquestador terminó en una sola ronda y el revisor aprobó el cambio. El contexto final de la variante multiagente fue de 51616 caracteres: 2489 del planificador, 31745 del ejecutor y 17382 del revisor. Aunque requirió más acciones, la solución también verificó que la respuesta completa del sistema académico fuera un diccionario. Esta mejora fue introducida por el ejecutor multiagente y ratificada por el revisor; no se produjo una solicitud de cambios. El agente único omitió esa validación, como se aprecia al comparar los dos archivos `validadores.py`. Las pruebas adicionales de E7 permiten comprobar esta diferencia después de las ejecuciones.

En E6 se reutilizó una trayectoria del agente único y se duplicó la solicitud de edición para una demostración controlada. El integrante rechazó la primera edición (paso 6) y aprobó la segunda (paso 7). El mecanismo también rechazó una entrada de consola inválida. La única acción bloqueada se debió al rechazo humano, no a un contrato incorrecto. Esta demostración no generó nuevas decisiones de un LLM y no sustituyó la solución multiagente incorporada al repositorio.

En conjunto, las trazas muestran que las herramientas, la revisión y la intervención humana cumplen funciones distintas. Para tareas pequeñas conviene empezar con un solo agente y reservar la coordinación multiagente para cambios donde una revisión adicional aporte valor. No hubo rechazos de contrato en las cinco trayectorias propias; los casos inválidos se probaron por separado en E3.

## Diagrama de trayectoria

![Trayectoria del ISSUE-02 con aprobación humana](trazas/issue02-aprobacion/trayectoria.png)

El diagrama muestra la solicitud al humano, el rechazo de la primera edición y la posterior aprobación. Su fuente es el [diagrama Mermaid](trazas/issue02-aprobacion/trayectoria.mmd), generado a partir de la [traza JSONL](trazas/issue02-aprobacion/ejecutor.jsonl). También se puede consultar la [trayectoria del ISSUE-02 multiagente](trazas/issue02-multi/trayectoria.mmd).

## Reproducción de las métricas

Desde la raíz del repositorio:

```bash
python agentes/observar.py
```

El script lee los JSONL de las cinco ejecuciones y calcula las tablas sin alterar las trazas ni los diagramas. La comparación adicional de los adaptadores se documenta en [la bitácora](bitacora-ia.md).
