"""E3: contrato MCP de BiblioUNSA, en proceso, sin LLM ni red."""
import asyncio
import sys
from pathlib import Path
from uuid import UUID

import pytest
from mcp import Client

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "servidor_mcp"))
import bibliounsa_mcp as srv


ALUMNO = "00000000-0000-4000-8000-000000000001"
ALUMNO_NO_VIGENTE = "00000000-0000-4000-8000-000000000002"
EJEMPLAR = "00000000-0000-4000-8000-000000000101"
OTRO_EJEMPLAR = "00000000-0000-4000-8000-000000000104"


@pytest.fixture(autouse=True)
def datos_aislados(monkeypatch):
    """Cada caso inicia con los mismos libros y préstamos ficticios de E2."""
    monkeypatch.setattr(srv, "DATOS", srv.DatosMCP())


def correr(coro_fn):
    async def ejecutar():
        async with Client(srv.mcp) as cliente:
            return await coro_fn(cliente)
    return asyncio.run(ejecutar())


def contenido(resultado):
    assert not resultado.is_error, mensaje(resultado)
    assert isinstance(resultado.structured_content, dict)
    return resultado.structured_content


def mensaje(resultado):
    return " ".join(getattr(c, "text", "") for c in resultado.content)


def llamar(nombre, argumentos):
    return correr(lambda c: c.call_tool(nombre, argumentos))


def prestamos_actuales():
    return {p.id: (p.estado, p.fecha_reserva, p.fecha_vencimiento, p.fecha_devolucion)
            for p in srv.DATOS.repo_prestamos.prestamos}


def test_catalogo_estable_y_documentado():
    tools = correr(lambda c: c.list_tools()).tools
    assert [t.name for t in tools] == ["buscar_libro", "prestamos_vencidos", "crear_reserva"]
    assert [t.name for t in correr(lambda c: c.list_tools()).tools] == [t.name for t in tools]
    for tool in tools:
        assert tool.description and len(tool.description) > 30
        assert tool.input_schema["type"] == "object"
    assert set(tools[0].input_schema["required"]) == {"consulta"}
    assert set(tools[1].input_schema["required"]) == {"hoy"}
    assert set(tools[2].input_schema["required"]) == {"estudiante_id", "ejemplar_id"}


def test_esquemas_de_salida_estructurada():
    tools = correr(lambda c: c.list_tools()).tools
    esperados = {"buscar_libro": {"libros"},
                 "prestamos_vencidos": {"fecha_corte", "total", "prestamos"},
                 "crear_reserva": {"reserva_id", "estudiante_id", "ejemplar_id", "estado",
                                   "fecha_reserva", "requiere_reverificacion"}}
    for tool in tools:
        assert tool.output_schema is not None
        assert tool.output_schema["type"] == "object"
        assert esperados[tool.name] <= set(tool.output_schema["properties"])


def test_minimo_privilegio_una_sola_escritura():
    tools = correr(lambda c: c.list_tools()).tools
    assert all(t.annotations is not None for t in tools)
    escritura = [t for t in tools if not t.annotations.read_only_hint]
    assert [t.name for t in escritura] == ["crear_reserva"]
    assert escritura[0].annotations.destructive_hint is False
    assert escritura[0].annotations.idempotent_hint is False
    assert all(t.annotations.open_world_hint is False for t in tools)


def test_busqueda_estructurada_y_disponibilidad():
    resultado = contenido(llamar("buscar_libro", {"consulta": "  REDES  ", "biblioteca": "central"}))
    assert len(resultado["libros"]) == 1
    libro = resultado["libros"][0]
    assert libro["titulo"] == "Redes de computadoras"
    assert {e["codigo_inventario"]: e["disponible"] for e in libro["ejemplares"]} == {
        "LAB11-101": True, "LAB11-102": False}
    assert all(e["biblioteca"] == "Central" for e in libro["ejemplares"])
    assert UUID(libro["libro_id"])
    assert all(UUID(e["ejemplar_id"]) for e in libro["ejemplares"])


def test_busqueda_por_autor_y_filtro_sin_coincidencias():
    resultado = contenido(llamar("buscar_libro", {"consulta": "Autor de prueba B"}))
    assert [l["titulo"] for l in resultado["libros"]] == ["Sistemas operativos"]
    assert contenido(llamar("buscar_libro", {"consulta": "redes", "biblioteca": "Ingeniería"})) == {"libros": []}
    assert contenido(llamar("buscar_libro", {"consulta": "sin coincidencias"})) == {"libros": []}


def test_vencidos_respeta_fecha_estado_y_privacidad():
    antes = prestamos_actuales()
    salida = contenido(llamar("prestamos_vencidos", {"hoy": "2026-11-27"}))
    assert salida["fecha_corte"] == "2026-11-27"
    assert salida["total"] == len(salida["prestamos"]) == 2
    assert {p["codigo_inventario"]: p["dias_atraso"] for p in salida["prestamos"]} == {
        "LAB11-102": 7, "LAB11-103": 4}
    assert {p["estado"] for p in salida["prestamos"]} == {"PRESTADO", "VENCIDO"}
    for p in salida["prestamos"]:
        assert set(p) == {"prestamo_id", "ejemplar_id", "codigo_inventario", "biblioteca",
                          "estado", "fecha_vencimiento", "dias_atraso"}
    assert prestamos_actuales() == antes


def test_vencidos_sin_resultados():
    salida = contenido(llamar("prestamos_vencidos", {"hoy": "2026-11-20"}))
    assert salida == {"fecha_corte": "2026-11-20", "total": 0, "prestamos": []}


@pytest.mark.parametrize("fecha", ["27/11/2026", "2026-02-30", "2026-1-1"])
def test_fecha_invalida_devuelve_error_util(fecha):
    r = llamar("prestamos_vencidos", {"hoy": fecha})
    assert r.is_error
    assert "AAAA-MM-DD" in mensaje(r)


@pytest.mark.parametrize("args, campo", [({"consulta": "   "}, "consulta"),
    ({"consulta": "a" * 101}, "consulta"),
    ({"consulta": "redes", "biblioteca": "b" * 81}, "biblioteca")])
def test_busqueda_rechaza_limites_invalidos(args, campo):
    r = llamar("buscar_libro", args)
    assert r.is_error
    assert campo in mensaje(r) and "caracteres" in mensaje(r)


def test_crear_reserva_solo_agrega_registros_y_cambia_disponibilidad():
    antes = prestamos_actuales()

    async def escenario(c):
        primera = contenido(await c.call_tool("crear_reserva", {"estudiante_id": ALUMNO, "ejemplar_id": EJEMPLAR}))
        segunda = contenido(await c.call_tool("crear_reserva", {"estudiante_id": ALUMNO, "ejemplar_id": OTRO_EJEMPLAR}))
        busqueda = contenido(await c.call_tool("buscar_libro", {"consulta": "redes"}))
        return primera, segunda, busqueda

    primera, segunda, busqueda = correr(escenario)
    ids = {UUID(primera["reserva_id"]), UUID(segunda["reserva_id"])}
    assert len(ids) == 2 and ids.isdisjoint(antes)
    assert primera["estado"] == segunda["estado"] == "RESERVADO"
    assert primera["estudiante_id"] == ALUMNO and primera["ejemplar_id"] == EJEMPLAR
    assert primera["requiere_reverificacion"] is False
    despues = prestamos_actuales()
    assert set(despues) == set(antes) | ids
    assert all(despues[k] == v for k, v in antes.items())
    ejemplares = busqueda["libros"][0]["ejemplares"]
    assert next(e for e in ejemplares if e["ejemplar_id"] == EJEMPLAR)["disponible"] is False


def test_reserva_duplicada_no_crea_otro_prestamo():
    args = {"estudiante_id": ALUMNO, "ejemplar_id": EJEMPLAR}

    async def escenario(c):
        contenido(await c.call_tool("crear_reserva", args))
        antes = prestamos_actuales()
        r = await c.call_tool("crear_reserva", args)
        assert r.is_error and "no disponible" in mensaje(r).lower()
        assert prestamos_actuales() == antes

    correr(escenario)


@pytest.mark.parametrize("args, fragmento", [
    ({"estudiante_id": ALUMNO_NO_VIGENTE, "ejemplar_id": EJEMPLAR}, "Matrícula no vigente"),
    ({"estudiante_id": "incorrecto", "ejemplar_id": EJEMPLAR}, "UUID"),
    ({"estudiante_id": ALUMNO, "ejemplar_id": "00000000-0000-4000-8000-000000000999"}, "Ejemplar inexistente"),
    ({"estudiante_id": "00000000-0000-4000-8000-000000000999", "ejemplar_id": EJEMPLAR}, "Estudiante inexistente"),
])
def test_reserva_invalida_no_modifica_prestamos(args, fragmento):
    antes = prestamos_actuales()
    r = llamar("crear_reserva", args)
    assert r.is_error and fragmento in mensaje(r)
    assert prestamos_actuales() == antes
    assert srv.DATOS.repo_ejemplares.buscar(UUID(EJEMPLAR)).esta_disponible()


def test_catalogo_de_recursos_y_reglas():
    async def escenario(c):
        recursos = (await c.list_resources()).resources
        plantillas = (await c.list_resource_templates()).resource_templates
        assert "bibliounsa://prestamos/reglas" in [str(r.uri) for r in recursos]
        assert "bibliounsa://adr/{numero}" in [str(t.uri_template) for t in plantillas]
        return await c.read_resource("bibliounsa://prestamos/reglas")
    r = correr(escenario)
    assert "matrícula vigente" in r.contents[0].text
    assert "RESERVADO" in r.contents[0].text


def test_recurso_adr_valido():
    r = correr(lambda c: c.read_resource("bibliounsa://adr/001"))
    assert "ADR-001" in r.contents[0].text
    assert "monolito modular" in r.contents[0].text.lower()


@pytest.mark.parametrize("numero", ["999", "..%2F..%2Fsecretos"])
def test_recurso_adr_rechaza_identificadores_invalidos(numero):
    async def escenario(c):
        # Primero comprobamos que el mismo cliente lee un recurso real.
        assert "ADR-001" in (await c.read_resource("bibliounsa://adr/001")).contents[0].text
        # El SDK puede rechazar la URI o devolver un error de recurso/protocolo.
        with pytest.raises(Exception):
            await c.read_resource(f"bibliounsa://adr/{numero}")
    correr(escenario)


def test_prompts_publicados_y_plantillas_reutilizadas():
    async def escenario(c):
        prompts = (await c.list_prompts()).prompts
        assert {p.name for p in prompts} == {"aviso_vencimiento", "generar_criterios"}
        aviso = await c.get_prompt("aviso_vencimiento", {"titulo": "Redes <prueba>", "fecha_vencimiento": "2026-11-20"})
        criterios = await c.get_prompt("generar_criterios", {"id": "HU-03", "historia": "Como estudiante quiero reservar."})
        return aviso.messages[0].content.text, criterios.messages[0].content.text
    aviso, criterios = correr(escenario)
    assert "Redes &lt;prueba&gt;" in aviso and "2026-11-20" in aviso
    assert "No envíes ningún mensaje" in aviso
    assert "INVEST" in criterios and "JSON" in criterios
    assert '<historia id="HU-03">Como estudiante quiero reservar.</historia>' in criterios
    assert "{{historia}}" not in criterios and "{{id}}" not in criterios
