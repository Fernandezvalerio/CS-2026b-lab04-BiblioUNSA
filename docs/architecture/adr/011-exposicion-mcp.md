# ADR-011: Exposición de BiblioUNSA mediante MCP

- Estado: Propuesto para ratificación por el equipo
- Fecha: 2026-11-27
- Decisores: Equipo BiblioUNSA (Grupo 04)

## Contexto

El agente del Laboratorio 10 necesita consultar el catálogo de libros, identificar préstamos vencidos y realizar reservas de prueba sin depender directamente de los repositorios o de la implementación interna de BiblioUNSA. También queremos que otros hosts, como GitHub Copilot, puedan utilizar las mismas capacidades sin desarrollar una integración distinta para cada asistente. Se conserva el monolito modular del ADR-001, la integración académica aislada del ADR-003 y el control humano definido en el ADR-010.

El alcance del laboratorio es local y educativo: trabajamos con datos ficticios en memoria, sin acceder a la base de datos institucional ni requerir claves de API para el agente interactivo. La exposición de una operación de escritura exige mantener las validaciones de dominio y limitar las acciones del cliente.

## Alternativas consideradas

| Alternativa | Evaluación |
|---|---|
| API REST directa | Es útil para clientes convencionales y puede mantenerse en la arquitectura general. Sin embargo, cada host necesitaría adaptar las rutas, los esquemas y la interpretación de resultados; no ofrece por sí sola el catálogo MCP de herramientas, recursos y prompts. |
| Function calling dentro del agente | Permite definir funciones específicas para un modelo, pero concentra la integración en ese agente. Reutilizarlas en otro host exige adaptar sus contratos y mecanismos de ejecución. |
| MCP sobre stdio | Ofrece un catálogo común y descubrible, separa el host del servicio y permite reutilizar las operaciones con el agente del Lab 10 y Copilot. Es adecuado para el alcance local y los datos de prueba. |
| MCP sobre Streamable HTTP | Facilitaría el acceso remoto y la interoperabilidad entre equipos, pero exige controles adicionales de autenticación, autorización, exposición de red y despliegue. Se reserva para una etapa posterior. |

## Decisión

Usaremos un servidor MCP local llamado `bibliounsa`, implementado en Python con el SDK v2 (`mcp>=2,<3`), con transporte **stdio** y mensajes JSON-RPC 2.0. La versión de protocolo objetivo es **2026-07-28**, según la guía del Laboratorio 11. El cliente obtiene las capacidades mediante `server/discover` y el catálogo mediante `tools/list`, como se observa en la traza E4. La versión concreta reportada por el SDK puede comprobarse con `python agentes/mcp/cliente/explorar.py`; no debe confundirse la versión del protocolo con la del paquete Python ni con la etiqueta del repositorio.

El servidor actúa como adaptador de las operaciones de dominio y no sustituye la arquitectura existente. El agente del Lab 10 usa `HerramientasMCP` para conectar el núcleo síncrono con el cliente MCP. VS Code usa su configuración local `.vscode/mcp.json` para iniciar el servidor.

### Superficie expuesta

| Tipo | Identificador | Alcance |
|---|---|---|
| Herramienta | `buscar_libro(consulta, biblioteca="")` | Lectura de títulos, autores, ejemplares y disponibilidad. |
| Herramienta | `prestamos_vencidos(hoy)` | Lectura de préstamos no devueltos con vencimiento anterior a la fecha indicada. |
| Herramienta | `crear_reserva(estudiante_id, ejemplar_id)` | Única escritura: crea una reserva ficticia en memoria, previa aprobación en el host. |
| Recurso | `bibliounsa://prestamos/reglas` | Reglas del proyecto de laboratorio. |
| Plantilla de recurso | `bibliounsa://adr/{numero}` | Lectura de un ADR existente mediante un número de tres dígitos. |
| Prompt | `aviso_vencimiento(titulo, fecha_vencimiento)` | Plantilla para redactar un aviso, sin envío real. |
| Prompt | `generar_criterios(id, historia)` | Reutilización de la plantilla v3 de criterios de aceptación del Lab 09. |

No se expondrán consultas SQL arbitrarias, acceso libre al sistema de archivos, ejecución de comandos, modificación de ADR, borrado de préstamos, pago de multas, envío de correos, credenciales o datos institucionales reales. `leer_recurso` es una adaptación local del agente, no una cuarta herramienta publicada por el servidor.

### Controles de seguridad

- Mínimo privilegio: dos herramientas de lectura y una de escritura. El agente comprueba el catálogo permitido, limita su ejecución a diez pasos y exige aprobación antes de `crear_reserva`.
- Validación: límites de texto, fechas reales AAAA-MM-DD, UUID, matrícula vigente y disponibilidad. La reserva se ejecuta bajo un bloqueo para proteger el estado compartido en memoria.
- Recursos: el ADR exige tres dígitos y comprueba que el archivo resuelto permanezca en el directorio previsto; no admite rutas arbitrarias.
- Anotaciones: `readOnlyHint`, `destructiveHint`, `idempotentHint` y `openWorldHint` describen las herramientas, pero no sustituyen los permisos. La aprobación de la escritura corresponde al host; un cliente directo no queda protegido por esa política.
- Datos: se emplean registros ficticios; la revisión de nombres de archivos versionados no encontró coincidencias con los patrones de secretos. No equivale a un escaneo completo del contenido.
- Auditoría: los catálogos de terceros se consideran datos no confiables. Se inspeccionan descripciones, esquemas y anotaciones antes de su incorporación; la muestra `clima-majes` no se conecta a un host real.

## Consecuencias

- **Positivas:** se reutilizan las capacidades del dominio con distintos hosts, se reduce el acoplamiento del agente y se obtienen contratos y trazas verificables. El protocolo conserva la separación entre herramientas, recursos y prompts.
- **Costo de contexto:** E6 redujo el catálogo MCP de 1086 a 1051 tokens estimados (3.22 %) y el catálogo del agente de 432 a 396 (8.33 %). Se conservó la secuencia de cinco llamadas, la corrección de fecha, la aprobación humana y la verificación de disponibilidad. La estimación usa cuatro caracteres por token y no demuestra un ahorro exacto de API ni una mejora de latencia.
- **Seguridad y pruebas:** E7 obtuvo cinco advertencias medias R09 para BiblioUNSA y ninguna alta. El servidor de terceros obtuvo dos altas, cuatro medias y una baja; se decidió no conectarlo. Las nueve pruebas del auditor y las 151 pruebas generales fueron aprobadas en la ejecución local del equipo.
- **Limitaciones:** el estado en memoria se pierde al reiniciar el proceso y no se comparte entre sesiones independientes. No se ha implementado autenticación institucional ni autorización independiente de la escritura en el servidor. Los cinco límites detectados por R09 están validados en Python pero no publicados como `maxLength`; su publicación queda pendiente. La auditoría por patrones puede omitir riesgos y no certifica seguridad. Para producción se requerirían persistencia, autenticación, autorización y controles de despliegue adicionales.

## Evidencias y relación

- [Catálogo MCP (E1)](../../../agentes/mcp/diseno/catalogo-mcp.md).
- [Pruebas e Inspector (E3)](../../../agentes/mcp/pruebas/inspector.md).
- [Traza del agente (E4)](../../../agentes/mcp/trazas/e4/resumen.md).
- [Conexión a un host real (E5)](../../../agentes/mcp/uso-en-host.md).
- [Protocolo y contexto (E6)](../../../agentes/mcp/protocolo.md).
- [Auditoría y seguridad (E7)](../../../agentes/mcp/seguridad.md) y [bitácora de IA](../../../agentes/mcp/bitacora-ia.md).
- ADR-001, ADR-003, ADR-005, ADR-006 y ADR-010.
- Guía de Laboratorio 11 de Construcción de Software, UNSA (2026-B), E1–E8.
