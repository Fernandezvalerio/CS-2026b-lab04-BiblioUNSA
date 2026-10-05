# Drivers arquitectónicos — BiblioUNSA

## 1. Requisitos funcionales clave
| ID    | Requisito                                                              | Actor                    | Prioridad |
|-------|------------------------------------------------------------------------|--------------------------|-----------|
| RF-01 | Iniciar sesión con el correo institucional                             | Estudiante, Bibliotecario| Alta      |
| RF-02 | Consultar el catálogo en línea (búsqueda por título, autor, biblioteca)| Estudiante               | Alta      |
| RF-03 | Reservar libros disponibles                                            | Estudiante               | Alta      |
| RF-04 | Registrar préstamos y devoluciones escaneando el carné QR              | Bibliotecario            | Alta      |
| RF-05 | Validar matrícula vigente consultando al sistema académico (por API)   | Sistema académico        | Alta      |
| RF-06 | Calcular y controlar multas por devolución tardía                      | Bibliotecario            | Media     |
| RF-07 | Consultar mis préstamos, reservas y multas                             | Estudiante               | Media     |

## 2. Atributos de calidad (ordenados por prioridad)
1. **Seguridad e interoperabilidad** — Es el atributo crítico: solo debe entrar personal y estudiantes de la UNSA, y el acceso al sistema académico debe ser únicamente por API, sin tocar su base de datos.
2. **Fiabilidad (tolerancia a fallas externas)** — La biblioteca debe seguir atendiendo aunque el sistema académico o el proveedor de identidad fallen temporalmente.
3. **Modificabilidad** — El contrato de la API académica o las reglas de multas pueden cambiar sin que se deba reescribir el sistema.
4. **Capacidad de interacción** — El estudiante y el bibliotecario deben completar reserva y préstamo en pocos pasos, desde celular o PC de la biblioteca.
5. **Eficiencia de desempeño** — Al inicio del semestre muchos estudiantes consultan el catálogo a la vez.

## 3. Restricciones
| ID   | Tipo         | Restricción                                                                              |
|------|--------------|------------------------------------------------------------------------------------------|
| R-01 | Plazo        | MVP en producción en 1 mes                                                               |
| R-02 | Equipo       | 3 developers con experiencia en Python/Django, PostgreSQL y Git (ajustar al equipo real) |
| R-03 | Presupuesto  | Bajo: un solo servidor (VPS) o hosting gratuito/estudiantil; sin servicios de pago       |
| R-04 | Normativa    | Ley 29733 de protección de datos personales (datos de estudiantes)                       |
| R-05 | Tecnología   | Acceso al sistema académico solo mediante su API; prohibido el acceso directo a su BD    |
| R-06 | Tecnología   | Autenticación solo con correo institucional (⚠️ verificar el proveedor: OAuth/OIDC)      |

## 4. Escenarios de atributos de calidad
| ID    | Atributo                 | Fuente                          | Estímulo                                                | Entorno                              | Artefacto                    | Respuesta                                                                 | Medida                                                                 |
|-------|--------------------------|---------------------------------|---------------------------------------------------------|--------------------------------------|------------------------------|---------------------------------------------------------------------------|------------------------------------------------------------------------|
| QA-01 | Seguridad (crítico)      | Persona con correo ajeno a la UNSA | Intenta iniciar sesión y reservar un libro           | Operación normal en producción       | Módulo de Autenticación      | Rechaza el acceso, no crea sesión y registra el intento                   | 100 % de 30 intentos de prueba rechazados; 0 conexiones a la BD académica |
| QA-02 | Fiabilidad / interoperabilidad | El sistema académico no responde | El bibliotecario registra un préstamo y se valida la matrícula | Horario de atención, operación normal | Módulo de Integración académica | Usa la última validación en caché y marca el préstamo para reverificar | Timeout ≤ 3 s; 0 préstamos bloqueados con caché ≤ 24 h; reverificación ≤ 30 min |
| QA-03 | Modificabilidad          | La UNSA publica una nueva versión de la API académica | El equipo debe adaptar la integración           | Desarrollo                           | Módulo de Integración académica | Se cambia solo el adaptador, sin tocar Catálogo, Reservas ni Préstamos | ≤ 2 días-persona; 0 módulos adicionales modificados                    |
