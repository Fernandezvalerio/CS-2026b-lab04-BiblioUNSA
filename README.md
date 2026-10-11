# BiblioUNSA — Laboratorio 04: Fundamentos de arquitectura de software
Construcción de Software · EPIS-UNSA · 2026-B · Grupo 04
 
## Integrantes
| Nombre | Rol en el laboratorio |
|--------|-----------------------|
| Valerio | Analista de drivers y responsable de la matriz de decisión |
| Mijael | Diagramador y redactor de ADR |
| Mauricio | Verificador de IA y responsable de documentación adicional |
 
## Caso
BiblioUNSA es una plataforma para el préstamo y la reserva de libros de las bibliotecas de la UNSA. Los estudiantes consultan el catálogo y reservan libros, y los bibliotecarios registran préstamos y devoluciones con el carné QR y controlan las multas. El sistema valida la matrícula vigente consultando al sistema académico solo mediante su API, sin acceder a su base de datos. El atributo de calidad crítico es la **seguridad e interoperabilidad**: únicamente debe entrar personal y estudiantes de la UNSA con su correo institucional.
 
## Arquitectura elegida
Monolito modular: un solo despliegue, con módulos separados y la integración académica aislada en un adaptador.

```mermaid
flowchart TB
    ES["Estudiante"]
    BI["Bibliotecario"]
    subgraph APP["BiblioUNSA — Monolito modular (un solo despliegue)"]
        API["Capa de presentación: API REST + web responsive"]
        M1["Autenticación<br/>y acceso"]
        M2["Catálogo"]
        M3["Reservas"]
        M4["Préstamos y<br/>devoluciones (QR)"]
        M5["Multas"]
        M6["Integración<br/>académica"]
        INF["Capa de infraestructura: repositorios y adaptadores externos"]
    end
    DB[("PostgreSQL<br/>(un esquema por módulo)")]
    IDP["Proveedor de identidad<br/>(correo institucional)"]
    SA["Sistema académico UNSA<br/>(API)"]
    ES & BI --> API
    API --> M1 & M2 & M3 & M4 & M5
    M3 & M4 --> M6
    M1 & M2 & M3 & M4 & M5 & M6 --> INF
    INF --> DB
    INF --> IDP
    INF --> SA
    classDef mod fill:#E8F5E9,stroke:#2E7D32,color:#000
    classDef ext fill:#F2F2F2,stroke:#7F7F7F,color:#000,stroke-dasharray: 4 3
    classDef usr fill:#FDEDEC,stroke:#C8310E,color:#000
    class M1,M2,M3,M4,M5,M6 mod
    class IDP,SA ext
    class ES,BI usr
```

## Decisiones arquitectónicas
- [ADR-001: Estilo arquitectónico](docs/architecture/adr/001-estilo-arquitectonico.md)
- [ADR-002: Autenticación](docs/architecture/adr/002-autenticacion.md)
- [ADR-003: Integración Académica](docs/architecture/adr/003-integracion-academica.md)

## Reflexión sobre el uso de la IA (5–8 líneas)
La IA (Claude) nos ayudó a generar alternativas de estilo, redactar el borrador de los drivers y escenarios de calidad, puntuar la matriz de decisión y escribir el código Mermaid del diagrama. También cometió errores: recomendó microservicios, que no encajan con el plazo de 1 mes, los 3 developers ni el presupuesto de un VPS, y afirmó sin evidencia que el sistema académico de la UNSA tiene una API REST pública y documentada. Además, propuso un proveedor de identidad OAuth/OIDC que aún no está confirmado. Aprendimos a contrastar cada recomendación con nuestras restricciones, a recalcular a mano los totales de la matriz, a validar el diagrama en mermaid.live y GitHub, y a confirmar con la oficina responsable cualquier afirmación sobre sistemas reales. Por eso aislamos la integración en un adaptador con caché. La IA propone, pero el equipo decide y verifica; todo quedó registrado en la [bitácora](docs/architecture/bitacora-ia.md).

## Diseño UML (Lab 05)
Diseño detallado de la historia **HU-03: reservar un libro validando la matrícula vigente**, escrito como código (PlantUML y Mermaid), coherente con el ADR-001 y el ADR-003. La IA propuso los diagramas y el equipo los revisó con las reglas de consistencia C1–C5; todo quedó en la [bitácora de IA del Lab 05](docs/design/bitacora-ia.md).

### Máquina de estados del préstamo
Cada transición se nombra con una operación de la clase `Prestamo` (regla C2) y los estados coinciden con la enumeración `EstadoPrestamo`.

```mermaid
stateDiagram-v2
    [*] --> RESERVADO : Prestamo() [matrícula vigente y ejemplar disponible]
    RESERVADO --> RESERVADO : marcarParaReverificacion() [validación proveniente de caché]
    RESERVADO --> PRESTADO : entregar() [estudiante recoge el libro con carné QR]
    PRESTADO --> DEVUELTO : registrarDevolucion(fecha) [fecha <= fechaVencimiento]
    PRESTADO --> VENCIDO : marcarVencido() [hoy > fechaVencimiento]
    VENCIDO --> CON_MULTA : registrarDevolucion(fecha) / aplicarMulta(monto) [fecha > fechaVencimiento]
    DEVUELTO --> [*]
    CON_MULTA --> [*] : multa pagada (módulo Multas)
    note right of RESERVADO
        requiereReverificacion = true
        si la matrícula vino de caché
        (reverificar en ≤ 30 min, ADR-003)
    end note
    note right of CON_MULTA
        montoMulta > 0
    end note
```

### Diagramas y documentos
| Entregable | Fuente | Imagen |
|------------|--------|--------|
| E1 Historia de usuario | [historia.md](docs/design/historia.md) | — |
| E1 Diagrama de clases | [clases.puml](docs/design/clases.puml) | [PNG](docs/design/img/diagrama_clases.png) |
| E2 Diagrama de secuencia | [secuencia-reservar-libro.puml](docs/design/secuencia-reservar-libro.puml) | [PNG](docs/design/img/secuencia-reservar-libro.png) |
| E3 Máquina de estados | [estados-prestamo.mmd](docs/design/estados-prestamo.mmd) | [PNG](docs/design/img/estados-prestamo.png) |
| E4 Diagrama de actividades | [actividades-devolucion-multa.puml](docs/design/actividades-devolucion-multa.puml) | [PNG](docs/design/img/actividades-devolucion-multa.png) |
| E5 Diagrama de paquetes | [paquetes.puml](docs/design/paquetes.puml) | [PNG](docs/design/img/paquetes.png) |
| E6 Round-trip | [round-trip.md](docs/design/round-trip.md) · [dominio.py](src/reservas/dominio.py) | [PNG](docs/design/img/classes_reservas.png) |
| E7 Consistencia C1–C5 | [consistencia.md](docs/design/consistencia.md) | — |
| E7 Bitácora de IA (Lab 05) | [bitacora-ia.md](docs/design/bitacora-ia.md) | — |
