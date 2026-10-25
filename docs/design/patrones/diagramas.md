# Laboratorio 07 — diagramas de clases por patrón

Se documentaron las clases **reales** de `src/reservas/`. Cada diagrama
incluye los estereotipos del papel que desempeñan las clases. El nombre del
patrón no reemplaza las relaciones del código.

| Patrón o variante | Fuente PlantUML | Imagen | Prueba relacionada |
|---|---|---|---|
| Strategy académica | [strategy.puml](strategy.puml) | [PNG](img/strategy.png) | `test_open_closed_nuevo_proveedor_sin_modificar_servicio` |
| Adapter académico | [adapter.puml](adapter.puml) | [PNG](img/adapter.png) | `test_adapter_json_devuelve_el_contrato_comun` |
| Factory por registro | [factory.puml](factory.puml) | [PNG](img/factory.png) | `test_factory_crea_la_estrategia_registrada_y_rechaza_desconocida` |
| State | [state.puml](state.puml) | [PNG](img/state.png) | `test_transicion_invalida_no_permite_devolver_reservado` |
| Observer | [observer.puml](observer.puml) | [PNG](img/observer.png) | `test_observer_publica_un_evento_a_dos_suscriptores` |
| Decorator para reintentos | [decorator.puml](decorator.puml) | [PNG](img/decorator.png) | `test_decorator_reintenta_dos_timeouts_y_luego_devuelve_respuesta` |
| Strategy y Adapter para IA | [strategy-adapter-ia.puml](strategy-adapter-ia.puml) | [PNG](img/strategy_adapter_ia.png) | `test_proveedor_llm_puede_sustituirse_sin_modificar_recomendador` |
| Decorator caché de IA | [decorator-cache-ia.puml](decorator-cache-ia.puml) | [PNG](img/decorator_cache_ia.png) | `test_decorator_cache_evita_otra_llamada_al_mismo_prompt` |
| Chain of Responsibility | [chain-of-responsibility.puml](chain-of-responsibility.puml) | [PNG](img/chain_of_responsibility.png) | `test_guardrail_catalogo_bloquea_libros_inventados` |

El diagrama de conjunto actualizado está en
[`docs/design/clases.puml`](../clases.puml), con su
[imagen PNG](../img/clases-reservas-lab07.png). Conservamos el original del Laboratorio 05
como `docs/design/clases-lab05-original.puml`.

## Aclaraciones importantes

- **Factory** aquí es un registro de constructores (`FabricaValidadores`).
  Es una *Simple Factory*; no se pretende presentar como una
  *Abstract Factory* de GoF, que se rechazó en E1.
- **Observer** usa `typing.Protocol`: los suscriptores tienen
  `actualizar(evento)`, pero no heredan formalmente de
  `ObservadorEventos` en Python.
- **State** mantiene el valor `EstadoPrestamo` y el objeto
  `_estado_objeto` sincronizados; la clase base rechaza transiciones
  inválidas.
- **Chain of Responsibility** valida texto no confiable. Un resultado
  encontrado en la caché del LLM sigue pasando por ambos guardrails.
- Las APIs académicas y el LLM son **simuladores**. No se documenta ninguna
  clave, acceso de producción ni envío real de notificaciones.

## Cómo regenerar PNG y SVG

Con Java y PlantUML disponibles, desde la raíz del proyecto:

```bash
java -jar plantuml.jar -tpng -o img docs/design/patrones/*.puml
java -jar plantuml.jar -tpng -o img docs/design/clases.puml
java -jar plantuml.jar -tsvg -o img docs/design/patrones/*.puml
java -jar plantuml.jar -tsvg -o img docs/design/clases.puml
```

PlantUML toma el nombre de salida de `@startuml` cuando el archivo
especifica un identificador, por eso algunas imágenes utilizan guiones bajos.
Se agregó `!pragma layout smetana` para que estos diagramas puedan
renderizarse con PlantUML sin necesitar Graphviz instalado por separado.
