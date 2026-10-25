# E3 - Patrón State para Prestamo (BiblioUNSA)

## Problema del E1 y E2

En `dominio.py`, el préstamo tenía comprobaciones sobre el valor de
`EstadoPrestamo` en cada método. Al añadir transiciones habría que extender
esos condicionales, con riesgo de permitir cambios de estado incorrectos.
El diagrama `docs/design/estados-prestamo.mmd` del Lab 05 ya indicaba las
transiciones y los estados finales.

## Solución

Se implementó `src/reservas/estados.py` con una clase base
`EstadoPrestamoBase` que rechaza por defecto todas las operaciones. Las
subclases `Reservado`, `Prestado`, `Vencido`, `Devuelto` y `ConMulta` redefinen
solo los métodos permitidos en cada estado.

La entidad `Prestamo` conserva el atributo público `estado` como enumeración,
útil para guardar y consultar el estado, y mantiene internamente un objeto
`_estado_objeto`. Sus métodos (`entregar`, `marcar_vencido`,
`registrar_devolucion`, `aplicar_multa` y `marcar_para_reverificacion`)
delegan en ese objeto. Las transiciones actualizan ambos de forma coordinada.

## Transiciones implementadas

| Desde | Operación | Hacia | Regla |
|---|---|---|---|
| `RESERVADO` | `marcar_para_reverificacion()` | `RESERVADO` | Marca la validación pendiente, sin cambiar estado. |
| `RESERVADO` | `entregar()` | `PRESTADO` | El estudiante recoge el ejemplar. |
| `PRESTADO` | `registrar_devolucion(fecha)` | `DEVUELTO` | La devolución no supera la fecha de vencimiento. |
| `PRESTADO` | `marcar_vencido(hoy)` | `VENCIDO` | Si hay fecha límite, el día actual debe ser posterior. |
| `VENCIDO` | `registrar_devolucion(fecha)` | `VENCIDO` | Registra una devolución tardía sin cerrar todavía la multa. |
| `VENCIDO` | `aplicar_multa(monto)` | `CON_MULTA` | Requiere devolución registrada y monto positivo. |
| `DEVUELTO` y `CON_MULTA` | Otras transiciones | Rechazadas | Son finales para esta historia de usuario. |

Los métodos inválidos lanzan `ValueError` desde la clase base. En particular,
la devolución tardía debe pasar antes por `marcar_vencido`, coherentemente con
la máquina de estados del Lab 05. Se comprueba con pruebas explícitas.

## Pruebas

- `tests/test_estados.py` cubre transiciones correctas, intentos inválidos,
  guardas de fecha y monto, estados finales y reconstrucción desde un estado
  persistido.
- `tests/test_comportamiento.py` y `tests/test_patrones.py` se conservan, para
  comprobar que la creación de una reserva y los patrones de E2 siguen activos.

## Alcance

Solo se aplicó **State**. Las notificaciones y reintentos todavía no usan
Observer ni Decorator (E4). La gestión del pago de una multa queda fuera de
HU-03 y el diagrama ya considera `CON_MULTA` como final.
