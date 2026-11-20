"""E7: regresión posterior al experimento; comprueba un caso omitido en E5."""
from types import SimpleNamespace
from uuid import uuid4

import pytest

from reservas.validadores import AdaptadorMatriculaJSON, IntegracionException


@pytest.mark.parametrize("respuesta", [None, []], ids=["nula", "lista"])
def test_respuesta_academica_no_diccionario(respuesta):
    cliente = SimpleNamespace(consultar_matricula=lambda *args, **kwargs: respuesta)
    with pytest.raises(IntegracionException):
        AdaptadorMatriculaJSON(cliente).validar(uuid4())
