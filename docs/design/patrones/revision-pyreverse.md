# Laboratorio 07 — contraste del diagrama con pyreverse

## Cómo se realizó la comprobación

Desde la raíz del proyecto se ejecutó la ingeniería inversa sobre las clases
de `src/reservas`, excluyendo `antes/` para no mezclar el código antiguo
con el refactor. La herramienta analizó **9 módulos con 13 importaciones** y
generó `classes_BiblioUNSA_E7.puml` y
`packages_BiblioUNSA_E7.puml` en
`docs/design/patrones/verificacion-pyreverse/`.

```bash
python -m pip install pylint
pyreverse --ignore=antes --source-roots src -o puml -p BiblioUNSA_E7 -d docs/design/patrones/verificacion-pyreverse src/reservas
```

Después se cotejó esa salida **generada automáticamente** con el
`docs/design/clases.puml` revisado para E7.

## Hallazgos del contraste

| Elemento revisado | Lo que aparece en el código/pyreverse | Decisión en el diagrama E7 |
|---|---|---|
| Strategy y Adapter | `AdaptadorMatriculaJSON` y `AdaptadorMatriculaCodigos` heredan de `ValidadorMatricula`. | Representados con herencia y roles Strategy/Adapter. |
| Decorator de matrícula | `ConReintentos` hereda de `ValidadorMatricula` y contiene un `interno` del mismo contrato. | Se representa la herencia y la referencia al componente envuelto. |
| State | Los cinco estados heredan de `EstadoPrestamoBase`; `Prestamo` delega en `_estado_objeto`. | Se muestran los cinco ConcreteState y la delegación del contexto. |
| Observer | `ObservadorEventos` es un `Protocol` de tipado estructural. `ObservadorHistorial` y `ObservadorAvisos` no declaran herencia. | **Corrección:** dependencias de compatibilidad con el protocolo, no flechas de herencia falsa. |
| IA (Strategy, Adapter y Decorator) | `AdaptadorMotorSimulado` y `ConCacheLLM` heredan de `ProveedorLLM`. | Relaciones exactas en los diagramas individuales de E5. |
| Chain | `GuardrailFormato` y `GuardrailCatalogo` heredan de `Guardrail`, que tiene el atributo `siguiente`. | Se representa como cadena de responsabilidad, con los dos validadores. |
| Servicio de reservas | Existen **dos clases** llamadas `ServicioReservas`: la de `dominio.py` es el esqueleto conservado del Lab 05 y la de `servicio.py` es la operativa. | **Corrección:** en el diagrama general se identifica expresamente `ServicioReservas (servicio.py)` para no confundirlas. |
| Relación Libro–Ejemplar | La entidad `Libro` tiene `ejemplares: list[Ejemplar]` con lista vacía por defecto. | La multiplicidad queda en **0..***, no en 1..* del supuesto original del Lab 05. |
| Estados persistidos | `EstadoPrestamo` es un `Enum` con cinco valores. Pyreverse muestra la clase pero no reconstruye necesariamente los literales como una enumeración UML completa. | Se mantiene como `enum` con `RESERVADO`, `PRESTADO`, `VENCIDO`, `DEVUELTO` y `CON_MULTA`. |
| Asociaciones y patrones | Pyreverse detecta dependencias estáticas y algunas asociaciones; las creaciones con funciones lambda o los roles GoF no quedan completos. | Se completaron **a mano** las relaciones justificadas por lectura del código y estereotipos. |

## Qué se verificó y qué no

- Los nombres de clases, métodos importantes, herencias y colaboradores de
  los diagramas proceden del código Python actual.
- `pyreverse` es una **verificación parcial**, no prueba que todas las
  multiplicidades ni los roles de diseño sean correctos automáticamente.
- El diagrama general es intencionalmente selectivo: presenta el flujo de
  HU-03 y la función de IA, mientras que los detalles de los patrones se
  documentan en nueve diagramas más pequeños.
- Las clases externas de las pruebas son **simuladores en memoria**. No se
  ha verificado una integración real con la UNSA o un servicio LLM externo.
- Se comprobó que las fuentes PlantUML no tienen errores de sintaxis y se
  generaron los PNG de E7, sin editar el código de negocio.

## Resultado

El contraste confirmó las relaciones fundamentales y permitió evitar errores
concretos en la representación de **Observer**, el **servicio operativo** y
la multiplicidad **Libro–Ejemplar**. No fue necesario alterar los módulos ni
las pruebas del proyecto.
