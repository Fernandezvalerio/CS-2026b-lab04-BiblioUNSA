# Laboratorio 07 — E6: métricas y costo de los patrones

## 1. Qué se comparó

Revisamos el flujo **HU-03: reservar un libro con matrícula vigente** de
BiblioUNSA. La versión **antes** corresponde a E1 y permanece guardada en
`src/reservas/antes/servicio.py`. La versión **después** es la implementación
acumulada hasta E5, en `src/reservas/servicio.py` y sus colaboradores.

Medimos con **Radon 6.0.1**: `cc -s -a` para complejidad ciclomática y
`raw -s` para **SLOC** (líneas de código fuente, sin contar líneas vacías ni
comentarios). No usamos el número de líneas físicas `LOC` como si fuera SLOC.

Para que la comparación sea entendible, separamos tres alcances:

1. **Servicio principal:** un archivo antes y otro después, centrados en el
   mismo caso de uso.
2. **Lógica de reservas y dominio:** dos archivos antes (`antes/servicio.py`,
   `antes/dominio_e1.py`) y seis después (`servicio.py`, `dominio.py`, `validadores.py`,
   `decoradores.py`, `eventos.py`, `estados.py`). No contamos la versión `antes`
   dentro del resultado después. `antes/dominio_e1.py` es una copia fiel de
   `dominio.py` de E1, incluida para poder repetir las mediciones en este ZIP.
   Tampoco contamos los dobles externos en ninguno de los dos grupos.
3. **IA de E5:** la mostramos aparte porque recomienda libros y no existía en
   el flujo inicial. Sumarla al después daría una comparación engañosa.

## 2. Complejidad ciclomática antes y después

### Métodos del servicio que sí son directamente comparables

| Bloque de código | E1 antes | E5 después | Interpretación |
|---|---:|---:|---|
| `ServicioReservas.reservar_libro` | **15 (C)** | **9 (B)** | La lógica principal tiene seis puntos menos de complejidad. |
| `ServicioReservas.__init__` | 3 (A) | 6 (B) | Creció el ensamblaje de Factory y suscriptores. |
| Clase `ServicioReservas` (métrica de clase) | 10 (B) | 9 (B) | Ligera reducción según Radon. |
| **Promedio de bloques del archivo del servicio** | **5,17 (B)** | **5,20 (B)** | Prácticamente no cambió; no sería correcto afirmar que este promedio mejoró. |

El promedio del archivo incluye **clases y métodos**, no solo métodos. En E1
Radon analiza seis bloques en ese archivo y en E5 analiza cinco. Por eso el
descenso del método principal **no implica** que baje su promedio de archivo.

### Complejidad trasladada a los patrones

Los métodos siguientes no tienen equivalente uno a uno en E1; surgieron al
dividir responsabilidades. Mostramos el valor que reporta Radon en E5:

| Archivo y método | Después | Responsabilidad |
|---|---:|---|
| `validadores.py`: `AdaptadorMatriculaJSON.validar` | 1 (A) | Traduce la respuesta JSON de matrícula. |
| `validadores.py`: `AdaptadorMatriculaCodigos.validar` | 2 (A) | Traduce los códigos académicos. |
| `validadores.py`: `FabricaValidadores.crear` | 2 (A) | Selecciona la estrategia registrada. |
| `decoradores.py`: `ConReintentos.validar` | 4 (A) | Reintenta errores de tiempo de espera. |
| `eventos.py`: `PublicadorEventos.publicar` | 2 (A) | Notifica a los observadores. |
| `eventos.py`: `ObservadorAvisos.actualizar` | 3 (A) | Produce los avisos de reserva. |
| `estados.py`: `Prestado.marcar_vencido` | 3 (A) | Gestiona transición de préstamo. |
| `estados.py`: `Vencido.aplicar_multa` | 3 (A) | Gestiona multa desde estado vencido. |
| `dominio.py`: `Prestamo.aplicar_multa` | 1 (A) | Delega al objeto de estado; en E1 era 3 (A). |
| `dominio.py`: `Prestamo.registrar_devolucion` | 1 (A) | Delega al estado; en E1 era 2 (A). |

### Promedio del código de reservas + dominio

| Indicador | E1 antes | E5 después |
|---|---:|---:|
| Promedio Radon de todos los bloques del alcance | **1,95 (A)** | **1,83 (A)** |
| Bloques analizados (clases, funciones y métodos) | 40 | 87 |

Este promedio disminuyó ligeramente, pero **no prueba por sí solo** que el
sistema completo sea más sencillo: ahora existen muchas clases y métodos
pequeños. Por eso también consideramos el aumento de SLOC, la separación de
responsabilidades y las pruebas.

## 3. Líneas de código fuente (SLOC)

| Archivo o grupo de archivos | E1 antes | E5 después |
|---|---:|---:|
| Servicio de reservas | 104 | 101 |
| Dominio (`antes/dominio_e1.py` frente a `dominio.py`) | 118 | 114 |
| `validadores.py` | — | 41 |
| `decoradores.py` | — | 17 |
| `eventos.py` | — | 35 |
| `estados.py` | — | 70 |
| **Total: reservas + dominio, sin simuladores externos ni IA** | **222** | **378** |
| Archivos medidos en ese total | 2 | 6 |

El **servicio principal** bajó de 104 a 101 SLOC (tres líneas menos, un 2,9 %).
Sin embargo, el **conjunto de reservas + dominio** creció de 222 a 378 SLOC:
**156 líneas adicionales**, aproximadamente **70,3 % más**, distribuidas en
cuatro archivos adicionales. Los patrones organizaron el código, pero no lo
hicieron más corto en términos globales.

La función de recomendaciones con IA de E5 tiene **102 SLOC adicionales** en
`ia.py`. No la sumamos a la tabla anterior porque es una función nueva, no
una refactorización de HU-03. En ese archivo, por ejemplo,
`GuardrailFormato.validar` tiene CC **9 (B)**,
`GuardrailCatalogo.validar` **6 (B)** y `RecomendadorLibros.recomendar`
**6 (B)**. Son puntos a vigilar si las reglas de validación crecen.

## 4. Análisis del trade-off (7 líneas)

1. **Ganamos** un método de reserva más entendible: bajó de complejidad 15 a 9 porque ya no decide directamente cómo consultar cada sistema académico.
2. **Ganamos** la posibilidad de registrar nuevos validadores sin tener que editar el flujo principal de reservas.
3. También quedó más claro dónde se controlan los reintentos, los avisos y las transiciones del préstamo.
4. **El costo** es que ahora tenemos 378 SLOC en vez de 222, repartidas entre más archivos y clases.
5. Además, el constructor del servicio se volvió más complejo (de 3 a 6), porque debe conectar los colaboradores.
6. La versión **antes** habría sido suficiente si solo existiera un proveedor académico, no se necesitaran avisos y las reglas del préstamo fueran estables.
7. **Sí consideramos útil el refactor** para BiblioUNSA, donde se prevén integraciones diferentes, nuevas reglas y varias notificaciones, siempre que las 69 pruebas sigan pasando.

## 5. Patrón propuesto y rechazado

**Abstract Factory — rechazado.** Se consideró en E1, pero aquí no tenemos
familias de objetos relacionados que deban crearse juntas: necesitamos elegir
un validador académico entre varios contratos. `FabricaValidadores` ya resuelve
esa variación. Incorporar Abstract Factory habría exigido más interfaces y
clases sin atender un problema distinto. También evitamos **Singleton** para
no compartir estado global de repositorios, caché o integraciones entre pruebas.

Esta es la diferencia entre aplicar patrones por necesidad y caer en
*patternitis*: agregar capas solo porque conocemos el patrón puede volver más
difícil de mantener un programa que ya era comprensible.

## 6. Reproducción de resultados

Ejecutar en la raíz del proyecto, con las dependencias instaladas desde
`requirements-lab07.txt`:

```bash
python -m pip install -r requirements-lab07.txt

# Complejidad de los dos servicios, por método, y su promedio conjunto
python -m radon cc -s -a src/reservas/antes/servicio.py src/reservas/servicio.py

# Para promedios individuales, ejecutar cada archivo por separado
python -m radon cc -s -a src/reservas/antes/servicio.py
python -m radon cc -s -a src/reservas/servicio.py

# Promedios de la lógica y el dominio (sin IA ni simuladores)
python -m radon cc -s -a src/reservas/antes/servicio.py src/reservas/antes/dominio_e1.py
python -m radon cc -s -a src/reservas/servicio.py src/reservas/dominio.py src/reservas/validadores.py src/reservas/decoradores.py src/reservas/eventos.py src/reservas/estados.py

# SLOC del alcance antes, con el dominio original incluido en esta entrega
python -m radon raw -s src/reservas/antes/servicio.py src/reservas/antes/dominio_e1.py

# SLOC de cada archivo del refactor (sin contar 'antes' ni IA)
python -m radon raw -s src/reservas/servicio.py src/reservas/dominio.py src/reservas/validadores.py src/reservas/decoradores.py src/reservas/eventos.py src/reservas/estados.py

# Verificación de comportamiento
python -m pytest -q tests/
```

**Nota sobre el promedio de grupos:** el valor de E1 (1,95) se verificó con
`antes/servicio.py` y `antes/dominio_e1.py`; el valor E5 (1,83) corresponde a
los seis archivos del código refactorizado.
