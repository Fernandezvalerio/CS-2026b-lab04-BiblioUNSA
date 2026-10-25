"""Pruebas de la integración de IA simulada, caché y guardrails (E5)."""

import pytest

from reservas.dominio import Libro
from reservas.externos import MotorTextoSimulado
from reservas.ia import (
    AdaptadorMotorSimulado,
    ConCacheLLM,
    ProveedorLLM,
    RecomendadorLibros,
    RespuestaLLMInvalida,
)


def catalogo():
    return [
        Libro(titulo="Algoritmos", autor="Autor A", isbn="ISBN-A"),
        Libro(titulo="Estructuras de datos", autor="Autor B", isbn="ISBN-B"),
        Libro(titulo="Programación en Python", autor="Autor C", isbn="ISBN-C"),
        Libro(titulo="Bases de datos", autor="Autor D", isbn="ISBN-D"),
        Libro(titulo="Redes", autor="Autor E", isbn="ISBN-E"),
    ]


def sistema(respuestas, libros=None):
    motor = MotorTextoSimulado(respuestas)
    proveedor = ConCacheLLM(AdaptadorMotorSimulado(motor))
    recomendador = RecomendadorLibros(libros if libros is not None else catalogo(), proveedor)
    return recomendador, motor, proveedor


def test_llm_simulado_recomienda_libros_reales_del_catalogo():
    libros = catalogo()
    recomendador, motor, _ = sistema('{"isbns": ["ISBN-B", "ISBN-C"]}', libros)

    sugeridos = recomendador.recomendar("ISBN-A")

    assert sugeridos == [libros[1], libros[2]]
    assert sugeridos[0] is libros[1]
    assert motor.llamadas == 1


def test_decorator_cache_evita_otra_llamada_al_mismo_prompt():
    recomendador, motor, cache = sistema(
        ['{"isbns": ["ISBN-B"]}', '{"isbns": ["ISBN-INVENTADO"]}']
    )

    primera = recomendador.recomendar("ISBN-A")
    segunda = recomendador.recomendar("ISBN-A")

    assert [libro.isbn for libro in primera] == ["ISBN-B"]
    assert [libro.isbn for libro in segunda] == ["ISBN-B"]
    assert motor.llamadas == 1
    assert cache.aciertos == 1


def test_cache_diferencia_peticiones_por_libro_de_origen():
    recomendador, motor, _ = sistema(
        ['{"isbns": ["ISBN-B"]}', '{"isbns": ["ISBN-A"]}']
    )

    assert recomendador.recomendar("ISBN-A")[0].isbn == "ISBN-B"
    assert recomendador.recomendar("ISBN-B")[0].isbn == "ISBN-A"
    assert motor.llamadas == 2


def test_proveedor_llm_puede_sustituirse_sin_modificar_recomendador():
    class ProveedorLocal(ProveedorLLM):
        def generar(self, prompt):
            return '{"isbns": ["ISBN-D"]}'

    recomendador = RecomendadorLibros(catalogo(), ProveedorLocal())

    assert recomendador.recomendar("ISBN-A")[0].titulo == "Bases de datos"


def test_guardrail_formato_bloquea_json_mal_formado():
    recomendador, _, _ = sistema("Recomiendo un libro muy bueno")
    with pytest.raises(RespuestaLLMInvalida, match="JSON válido"):
        recomendador.recomendar("ISBN-A")


def test_guardrail_formato_bloquea_campos_extra_y_datos_personales():
    recomendador, _, _ = sistema(
        '{"isbns": ["ISBN-B"], "correo": "alumno@unsa.edu.pe"}'
    )
    with pytest.raises(RespuestaLLMInvalida, match="solo 'isbns'"):
        recomendador.recomendar("ISBN-A")


def test_guardrail_formato_rechaza_mas_de_tres_recomendaciones():
    recomendador, _, _ = sistema(
        '{"isbns": ["ISBN-B", "ISBN-C", "ISBN-D", "ISBN-E"]}'
    )
    with pytest.raises(RespuestaLLMInvalida, match="entre 1 y 3"):
        recomendador.recomendar("ISBN-A")


def test_guardrail_formato_rechaza_una_lista_incorrecta():
    recomendador, _, _ = sistema('{"isbns": "ISBN-B"}')
    with pytest.raises(RespuestaLLMInvalida, match="entre 1 y 3"):
        recomendador.recomendar("ISBN-A")


def test_guardrail_catalogo_bloquea_libros_inventados():
    recomendador, _, _ = sistema('{"isbns": ["ISBN-INVENTADO"]}')
    with pytest.raises(RespuestaLLMInvalida, match="inventó libros"):
        recomendador.recomendar("ISBN-A")


def test_guardrail_catalogo_bloquea_recomendar_el_mismo_libro():
    recomendador, _, _ = sistema('{"isbns": ["ISBN-A"]}')
    with pytest.raises(RespuestaLLMInvalida, match="mismo libro"):
        recomendador.recomendar("ISBN-A")


def test_guardrail_catalogo_bloquea_isbn_repetidos():
    recomendador, _, _ = sistema('{"isbns": ["ISBN-B", "ISBN-B"]}')
    with pytest.raises(RespuestaLLMInvalida, match="repitió un ISBN"):
        recomendador.recomendar("ISBN-A")


def test_un_libro_desconocido_se_rechaza_antes_de_consultar_llm():
    recomendador, motor, _ = sistema('{"isbns": ["ISBN-B"]}')
    with pytest.raises(ValueError, match="no existe en el catálogo"):
        recomendador.recomendar("ISBN-DESCONOCIDO")
    assert motor.llamadas == 0


def test_guardrails_validan_incluso_respuestas_procedentes_de_cache():
    recomendador, motor, cache = sistema('{"isbns": ["ISBN-FALSO"]}')
    with pytest.raises(RespuestaLLMInvalida):
        recomendador.recomendar("ISBN-A")
    with pytest.raises(RespuestaLLMInvalida):
        recomendador.recomendar("ISBN-A")
    assert motor.llamadas == 1
    assert cache.aciertos == 1


def test_catalogo_sin_otras_opciones_no_necesita_consultar_llm():
    unico = [Libro(titulo="Único libro", autor="Autor", isbn="SOLO")]
    recomendador, motor, _ = sistema('{"isbns": ["SOLO"]}', unico)
    assert recomendador.recomendar("SOLO") == []
    assert motor.llamadas == 0
