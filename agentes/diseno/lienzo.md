# Lienzo de diseño — BiblioUNSA (Lab 10)

|Decisión|Elección|Justificación|
|-|-|-|
|Agente o flujo|Agente para localizar y corregir errores; flujo fijo para calcular multas y validar matrícula|Explorar código y reaccionar a pruebas requiere flexibilidad; las reglas de negocio son deterministas.|
|Arquetipo|ReAct y planificador-ejecutor|ReAct explora y verifica; un plan previo ayuda a organizar la revisión de matrícula.|
|Herramientas|Listar, leer, buscar, editar código, ejecutar pruebas y ver cambios; luego mapa AST y notas|Son suficientes para localizar, corregir y comprobar sin acceso a red ni comandos arbitrarios.|
|Memoria|Historial de corto plazo y notas en archivo por ejecución (E4)|Conserva hipótesis y resultados sin mezclar ejecuciones.|
|Coordinación|Agente único como opción inicial; gestor y actor-crítico para ISSUE-02|Separa edición de revisión cuando afecta al acceso a reservas.|
|Rol humano|Revisor de cambios, con aprobación por edición en E6|No se confía al agente la decisión de incorporar cambios al repositorio.|
|Control|Contrato JSON, copia local, rutas protegidas, permisos por rol, máximo 12 decisiones del ejecutor, 8 del revisor y 2 rondas|Limita acciones indebidas y mantiene una traza verificable.|



Los issues 01 y 03 son sembrados porque el cálculo y la consulta aún no existían. El 02 reproduce un defecto de validación del adaptador JSON existente. El flujo de devolución y multa del Lab 05 conserva su máquina State: un préstamo con devolución registrada no debe aparecer en la consulta de vencidos aunque aún no se haya aplicado la multa. La tarifa de multa se recibe como parámetro; excluir domingos es la regla de este ejercicio, no una política institucional verificada.

