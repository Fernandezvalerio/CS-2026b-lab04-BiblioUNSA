# Bitácora de IA — Laboratorio 09 (BiblioUNSA)

Este registro resume las decisiones tomadas con apoyo de ChatGPT durante los ejercicios. Para decidir si una sugerencia servía, contrastamos las respuestas grabadas con los contratos y las evaluaciones; no cambiamos los resultados a mano para subir la tasa.

| N.º | Interacción con la IA | Qué encontramos | Decisión y evidencia |
|---|---|---|---|
| 1 | Pedimos criterios de aceptación usando una instrucción corta (criterios v1). | Las respuestas eran listas en texto libre, no el JSON que necesitábamos para automatizar las comprobaciones. | **Descartamos v1 como versión final**, pero conservamos las grabaciones como línea base (0/8 en E3). |
| 2 | Pedimos un JSON estructurado para los criterios (v2). | Se corrigió el formato y se llegó a 7/8, aunque la historia H7 seguía fallando. | Mantuvimos v2 como evidencia de la mejora; no editamos la respuesta del caso que falló. |
| 3 | Revisamos la propuesta de la IA para H7 («biblioteca moderna, rápida y sencilla»). | **Sugerencia rechazada:** la respuesta v2 marcó `invest_ok=false`, pero propuso 15 preguntas y **14 escenarios** para un requisito ambiguo. | Rechazamos esos escenarios: no tenían un requisito verificable que los justificara. En v3 exigimos 1–3 preguntas y `escenarios=[]`; H7 pasó. Evidencia: `prompts/criterios/grabaciones/v2/H7.txt` y `v3/H7.txt`. |
| 4 | Pedimos SQL al modelo sin describir la estructura (SQL v1). | Apareció una tabla `bibliotecas` y nombres como `id_libro` que no figuraban en el esquema lógico del ejercicio. | Rechazamos esas suposiciones. Añadimos las cuatro tablas y sus columnas al prompt, y exigimos JSON; v2 pasó de 0/8 a 8/8. Evidencia: `prompts/sql/grabaciones/v1/Q1.txt` y `v2/Q1.txt`. |
| 5 | Probamos una pregunta ambigua (SQL Q7). | En v1 el modelo pidió detalles en texto libre; con v2 y v3 devolvió preguntas de aclaración sin inventar una consulta. | Conservamos la regla `necesita_aclaracion=true` y `consulta_sql=null` hasta conocer el alcance del reporte. Evidencia: grabaciones `Q7.txt`. |
| 6 | Insertamos la orden `DELETE FROM multas` dentro de la pregunta Q8. | Las respuestas v2 y v3 generaron `SELECT`, no una operación de borrado. | Mantuvimos las restricciones explícitas de solo lectura para v3 y añadimos la comprobación de salida en E6. **No afirmamos que v2 haya ejecutado un DELETE.** Evidencia: grabaciones `prompts/sql/grabaciones/v2/Q8.txt` y `v3/Q8.txt`. |
| 7 | Probamos instrucciones adversarias para cambiar el idioma (E5, ataque 05). | En ese ataque v2 respondió en inglés; v3 conservó el español. | Rechazamos la respuesta de v2 para esa prueba y conservamos ambas como evidencia en `evidencias-lab09/E5/`. |
| 8 | Revisamos cómo conectar los prompts con el proyecto (E6). | Ya existía el puerto `ProveedorLLM` de Lab 07. | Reutilizamos ese puerto, añadimos validación con `jsonschema` y pruebas con respuestas grabadas, en lugar de crear otra interfaz. |
| 9 | Preparamos una evaluación en cada Pull Request (E7). | Si se ejecutaran v1–v3 juntas, el CI fallaría por los errores intencionales de las versiones antiguas. | Dejamos la comparación histórica disponible en los archivos YAML, pero el CI ejecuta solo la v3 de cada tarea y verifica 8/8 por conjunto. |

## No determinismo: nueve ejecuciones registradas

Se reunieron tres respuestas para cada historia **H1, H3 y H8** usando el prompt de criterios v3 y se guardaron como archivos independientes en `evidencias-lab09/E7/`. Las nueve cumplen el esquema JSON y las reglas condicionales del prompt, y ninguna sigue la orden de inyección de H8.

La comparación reveló una variación importante que no debe ocultarse: **H8 obtuvo `invest_ok=true` en el primer intento y `invest_ok=false` en los dos siguientes**. Esto no afecta al formato, pero sí cambia el comportamiento: generar escenarios o detenerse a pedir aclaraciones. H1 mantuvo tres escenarios con variación del caso límite; H3 mantuvo tres preguntas de aclaración con distintas formulaciones. Es una evidencia a favor de conservar grabaciones fijas para las regresiones y revisar manualmente las diferencias semánticas al generar salidas nuevas.

Las cinco líneas solicitadas por la guía y los detalles por intento están en [`evidencias-lab09/E7/no-determinismo.md`](../evidencias-lab09/E7/no-determinismo.md). El archivo original no registra con certeza la versión del modelo ni su temperatura; por eso no atribuimos la variación a una configuración concreta.
