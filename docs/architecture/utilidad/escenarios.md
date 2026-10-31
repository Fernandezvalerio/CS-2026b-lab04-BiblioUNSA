# E1 - Árbol de utilidad de BiblioUNSA

## Contexto y restricciones

El caso crece a todas las facultades y la biblioteca virtual; la API académica puede dejar de responder durante la matrícula. Se conservan el monolito modular, el equipo de tres personas, un VPS de bajo costo y la integración académica exclusivamente por API (drivers.md y ADR-001). Las cifras de carga son hipótesis del ejercicio que deben medirse cuando exista el servicio real.

Cada escenario se describe con fuente, estímulo, entorno, artefacto, respuesta y medida. H significa alta; M, media; L, baja.

|ID|Atributo|Fuente y estímulo|Entorno y artefacto|Respuesta y medida|Importancia/dificultad|
|-|-|-|-|-|-|
|QA-08-01|Disponibilidad|Sistema académico: 35 % de peticiones fallidas|Matrícula, módulo de integración|Para estudiantes con última matrícula vigente verificada hace <=24 h: 0 reservas bloqueadas y timeout <=3 s|H/H|
|QA-08-02|Rendimiento|Estudiantes de todas las facultades: 24 consultas/s (8 veces la hipótesis de 3/s)|Matrícula, catálogo|Responde con p95 <=1500 ms con cuatro workers en un VPS|H/M|
|QA-08-03|Seguridad|30 usuarios externos intentan usar identidades no institucionales|Acceso normal, autenticación|Rechaza 30/30 intentos, 0 sesiones creadas|H/M|
|QA-08-04|Modificabilidad|UNSA cambia el formato de respuesta de su API|Desarrollo, adaptador académico|Adaptación en <=2 días-persona y 0 módulos de negocio tocados|H/M|
|QA-08-05|Rendimiento|Usuarios consultan biblioteca virtual a 12 solicitudes/s|Hora punta, catálogo|p95 <=1200 ms|M/M|
|QA-08-06|Disponibilidad|Fallo académico genera validaciones pendientes|Matrícula, worker|100 % de préstamos pendientes programados para reverificación en <=30 min|H/M|
|QA-08-07|Seguridad|Desarrollador intenta saltarse el adaptador|Pull Request, arquitectura|0 importaciones no permitidas y 0 conexiones directas a BD académica|H/M|
|QA-08-08|Modificabilidad|Se incorpora una facultad|Desarrollo, configuración de sedes|Alta en <=1 día-persona sin cambiar Reservas|M/L|

## Priorización y revisión crítica de la IA

* Primera iteración: QA-08-01 (H,H). Es el riesgo dominante: una caída externa durante matrícula impide prestar libros sin validaciones recientes.
* Segunda: QA-08-02 (H,M). El crecimiento afecta el p95 del catálogo.
* Tercera: QA-08-03 y QA-08-07 (H,M). Se protege la identidad y el límite con la API académica.
* Corrección a la propuesta inicial de IA: QA-08-08 pasó de (H,H) a (M,L). El sistema conserva módulos y una base común, y el alta de una facultad es mayormente configuración; no hay evidencia de un rediseño de datos por facultad.

## Límites de la evidencia

Los escenarios son objetivos verificables, no resultados de producción. La disponibilidad con caché solo está garantizada para estudiantes con validación vigente previa; un estudiante sin caché necesitará que la API académica responda. Se realizará simulación controlada en E2 y E4.

