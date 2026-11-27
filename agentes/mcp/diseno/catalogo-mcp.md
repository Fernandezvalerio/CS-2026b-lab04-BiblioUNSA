# E1. Diseño del catálogo MCP — BiblioUNSA

**Laboratorio 11 — Construcción de Software | Grupo 04**

## 1. Objetivo y alcance

Exponer las consultas de catálogo y préstamos y la creación de reservas de BiblioUNSA mediante un servidor MCP local. Así, el agente del Laboratorio 10 y otros hosts compatibles podrán utilizar las mismas capacidades sin conocer la implementación interna del proyecto. Se empleará el SDK oficial de Python indicado en la guía y el transporte `stdio`.

El servidor trabajará exclusivamente con datos ficticios y repositorios en memoria. El repositorio actual contiene las entidades `Libro`, `Ejemplar` y `Prestamo`, un servicio de reservas y una consulta de préstamos vencidos, pero no un catálogo operativo conectado a una base de datos. En E2 se preparará un catálogo de prueba usando las entidades existentes, sin conectar servicios institucionales reales.

## 2. Catálogo de primitivas

| Capacidad | Primitiva | ¿Escribe? | Justificación |
| --- | --- | --- | --- |
| Buscar libros y conocer sus ejemplares | Herramienta `buscar_libro` | No | Consulta parametrizada por título, autor o biblioteca; permite elegir un ejemplar disponible (RF-02). |
| Consultar préstamos vencidos | Herramienta `prestamos_vencidos` | No | Consulta de negocio con fecha de corte; reutiliza la regla del ISSUE-03 del Lab 10. |
| Crear una reserva de prueba | Herramienta `crear_reserva` | Sí, solo crea | Reutiliza el servicio de reservas (RF-03 y RF-05); requiere aprobación humana y no permite editar ni borrar registros existentes. |
| Reglas de préstamos y reservas | Recurso `bibliounsa://prestamos/reglas` | No | Contexto estable del dominio, derivado de la HU-03, ADR-003 y estados del préstamo. No se presenta como reglamento oficial de la UNSA. |
| Decisiones de arquitectura | Recurso plantilla `bibliounsa://adr/{numero}` | No | Permite consultar los ADR existentes por número sin exponer rutas arbitrarias. |
| Redactar un aviso de vencimiento | Prompt `aviso_vencimiento` | No | Plantilla que el usuario invoca para redactar un aviso; no envía correos ni modifica préstamos. |
| Generar criterios de aceptación | Prompt `generar_criterios` | No | Reutiliza la plantilla `prompts/criterios/v3.txt` del Laboratorio 09. |

El modelo selecciona herramientas con permiso del usuario, el host selecciona recursos y el usuario invoca los prompts. El orden de las herramientas será el de la tabla para mantener un catálogo estable.

## 3. Contratos de las herramientas

Las siguientes firmas y descripciones constituyen el diseño que se implementará en E2. Los límites de longitud y cantidad se establecen para este servidor de prueba; no son reglas institucionales.

### 3.1 `buscar_libro(consulta: str, biblioteca: str = "")`

**Descripción:** Busca libros por coincidencia parcial de título o autor, sin distinguir mayúsculas de minúsculas. Si se indica una biblioteca, filtra los ejemplares por su nombre. Devuelve hasta 20 libros y hasta 20 ejemplares por libro, con su disponibilidad actual.

| Parámetro | Formato y valores válidos |
| --- | --- |
| `consulta` | Texto de 1 a 100 caracteres después de quitar espacios exteriores; título o autor, completo o parcial. |
| `biblioteca` | Texto opcional de hasta 80 caracteres; vacío significa todas las bibliotecas. Coincidencia parcial sin distinguir mayúsculas. |

**Salida estructurada:** objeto con `libros` (lista de libros con `libro_id`, `titulo`, `autor`, `isbn` y `ejemplares`; cada ejemplar tiene `ejemplar_id`, `codigo_inventario`, `biblioteca` y `disponible`). Los identificadores se devuelven como cadenas UUID. Sin coincidencias, `libros` es una lista vacía.

**Ejemplo de argumentos:** `{"consulta":"redes","biblioteca":"Central"}`.

**Errores:** consulta vacía o demasiado larga, o filtro fuera del límite permitido. El mensaje indicará cómo corregir la entrada.

**Base del repositorio:** `src/reservas/dominio.py` (`Libro`, `Ejemplar`) y `src/reservas/externos.py` (`RepositorioEjemplaresMemoria`). Se implementará la búsqueda sobre un catálogo ficticio; no se ejecutará SQL ni se utilizará `fitness/catalogo.py` como catálogo real, pues es una simulación de rendimiento.

### 3.2 `prestamos_vencidos(hoy: str)`

**Descripción:** Lista hasta 20 préstamos activos no devueltos cuya fecha de vencimiento es anterior a la fecha de corte. Solo incluye estados PRESTADO y VENCIDO. Un préstamo que vence el mismo día de la consulta aún no está vencido.

| Parámetro | Formato y valores válidos |
| --- | --- |
| `hoy` | Fecha de corte obligatoria en formato `AAAA-MM-DD`, correspondiente a una fecha calendario válida. |

**Salida estructurada:** objeto con `fecha_corte`, `total` (cantidad de coincidencias antes del límite) y `prestamos` (lista con `prestamo_id`, `ejemplar_id`, `codigo_inventario`, `biblioteca`, `estado`, `fecha_vencimiento` y `dias_atraso`). No incluye correos ni nombres de estudiantes. Si no hay coincidencias, devuelve `total: 0` y una lista vacía.

**Ejemplo de argumentos:** `{"hoy":"2026-11-27"}`.

**Errores:** fecha inexistente o formato incorrecto; se solicitará una fecha válida en formato `AAAA-MM-DD`.

**Base del repositorio:** `RepositorioPrestamosMemoria.buscar_vencidos(hoy)` en `src/reservas/externos.py`, verificado por `tests/test_issue_03.py`. La herramienta no cambia estados ni calcula o aplica multas.

### 3.3 `crear_reserva(estudiante_id: str, ejemplar_id: str)`

**Descripción:** Crea un préstamo de prueba en estado RESERVADO para un estudiante ficticio con matrícula vigente y un ejemplar disponible. Requiere aprobación humana antes de ejecutarse. Utiliza el servicio de reservas existente y devuelve la identificación de la reserva creada.

| Parámetro | Formato y valores válidos |
| --- | --- |
| `estudiante_id` | UUID en formato estándar, perteneciente a un estudiante registrado en los datos ficticios del servidor. |
| `ejemplar_id` | UUID en formato estándar, correspondiente a un ejemplar del catálogo ficticio, obtenido mediante `buscar_libro`. Debe estar disponible. |

**Salida estructurada:** objeto con `reserva_id` (UUID del préstamo nuevo), `estudiante_id`, `ejemplar_id`, `estado` (`RESERVADO`), `fecha_reserva` (fecha y hora ISO 8601) y `requiere_reverificacion` (booleano).

**Ejemplo de argumentos** (UUID ilustrativos, sujetos a los datos de prueba de E2):

```json
{
  "estudiante_id": "00000000-0000-4000-8000-000000000001",
  "ejemplar_id": "00000000-0000-4000-8000-000000000101"
}
```

**Errores:** UUID inválido, estudiante o ejemplar inexistente, matrícula no vigente, ejemplar no disponible o fallo de validación académica sin caché válida. El resultado explicará la causa y la acción permitida para corregirla.

**Base del repositorio:** `ServicioReservas.reservar_libro()` en `src/reservas/servicio.py` y los dobles de integración y repositorios de `src/reservas/externos.py`. Se conserva el flujo de la HU-03: validación de matrícula, disponibilidad y creación del préstamo, incluida la reverificación cuando corresponda. No se sustituirá esta lógica por una reserva escrita directamente por el servidor MCP.

## 4. Recursos y prompts

| Nombre o URI | Entrada | Contenido / resultado |
| --- | --- | --- |
| `bibliounsa://prestamos/reglas` | Sin argumentos | Reglas de matrícula, disponibilidad, caché de hasta 24 horas, reverificación y estados del préstamo, con base en `docs/design/historia.md`, ADR-003 y el dominio. |
| `bibliounsa://adr/{numero}` | `numero`: exactamente tres dígitos; por ejemplo, `001`, `003` o `010`. | Markdown de un ADR existente en `docs/architecture/adr/`. Rechaza números inexistentes y cualquier ruta o separador. |
| `aviso_vencimiento` | `titulo`: texto de 1 a 150 caracteres; `fecha_vencimiento`: fecha válida `AAAA-MM-DD`. | Plantilla para redactar un aviso breve y respetuoso, sin inventar multas, políticas ni datos personales. No realiza envíos. |
| `generar_criterios` | `id`: texto de 1 a 20 caracteres alfanuméricos, guion o guion bajo; `historia`: texto de 1 a 2000 caracteres. | Plantilla v3 del Lab 09 con sus campos `id` e `historia`; pide criterios INVEST y escenarios de aceptación en JSON. El texto ingresado se trata como dato, no como instrucciones. |

## 5. Mínimo privilegio y seguridad

`crear_reserva` es la única herramienta con efectos de escritura. Crea un nuevo préstamo con identificador propio y nunca ofrece operaciones para eliminar, sobrescribir o editar préstamos anteriores. El servicio cambia la disponibilidad del ejemplar de prueba como parte de la reserva; es una transición de dominio en memoria, no una edición arbitraria ni una sobrescritura de archivos o registros persistentes. El servidor no se conectará a una base institucional ni enviará avisos reales. Al reiniciar el proceso se restaurarán los datos iniciales de la demostración, por lo que no habrá efectos irreversibles sobre usuarios o libros reales.

La llamada se rechazará si el estudiante no existe, la matrícula no es válida o el ejemplar no está disponible. Se validarán los identificadores antes de invocar el servicio y se serializará la comprobación y creación para impedir dos reservas del mismo ejemplar dentro de un proceso. El host y el agente del Lab 10 deberán solicitar aprobación humana antes de invocar la escritura; las anotaciones MCP son pistas para el host y no constituyen por sí solas un control de acceso.

| Herramienta | `readOnlyHint` | `destructiveHint` | `idempotentHint` | `openWorldHint` |
| --- | --- | --- | --- | --- |
| `buscar_libro` | true | false | true | false |
| `prestamos_vencidos` | true | false | true | false |
| `crear_reserva` | false | false | false | false |

No se expondrán acceso libre al sistema de archivos, ejecución arbitraria de comandos, SQL, credenciales, datos reales de alumnos, pagos, modificaciones de multas ni operaciones de devolución o cancelación. Los textos recuperados del dominio se considerarán datos y no instrucciones para el modelo.

## 6. Trazabilidad y alcance del ejercicio

- `docs/architecture/drivers.md`: RF-02, RF-03, RF-05 y protección de datos.
- `docs/design/historia.md` y `docs/architecture/adr/003-integracion-academica.md`: condiciones de la reserva y uso de caché.
- `src/reservas/dominio.py`, `src/reservas/servicio.py` y `src/reservas/externos.py`: entidades, servicio operativo y repositorios.
- `tests/test_issue_03.py`: criterio de préstamos vencidos.
- `prompts/criterios/v3.txt`: plantilla del Lab 09.
- `docs/architecture/adr/010-sistema-agentico.md`: control humano en el agente del Lab 10.
