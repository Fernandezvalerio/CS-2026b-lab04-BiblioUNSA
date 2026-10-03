# ADR-002: Autenticar con el correo institucional mediante un proveedor de identidad externo

- Estado: Aceptado
- Fecha: 2026-10-03
- Decisores: Mauricio Antonio Paredes Miranda, Mijael Paul León Ramos, Valerio Piero Fernández Lastarria

## Contexto
Solo pueden ingresar estudiantes y personal de la UNSA (RF-01, R-06). El escenario QA-01 exige rechazar el 100 % de los intentos con correos ajenos a la institución y registrar cada intento. Además, la Ley 29733 (R-04) limita el manejo de datos personales y el equipo no tiene capacidad para operar un sistema de credenciales propio (R-02, R-01).

## Alternativas consideradas
1. Delegar el inicio de sesión en el proveedor del correo institucional mediante OAuth 2.0 / OpenID Connect, y validar en el servidor el dominio y la identidad devueltos. Requiere confirmar que la UNSA permite registrar la aplicación (por verificar).
2. Cuentas propias en BiblioUNSA (usuario y contraseña) con verificación del correo institucional por enlace. No depende de terceros, pero obliga a guardar contraseñas y a gestionar su recuperación.

## Decisión
Usaremos el inicio de sesión delegado (alternativa 1) con OAuth 2.0 / OpenID Connect, encapsulado en el módulo de Autenticación y acceso y accedido a través de un adaptador. Si la verificación con la UNSA muestra que no es posible, aplicaremos la alternativa 2 como plan de contingencia sin cambiar los demás módulos. El servidor rechazará cualquier identidad cuyo dominio no sea institucional y registrará el intento (QA-01).

## Consecuencias
- Positivas: BiblioUNSA no almacena contraseñas, lo que reduce el riesgo de seguridad y la exposición de datos personales (R-04); la implementación es corta y encaja en el plazo (R-01); el adaptador permite cambiar de proveedor sin tocar el resto (QA-03).
- Negativas / riesgos: depende de que la UNSA permita registrar la aplicación y de la disponibilidad del proveedor; si este falla, nadie puede iniciar sesión nueva (se mitiga con sesiones vigentes y mensaje claro al usuario).
