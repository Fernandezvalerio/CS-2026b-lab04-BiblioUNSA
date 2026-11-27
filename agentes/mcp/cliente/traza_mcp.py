"""E6: analiza trazas reales de BiblioUNSA (sin SDK ni LLM)."""
import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
from statistics import mean

MCP = Path(__file__).resolve().parents[1]
LECTURAS = {'buscar_libro', 'prestamos_vencidos'}
ESCRITURA = 'crear_reserva'


def cargar(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8-sig').splitlines() if line.strip()]


def compacto(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))


def costo(obj):
    s = compacto(obj)
    return {'bytes_utf8': len(s.encode('utf-8')), 'caracteres': len(s),
            'tokens_estimados': math.ceil(len(s) / 4)}


def error(m):
    return 'error' in m or bool((m.get('result') or {}).get('isError'))


def analizar(carpeta):
    eventos = cargar(carpeta / 'mcp_trafico.jsonl')
    aprobaciones = cargar(carpeta / 'aprobaciones.jsonl')
    pendientes, latencias, llamadas, catalogos = {}, defaultdict(list), [], []
    errores = Counter()
    metodos = Counter()
    diagrama = ['sequenceDiagram', '    autonumber', '    actor U as Humano',
                '    participant A as Agente Lab 10', '    participant S as Servidor MCP BiblioUNSA']
    for e in eventos:
        m = e['msg']
        if e['dir'] == 'host->servidor' and 'method' in m:
            metodo = m['method']
            p = m.get('params') or {}
            nombre = p.get('name', '')
            metodos[metodo] += 1
            if 'id' in m:
                pendientes[m['id']] = e
            if metodo == 'tools/call' and nombre == ESCRITURA:
                aprobada = any(a.get('accion') == ESCRITURA and a.get('permitida') is True
                               and a.get('args') == p.get('arguments', {}) for a in aprobaciones)
                if aprobada:
                    diagrama += ['    A->>U: Solicitar aprobación de reserva', '    U-->>A: Aprobación registrada']
            etiqueta = f'{metodo} {nombre}' if nombre in LECTURAS | {ESCRITURA} else metodo
            diagrama.append('    A->>S: ' + etiqueta)
        elif e['dir'] == 'servidor->host' and 'id' in m and m['id'] in pendientes:
            ida = pendientes.pop(m['id'])
            pet = ida['msg']; metodo = pet['method']
            p = pet.get('params') or {}; r = m.get('result') or {}
            latencias[metodo].append((e['t'] - ida['t']) * 1000)
            fallo = error(m)
            if fallo:
                errores['protocolo' if 'error' in m else 'herramienta'] += 1
            if metodo == 'tools/list' and not fallo:
                catalogos.append(r.get('tools', []))
            if metodo == 'tools/call':
                llamadas.append({'nombre': p.get('name'), 'args': p.get('arguments', {}),
                                 'error': fallo, 'salida': r.get('structuredContent')})
            etiqueta = ('Error JSON-RPC' if 'error' in m else 'Error de herramienta') if fallo else (
                f'{len(r.get("tools", []))} herramientas con esquema' if metodo == 'tools/list' else
                'Resultado de ' + metodo)
            diagrama.append('    S--xA: ' + etiqueta if fallo else '    S-->>A: ' + etiqueta)
    if not catalogos or not catalogos[0]:
        raise ValueError(f'{carpeta}: no existe respuesta tools/list con catálogo')
    if len(catalogos) != 1:
        raise ValueError(f'{carpeta}: se esperaba un único tools/list; revise la ejecución')
    tools = catalogos[0]
    # Replica el catálogo enviado al modelo por HerramientasMCP.catalogo().
    cat_agente = {t['name']: f'{(t.get("description") or "").strip()} Esquema: '
                  + json.dumps(t['inputSchema'], ensure_ascii=False) for t in tools}
    cat_agente['leer_recurso'] = ('Lee reglas o ADR del proyecto. uri: '
                                 'bibliounsa://prestamos/reglas o bibliounsa://adr/001 (tres dígitos).')
    texto_agente = json.dumps(cat_agente, ensure_ascii=False)
    def disponibilidad(c):
        return next((e['disponible'] for l in (c.get('salida') or {}).get('libros', [])
                     for e in l.get('ejemplares', []) if e.get('codigo_inventario') == 'LAB11-101'), None)
    reservas = [c for c in llamadas if c['nombre'] == ESCRITURA]
    indice = next((i for i,c in enumerate(llamadas) if c['nombre'] == ESCRITURA), len(llamadas))
    antes = [c for c in llamadas[:indice] if c['nombre'] == 'buscar_libro' and not c['error']]
    despues = [c for c in llamadas[indice+1:] if c['nombre'] == 'buscar_libro' and not c['error']]
    err_fecha = next((i for i,c in enumerate(llamadas) if c['nombre']=='prestamos_vencidos' and c['error'] and c['args'].get('hoy')=='27/11/2026'), None)
    correccion = err_fecha is not None and any(c['nombre']=='prestamos_vencidos' and not c['error'] and c['args'].get('hoy')=='2026-11-27' and (c.get('salida') or {}).get('total')==2 for c in llamadas[err_fecha+1:])
    ok_reserva = len(reservas)==1 and not reservas[0]['error'] and (reservas[0].get('salida') or {}).get('estado')=='RESERVADO' and any(a.get('accion')==ESCRITURA and a.get('permitida') is True and a.get('args')==reservas[0]['args'] for a in aprobaciones)
    checks = {'error_fecha_corregido': bool(correccion), 'reserva_unica_aprobada': bool(ok_reserva),
              'disponibilidad_antes': bool(antes and disponibilidad(antes[-1]) is True),
              'no_disponible_despues': bool(despues and disponibilidad(despues[-1]) is False),
              'dos_lecturas_exitosas': LECTURAS <= {c['nombre'] for c in llamadas if not c['error']}}
    datos = {'mensajes': len(eventos), 'bytes_json_utf8_normalizados': sum(len(compacto(e['msg']).encode('utf-8')) for e in eventos),
             'metodos': dict(metodos), 'errores': dict(errores), 'sin_respuesta': len(pendientes),
             'latencias_ms': {k: {'n':len(v), 'media':round(mean(v),3), 'min':round(min(v),3), 'max':round(max(v),3), 'muestras':[round(x,3) for x in v]} for k,v in latencias.items()},
             'catalogo_mcp': costo(tools), 'por_herramienta': {t['name']: costo(t) for t in tools},
             'catalogo_agente': {'caracteres':len(texto_agente), 'bytes_utf8':len(texto_agente.encode('utf-8')), 'tokens_estimados':math.ceil(len(texto_agente)/4)},
             'seleccion': [{'nombre':c['nombre'], 'error':c['error']} for c in llamadas], 'verificaciones':checks}
    return datos, '\n'.join(diagrama)+'\n', tools


def reduccion(a,b):
    return f'{(a-b)/a*100:.2f} %' if a else 'No calculable'


def informe(a,b,diagrama, ruta_a, ruta_b, mismos_contratos):
    l = ['# E6. Análisis del protocolo y costo de contexto', '',
         'Se analizaron los mensajes JSON-RPC capturados por el espía stdio. La ejecución original de E4 se conserva sin cambios. La optimización acorta las descripciones de las tres herramientas sin cambiar sus nombres, parámetros, anotaciones ni lógica de dominio.', '',
         f'- Traza original: `{ruta_a}`.',
         f'- Traza optimizada: `{ruta_b}`.' if b else '- Traza optimizada: todavía no disponible.', '',
         '## 1. Diagrama de secuencia de E4', '', '```mermaid', diagrama.rstrip(), '```', '',
         'El diagrama se genera a partir de peticiones y respuestas emparejadas por id. La aprobación se incorpora solo si consta en el registro de aprobaciones de la ejecución.', '',
         '## 2. Métricas de la comunicación', '', '| Métrica | Original | Optimizado |', '|---|---:|---:|']
    for k, etiqueta in [('mensajes','Mensajes JSON-RPC'),('bytes_json_utf8_normalizados','Bytes JSON UTF-8 normalizados'),('sin_respuesta','Peticiones sin respuesta registrada')]:
        l.append(f'| {etiqueta} | {a[k]} | {b[k] if b else "Pendiente"} |')
    l += [f'| Errores de herramienta | {a["errores"].get("herramienta",0)} | {b["errores"].get("herramienta",0) if b else "Pendiente"} |',
          f'| Errores de protocolo | {a["errores"].get("protocolo",0)} | {b["errores"].get("protocolo",0) if b else "Pendiente"} |','',
          'Los bytes se calculan sobre los objetos JSON serializados de forma compacta en UTF-8, sin separadores de línea; no equivalen necesariamente a los bytes originales del transporte, que el espía de E4 no guardó. La latencia mide desde el registro de la petición hasta el registro de la respuesta; no incluye el tiempo humano ni el del modelo entre llamadas.', '',
          '| Método | N original | Media original (ms) | Mín–máx original (ms) | N optimizado | Media optimizada (ms) | Mín–máx optimizado (ms) |','|---|---:|---:|---:|---:|---:|---:|']
    for k in sorted(set(a['latencias_ms']) | set(b['latencias_ms'] if b else {})):
        def fila(d):
            x=d['latencias_ms'].get(k) if d else None
            return f'{x["n"]} | {x["media"]} | {x["min"]}–{x["max"]}' if x else '— | — | —'
        l.append(f'| `{k}` | {fila(a)} | {fila(b)} |')
    l += ['', '## 3. Costo de contexto del catálogo', '', 'Se emplea la misma estimación de un token por cada cuatro caracteres (redondeada hacia arriba) en las dos ejecuciones. No es el conteo exacto de ningún modelo. Se mide tanto la lista completa de herramientas MCP como el catálogo de descripciones y esquemas de entrada que el adaptador del agente incorpora al contexto; no se incluye el historial ni las instrucciones generales.', '', '| Catálogo | Tokens estimados antes | Tokens estimados después | Reducción |','|---|---:|---:|---:|']
    for k, etiqueta in [('catalogo_mcp','MCP completo'),('catalogo_agente','Catálogo del agente')]:
        x=a[k]['tokens_estimados']; y=b[k]['tokens_estimados'] if b else None
        l.append(f'| {etiqueta} | {x} | {y if b else "Pendiente"} | {reduccion(x,y) if b else "Pendiente"} |')
    l += ['', '| Herramienta | Tokens estimados antes | Tokens estimados después | Reducción |','|---|---:|---:|---:|']
    for k,x in a['por_herramienta'].items():
        x=x['tokens_estimados']; y=b['por_herramienta'].get(k,{}).get('tokens_estimados') if b else None
        l.append(f'| `{k}` | {x} | {y if y is not None else "—"} | {reduccion(x,y) if y is not None else "—"} |')
    l += ['', '## 4. Selección de herramientas después de optimizar', '', '| Verificación | Original | Optimizado |','|---|---|---|']
    for k,x in a['verificaciones'].items():
        l.append(f'| {k.replace("_"," ")} | {"Sí" if x else "No"} | {"Sí" if b["verificaciones"][k] else "No" if b else "Pendiente"} |' if b else f'| {k.replace("_"," ")} | {"Sí" if x else "No"} | Pendiente |')
    if b:
        l += ['', 'Secuencia original: ' + ' → '.join(f'`{c["nombre"]}`'+(' (error)' if c['error'] else '') for c in a['seleccion']) + '.', '', 'Secuencia optimizada: ' + ' → '.join(f'`{c["nombre"]}`'+(' (error)' if c['error'] else '') for c in b['seleccion']) + '.', '', 'Contratos publicados (sin descripciones) idénticos: **'+('Sí' if mismos_contratos else 'No')+'**.', '', '## 5. Conclusión', '']
        if all(b['verificaciones'].values()) and mismos_contratos and b['catalogo_agente']['tokens_estimados'] < a['catalogo_agente']['tokens_estimados']:
            l.append('En la ejecución interactiva optimizada se conservaron los contratos y se seleccionaron correctamente las herramientas para resolver el mismo caso, con un costo estimado menor de contexto. La corrección de fecha y la aprobación humana continuaron funcionando. Esto evidencia el resultado de este caso, no una garantía general sobre otros modelos o consultas. Las latencias pueden variar por el arranque del proceso y las condiciones de ejecución.')
        else:
            l.append('La comparación no confirma todos los objetivos de la optimización. Revisar las verificaciones y los contratos antes de afirmar que se mantuvo la funcionalidad o se redujo el contexto.')
    else:
        l += ['', '## 5. Conclusión', '', 'Pendiente de ejecutar el agente con el catálogo optimizado y comparar los resultados reales.']
    return '\n'.join(l)+'\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original',type=Path,default=MCP/'trazas/e4')
    parser.add_argument('--optimizado',type=Path,default=None)
    args=parser.parse_args()
    salida=MCP/'trazas/e6'; salida.mkdir(parents=True,exist_ok=True)
    a,da,ta=analizar(args.original)
    b=db=tb=None
    if args.optimizado is not None:
        b,db,tb=analizar(args.optimizado)
    (salida/'mcp_trafico.mmd').write_text(da,encoding='utf-8')
    (salida/'metricas-original.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if b:
        (salida/'mcp_trafico-optimizado.mmd').write_text(db,encoding='utf-8')
        (salida/'metricas-optimizado.json').write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    contratos=lambda ts:[{k:v for k,v in t.items() if k!='description'} for t in ts]
    ruta=lambda p: str(Path(p).resolve().relative_to(MCP.parent.parent)) if Path(p).resolve().is_relative_to(MCP.parent.parent) else str(p)
    (MCP/'protocolo.md').write_text(informe(a,b,da,ruta(args.original),ruta(args.optimizado) if b else '',contratos(ta)==contratos(tb) if b else False),encoding='utf-8')
    print(json.dumps({'original':a,'optimizado':b},ensure_ascii=False,indent=2))
    print('Informe:', MCP/'protocolo.md')
    print('Diagramas y métricas:', salida)


if __name__=='__main__':
    main()
