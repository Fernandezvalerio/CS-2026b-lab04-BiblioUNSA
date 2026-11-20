# Comparación de ejecuciones: E2 y E4

En el E2 se utilizó un agente ReAct para corregir el cálculo de multas (ISSUE-01). En el E4 se incorporaron un mapa del repositorio y una memoria de notas para resolver la consulta de préstamos vencidos (ISSUE-03). Los resultados corresponden a las ejecuciones interactivas del equipo.

| Métrica | E2 (ISSUE-01) | E4 (ISSUE-03) |
| --- | ---: | ---: |
| Pasos | 8 | 12 |
| Rondas | 1 | 1 |
| Acciones | 7 | 11 |
| Acciones bloqueadas | 0 | 0 |
| Rechazos del contrato | 0 | 0 |
| Contexto final (caracteres) | 8027 | 24432 |
| Uso del mapa del repositorio | No | Sí |
| Uso de memoria de notas | No | Sí |

## Análisis

En el E4, el agente necesitó cuatro pasos más y utilizó aproximadamente tres veces el contexto del E2. El mapa del repositorio permitió identificar la estructura del código y ubicar los componentes relacionados con los préstamos. Por su parte, la memoria de notas sirvió para conservar la hipótesis sobre la fecha de devolución y recuperarla antes de realizar la corrección. Aunque estas herramientas facilitaron la organización de la tarea, en esta ejecución no redujeron los pasos ni el contexto utilizado. Además, como se resolvieron problemas diferentes, no se puede atribuir todo el aumento exclusivamente a las nuevas herramientas. En ambos casos el agente resolvió el issue sin acciones bloqueadas ni rechazos del contrato.
