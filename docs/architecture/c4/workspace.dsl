workspace "BiblioUNSA" "Modelo C4 de la plataforma de préstamo y reserva de libros de las bibliotecas de la UNSA" {

    !identifiers hierarchical

    model {
        estudiante = person "Estudiante" "Consulta el catálogo, reserva libros y revisa sus préstamos y multas."
        bibliotecario = person "Bibliotecario" "Registra préstamos y devoluciones con el carné QR y controla las multas."

        biblio = softwareSystem "BiblioUNSA" "Permite consultar el catálogo, reservar libros, registrar préstamos y devoluciones y controlar multas en las bibliotecas de la UNSA."

        sa = softwareSystem "Sistema académico UNSA" "Informa si la matrícula del estudiante está vigente." "Externo"
        idp = softwareSystem "Proveedor de identidad" "Autentica con el correo institucional de la UNSA." "Externo"

        # --- Nivel 1: contexto ---
        estudiante -> biblio "Consulta el catálogo y reserva libros"
        bibliotecario -> biblio "Registra préstamos y devoluciones y controla multas"
        biblio -> sa "Consulta la matrícula vigente" "HTTPS/JSON"
        biblio -> idp "Verifica la identidad institucional" "OpenID Connect"
    }

    views {

        systemContext biblio "Contexto" "Nivel 1: BiblioUNSA y su entorno." {
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
        }
    }
}
