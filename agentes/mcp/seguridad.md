# E7. Auditoría y seguridad — BiblioUNSA

## 1. Objetivo y alcance

Se adapta el auditor proporcionado en el ejemplo AgroConecta para revisar el catálogo MCP de BiblioUNSA y el servidor ficticio `clima-majes`. El auditor descubre las herramientas mediante `tools/list`, examina su descripción, esquema de entrada y anotaciones; no ejecuta ninguna herramienta. La muestra docente se conserva sin cambios y se usa exclusivamente desde el auditor, nunca desde Copilot u otro host real. Su código fue revisado: la función devuelve un pronóstico ficticio; el riesgo analizado se encuentra en su descripción. El auditor restringe el inicio a los dos archivos conocidos y verifica la huella de la muestra (normalizando saltos CRLF). Esto no constituye un sandbox ni certifica otros servidores.

## 2. Reglas de auditoría

| Regla | Severidad | Qué detecta |
|---|---|---|
| R01 | Alta | Instrucciones ocultas dirigidas al modelo. |
| R02 | Alta | Referencias a secretos o credenciales. |
| R03 | Alta | Comandos o URL externas en las descripciones. |
| R04 | Media | Solicitudes de lectura ajenas a la función. |
| R05 | Media | Parámetros genéricos que podrían facilitar filtraciones. |
| R06 | Baja | Ausencia de anotaciones. |
| R07 | Baja | Descripciones de más de 400 caracteres. |
| R08 (nueva) | Media | Posible escritura sin `destructiveHint` explícito. |
| R09 (nueva) | Media | Parámetro de tipo string sin `maxLength` en el esquema publicado. |

R08 considera escritura potencial cuando `readOnlyHint` no es verdadero. Distingue un valor `false` declarado de un valor ausente (`None`). R09 analiza los parámetros string directos del esquema; no intenta resolver todos los posibles esquemas anidados. Una advertencia de R09 no prueba que falte validación en el código. Las reglas por patrones pueden producir falsos positivos y negativos.

## 3. Ejecución y evidencias

Desde la raíz del repositorio:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
python agentes/mcp/cliente/auditar.py agentes/mcp/servidor_mcp/bibliounsa_mcp.py --salida agentes/mcp/trazas/e7/auditoria-propio.json
python agentes/mcp/cliente/auditar.py agentes/mcp/terceros/clima_mcp.py --salida agentes/mcp/trazas/e7/auditoria-tercero.json
python -m pytest -v agentes/mcp/pruebas/test_auditor.py
python -m pytest -q tests agentes/pruebas_agente agentes/mcp/pruebas
```

Los informes JSON registran el resultado observado en cada ejecución:

- [Auditoría de BiblioUNSA](trazas/e7/auditoria-propio.json).
- [Auditoría de clima-majes](trazas/e7/auditoria-tercero.json).

Las dos auditorías se ejecutaron en el entorno Windows del equipo. El servidor propio presentó cinco advertencias medias y ninguna alerta alta; el servidor de terceros presentó siete hallazgos, entre ellos dos de severidad alta.

| Servidor | Altas | Medias | Bajas | Decisión del auditor |
|---|---:|---:|---:|---|
| bibliounsa | 0 | 5 | 0 | REVISIÓN HUMANA REQUERIDA |
| clima-majes | 2 | 4 | 1 | NO CONECTAR |

### Resultados de BiblioUNSA

| Regla | Herramienta | Parámetro observado | Severidad |
|---|---|---|---|
| R09 | `buscar_libro` | `biblioteca` | Media |
| R09 | `buscar_libro` | `consulta` | Media |
| R09 | `prestamos_vencidos` | `hoy` | Media |
| R09 | `crear_reserva` | `ejemplar_id` | Media |
| R09 | `crear_reserva` | `estudiante_id` | Media |

Los cinco parámetros carecen de `maxLength` en el esquema publicado. No se detectaron alertas R08: la escritura cuenta con anotaciones explícitas. El resultado no constituye una certificación de seguridad.

### Resultados de clima-majes

| Regla | Hallazgo en `clima_majes` | Severidad |
|---|---|---|
| R01 | Instrucciones ocultas dirigidas al modelo. | Alta |
| R02 | Solicitud de secretos o credenciales. | Alta |
| R04 | Solicitud de lectura de datos ajenos a su función. | Media |
| R05 | Parámetro genérico `contexto` con posible riesgo de filtración. | Media |
| R06 | Ausencia de anotaciones. | Baja |
| R08 | Posible escritura sin `destructiveHint` explícito. | Media |
| R09 | Parámetro `contexto` sin `maxLength` publicado. | Media |

El auditor emitió la decisión `NO CONECTAR` y devolvió el código de salida `1`, confirmado mediante `$LASTEXITCODE`. Este código indica hallazgos de severidad alta, no un fallo de ejecución. El código 2 indicaría una auditoría incompleta. No se invocó la herramienta de terceros ni se incorporó al host real.

En BiblioUNSA la búsqueda limita `consulta` a 100 caracteres y `biblioteca` a 80 mediante `_texto`; `_fecha` exige una fecha real de formato AAAA-MM-DD y `_uuid` exige UUID de 36 caracteres. Las advertencias del esquema son una mejora pendiente de publicación del contrato, aunque las validaciones efectivas existen. No se cambia el servidor en E7, para conservar el catálogo evaluado en E6.

### Pruebas de las reglas nuevas

`pruebas/test_auditor.py` incluye nueve casos sin red ni LLM: ausencia y valores explícitos de `destructiveHint`, lectura, ausencia de anotaciones, texto con y sin límite, enteros y conservación de reglas anteriores. En la preparación del ejercicio se obtuvo **9 passed** tras corregir la distinción entre `false` y ausencia. La ejecución local del equipo confirmó **9 passed in 0.09s** (Python 3.15.1, pytest 9.1.1). Las cinco pruebas de R08, las tres de R09 y la prueba de conservación de las reglas originales se aprobaron.

La suite completa obtuvo **151 passed in 1.60s**, sin fallos: 118 pruebas anteriores, 24 de contrato MCP y 9 del auditor. Esto verifica que las nuevas reglas no introdujeron regresiones en las pruebas ejecutadas.

## 4. Lista de verificación

| Control | Estado y evidencia |
|---|---|
| Mínimo privilegio | Revisado: tres herramientas, solo `crear_reserva` escribe; crea un registro ficticio en memoria y cambia la disponibilidad sin eliminar ni sobrescribir préstamos existentes. Pruebas de E3 y ejecución E4/E6. |
| Validación de entradas | Revisado: límites de texto, fechas, UUID, disponibilidad y matrícula. E4/E6 demuestran el rechazo de la fecha inválida. R09 señala límites no publicados en el esquema. |
| Rutas seguras | Revisado: el recurso ADR exige tres dígitos y comprueba que el archivo resuelto permanezca en el directorio de ADR. E3 contiene pruebas de URI inválida. |
| Ausencia de secretos | Los archivos MCP revisados usan datos ficticios, no requieren claves ni contienen credenciales reales identificadas en su código. La revisión de nombres de archivos versionados no devolvió coincidencias con los patrones de archivos sensibles. Queda pendiente la revisión de contenido de todo el repositorio; no copiar secretos en la evidencia. |
| Aprobación de escritura | Observada en E4, E5 y E6: el host pidió autorización antes de la reserva. No se presenta como control independiente del servidor; un cliente directo puede invocarlo sin la política del host. |

### Revisión de archivos sensibles versionados

El 27 de noviembre de 2026 se ejecutó desde la raíz del repositorio el siguiente comando en PowerShell:

```powershell
git ls-files | Select-String -Pattern '(^|/)\.env($|\.)|\.pem$|\.key$|credentials|secrets'
```

La búsqueda no devolvió coincidencias. No se identificaron archivos versionados cuyos nombres coincidan con los patrones de archivos de entorno, claves privadas o credenciales utilizados. Esta comprobación se limita a los nombres de los archivos y no sustituye una revisión de contenido ni un escáner de secretos. Se recomienda revisar también `.vscode/mcp.json` y las trazas, sin publicar posibles credenciales.


## 5. Conclusión

La auditoría permite identificar señales de envenenamiento antes de incorporar un catálogo al contexto del modelo. BiblioUNSA limita sus operaciones, valida las entradas y exige aprobación desde el host para la escritura. El ejemplo de terceros ilustra por qué el texto del catálogo no debe tratarse como instrucciones confiables. El análisis automático debe complementarse con la revisión del código, una lista de servidores autorizados y el control de permisos. Los resultados de la ejecución confirmaron cinco advertencias medias en el servidor propio y siete hallazgos en el ejemplo de terceros, dos de ellos de severidad alta. Se mantiene la decisión de no conectar clima-majes. Las 151 pruebas aprobadas respaldan el funcionamiento del sistema en los casos evaluados. La revisión de nombres de archivos sensibles versionados no encontró coincidencias. Quedan pendientes una revisión integral del contenido del repositorio y la publicación explícita de límites en el esquema como mejora futura.
