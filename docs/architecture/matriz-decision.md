# Matriz de decisión — BiblioUNSA

## Alternativas
- **A. Monolito en capas:** una sola aplicación con capas de presentación, lógica de negocio y acceso a datos. Un solo despliegue y una sola base de datos compartida; es la opción más simple de construir.
- **B. Monolito modular:** un solo despliegue dividido en módulos de dominio (Autenticación, Catálogo, Reservas, Préstamos, Multas, Integración académica) con interfaces explícitas. La integración con el sistema académico queda aislada en un adaptador.
- **C. Microservicios:** servicios independientes (Catálogo, Reservas/Préstamos, Multas, Integración académica) detrás de un API Gateway, cada uno con su base de datos y comunicados por un broker de eventos.

## Criterios y pesos (deben sumar 100 %)
| Criterio                        | Peso | Justificación (driver relacionado)                                         |
|---------------------------------|------|----------------------------------------------------------------------------|
| Tiempo de entrega               | 25 % | R-01: el MVP debe salir en 1 mes                                           |
| Seguridad e interoperabilidad   | 25 % | QA-01, QA-02, R-05: es el atributo crítico del caso                        |
| Costo operativo                 | 20 % | R-03: presupuesto bajo, un solo servidor                                   |
| Modificabilidad                 | 15 % | QA-03: la API académica y las reglas de multas pueden cambiar              |
| Simplicidad operativa           | 15 % | R-02: equipo de 3 developers sin experiencia en DevOps                     |
| **Total**                       | **100 %** |                                                                       |

## Matriz (puntaje 1 = muy malo … 5 = excelente)
| Criterio (peso)                       | A. Capas | B. Monolito modular | C. Microservicios |
|---------------------------------------|----------|---------------------|-------------------|
| Tiempo de entrega (25 %)              | 5        | 4                   | 2                 |
| Seguridad e interoperabilidad (25 %)  | 3        | 4                   | 4                 |
| Costo operativo (20 %)                | 5        | 5                   | 2                 |
| Modificabilidad (15 %)                | 2        | 4                   | 5                 |
| Simplicidad operativa (15 %)          | 5        | 4                   | 1                 |
| **Total ponderado**                   | **4,05** | **4,20**            | **2,80**          |

Total ponderado = Σ (peso × puntaje).
- A: 0,25×5 + 0,25×3 + 0,20×5 + 0,15×2 + 0,15×5 = 1,25 + 0,75 + 1,00 + 0,30 + 0,75 = **4,05**
- B: 0,25×4 + 0,25×4 + 0,20×5 + 0,15×4 + 0,15×4 = 1,00 + 1,00 + 1,00 + 0,60 + 0,60 = **4,20**
- C: 0,25×2 + 0,25×4 + 0,20×2 + 0,15×5 + 0,15×1 = 0,50 + 1,00 + 0,40 + 0,75 + 0,15 = **2,80**

Justificación de puntajes clave:
- Seguridad e interoperabilidad: en capas (3) el acceso externo queda disperso por toda la lógica; en el monolito modular (4) y en microservicios (4) la integración académica se aísla en un adaptador/servicio único con un solo punto de control.
- Modificabilidad: en capas (2) los módulos quedan acoplados; en microservicios (5) cada servicio cambia de forma independiente.

## Conclusión
Elegimos el **monolito modular (4,20)** porque cumple el plazo de 1 mes (R-01), cabe en un solo servidor (R-03), lo puede operar un equipo de 3 developers (R-02) y permite aislar la integración con el sistema académico en un adaptador (QA-01, QA-02, QA-03, R-05). La segunda mejor alternativa fue el monolito en capas (4,05), con una diferencia pequeña; se descartó porque acopla los módulos y dificulta el cambio del adaptador académico (QA-03). Los microservicios (2,80) exceden la capacidad operativa del equipo. Ver [ADR-001](adr/001-estilo-arquitectonico.md).

## Afirmación incorrecta de la IA y verificación
La IA afirmó que el sistema académico de la UNSA expone una API REST pública y documentada lista para consumir. No hay evidencia de ello: lo verificamos preguntando a la oficina responsable del sistema académico. Por eso la arquitectura aísla la integración en un adaptador reemplazable y usa caché (QA-02).
