# E3 - ATAM-lite de BiblioUNSA (evaluación preliminar)

## Alcance

Se revisan E1 y E2. Las observaciones de esta tabla son **autoevaluación técnica preliminar**, no se hacen pasar por la evaluación real de un grupo externo. Para completar el cruce, crear el issue en el repositorio asignado por el docente, responder el issue recibido y registrar ambos enlaces.

|Tipo|Hallazgo preliminar|Evidencia o hipótesis|Evaluación|
|-|-|-|-|
|Sensibilidad|El número de estudiantes con caché reciente gobierna la tasa de bloqueos|Simulación: 53/1000 bloqueos con 80 % de caché y 35 % de fallas|Confirmado por simulación|
|Trade-off|Caché de matrícula conserva atención, pero expone estado académico desactualizado por hasta 24 h|ADR-003 y política de E2|Aceptado con reverificación|
|Riesgo R1|Falta de caché para estudiantes nuevos durante matrícula|53 reservas bloqueadas aun con respaldo|Alto, aceptar rechazo seguro; informar y reintentar|
|Riesgo R2|Outbox y caché en DB pueden aumentar carga sobre el único VPS|Presupuesto R-03 y E2; no hay medición de DB real|Alto, medir antes de desplegar|
|No riesgo|Cambiar de proveedor académico no obliga a editar Reservas|Strategy y Adapter del ADR-005, pruebas existentes del Lab 07|Sustentado en pruebas existentes|

## Matriz preliminar de riesgos

Escala de probabilidad (P) e impacto (I): 1=bajo, 2=medio, 3=alto. Crítico si P x I >= 6.

|ID|Riesgo|P|I|P x I|Respuesta prevista|
|-|-|-:|-:|-:|-|
|R1|API caída sin caché reciente|3|3|9|Rechazo seguro, reintento y comunicación clara|
|R2|Sobrecarga del VPS al persistir caché/outbox|2|3|6|Medir consultas e índices; E4 rendimiento|
|R3|Estado de matrícula obsoleto|2|3|6|Caducidad <=24 h y reverificación <=30 min|
|R4|Acceso indebido con dominio de correo falsificado|2|3|6|Validación OIDC en servidor; E4 seguridad|



