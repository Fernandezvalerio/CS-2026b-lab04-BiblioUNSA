# E4. Evidencias de integración MCP

Consulta: préstamos vencidos y reserva ficticia de Redes de computadoras.

Los siguientes datos proceden de la ejecución registrada; no son resultados simulados en este informe.

Mensajes JSON-RPC: 14. Llamadas respondidas: 5.

## Verificación

- [x] Dos herramientas de lectura exitosas
- [x] Error de fecha corregido
- [x] Una escritura exitosa con aprobación registrada
- [x] Respuesta final del agente

## Error y corrección

Argumentos rechazados: `{"hoy": "27/11/2026"}`.

Respuesta de error:
```json
{
  "content": [
    {
      "text": "Error executing tool prestamos_vencidos: Fecha inválida: use una fecha real en formato AAAA-MM-DD.",
      "type": "text"
    }
  ],
  "isError": true,
  "resultType": "complete",
  "_meta": {
    "io.modelcontextprotocol/serverInfo": {
      "name": "bibliounsa",
      "version": ""
    }
  }
}
```

Argumentos corregidos: `{"hoy": "2026-11-27"}`.

Respuesta correcta:
```json
{
  "fecha_corte": "2026-11-27",
  "total": 2,
  "prestamos": [
    {
      "prestamo_id": "00000000-0000-4000-8000-000000000301",
      "ejemplar_id": "00000000-0000-4000-8000-000000000102",
      "codigo_inventario": "LAB11-102",
      "biblioteca": "Central",
      "estado": "PRESTADO",
      "fecha_vencimiento": "2026-11-20",
      "dias_atraso": 7
    },
    {
      "prestamo_id": "00000000-0000-4000-8000-000000000302",
      "ejemplar_id": "00000000-0000-4000-8000-000000000103",
      "codigo_inventario": "LAB11-103",
      "biblioteca": "Ingeniería",
      "estado": "VENCIDO",
      "fecha_vencimiento": "2026-11-23",
      "dias_atraso": 4
    }
  ]
}
```

## Aprobación humana

```json
[
  {
    "tipo": "aprobacion",
    "paso": 4,
    "accion": "crear_reserva",
    "args": {
      "estudiante_id": "00000000-0000-4000-8000-000000000001",
      "ejemplar_id": "00000000-0000-4000-8000-000000000101"
    },
    "permitida": true,
    "fecha_utc": "2026-11-27T22:28:58.263468+00:00"
  }
]
```

## Respuesta final del agente

Al 27 de noviembre de 2026 se identificaron dos préstamos vencidos: LAB11-102 de la biblioteca Central, con 7 días de atraso, y LAB11-103 de la biblioteca Ingeniería, con 4 días de atraso. Se creó correctamente la reserva ficticia 84dbcdd5-110b-4ad4-bf84-6c3ed81fbd1d para el ejemplar LAB11-101, previa aprobación humana. La consulta posterior confirmó que el ejemplar dejó de estar disponible. También se corrigió el error inicial de formato de fecha. El catálogo optimizado permitió seleccionar correctamente las herramientas, mantener las validaciones y completar el mismo escenario de E4 sin perder funcionalidad.
