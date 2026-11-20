# ISSUE-01 — La multa incluye domingos

- Observado: del sábado 14/11/2026 al lunes 16/11/2026 se cobran dos días de mora.
- Esperado: excluir domingos, contar desde el día posterior al vencimiento hasta la devolución inclusive; a tarifa S/ 2 corresponde S/ 2. No cobrar si se devuelve a tiempo.
- Prueba: `tests/test_issue_01.py::test_no_cobra_domingo`.
- Tipo: error sembrado en `src/reservas/multas.py` para el laboratorio. No usar datos reales.
