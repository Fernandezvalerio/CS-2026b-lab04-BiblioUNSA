\# Historia de usuario — BiblioUNSA (Lab 05, E1)



\*\*HU-03 (RF-03 + RF-05):\*\* Como estudiante de la UNSA, quiero reservar un libro disponible

de una biblioteca, para que me lo aparten hasta recogerlo y no ir a ciegas.



\## Criterios de aceptación



1\. \*\*Reserva exitosa\*\*

&#x20;  - Dado un estudiante con matrícula vigente y un ejemplar disponible,

&#x20;  - cuando reserva el libro,

&#x20;  - entonces se crea un préstamo en estado RESERVADO y el ejemplar deja de estar disponible.



2\. \*\*Matrícula no vigente\*\*

&#x20;  - Dado un estudiante cuya matrícula no está vigente según el sistema académico,

&#x20;  - cuando intenta reservar un libro,

&#x20;  - entonces se rechaza la reserva con un mensaje claro, no se crea el préstamo y el ejemplar sigue disponible.



3\. \*\*Sistema académico sin respuesta (QA-02)\*\*

&#x20;  - Dado que el sistema académico no responde en 3 s y existe una validación en caché de hasta 24 h con matrícula vigente,

&#x20;  - cuando el estudiante reserva un libro,

&#x20;  - entonces la reserva se crea marcada para reverificación (≤ 30 min) y no se bloquea al estudiante.

&#x20;  - Si no existe una validación en caché reciente, la reserva se rechaza con el mensaje "intente nuevamente en unos minutos".



4\. \*\*Ejemplar no disponible\*\*

&#x20;  - Dado un ejemplar que ya está reservado o prestado,

&#x20;  - cuando otro estudiante intenta reservarlo,

&#x20;  - entonces se rechaza la reserva y se informa que el ejemplar no está disponible.



\## Trazabilidad

\- Requisitos: RF-03 (reservar), RF-05 (validar matrícula por API).

\- Escenarios de calidad: QA-02 (tolerancia a fallas del sistema académico), QA-03 (el contrato externo queda en un adaptador).

\- Decisiones: ADR-001 (monolito modular, puertos y adaptadores), ADR-003 (adaptador con caché).

\- Módulos involucrados: Reservas, Préstamos y devoluciones, Catálogo, Integración académica.

