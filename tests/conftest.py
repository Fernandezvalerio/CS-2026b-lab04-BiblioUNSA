"""Permite ejecutar pytest desde la raíz sin instalar el proyecto."""

import sys
from pathlib import Path

RAIZ_SRC = Path(__file__).resolve().parents[1] / "src"
if str(RAIZ_SRC) not in sys.path:
    sys.path.insert(0, str(RAIZ_SRC))
