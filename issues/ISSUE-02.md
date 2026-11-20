# ISSUE-02 — El adaptador JSON interpreta una matrícula inválida como vigente

- Observado: si el sistema académico devuelve la cadena `"false"` en vez del booleano `false`, la reserva es aceptada porque Python considera verdadera una cadena no vacía.
- Esperado: no autorizar la reserva ante una respuesta no booleana; no ocupar el ejemplar ni crear préstamo. Tratar una respuesta mal formada como error de integración es preferible a confundirla con una matrícula no vigente.
- Prueba: `tests/test_issue_02.py::test_matricula_textual_no_autoriza`.
- Tipo: defecto real del adaptador JSON de la versión recibida, reproducido con un doble local.
