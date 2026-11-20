# E6 — Delegación progresiva en BiblioUNSA

| Rol humano | Permisos del agente | Evidencia para avanzar |
|---|---|---|
| Ejecutor | Solo lectura, mapa, búsqueda; el humano hace los cambios | Localiza causas y propone cambios que reproducen y resuelven el fallo sin tocar rutas prohibidas. |
| Revisor (nivel actual) | Ejecuta pruebas y edita src/ tras aprobación s/n; el revisor agente es de solo lectura | Pruebas verdes, diff revisado, trazas completas, aprobación registrada y ninguna edición no autorizada. |
| Colaborador | En rama aislada puede editar cambios de bajo riesgo; revisión obligatoria de matrícula, permisos y multas | Varias tareas consecutivas correctas, tasa baja de rechazos y sin regresiones ni intentos de escapar de la copia. |
| Gobernador | Delega tareas acotadas y evalúa auditorías; no permite secretos, cambios de pruebas, despliegue o fusión autónoma | Evaluación sostenida con casos adversarios, límites respetados, aprobación final y mecanismo de revocación. |

La implementación queda en nivel revisor: se muestra ruta, fragmento anterior y propuesto; únicamente s o n son entradas válidas. Con n no se ejecuta la modificación y la observación vuelve al agente. La aprobación del crítico no equivale a la aprobación humana del PR. Al terminar, una persona revisa el diff y las pruebas antes de incorporar el cambio. Se usa una copia local y no un aislamiento del sistema operativo; nunca entregar secretos, no ejecutar código no confiable y mantener la aprobación activa.

Los resultados del E5 (91 pruebas del proyecto y revisión aprobada en una ronda) justifican ensayar este nivel, pero no autorizan aumentar la autonomía automáticamente. En E6 se verificará el rechazo y la aceptación usando la misma base del ISSUE-02 y se conservará la evidencia real en `trazas/issue02-aprobacion/`.
