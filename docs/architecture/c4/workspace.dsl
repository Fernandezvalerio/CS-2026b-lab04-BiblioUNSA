workspace "BiblioUNSA" "Modelo C4 de la plataforma de préstamo y reserva de libros de las bibliotecas de la UNSA" {

    !identifiers hierarchical

    model {
        estudiante = person "Estudiante" "Consulta el catálogo, reserva libros y revisa sus préstamos y multas."
        bibliotecario = person "Bibliotecario" "Registra préstamos y devoluciones con el carné QR y controla las multas."

        biblio = softwareSystem "BiblioUNSA" "Permite consultar el catálogo, reservar libros, registrar préstamos y devoluciones y controlar multas en las bibliotecas de la UNSA." {

            web = container "Interfaz web responsive" "Interfaz para estudiantes (celular) y bibliotecarios (PC con lector QR)." "HTML + JavaScript" "Web Browser"

            api = container "Monolito modular BiblioUNSA" "Un solo despliegue; continuidad académica [QA-08-01], catálogo [QA-08-02] e identidad institucional [QA-08-03]." "Python / Django" {
                autenticacion = component "Módulo Autenticación y acceso" "Verifica tokens OIDC y dominio institucional con denegación segura [QA-08-03]." "Django app"
                catalogo = component "Módulo Catálogo" "Búsquedas optimizadas con índices SQL y presupuesto de p95 [QA-08-02]." "Django app"
                reservas = component "Módulo Reservas" "Reserva libros validando la matrícula vigente y reverifica las validaciones hechas con caché." "Django app"
                prestamos = component "Módulo Préstamos y devoluciones" "Registra la entrega y la devolución con carné QR y controla el ciclo de vida del préstamo." "Django app"
                multas = component "Módulo Multas" "Calcula y controla las multas por devolución tardía." "Django app"
                integracion = component "Módulo Integración académica" "Único contacto con API académica; respaldo <= 24 h, timeout 3 s y outbox [QA-08-01, QA-08-06, QA-08-07]." "Django app"
            }

            db = container "Base de datos" "PostgreSQL con módulos, índice de catálogo [QA-08-02], validaciones recientes y outbox durable [QA-08-01]." "PostgreSQL" "Database"
            cola = container "Caché y señalización rápida" "Redis acelera consultas y despierta al worker, pero PostgreSQL mantiene el estado durable [QA-08-01]." "Redis" "Queue"
            worker = container "Worker de reverificación" "Procesa pendientes persistidos y reverifica en <= 30 min [QA-08-06]." "Celery"
        }

        sa = softwareSystem "Sistema académico UNSA" "Informa si la matrícula del estudiante está vigente." "Externo"
        idp = softwareSystem "Proveedor de identidad" "Autentica con el correo institucional de la UNSA." "Externo"

        # --- Nivel 1: contexto ---
        estudiante -> biblio "Consulta el catálogo y reserva libros"
        bibliotecario -> biblio "Registra préstamos y devoluciones y controla multas"
        biblio -> sa "Consulta la matrícula vigente" "HTTPS/JSON"
        biblio -> idp "Verifica la identidad institucional" "OpenID Connect"

        # --- Nivel 2: contenedores ---
        estudiante -> biblio.web "Usa" "HTTPS"
        bibliotecario -> biblio.web "Usa" "HTTPS"
        biblio.web -> biblio.api "Llama a" "HTTPS/JSON (REST)"
        biblio.api -> biblio.db "Lee y escribe" "SQL/TCP"
        biblio.api -> biblio.cola "Lee y guarda la caché y encola tareas" "Redis protocol"
        biblio.api -> sa "Consulta la matrícula vigente" "HTTPS/JSON"
        biblio.api -> idp "Verifica la identidad institucional" "OpenID Connect"
        biblio.worker -> biblio.cola "Consume tareas" "Redis protocol"
        biblio.worker -> biblio.api "Ejecuta la reverificación" "Tarea Celery"
        biblio.worker -> biblio.db "Consulta y marca el outbox duradero [QA-08-01]" "SQL/TCP"

        # --- Nivel 3: componentes de la API ---
        biblio.web -> biblio.api.autenticacion "Inicia sesión" "HTTPS/JSON"
        biblio.web -> biblio.api.catalogo "Consulta el catálogo" "HTTPS/JSON"
        biblio.web -> biblio.api.reservas "Reserva libros" "HTTPS/JSON"
        biblio.web -> biblio.api.prestamos "Registra préstamos y devoluciones" "HTTPS/JSON"
        biblio.web -> biblio.api.multas "Consulta y cobra multas" "HTTPS/JSON"

        biblio.api.reservas -> biblio.api.integracion "Valida la matrícula vigente" "Llamada interna (Python)"
        biblio.api.reservas -> biblio.api.catalogo "Reserva el ejemplar" "Llamada interna (Python)"
        biblio.api.reservas -> biblio.api.prestamos "Crea el préstamo en estado RESERVADO" "Llamada interna (Python)"
        biblio.api.reservas -> biblio.api.autenticacion "Identifica al estudiante" "Llamada interna (Python)"
        biblio.api.prestamos -> biblio.api.catalogo "Libera el ejemplar al devolverlo" "Llamada interna (Python)"
        biblio.api.prestamos -> biblio.api.autenticacion "Identifica al estudiante" "Llamada interna (Python)"
        biblio.api.multas -> biblio.api.prestamos "Aplica la multa al préstamo" "Llamada interna (Python)"

        biblio.api.autenticacion -> idp "Verifica identidad y dominio" "OpenID Connect"
        biblio.api.integracion -> sa "Consulta la matrícula (timeout 3 s)" "HTTPS/JSON"
        biblio.api.integracion -> biblio.cola "Lee y guarda la caché de matrícula (≤ 24 h)" "Redis protocol"
        biblio.api.integracion -> biblio.db "Consulta instantáneas y pendientes duraderos [QA-08-01]" "SQL/TCP"
        biblio.api.reservas -> biblio.cola "Encola la reverificación" "Redis protocol"
        biblio.api.autenticacion -> biblio.db "Lee y escribe" "SQL/TCP"
        biblio.api.catalogo -> biblio.db "Lee y escribe" "SQL/TCP"
        biblio.api.prestamos -> biblio.db "Lee y escribe" "SQL/TCP"
        biblio.api.multas -> biblio.db "Lee y escribe" "SQL/TCP"
        biblio.worker -> biblio.api.reservas "Ejecuta reverificarPendientes()" "Tarea Celery"

        # --- Despliegue ---
        produccion = deploymentEnvironment "Producción" {
            deploymentNode "Celular o PC del usuario" "Estudiante (celular) o bibliotecario (PC con lector QR)." "Android / navegador web" {
                containerInstance biblio.web
            }
            deploymentNode "Servidor en la nube (VPS)" "Único servidor del MVP (presupuesto bajo)." "Ubuntu 24.04 · 2 vCPU · 4 GB RAM" {
                deploymentNode "Docker Compose" "Orquesta los contenedores en el VPS." "Docker" {
                    containerInstance biblio.api
                    containerInstance biblio.worker
                    containerInstance biblio.db
                    containerInstance biblio.cola
                }
            }
        }
    }

    views {

        properties {
            "c4plantuml.tags" "true"
        }
        systemContext biblio "Contexto" "Nivel 1: BiblioUNSA y su entorno." {
            include *
            autolayout lr
        }

        container biblio "Contenedores" "Nivel 2: contenedores de BiblioUNSA." {
            include *
            autolayout lr
        }

        component biblio.api "Componentes" "Nivel 3: módulos del monolito modular." {
            include *
            autolayout lr
        }

        dynamic biblio.api "ReservarLibro" "Dinámico: reservar un libro validando la matrícula vigente (historia de usuario HU-03, camino con respuesta a tiempo)." {
            biblio.web -> biblio.api.reservas "POST /reservas {ejemplarId}"
            biblio.api.reservas -> biblio.api.integracion "validar(estudianteId)"
            biblio.api.integracion -> sa "Consulta la matrícula (timeout 3 s)"
            biblio.api.integracion -> biblio.cola "Guarda el resultado en caché (≤ 24 h)"
            biblio.api.reservas -> biblio.api.catalogo "Reserva el ejemplar"
            biblio.api.reservas -> biblio.api.prestamos "Crea el préstamo en estado RESERVADO"
            autolayout lr
        }

        deployment biblio produccion "Despliegue" "Despliegue en producción (MVP en un solo VPS)." {
            include *
            autolayout lr
        }

        styles {
            element "Person" {
                shape person
                background #08427B
                color #ffffff
            }
            element "Software System" {
                background #1168BD
                color #ffffff
            }
            element "Externo" {
                background #999999
                color #ffffff
            }
            element "Container" {
                background #438DD5
                color #ffffff
            }
            element "Component" {
                background #85BBF0
                color #000000
            }
            element "Database" {
                shape cylinder
            }
            element "Queue" {
                shape pipe
            }
            element "Web Browser" {
                shape WebBrowser
            }
        }
    }
}
