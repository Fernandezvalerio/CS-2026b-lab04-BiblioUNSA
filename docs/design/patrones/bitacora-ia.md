# Laboratorio 07 — E7: bitácora de interacción con IA

**Proyecto:** BiblioUNSA, flujo HU-03 (reservar un libro validando la
matrícula) y recomendaciones de libros con IA simulada.

Estas interacciones resumen el trabajo con asistencia de IA desarrollado en
E1–E7. Los prompts están **resumidos**, no se presentan como transcripciones
literales. Cada decisión se verificó contra el código, la guía o las
pruebas automatizadas. No se introdujeron claves ni datos reales de alumnos.

| # | Etapa y prompt (resumen) | Propuesta de la IA | Verificación o corrección | Decisión del equipo |
|---|---|---|---|---|
| 1 | **E1.** «Detecta olores reales en HU-03 y sugiere patrones, indicando su costo». | Extraer la selección de proveedor; considerar Strategy, Adapter y Abstract Factory. | Revisamos `antes/servicio.py` y los dos formatos de respuesta. No hay familias de productos para Abstract Factory; `olores.md` recoge la razón. | **Aceptar** Strategy y Adapter; **rechazar** Abstract Factory por complejidad innecesaria. |
| 2 | **E2.** «Permite añadir otro sistema académico sin cambiar reservar_libro». | Un contrato `ValidadorMatricula`, dos adaptadores y una fábrica registrable. | `test_open_closed_nuevo_proveedor_sin_modificar_servicio` crea la variante LOCAL inyectando otra `FabricaValidadores`. Se conservan los casos de E1. | **Aceptar** Strategy + Adapter + Simple Factory. |
| 3 | **E3.** «Implementa el diagrama de estados del préstamo con State». | Una clase por estado y delegación desde `Prestamo`. | `test_transicion_invalida_no_permite_devolver_reservado` y `test_devolucion_tardia_exige_pasar_primero_por_vencido` comprueban restricciones que un esquema superficial podría omitir. | **Aceptar** State, manteniendo sincronizado el enum persistible. |
| 4 | **E4.** «Separa los avisos del servicio de reserva». | Publicador con `ObservadorHistorial` y `ObservadorAvisos`. | `test_observer_publica_un_evento_a_dos_suscriptores` prueba ambos destinos y otra prueba retira un suscriptor. Revisamos que los objetos satisfacen el `Protocol` por sus métodos, sin herencia explícita. | **Aceptar** Observer sin integraciones de correo reales. |
| 5 | **E4.** «Aísla tres reintentos de la API académica». | Un Decorator alrededor de `ValidadorMatricula`. | `test_decorator_no_reintenta_fallos_distintos_de_timeout` exige que una excepción de integración HTTP no se reintente. `test_decorator_propaga_timeout_tras_agotar_intentos` limita los intentos. | **Aceptar** `ConReintentos`, únicamente para `TimeoutError`. |
| 6 | **E5 — corrección guiada por pruebas.** «Agrega caché de respuestas LLM; ¿podemos confiar en respuestas ya guardadas?». | La variante más corta validaría una respuesta al generar y podría reutilizar el texto de caché como si ya fuera seguro. | **Se descartó esa variante:** `test_guardrails_validan_incluso_respuestas_procedentes_de_cache` fuerza una respuesta con ISBN falso, la consulta dos veces y exige `RespuestaLLMInvalida` ambas veces, con una única llamada al motor. El diseño correcto ejecuta `cadena.procesar()` después de obtener la respuesta, sea nueva o cacheada. | **Corregir la propuesta** y mantener los dos guardrails después del proveedor/caché. Es una corrección de diseño detectada al contrastar con una prueba, no un fallo que se dejara en la versión final. |
| 7 | **E6.** «Compara Radon y SLOC sin ocultar los costos de refactorizar». | La complejidad del método principal bajó, pero se agregaron clases de patrones. | Medimos **15 → 9** de complejidad en `reservar_libro`, mientras reservas y dominio pasan de **222 → 378 SLOC**. El promedio del archivo del servicio es **5,17 → 5,20**, casi igual. Se verificaron las 69 pruebas. | **Aceptar con matices:** mejora la separación de responsabilidades, no reduce el tamaño total. |
| 8 | **E7.** «Dibuja cada patrón y actualiza clases.puml con el código actual». | Diagramas con estereotipos de rol y relaciones de asociación, herencia y delegación. | Verificamos con `pyreverse` y revisamos cada clase contra los archivos `validadores.py`, `estados.py`, `eventos.py`, `ia.py` y `servicio.py`. Se distinguieron los esqueletos del Lab 05 del servicio operativo y se evitó dibujar a los observadores como herederos directos del `Protocol`. | **Aceptar tras correcciones**; los diagramas editables y el informe de contraste quedan en esta carpeta. |

## Corrección destacada: respuesta almacenada no es respuesta confiable

La sexta interacción es la revisión más importante de seguridad. Aunque una
salida se recupere de `ConCacheLLM`, puede contener un ISBN inventado. La
prueba de E5 comprueba que **tanto la primera llamada como el acierto de
caché son rechazados** por los guardrails. Por eso se mantiene el orden:

1. El recomendador solicita texto al proveedor (`ProveedorLLM` o su Decorator).
2. `GuardrailFormato` comprueba JSON y cantidad de ISBN.
3. `GuardrailCatalogo` comprueba que los ISBN existen y son adecuados.
4. Solo entonces se devuelven los objetos `Libro` reales.

La prueba sirve para descartar una modificación insegura antes de aceptarla
en la implementación. No afirmamos haber utilizado una API de LLM real.

## Evidencia que puede revisar el docente

- E1: `docs/design/patrones/olores.md` y `radon-e1.txt`.
- E2–E4: `tests/test_patrones.py`, `test_estados.py` y `test_e4.py`.
- E5: `tests/test_ia.py`, especialmente la prueba de caché y guardrails.
- E6: `docs/design/patrones/metricas.md` y `radon-e6.txt`.
- E7: los `*.puml`, las imágenes en `img/` y `revision-pyreverse.md`.

**Resultado de la última comprobación:** 69 pruebas aprobadas.
