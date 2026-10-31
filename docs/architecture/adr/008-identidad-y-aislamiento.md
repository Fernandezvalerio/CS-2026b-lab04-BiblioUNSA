# ADR-008: Validar identidad institucional y mantener aislada la API académica

- Estado: Propuesto para ratificación por el equipo
- Fecha: 2026-10-31
- Iteración ADD: 3 (E4)
- Escenarios: QA-08-03, QA-08-07 y QA-08-04

## Contexto

El crecimiento a todas las facultades aumenta la exposición a accesos no autorizados. El sistema académico solo puede consultarse mediante su API y el proveedor OIDC real debe confirmarse con la UNSA.

## Alternativas

1. Aceptar un correo declarado con sufijo institucional: falsificable; rechazada.
2. Gestionar credenciales propias: mayor responsabilidad legal y operativa; rechazada.
3. Comprobar servidor OIDC (firma, audiencia, issuer y expiración) y exigir identidad institucional verificada, centralizando API académica en un adaptador: **elegida**.

## Decisión

No confiar en claims sin validación criptográfica. La autorización de dominio y rol ocurre en el servidor tras verificar el token. Ningún módulo de negocio consulta la base del sistema académico ni depende del formato del proveedor. Un contrato de imports protege el límite interno y se conserva el patrón Adapter/Strategy del ADR-005.

## Evidencia

fitness/seguridad.py rechaza 30/30 casos adversos sintéticos (correo externo, issuer erróneo o token no verificado). FF-01 y FF-02 impiden dependencias internas no previstas, pero **no prueban seguridad OIDC ni ausencia de conexiones SQL externas en producción**. Hace falta la integración real con el IdP.

## Trade-off

Se depende de la autorización institucional y de la disponibilidad de OIDC. Una política de denegación segura puede dificultar nuevos inicios de sesión durante una caída; sesiones existentes se tratan según ADR-002 y reglas acordadas.

## Relación

ADR-001, ADR-002, ADR-003, ADR-005, docs/architecture/add/iteracion-3.md.
