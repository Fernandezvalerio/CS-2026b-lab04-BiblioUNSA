# ADR-003: Integrar el sistema académico mediante un adaptador con caché

- Estado: Aceptado
- Fecha: 2026-10-03
- Decisores: Mauricio Antonio Paredes Miranda, Mijael Paul León Ramos, Valerio Piero Fernández Lastarria

## Contexto
La validación de matrícula vigente (RF-05) debe hacerse solo por la API del sistema académico, sin acceso a su base de datos (R-05). El escenario QA-02 exige seguir prestando libros cuando ese sistema no responde (timeout ≤ 3 s, 0 préstamos bloqueados con caché ≤ 24 h, reverificación ≤ 30 min) y QA-03 exige adaptar la integración en ≤ 2 días-persona si la API cambia. No hay evidencia confirmada de que la API sea pública y documentada, por lo que el contrato puede variar (R-02, R-01).

## Alternativas consideradas
1. Consulta síncrona directa a la API en cada préstamo, sin caché ni aislamiento. Es la más simple, pero cualquier caída del sistema académico detiene los préstamos y el código de la API queda disperso en varios módulos.
2. Módulo de Integración académica con adaptador y caché de la última validación. Aísla el contrato externo y permite continuar con un resultado reciente.

## Decisión
Usaremos la alternativa 2: el módulo de Integración académica será el único punto de contacto con el sistema académico. Aplicará un timeout de 3 s, guardará en caché solo el resultado mínimo necesario (estado de matrícula y fecha de consulta) durante un máximo de 24 h, marcará el préstamo para reverificación cuando use un dato en caché y reintentará en ≤ 30 min. Los demás módulos dependerán de una interfaz propia, no de la API externa.

## Consecuencias
- Positivas: el sistema tolera caídas externas (QA-02); un cambio de la API solo afecta al adaptador (QA-03); se cumple R-05; guardar solo el estado de matrícula limita el tratamiento de datos personales (R-04).
- Negativas / riesgos: un estudiante podría tener un préstamo aprobado con una matrícula que ya venció dentro de la ventana de 24 h (se mitiga con la reverificación); se necesita un mecanismo de reintentos y una caché que operar; el contrato real de la API aún debe confirmarse con la oficina responsable.
