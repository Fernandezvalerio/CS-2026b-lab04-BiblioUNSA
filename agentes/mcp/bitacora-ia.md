# E7. Bitácora de interacciones con IA — BiblioUNSA

Esta bitácora resume interacciones reales de la conversación con ChatGPT durante el Laboratorio 11. Las solicitudes se presentan de forma resumida, no como transcripciones literales. Las evidencias del repositorio corresponden a los archivos y ejecuciones que el equipo reportó.

| N.º | Ejercicio y solicitud | Aporte del asistente | Verificación o decisión del equipo |
|---|---|---|---|
| 1 | E1: diseñar el catálogo según la guía y el repositorio. | Propuso tres herramientas, dos recursos y dos prompts, con una única escritura. | Se adoptó el catálogo en `diseno/catalogo-mcp.md`. |
| 2 | E2: implementar el servidor sin duplicar el dominio. | Preparó el servidor, cliente de exploración y datos ficticios; reutilizó los servicios de reservas y préstamos. | Las pruebas posteriores de E3 y la ejecución E4 permitieron verificar el funcionamiento. |
| 3 | E3: revisar las capturas y redactar nuevamente Inspector. | Sustituyó la plantilla pendiente por comentarios basados en las capturas aportadas. | El equipo ejecutó las pruebas; la terminal de E4 mostró 142 aprobadas. |
| 4 | E4: continuar el agente interactivo a partir de cada observación. | Propuso corregir el argumento de fecha después del error, buscar el ejemplar y solicitar una reserva. | Se obtuvieron dos vencidos, una reserva aprobada y disponibilidad posterior falsa. La verificación indicó COMPLETA. |
| 5 | E5: conectar VS Code y guiar las cinco consultas. | Ayudó a habilitar Copilot Chat, iniciar el servidor y formular las consultas; preparó el Markdown y las capturas. | El servidor descubrió tres herramientas, se aprobó la reserva y se verificó su efecto. Se aportó además la captura del aviso; esta no muestra explícitamente el comando MCP. |
| 6 | E6: reducir las descripciones y medir el costo de contexto. | Preparó el analizador, acortó descripciones y asistió en la nueva trayectoria. | La comparación real conservó 14 mensajes y redujo los tokens estimados del agente de 432 a 396 (8.33 %). |
| 7 | E7: ampliar las reglas del auditor y probarlas. | En una primera versión utilizó una condición booleana que confundía un indicador no destructivo explícito con su ausencia. La prueba detectó el problema y se corrigió antes de entregar el archivo. | La ejecución de preparación pasó de 8 aprobadas y 1 fallida a 9 aprobadas. El equipo ejecutó las dos auditorías: BiblioUNSA obtuvo cinco advertencias medias (R09), y clima-majes siete hallazgos, dos altos, con decisión NO CONECTAR. Las nueve pruebas del auditor pasaron en 0.09 s y la suite completa obtuvo 151 aprobadas en 1.60 s. |

## Sugerencia de código corregida

Durante la elaboración de R08, el asistente propuso inicialmente:

```python
if getattr(a, 'read_only_hint', None) is not True and not getattr(a, 'destructive_hint', None):
```

La prueba `test_r08_escritura_no_destructiva_explicita` falló: tanto `False` como `None` son falsos en una condición booleana. Por ello una herramienta que declaraba correctamente `destructiveHint=false` aparecía como si no hubiese declarado la anotación.

La condición se corrigió a:

```python
if getattr(a, 'read_only_hint', None) is not True and getattr(a, 'destructive_hint', None) is None:
```

Al repetir las pruebas del auditor se obtuvo `9 passed`. La ejecución posterior del equipo confirmó `9 passed in 0.09s` y `151 passed in 1.60s` en la suite completa. Esta revisión se realizó durante la preparación de E7 con objetos de catálogo simulados; no se presenta como una prueba de conexión al servidor real. Se conserva la versión corregida y la prueba de regresión para evitar que vuelva a introducirse el error.

## Reflexión

La IA facilitó el diseño, la programación y la documentación, pero sus propuestas debieron comprobarse con pruebas y resultados reales. El proceso permitió distinguir una respuesta esperada de una ejecución observada, conservar la intervención humana y corregir una condición de validación mediante una prueba automatizada. Las decisiones de publicación, permisos y entrega permanecen bajo responsabilidad del equipo.
