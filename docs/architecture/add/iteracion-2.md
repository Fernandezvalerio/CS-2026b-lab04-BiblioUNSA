# E4 - ADD iteración 2: catálogo para todas las facultades

## 1\. Entradas

QA-08-02 (H,M): 24 consultas/s y p95 <=1500 ms en el catálogo durante matrícula. Restricciones: un VPS y monolito modular del ADR-001; no es viable multiplicar despliegues. La cifra 24/s es una hipótesis de carga a validar.

## 2\. Objetivo y refinamiento

Reducir el tiempo de búsqueda del módulo Catálogo con una consulta optimizada y un índice PostgreSQL sobre los campos de búsqueda (p. ej., título/autor, según la consulta real). No se agrega una nueva dependencia externa.

## 3\. Conceptos candidatos

|Concepto|Ventaja|Trade-off|Evaluación|
|-|-|-|-|
|Escalar a microservicios + Kubernetes|Aislaría la carga|Costo y operación fuera del equipo/plazo|Rechazado|
|Redis como caché de catálogo|Reduce lecturas|Invalida datos de disponibilidad, más memoria|Aplazado|
|Índices y optimización de consulta|Menor servicio sin nuevo servidor|Escrituras y almacenamiento adicionales|Elegido|
|Aumentar workers sin optimizar|Mejora concurrencia parcial|Compite por CPU/RAM de un VPS de 2 vCPU|Alternativa limitada|

## 4\. Evidencia

Prototipo: fitness/catalogo.py, 5000 solicitudes con llegadas y servicios exponenciales, 4 workers, 24 rps, semilla 2026. Sin índice se supone una media de servicio de 230 ms; con índice, de 80 ms. Estos valores son supuestos, no benchmarks reales.

Ejecución: python -m fitness.catalogo

|Medida|Sin índice|Con índice|Meta|
|-|-:|-:|-:|
|p95 (ms)|76155,4|253,5|<=1500|
|Carga (req/s)|24|24|24|
|Workers|4|4|4|

## 5\. Instanciar elementos

Catálogo conserva su interfaz interna; el cambio queda en infraestructura de persistencia. La futura migración SQL debe usar EXPLAIN ANALYZE y medir en PostgreSQL real antes de aceptar el índice definitivo.

El modelo sin índice se satura: 24 solicitudes/s multiplicadas por 230 ms suponen 5,52 workers ocupados de media, más que los 4 disponibles. Con 80 ms, la demanda baja a 1,92 workers. Esta diferencia explica el p95 simulado; no debe leerse como medición del VPS real.

## 6\. Vista

En C4, el módulo Catálogo sigue accediendo a PostgreSQL; se etiqueta QA-08-02 en E6. No se agrega un segundo servicio para un MVP de tres personas.

## 7\. Verificación

Fitness function E5 exigirá p95 <=1500 ms con el modelo supuesto. Riesgo: la distribución de búsquedas y los índices reales pueden diferir mucho de esta simulación.

