# ISSUE-03 — Un préstamo devuelto sigue apareciendo como vencido

- Observado: la consulta de vencidos incluye un préstamo cuyo libro ya fue devuelto, mientras está pendiente el cálculo de multa.
- Esperado: excluir registros con fecha de devolución, conservar los préstamos activos atrasados y no incluir los que vencen hoy.
- Prueba: `tests/test_issue_03.py::test_devuelto_no_figura_como_vencido`.
- Tipo: error sembrado en la nueva consulta del repositorio; no se cambia la máquina State de Lab 07.
