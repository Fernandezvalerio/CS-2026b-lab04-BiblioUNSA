workspace "BiblioUNSA" "Modelo C4 de la plataforma de préstamo y reserva de libros de las bibliotecas de la UNSA" {

    !identifiers hierarchical

    model {
        estudiante = person "Estudiante" "Consulta el catálogo, reserva libros y revisa sus préstamos y multas."
        bibliotecario = person "Bibliotecario" "Registra préstamos y devoluciones con el carné QR y controla las multas."

        biblio = softwareSystem "BiblioUNSA" "Permite consultar el catálogo, reservar libros, registrar préstamos y devoluciones y controlar multas en las bibliotecas de la UNSA." {

            web = container "Interfaz web responsive" "Interfaz para estudiantes (celular) y bibliotecarios (PC con lector QR)." "HTML + JavaScript" "Web Browser"

            api = container "Monolito modular BiblioUNSA" "Un solo despliegue con seis módulos de dominio; expone la API REST que consume la interfaz web." "Python / Django"

            db = container "Base de datos" "Usuarios, catálogo, préstamos y multas (un esquema por módulo)." "PostgreSQL" "Database"
            cola = container "Caché y cola de tareas" "Guarda la última validación de matrícula y las tareas de reverificación." "Redis" "Queue"
            worker = container "Worker de reverificación" "Reverifica en ≤ 30 min las matrículas validadas con caché." "Celery"
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
