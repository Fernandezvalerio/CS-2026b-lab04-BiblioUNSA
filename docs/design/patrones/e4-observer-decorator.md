# E4 - Observer y Decorator (BiblioUNSA)

## Olores detectados en E1-E3

El servicio generaba directamente cadenas de eventos y las agregaba a una
lista. Además, controlaba con un bucle los tres intentos de validación de la
API académica. Ambas tareas mezclaban responsabilidades secundarias con el
proceso de reservar un ejemplar.

## Observer: avisos desacoplados

El archivo `src/reservas/eventos.py` define `EventoReserva`,
`PublicadorEventos` y el contrato `ObservadorEventos`. Cada reserva genera un
evento que reciben **dos suscriptores**:

1. `ObservadorHistorial`: almacena el historial de eventos con el mismo
   formato usado en E1-E3 (`reserva_creada:<id>` y
   `reverificacion_programada:<id>`).
2. `ObservadorAvisos`: prepara mensajes de aviso para la biblioteca en memoria,
   sin hacer llamadas reales de red.

El servicio ya no genera manualmente mensajes para cada destino; publica el
evento y los observadores deciden qué hacer. Un suscriptor puede agregarse o
retirarse sin modificar el servicio, cumpliendo SRP y OCP.

## Decorator: reintentos

`src/reservas/decoradores.py` incorpora `ConReintentos`, que implementa la
misma interfaz `ValidadorMatricula` que sus objetos internos. En el servicio,
la Strategy seleccionada por la Factory queda envuelta por el Decorator, con
tres intentos de hasta un segundo cada uno.

**Se reintenta únicamente `TimeoutError`.** Un rechazo o error de integración
distinto de timeout no genera nuevos intentos. Al agotarlos, el servicio puede
recurrir al caché de 24 horas, tal como hacía en E1-E3.

## Pruebas y verificación

- `tests/test_e4.py` demuestra que ambos observadores reciben eventos, que
  puede darse de baja un suscriptor, que los avisos se emiten en una reserva
  normal y con caché, y que el Decorator reintenta solo fallos transitorios.
- Las pruebas originales se mantienen para asegurar que E4 no modifique el
  comportamiento de las reservas, incluido el orden del historial observable.
- No se añadieron conexiones a API, mensajería, bases de datos ni claves.
- Como referencia para E6, `radon cc -s -a` mostró complejidad **9 (B)** en
  `ServicioReservas.reservar_libro`, frente a **11 (C)** en E2-E3.

## Trade-off

Se añaden clases y colaboradores, pero el servicio deja de conocer los
detalles de las notificaciones y la política de reintentos. En un prototipo
que nunca tuviera avisos ni fallas externas, estos patrones podrían no
compensar su costo de mantenimiento.
