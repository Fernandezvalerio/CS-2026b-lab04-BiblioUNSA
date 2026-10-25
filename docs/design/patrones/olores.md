# Lab 07 - E1: olores de código de BiblioUNSA

## Flujo analizado

Se revisó **HU-03: reservar un libro validando la matrícula vigente**, descrito en
`docs/design/secuencia-reservar-libro.puml`. La versión inicial está en
`src/reservas/antes/servicio.py`. Se mantienen los dobles de las APIs académicas
en `src/reservas/externos.py` y las entidades originales del Lab 05 en
`src/reservas/dominio.py`.

## Interacción con IA (Prompt IA 1)

**Solicitud:** "Actúa como revisor de código experto en refactorización y patrones
GoF. Analiza `antes/servicio.py`, el dominio de BiblioUNSA y la medición de
radon. Identifica olores concretos con ubicación, patrón propuesto, principio
SOLID que mejoraría y costo de aplicarlo. No escribas código ni propongas
patrones sin una necesidad real. No uses Singleton".

**Resultado:** Se propusieron los siguientes cambios. Se contrastaron con las
reglas de HU-03, el diagrama del Lab 05 y el ADR-003.

| Ubicación aproximada | Olor detectado | Patrón GoF propuesto | Principio SOLID | Decisión y costo |
|---|---|---|---|---|
| `antes/servicio.py:62-91` | Condicionales para distinguir dos contratos académicos. Cada contrato adicional obliga a editar el servicio. | **Strategy + Factory** | **O** (abierto/cerrado) | **Aceptar para E2**. Agrega un registro de estrategias y una implementación por contrato. |
| `antes/servicio.py:68-90` | El flujo de reservas sabe que un proveedor responde con diccionario y otro con tupla y código HTTP. | **Adapter** | **D** (inversión de dependencias) | **Aceptar para E2**. Hay que mantener adaptadores, pero se aísla el formato externo. |
| `antes/servicio.py:66-95` | El mismo método administra intentos, timeouts y la reserva. | **Decorator** para reintentos | **S** (responsabilidad única) | **Aceptar para E4**. Introduce un envoltorio, a cambio de evitar mezclar fallos de integración con reglas de reserva. |
| `antes/servicio.py:96-107` | Caducidad de caché, recuperación ante fallas y validación aparecen dentro del caso de uso. | **Proxy** o **Decorator** para la lectura con caché | **S** | **Evaluar en E4**, sin crear ambos patrones si uno basta. Su costo es una clase adicional y pruebas del límite de 24 h. |
| `antes/servicio.py:123-130` | El servicio genera y almacena a mano eventos de reserva y reverificación. | **Observer** | **S** y **O** | **Aceptar para E4** si aparecen suscriptores reales. Costará definir eventos y al menos dos suscriptores comprobables. |
| `dominio.py:74-101` | Los cambios de `Prestamo` dependen de comprobaciones de su enumeración de estado. | **State** | **O** y **L** (sustitución) | **Aceptar para E3**, usando la máquina de estados `estados-prestamo.mmd`. Aumenta el número de clases, pero concentra transiciones válidas. |
| `antes/servicio.py:44-56` | El servicio recibe dos colaboradores, pero no hay necesidad de una familia de objetos relacionados. | **Abstract Factory** (sugerencia examinada) | **D** (teórico) | **Rechazar**: no hay familias de productos ni un olor que la exija. Un registro Factory sencillo bastará; Abstract Factory añadiría clases sin beneficio. |

