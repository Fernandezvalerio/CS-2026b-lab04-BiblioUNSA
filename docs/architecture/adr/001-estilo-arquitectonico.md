# ADR-001: Adoptar un monolito modular para el MVP de BiblioUNSA

- Estado: Aceptado
- Fecha: 2026-10-03
- Decisores: Mauricio Antonio Paredes Miranda, Mijael Paul León Ramos, Valerio Piero Fernández Lastarria

## Contexto
BiblioUNSA debe salir a producción en 1 mes (R-01) con un equipo de 3 developers (R-02) y un solo servidor o hosting estudiantil (R-03). El atributo crítico es la seguridad e interoperabilidad (QA-01): solo accede personal y estudiantes de la UNSA, y el sistema académico se consulta únicamente por API (R-05). Además, la integración académica debe tolerar fallas externas (QA-02) y poder cambiar sin tocar los demás módulos (QA-03). Los requisitos funcionales abarcan autenticación, catálogo, reservas, préstamos con QR, multas y validación de matrícula (RF-01 a RF-07).

## Alternativas consideradas
1. Monolito en capas (4,05): el más simple y rápido de construir, pero los módulos quedan acoplados y el acceso al sistema académico se dispersa por la lógica de negocio, lo que dificulta QA-03.
2. Monolito modular (4,20): un solo despliegue con módulos de dominio e interfaces explícitas; la integración académica queda aislada en un adaptador.
3. Microservicios (2,80): máxima independencia, pero exige varios despliegues, bases de datos y un broker, lo cual excede R-01, R-02 y R-03.

## Decisión
Usaremos un monolito modular con seis módulos (Autenticación y acceso, Catálogo, Reservas, Préstamos y devoluciones, Multas, Integración académica). Los módulos se comunican solo mediante interfaces públicas, comparten un único despliegue y una base PostgreSQL con un esquema por módulo. Las conexiones externas (proveedor de identidad y sistema académico) se implementan como adaptadores en la capa de infraestructura. Ver [matriz de decisión](../matriz-decision.md).

## Consecuencias
- Positivas: cumple el plazo de 1 mes (R-01); cabe en un solo servidor (R-03); es operable por 3 developers (R-02); el adaptador académico permite cumplir QA-02 y QA-03 y respetar R-05; los módulos podrían extraerse a servicios más adelante si la carga lo exige.
- Negativas / riesgos: el equipo debe respetar los límites entre módulos (se propone una verificación automática de importaciones en la CI); una falla grave afecta a todo el sistema porque hay un solo despliegue; cualquier cambio obliga a redesplegar todo.
