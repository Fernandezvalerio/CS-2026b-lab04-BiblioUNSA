# E2 - Strategy, Adapter y Factory en BiblioUNSA

## Problema del E1

El método `reservar_libro` tenía condicionales `if/elif` para seleccionar
la versión de API académica, leía directamente sus formatos distintos y
necesitaba cambios cada vez que aparecía otro contrato externo.

## Patrones incorporados

| Patrón | Clase | Responsabilidad |
|---|---|---|
| Strategy | `ValidadorMatricula` (`dominio.py`) | Interfaz común `validar(estudiante_id)`; el servicio depende de este contrato. |
| Adapter | `AdaptadorMatriculaJSON` | Traduce `consultar_matricula(...)` y su diccionario a `ResultadoMatricula`. |
| Adapter | `AdaptadorMatriculaCodigos` | Traduce `obtener_estado_alumno(...)` y su tupla a `ResultadoMatricula`. |
| Factory (registro) | `FabricaValidadores` | Relaciona el nombre del proveedor con una función creadora de la Strategy. |
| Cliente | `ServicioReservas` (`servicio.py`) | Obtiene la Strategy de la fábrica, valida y realiza la reserva sin condicionales por proveedor. |

## Explicación breve

El servicio ahora usa un validador común y ya no interpreta respuestas JSON
ni códigos HTTP. Cada Adapter traduce una interfaz externa, mientras la Factory
elige la implementación. Así se puede incorporar otro proveedor registrándolo
en la fábrica, sin modificar el flujo principal de reservas.

## Verificación

- `tests/test_comportamiento.py`: las **15 pruebas de E1** corren tanto con
  `reservas.antes.servicio` como con `reservas.servicio` (30 ejecuciones).
- `tests/test_patrones.py`: pruebas de los dos adaptadores, del registro y de
  una tercera Strategy `LOCAL`, añadida sin editar `ServicioReservas`.
- No hay SDK real, API de red ni clave. Todos los servicios externos se simulan.
- Medición exploratoria con `radon cc -s -a`: el método `reservar_libro` pasó de
  complejidad **15 (C)** en E1 a **11 (C)** en E2. La mejora restante se medirá
  en E6 después de extraer otras responsabilidades.
