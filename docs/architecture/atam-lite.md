# E3 - ATAM-lite de BiblioUNSA (evaluación preliminar)

## Alcance

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

## 

## E7 - Evaluación consolidada de riesgos internos

|ID|Hallazgo|Evidencia disponible|Mitigación / aceptación|Estado|
|-|-|-|-|-|
|R1|Sin caché reciente, la matrícula se bloquea|E2: 53/1000 rechazos aun con respaldo|Aceptado por seguridad; mensaje claro y reintento al restaurar API|Riesgo residual crítico|
|R2|Persistencia en un VPS puede saturar PostgreSQL|E4: catálogo sin índice satura el modelo; falta medir outbox|Optimizar consultas e índice; medir BD y outbox antes de despliegue|Mitigación propuesta|
|R3|La caché conserva un estado académico obsoleto|ADR-003 y E2: 274 respuestas de respaldo|Caducidad <=24 h y 274 reverificaciones a 15 min|Diseño pendiente de prueba en BD real|
|R4|Claims OIDC forjados autorizan acceso|E4: 30/30 intentos sintéticos rechazados|Verificar firma, issuer, audience y email en servidor, FF-05|Pendiente integrar IdP|

### 

### Matriz de probabilidad e impacto

|Probabilidad / Impacto|1 Bajo|2 Medio|3 Alto|
|-|-|-|-|
|3 Alta|—|—|R1 (9)|
|2 Media|—|—|R2, R3, R4 (6)|
|1 Baja|—|—|—|

Punto de sensibilidad principal: porcentaje de alumnos con validación reciente. Trade-off principal: continuidad con caché versus posible obsolescencia de matrícula. No riesgo justificado: Strategy/Adapter permite sustituir el contrato académico sin editar Reservas, según las pruebas del Lab 07.

