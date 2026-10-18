# Inventario de elementos C4 — BiblioUNSA (Laboratorio 06)

Cada elemento del modelo `workspace.dsl` sale de lo ya construido en los Laboratorios 04 y 05. Si un elemento no tiene origen, no entra al modelo.

## 1. Elementos del modelo

| Elemento | Tipo C4 | Origen |
|----------|---------|--------|
| Estudiante | Persona | `drivers.md` (RF-01, RF-02, RF-03, RF-07); README del Lab 04 |
| Bibliotecario | Persona | `drivers.md` (RF-04, RF-06); README del Lab 04 |
| BiblioUNSA | Sistema de software | Caso del Lab 04; ADR-001 |
| Sistema académico UNSA | Sistema externo | `drivers.md` (RF-05, R-05); ADR-003 |
| Proveedor de identidad (correo institucional) | Sistema externo | `drivers.md` (RF-01, R-06); ADR-002 |
| Interfaz web responsive | Contenedor | ADR-001 ("API REST + web responsive"); `despliegue.py` (celular y PC del bibliotecario) |
| Monolito modular BiblioUNSA | Contenedor | ADR-001 (un solo despliegue, seis módulos); `despliegue.py` ("Django API") |
| Base de datos | Contenedor | ADR-001 (PostgreSQL, un esquema por módulo); `despliegue.py` |
| Redis (caché de matrícula y cola) | Contenedor | ADR-003 (caché de ≤ 24 h y reintentos); `despliegue.py` |
| Worker de reverificación | Contenedor | ADR-003 (reverificar en ≤ 30 min); `despliegue.py` ("Celery") |
| Autenticación y acceso | Componente (del monolito) | ADR-001 y ADR-002; paquete `autenticacion` en `paquetes.puml` |
| Catálogo | Componente | ADR-001; paquete `catalogo` |
| Reservas | Componente | ADR-001; paquete `reservas`; `secuencia-reservar-libro.puml` (`ServicioReservas`) |
| Préstamos y devoluciones | Componente | ADR-001; paquete `prestamos` |
| Multas | Componente | ADR-001; paquete `multas` |
| Integración académica | Componente | ADR-001 y ADR-003; paquete `integracion` |
| Reservar un libro validando la matrícula (HU-03) | Vista dinámica | `secuencia-reservar-libro.puml` (Lab 05) |
| Celular o PC del usuario | Nodo de despliegue | `despliegue.py` (celular y PC del bibliotecario) |
| Servidor en la nube (VPS) y Docker Compose | Nodos de despliegue | R-03 (presupuesto: un solo VPS); `despliegue.py` |

## 2. Decisiones de modelado

- **Paquete `compartido` no se modela.** En `paquetes.puml` es un núcleo de utilidades del que dependen todos los módulos. Dibujarlo añadiría seis flechas sin aportar valor al nivel 3. No cambia la regla de ausencia de ciclos.
- **"Contenedor" en C4 no es Docker.** Docker Compose aparece solo como nodo de la vista de despliegue.
- **Los reintentos de matrícula los ejecuta el Worker** invocando `reverificarPendientes()` del componente Reservas (así lo define `paquetes.puml`: `prestamos` no depende de `integracion`). El worker llega al sistema académico únicamente a través del componente Integración académica, porque ADR-003 lo declara el único punto de contacto.
- **Nginx, Prometheus y Grafana (que aparecen en `despliegue.py`) no se modelan:** ningún ADR los fija y no son contenedores del sistema; si el equipo los mantiene, se agregarían como `infrastructureNode` en la vista de despliegue.
- **Notificaciones, correo y WhatsApp no se modelan:** no figuran en los drivers ni en los ADR.
- **No se incluyen versiones de tecnología** (por ejemplo, "PostgreSQL 16") porque ningún ADR las fija.

## 3. Supuestos pendientes de verificar

| Supuesto | Dónde aparece | Cómo se verifica |
|----------|---------------|------------------|
| VPS Ubuntu 24.04, 2 vCPU, 4 GB RAM | Vista de despliegue | Cotizar un VPS dentro del presupuesto de R-03 |
| El proveedor de identidad ofrece OAuth 2.0 / OIDC | Relación Autenticación → Proveedor de identidad | Confirmar con la oficina responsable de la UNSA (ADR-002, R-06) |
| La API del sistema académico es HTTPS/JSON | Relación Integración → Sistema académico | Confirmar con la oficina responsable (ADR-003) |
