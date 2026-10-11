# Round-trip: del diagrama de clases al código y de vuelta — BiblioUNSA (Lab 05, E6)

Flujo aplicado: `clases.puml` → IA (ingeniería directa, Prompt IA 2) → `src/reservas/dominio.py` → `pyreverse` (ingeniería inversa) → `classes_reservas.puml` → comparación humana (este archivo).

## Archivos

| Paso | Archivo |
|------|---------|
| Diagrama de diseño | [`clases.puml`](clases.puml) · [PNG](img/diagrama_clases.png) |
| Código generado y revisado | [`src/reservas/dominio.py`](../../src/reservas/dominio.py) |
| Diagrama obtenido del código | [`classes_reservas.puml`](classes_reservas.puml) · [PNG](img/classes_reservas.png) |

Comando de ingeniería inversa (desde `src/`):

```bash
pip install pylint
pyreverse -o puml -p reservas reservas      # genera classes_reservas.puml
java -jar plantuml.jar -tpng classes_reservas.puml
```

## Diferencias entre el diagrama de diseño y el diagrama obtenido del código

| # | Diferencia observada | Causa | Acción |
|---|----------------------|-------|--------|
| 1 | No hay multiplicidades en ninguna relación (`1`, `0..*`, `1..*`). | El código no expresa multiplicidades y `pyreverse` no las infiere. | Documentar la limitación. La regla C3 se verifica en el diagrama de diseño; en el código, `Libro.ejemplares` es una lista y `Ejemplar.marcar_reservado()` rechaza un ejemplar no disponible. |
| 2 | Desaparece la composición `Libro` *-- `Ejemplar`; solo queda el atributo `ejemplares : list[Ejemplar]` dentro de `Libro`. | `pyreverse` no infiere asociaciones desde colecciones tipadas (`list[Ejemplar]`). | Ninguna: es una limitación de la herramienta. Se mantiene la composición en el diagrama de diseño. |
| 3 | `ValidadorMatricula`, `RepositorioPrestamos` y `RepositorioEjemplares` aparecen como clases normales, sin `<<puerto>>`; `AdaptadorSistemaAcademico` y `ServicioReservas` pierden sus estereotipos `<<adaptador>>` y `<<servicio>>`. La realización del puerto se ve como herencia (`--|>`). | Python implementa las interfaces con clases abstractas (ABC) y `pyreverse` no conoce los estereotipos del diseño. | Aceptable en Python. Se documenta aquí que ABC = interfaz/puerto. |
| 4 | `ServicioReservas` aparece con agregación (`--o`) hacia `ValidadorMatricula`, `RepositorioPrestamos` y `RepositorioEjemplares`; el diseño las modela como dependencias (`..>`). | El servicio recibe los puertos por el constructor y los guarda como atributos (inyección de dependencias), y `pyreverse` interpreta eso como agregación. | Documentar. Para un servicio con puertos inyectados, la asociación es una descripción válida; el diseño se mantiene como dependencia de uso. |
| 5 | Faltan las dependencias `ValidadorMatricula ..> ResultadoMatricula`, `ServicioReservas ..> Prestamo` y `ServicioReservas ..> ResultadoMatricula`. `ResultadoMatricula` y `Libro` quedan sin ninguna flecha. | `pyreverse` solo detecta relaciones que se guardan como atributos, no las que aparecen en parámetros, tipos de retorno o variables locales. | Documentar la limitación. Las dependencias de uso se verifican en `secuencia-reservar-libro.puml` (regla C1). |
| 6 | La enumeración `EstadoPrestamo` aparece como una clase con un atributo `name`, sin los valores `RESERVADO`, `PRESTADO`, `VENCIDO`, `DEVUELTO` y `CON_MULTA`. | `pyreverse` trata `Enum` como una clase más y no lista sus miembros. | Documentar la limitación. Los 5 valores del código coinciden con el enum del diseño y con los estados de `estados-prestamo.mmd` (C2). |
| 7 | Se pierde la visibilidad (`-`, `+`) y los métodos privados `_consultar_api` y `_leer_cache` no aparecen. Además, `Prestamo.estado`, `ejemplar`, `estudiante` y `monto_multa` se muestran sin tipo. | Python no tiene visibilidad estricta, `pyreverse` oculta por defecto los miembros privados y omite el tipo cuando dibuja el atributo como asociación. | Documentar. Si se necesitan, se pueden mostrar con `pyreverse -f ALL`. |
| 8 | `Prestamo` apunta a `Estudiante` (`Prestamo --> Estudiante`); en el diseño la asociación es `Estudiante "1" -- "0..*" Prestamo`, sin dirección. | En el código, el préstamo guarda una referencia al estudiante, pero el estudiante no guarda una lista de sus préstamos. | Aceptado: se navega de `Prestamo` a `Estudiante`. Los préstamos de un estudiante se consultan por repositorio. Se documenta la navegabilidad. |
| 9 | Los nombres cambian de camelCase a snake_case (`registrarDevolucion` → `registrar_devolucion`, `marcarVencido` → `marcar_vencido`, `fechaVencimiento` → `fecha_vencimiento`). | Convención de Python (PEP 8). | Aceptable. Equivalencia documentada para la regla C5. |
| 10 | `AdaptadorSistemaAcademico.validar` aparece en cursiva (abstracto). | El método lanza `NotImplementedError`, y `pyreverse` lo trata como abstracto. | Aceptable: es un esqueleto. Cambiará cuando se implemente la integración con la API. |

## Revisión de la primera respuesta de la IA (ingeniería directa)

Antes de ejecutar `pyreverse` se revisó el código generado con la lista de verificación:

- Los nombres de clases y enumeraciones coinciden con `clases.puml` (C5).
- Cada operación del diagrama existe en el código (en snake_case).
- Solo `Ejemplar` y `Prestamo` tienen lógica; el resto lanza `NotImplementedError`.
- Las transiciones de `Prestamo` siguen `estados-prestamo.mmd`: `entregar()`, `marcar_vencido()`, `registrar_devolucion(fecha)`, `aplicar_multa(monto)` y `marcar_para_reverificacion()` rechazan los estados de origen inválidos con `ValueError` (C2).
- Se comprobó con un script que el flujo `RESERVADO → PRESTADO → VENCIDO → CON_MULTA` y `RESERVADO → PRESTADO → DEVUELTO` funciona, que una transición inválida lanza error y que `ValidadorMatricula` no se puede instanciar.
