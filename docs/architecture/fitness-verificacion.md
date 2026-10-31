# E5 - Fitness functions y prueba de violación

La CI corre en Pull Requests y pushes. El proyecto sigue siendo un prototipo de reservas del Lab 07; sus pruebas no equivalen a una prueba de carga HTTP real de Django.

| Fitness function | Tipo | Archivo | Qué evita |
|---|---|---|---|
| FF-01 | Estructural | .importlinter + fitness/estructura.py | Dominio importando casos de uso o integraciones externas |
| FF-02 | Estructural | .importlinter + fitness/estructura.py | Adaptadores y Decorator importando el servicio orquestador |
| FF-03 | Calidad | tests/test_fitness.py | Dejar bloqueadas reservas con caché reciente ante caída externa |
| FF-04 | Calidad | tests/test_fitness.py | Superar p95=1500 ms en la hipótesis de 24 req/s |
| FF-05 | Calidad | tests/test_fitness.py | Autorizar identidades externas o tokens sin verificar |

## Comandos de verificación

1. Instalar: python -m pip install -r requirements-lab08.txt
2. Estructura: PYTHONPATH=src lint-imports (en PowerShell: configurar antes PYTHONPATH=src).
3. Calidad y regresión: python -m pytest -q tests/
4. Alternativa local sin pytest: python tests/test_fitness.py

## Violación deliberada que debe fallar

La prueba test_demostracion_detecta_violacion_controlada alimenta la regla FF-02 con una importación inválida y exige que se detecte. Para cumplir además la comprobación de una rama en GitHub:

1. Crear rama temporal demo/violacion-ff02 desde el commit E5.
2. Agregar temporalmente al principio de src/reservas/validadores.py: from reservas.servicio import ServicioReservas
3. Ejecutar PYTHONPATH=src lint-imports; debe aparecer FF-02 BROKEN.
4. Deshacer la línea y no integrar la rama defectuosa. Guardar captura o enlace del workflow fallido.

**Estado de evidencia externa:** no se puede declarar workflow verde ni rama de demostración en GitHub hasta que el grupo lo ejecute en su repositorio remoto. El script AST tiene una violación sintética comprobable, pero eso no sustituye el issue y el run de GitHub.
