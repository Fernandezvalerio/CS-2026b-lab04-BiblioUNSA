# E7 - Bitácora de IA del Laboratorio 08

Registro de propuestas examinadas al preparar el diseño mediante ChatGPT, contrastadas con drivers, ADR y prototipos. No son mediciones de producción ni acuerdos ratificados por el equipo.

|N.º|Prompt resumido|Propuesta que se evaluó|Evidencia o contraste|Decisión|
|-|-|-|-|-|
|1|Prioriza escenarios al crecer a todas las facultades y fallar la API|Continuidad académica antes que nuevas funciones|Drivers QA-02 y matrícula|QA-08-01 (H,H)|
|2|¿Microservicios para 24 consultas/s?|Separar Catálogo con Kubernetes|E4 p95 253,5 ms con índice supuesto y un VPS|Rechazada: costo desproporcionado|
|3|¿Basta Redis para recordar una matrícula y programar pendientes?|Redis como única fuente|Una caída/reinicio puede perder datos no persistidos|Corregida: PostgreSQL y outbox|
|4|¿Dejar que toda caché permita préstamos durante caída?|Mantener respaldos sin caducidad|ADR-003 exige 24 h, 53 solicitudes sin caché reciente se bloquean|Rechazada: denegar sin prueba válida|
|5|¿Es suficiente comprobar el sufijo @unsa.edu.pe?|Confiar en correo declarado|Token no validado/issuer falso puede fingir email; E4 rechaza 30/30 casos|**Falso positivo refutado**|
|6|¿Redis siempre reduce el p95 del catálogo?|Añadir caché sin medir invalidación|E4 verifica índice bajo modelo; no mide caché ni frescura de stock|Rechazada por evidencia insuficiente|

## Prompts reproducibles (resumen)

1. Con los drivers de BiblioUNSA, prioriza escenarios de seis partes sin proponer soluciones todavía.
2. Para 24 rps en un único VPS, compara índice, caché, más workers y microservicios con costos y trade-offs.
3. Con 35 % de fallas de API académica, propone recuperación compatible con 24 h de caché.
4. Actúa como evaluador adversario de la pérdida de pendientes cuando Redis se reinicia.
5. Intenta falsificar una identidad con correo institucional sin token OIDC válido.
6. Enumera qué evidencia real falta para aprobar un índice o caché del catálogo.

