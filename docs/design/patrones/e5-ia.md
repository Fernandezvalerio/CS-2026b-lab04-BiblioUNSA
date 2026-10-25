# E5 - Integración de IA en BiblioUNSA

## Función elegida

Según la tabla de casos de la guía del Lab 07, BiblioUNSA debe **recomendar
libros similares del catálogo**. Se implementó con un LLM simulado: el modelo
propone ISBN y el sistema devuelve los datos reales de los libros, sin
inventar títulos, autores o ejemplares.

## Patrones utilizados

| Necesidad | Patrón | Implementación |
|---|---|---|
| Cambiar el modelo sin cambiar el recomendador | Strategy | Interfaz `ProveedorLLM` con método `generar(prompt)`. |
| Adaptar la interfaz de un motor externo | Adapter | `AdaptadorMotorSimulado` traduce `completar(...)` a `generar(...)`. |
| Evitar consultas repetidas | Decorator | `ConCacheLLM` guarda respuestas para prompts idénticos. |
| Validar una respuesta no confiable | Chain of Responsibility | `GuardrailFormato` → `GuardrailCatalogo`. |

El doble de servicio externo `MotorTextoSimulado`, ubicado en `externos.py`,
devuelve respuestas configurables y cuenta sus llamadas. No utiliza ninguna
API real ni requiere claves.

## Guardrails

**Guardrail 1 - Formato.** La salida debe ser JSON con una sola propiedad,
`"isbns"`, que contenga entre uno y tres ISBN no vacíos. Rechaza texto libre,
listas mal formadas, demasiadas recomendaciones y campos extra, incluso si
incluyen datos personales.

**Guardrail 2 - Catálogo.** Todos los ISBN deben existir en la lista real de
libros. Rechaza referencias inventadas, repetidas o iguales al libro desde el
que se solicita la recomendación.

Los dos forman una cadena: si cualquiera encuentra un error, lanza
`RespuestaLLMInvalida` y la recomendación no llega al usuario. Los guardrails
se ejecutan **también cuando la respuesta procede de la caché**.

Ejemplo de salida permitida:

```json
{"isbns": ["ISBN-B", "ISBN-C"]}
```

Los ISBN de este ejemplo corresponden a datos simulados de las pruebas. En
uso real, deben corresponder a libros existentes en el catálogo cargado.

## Ejemplo de uso local

```python
from reservas.dominio import Libro
from reservas.externos import MotorTextoSimulado
from reservas.ia import AdaptadorMotorSimulado, ConCacheLLM, RecomendadorLibros

catalogo = [
    Libro(titulo="Algoritmos", autor="Autor A", isbn="ISBN-A"),
    Libro(titulo="Estructuras de datos", autor="Autor B", isbn="ISBN-B"),
]
motor = MotorTextoSimulado('{"isbns": ["ISBN-B"]}')
proveedor = ConCacheLLM(AdaptadorMotorSimulado(motor))
recomendador = RecomendadorLibros(catalogo, proveedor)

for libro in recomendador.recomendar("ISBN-A"):
    print(libro.titulo)
```

Se mantiene separado el catálogo del texto generado por la IA. Por ello, el
modelo nunca crea objetos `Libro` directamente y sus afirmaciones no se
consideran confiables hasta verificar los ISBN.

## Evidencia experimental

`tests/test_ia.py` contiene 14 casos: respuesta válida, caché, prompts
distintos, proveedor intercambiable, JSON mal formado, campos extras, límite
de recomendaciones, respuesta con tipo incorrecto, libros inventados,
duplicados, recomendación del propio libro, origen desconocido, validación
de respuesta cacheada y catálogo sin alternativas.

**Resultado global verificado: 69 pruebas aprobadas**, incluidas todas las de
E1-E4. No se modificaron los flujos de reserva ni los estados del préstamo.

## Decisión y limitaciones

Se optó por guardrails deterministas. Usar otro LLM como juez añadiría costo,
latencia y nuevas respuestas inciertas, y no es necesario para comprobar ISBN.
La calidad semántica de la similitud depende del proveedor que se conecte en
el futuro; por ahora se prueba la seguridad del contrato y la integración,
no la calidad de las recomendaciones de un modelo real.
