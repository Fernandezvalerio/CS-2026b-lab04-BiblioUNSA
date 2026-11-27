# E5. Conexión a un host real — BiblioUNSA

## Objetivo y configuración

En este ejercicio se conectó el servidor MCP de BiblioUNSA con GitHub Copilot en Visual Studio Code, con el propósito de comprobar que un asistente externo puede descubrir y utilizar las funcionalidades del proyecto sin modificar su implementación. Se trabajó en una sesión Local, en modo Agent y con permisos predeterminados, utilizando el transporte stdio configurado en `.vscode/mcp.json`. Las consultas se realizaron con datos ficticios almacenados en memoria.

## Conexión del servidor

Se inició el servidor `bibliounsa` desde Visual Studio Code. En el panel de salida se observaron los mensajes `Connection state: Running` y `Discovered 3 tools`, lo que confirmó que la conexión se estableció correctamente y que el host pudo descubrir las tres herramientas del catálogo.

![Servidor MCP conectado en Visual Studio Code](capturas/e5/01-conexion.png)

*Figura 1. Inicio del servidor MCP y descubrimiento de sus tres herramientas.*

## Consulta 1. Búsqueda de libros

> Utiliza exclusivamente el servidor MCP BiblioUNSA para buscar Redes de computadoras en la biblioteca Central. Indica los códigos de inventario, sus UUID y su disponibilidad. No crees reservas ni modifiques archivos.

Copilot seleccionó la herramienta `buscar_libro` y presentó los dos ejemplares encontrados en la biblioteca Central, junto con sus identificadores y su disponibilidad.

| Ejemplar | UUID | Disponibilidad |
| --- | --- | --- |
| LAB11-101 | `00000000-0000-4000-8000-000000000101` | Disponible |
| LAB11-102 | `00000000-0000-4000-8000-000000000102` | No disponible |

La consulta coincidió con los datos iniciales del servidor. Al tratarse de una operación de lectura, no se solicitó ninguna modificación de registros. En la captura no se observa un diálogo de aprobación.

![Resultado de la búsqueda de libros](capturas/e5/02-consulta-busqueda.png)

*Figura 2. Consulta del catálogo mediante la herramienta `buscar_libro`.*

## Consulta 2. Préstamos vencidos

> Utiliza exclusivamente el servidor MCP BiblioUNSA para consultar los préstamos vencidos al 27 de noviembre de 2026. Indica la cantidad total, los códigos de inventario, las bibliotecas y los días de atraso. No modifiques ningún registro ni archivo.

Para responder a esta solicitud, Copilot utilizó `prestamos_vencidos` y obtuvo un total de dos préstamos vencidos a la fecha indicada.

| Ejemplar | Biblioteca | Días de atraso |
| --- | --- | ---: |
| LAB11-102 | Central | 7 |
| LAB11-103 | Ingeniería | 4 |

El resultado coincidió con lo obtenido anteriormente en E4. Se comprobó que el asistente pudo recuperar y presentar los datos de los préstamos en lenguaje natural, sin solicitar una operación de escritura. No se observa un diálogo de aprobación en la evidencia compartida.

![Consulta de préstamos vencidos](capturas/e5/03-consulta-vencidos.png)

*Figura 3. Identificación de los dos préstamos vencidos al 27 de noviembre de 2026.*

## Consulta 3. Uso de un prompt publicado por el servidor

Se utilizó la plantilla `aviso_vencimiento` del servidor BiblioUNSA, según la ejecución reportada por el equipo, con los siguientes argumentos:

- `titulo`: Redes de computadoras.
- `fecha_vencimiento`: 2026-11-20.

La plantilla solicitó redactar un aviso breve y respetuoso, sin inventar multas, políticas ni datos personales y sin enviar ningún mensaje. Copilot generó la siguiente respuesta:

> **Aviso de vencimiento — BiblioUNSA**
>
> Le recordamos que el ejemplar de Redes de computadoras tenía como fecha de vencimiento el 20 de noviembre de 2026. Por favor, proceda a su devolución a la mayor brevedad posible. Gracias por su colaboración.

El resultado respetó los datos proporcionados y mantuvo un tono cordial. No se observa ninguna operación de escritura, envío de mensajes ni solicitud de aprobación en esta consulta. La captura muestra el texto de la plantilla con los argumentos incorporados y la respuesta de Copilot, aunque no muestra el comando de invocación ni el intercambio `prompts/get`.

![Aviso de vencimiento generado en Copilot](capturas/e5/04-consulta-prompt.png)

*Figura 4. Plantilla de aviso de vencimiento y respuesta generada por Copilot.*

## Consulta 4. Creación de una reserva con aprobación humana

> Utiliza exclusivamente el servidor MCP BiblioUNSA para crear una única reserva ficticia del ejemplar LAB11-101 del libro Redes de computadoras para el estudiante 00000000-0000-4000-8000-000000000001. Utiliza el UUID del ejemplar obtenido anteriormente. Solicita aprobación humana antes de ejecutar crear_reserva. No modifiques archivos ni ejecutes comandos de terminal.

Antes de ejecutar la reserva, Copilot presentó una pregunta de confirmación con dos alternativas: aprobar o no aprobar la operación. Se seleccionó «Sí, aprobar», autorizando la creación de una única reserva ficticia.

![Solicitud de aprobación humana](capturas/e5/05-aprobacion-humana.png)

*Figura 5. Confirmación solicitada por Copilot antes de crear la reserva.*

Una vez recibida la autorización, el asistente ejecutó la herramienta `crear_reserva` del servidor MCP. La respuesta confirmó que la reserva fue creada correctamente.

| Campo | Resultado observado |
| --- | --- |
| Ejemplar | LAB11-101 |
| UUID del estudiante ficticio | `00000000-0000-4000-8000-000000000001` |
| UUID de la reserva | `098bd5a0-c7ab-4d75-be2c-d898ae14f86e` |
| Estado | `RESERVADO` |
| Fecha de creación | `2026-11-27T16:55:03.315332` |
| Aprobación humana | Sí |

![Resultado de la creación de la reserva](capturas/e5/06-resultado-reserva.png)

*Figura 6. Reserva creada exitosamente después de recibir la autorización del usuario.*

Esta prueba demuestra que el usuario intervino antes de realizar la operación de escritura. La confirmación observada corresponde a una pregunta del agente de Copilot; no constituye por sí sola evidencia de que el host bloquee automáticamente todas las escrituras sin aprobación. La reserva se realizó sobre datos ficticios en memoria.

## Consulta 5. Verificación de disponibilidad

> Utiliza exclusivamente el servidor MCP BiblioUNSA para consultar nuevamente el libro Redes de computadoras en la biblioteca Central. Verifica si el ejemplar LAB11-101 continúa disponible después de la reserva y compara el resultado con la primera consulta. No crees nuevas reservas ni modifiques archivos.

Copilot volvió a ejecutar `buscar_libro` y comparó la disponibilidad del ejemplar LAB11-101 con la obtenida al inicio de la sesión.

| Momento de la consulta | Disponibilidad de LAB11-101 |
| --- | --- |
| Antes de la reserva | Disponible |
| Después de la reserva | No disponible |

La respuesta confirmó que la reserva tuvo efecto sobre la disponibilidad del ejemplar y que el estado se mantuvo durante la misma ejecución del servidor. No se solicitó otra reserva. En la captura no se observa un diálogo de aprobación para esta lectura.

![Verificación posterior de la disponibilidad](capturas/e5/07-verificacion-reserva.png)

*Figura 7. Comparación de la disponibilidad del ejemplar antes y después de la reserva.*

## Conclusión

La conexión de BiblioUNSA con GitHub Copilot permitió comprobar que las herramientas del servidor MCP pueden ser utilizadas desde una aplicación externa, sin tener que implementar nuevamente las funcionalidades del proyecto. Las consultas de libros y préstamos vencidos proporcionaron resultados consistentes con los obtenidos en E4. Asimismo, se creó una reserva de prueba con aprobación humana y se verificó posteriormente el cambio en la disponibilidad del ejemplar.

La experiencia muestra la utilidad de MCP para compartir las capacidades de un sistema entre distintos asistentes. También resalta la importancia de distinguir las operaciones de lectura de aquellas que modifican el estado del sistema. Además, se generó un aviso de vencimiento coherente con la plantilla del proyecto, respetando el título, la fecha y las restricciones indicadas. La captura permite comprobar el resultado de la generación, aunque no registra explícitamente la invocación del prompt mediante el protocolo MCP.

## Referencias

- Guía de Laboratorio 11, paso 9 y ejercicio E5 (pp. 14–15, 18–19).
- Visual Studio Code, [Integrate MCP servers with Copilot](https://code.visualstudio.com/api/extension-guides/ai/mcp).
- Visual Studio Code, [Choose an agent harness](https://code.visualstudio.com/docs/agents/run/agent-harnesses).
- Visual Studio Code, [Manage approvals and permissions](https://code.visualstudio.com/docs/agents/run/approvals).
