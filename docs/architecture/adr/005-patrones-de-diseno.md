# ADR-005: Aplicar patrones de diseño de forma selectiva en BiblioUNSA

- **Estado:** Aceptado en la implementación del Laboratorio 07; pendiente de ratificación mediante revisión cruzada del equipo.
- **Fecha:** 2026-10-25
- **Decisores propuestos:** Mauricio Antonio Paredes Miranda, Mijael Paul León Ramos, Valerio Piero Fernández Lastarria.
- **Relacionado con:** [ADR-001](001-estilo-arquitectonico.md) (monolito modular), [ADR-003](003-integracion-academica.md) (validación de matrícula y recuperación ante fallos) y [HU-03](../../design/historia.md).

## Contexto

En BiblioUNSA, HU-03 permite reservar un ejemplar después de comprobar que el
estudiante tiene matrícula vigente. La primera versión del flujo, conservada
en `src/reservas/antes/servicio.py`, resolvía la reserva, elegía el contrato
académico con condicionales, convertía las respuestas externas, controlaba
los reintentos y guardaba los eventos en el mismo método. Según Radon,
`reservar_libro` tenía una complejidad ciclomática de **15 (C)**.

Nuestro MVP debe prepararse con un equipo de tres desarrolladores, en un mes
y con un solo despliegue, de acuerdo con el ADR-001. El ADR-003 exige que la
integración académica se haga a través de una API, tenga un presupuesto de
espera de hasta 3 segundos, permita recurrir a una validación guardada de no
más de 24 horas y programe reverificación dentro de 30 minutos.

También necesitamos representar el ciclo de vida del préstamo según la
máquina de estados del Lab 05, producir avisos sin mezclar sus destinatarios
con la lógica de reservas y aislar una función de recomendaciones de libros
mediante IA. Las respuestas del LLM no son confiables: podrían contener
ISBN inventados, formato incorrecto o datos extra que no debemos mostrar.

Por estas razones, el problema no es adoptar la mayor cantidad de patrones,
sino permitir cambios concretos manteniendo pruebas reproducibles.

## Alternativas consideradas

1. **Mantener la versión inicial.** Es corta y suficiente si existe un único
   proveedor académico y las reglas de estados y avisos no cambian. Sin
   embargo, las nuevas variantes exigirían modificar el método central y
   volver a probar todo el flujo cada vez.
2. **Añadir patrones a todas las clases.** Por ejemplo, Abstract Factory
   para construir familias de integraciones, Singleton para caché y
   repositorios, Proxy adicional y un segundo LLM para juzgar respuestas.
   El resultado tendría más clases, dependencias y mantenimiento sin
   responder a necesidades presentes del proyecto.
3. **Refactorizar solo los puntos de variación y los efectos secundarios.**
   Usar interfaces y patrones en integración, estados, eventos e IA, pero
   mantener la arquitectura general como monolito modular y conservar la
   política de recuperación por caché de matrícula en el servicio.

## Decisión

**Usaremos la alternativa 3.** Las decisiones concretas son:

| Patrón o decisión | Lugar en el código | Motivo y alcance |
|---|---|---|
| **Strategy** | `ValidadorMatricula` en `dominio.py` | El flujo depende de `validar()`, no de la variante concreta de sistema académico. |
| **Adapter** | `AdaptadorMatriculaJSON` y `AdaptadorMatriculaCodigos` en `validadores.py` | Transforman los dos formatos de integración al mismo `ResultadoMatricula`. |
| **Simple Factory por registro** | `FabricaValidadores` en `validadores.py` | Selecciona una Strategy por nombre y permite registrar otra sin cambiar el caso de uso. No es Abstract Factory. |
| **State** | `EstadoPrestamoBase` y los cinco estados en `estados.py` | Cada estado controla sus transiciones válidas; `Prestamo` conserva un enum persistible sincronizado. |
| **Observer** | `PublicadorEventos`, `ObservadorHistorial` y `ObservadorAvisos` en `eventos.py` | Una reserva genera eventos para dos destinos desacoplados. No envía correos reales. |
| **Decorator** | `ConReintentos` en `decoradores.py` | Reintenta solo `TimeoutError`, sin repetir errores de validación u otras fallas. |
| **Strategy + Adapter de IA** | `ProveedorLLM` y `AdaptadorMotorSimulado` en `ia.py` | Cambiar el proveedor de texto no requiere modificar `RecomendadorLibros`. Se utiliza un motor local simulado. |
| **Decorator de IA** | `ConCacheLLM` en `ia.py` | Evita generar de nuevo una respuesta para el mismo prompt. |
| **Chain of Responsibility** | `GuardrailFormato` → `GuardrailCatalogo` en `ia.py` | Rechaza JSON inválido e ISBN fuera del catálogo, incluso cuando el texto proviene de caché. |

El servicio conserva el control de la **ventana de caché de matrícula de
24 horas**, de modo que los patrones anteriores no cambian la regla funcional
del ADR-003. Cuando se usa una respuesta almacenada, se sigue marcando el
préstamo para reverificación dentro de 30 minutos.

### Patrones que decidimos no incorporar

- **Abstract Factory:** no creamos familias de objetos relacionados. La
  única variación de E2 es el validador, ya cubierta por un registro simple.
  Agregar fábricas abstractas sería sobreingeniería.
- **Singleton:** repositorios, caché, publicadores y motores de texto se
  pueden inyectar o instanciar por escenario. Un estado global aumentaría
  el acoplamiento y dificultaría el aislamiento de las pruebas.
- **Proxy adicional para caché académica:** no aporta una ventaja clara
  en este alcance. La política de respaldo de 24 horas debe seguir visible
  en el caso de uso porque afecta a la autorización de la reserva.
- **Un segundo LLM como juez:** para comprobar JSON e ISBN ya tenemos reglas
  deterministas. Otro modelo aumentaría latencia, costo y posibles errores.

## Consecuencias

### Positivas

- La complejidad de `ServicioReservas.reservar_libro` bajó de
  **15 (C) a 9 (B)**. La validación externa dejó de depender de
  condicionales por proveedor dentro del método.
- La prueba `test_open_closed_nuevo_proveedor_sin_modificar_servicio`
  demuestra una nueva implementación de validación sin editar
  `ServicioReservas`.
- Las pruebas de State rechazan transiciones inválidas. Observer permite
  suscribir más destinos y Decorator centraliza la política de reintentos.
- La IA no inventa libros en la respuesta final: los ISBN pasan por dos
  guardrails y los objetos `Libro` se leen del catálogo real en memoria.
- Se conservan **69 pruebas automatizadas aprobadas** y las salidas de
  Radon para contrastar la versión inicial y la refactorizada.

### Negativas y riesgos

- La lógica de reservas y dominio creció de **222 a 378 SLOC**
  (**156 líneas más, aproximadamente 70,3 %**), repartidas entre
  **2 y 6 archivos**, respectivamente. Los patrones cuestan más archivos,
  clases y esfuerzo para comprender las relaciones.
- El promedio de complejidad del **archivo de servicio** cambió de
  **5,17 a 5,20**. No afirmamos que todos los indicadores mejoraron.
  `__init__` pasó de 3 a 6 porque conecta Factory y observadores.
- El promedio de complejidad de los bloques de **reservas + dominio**
  cambió de **1,95 a 1,83**, pero hay más bloques analizados y eso
  limita la comparación directa.
- No se verificó un servicio académico ni un LLM real. Las integraciones
  son simuladas, por lo que hay que validar contratos, tiempos y aspectos
  de seguridad antes de desplegar.
- El código conserva interfaces y una clase `ServicioReservas`
  esquelética de Lab 05 en `dominio.py`; la clase operativa está en
  `servicio.py`. Antes de producción convendría revisar y simplificar
  esas duplicidades de documentación/código.
- Los guardrails son controles de formato y pertenencia al catálogo,
  **no garantizan relevancia semántica** de las recomendaciones.

## Evidencia y seguimiento

- [Tabla de olores y patrones descartados](../../design/patrones/olores.md).
- [Métricas antes/después y análisis honesto](../../design/patrones/metricas.md).
- [Diagramas PlantUML e imágenes](../../design/patrones/diagramas.md).
- [Bitácora de IA con corrección contrastada por pruebas](../../design/patrones/bitacora-ia.md).
- [Instrucciones de revisión cruzada y entrega](../../design/patrones/revision-cruzada-pr.md).
- Pruebas: `tests/test_comportamiento.py`, `test_patrones.py`,
  `test_estados.py`, `test_e4.py` y `test_ia.py`.