# E4 - ADD iteración 3: identidad institucional e aislamiento académico

## 1\. Entradas

QA-08-03 (H,M): rechazar 30/30 identidades externas; QA-08-07 (H,M): sin saltos al adaptador académico. El ADR-002 define OIDC institucional pendiente de confirmar con la UNSA. La API académica no permite acceso directo a su base de datos (R-05).

## 2\. Objetivo y refinamiento

Proteger el módulo Autenticación y mantener la comunicación con la API académica centralizada en Integración académica, sin aumentar la infraestructura del VPS.

## 3\. Conceptos candidatos

|Concepto|Ventaja|Trade-off|Resultado|
|-|-|-|-|
|Revisar solo sufijo del correo|Muy fácil|Se puede falsificar el correo en una entrada no confiable|Rechazado|
|Middleware OIDC que verifica firma, issuer, audience y correo verificado; autorización del dominio en servidor|Separa identidad de reglas de acceso|Requiere coordinar registro de aplicación con UNSA|Elegido|
|Base propia de contraseñas|Evita dependencia OIDC|Mayor exposición de datos y recuperación de cuentas|Rechazado|
|Permitir lectura directa de BD académica|Sin llamadas HTTP|Viola la restricción R-05 y amplía privilegios|Rechazado|

## 4\. Evidencia

Prototipo: fitness/seguridad.py. Se simulan 30 intentos: 10 correos no institucionales, 10 emisores ajenos y 10 tokens no verificados. El prototipo recibe un indicador de verificación OIDC **desde un middleware confiable** y no reemplaza la validación criptográfica real.

Ejecución: python -m fitness.seguridad

|Medida|Confiar solo en correo declarado|Validación de claims ya verificados|Meta|
|-|-|-|-|
|Identidades externas rechazadas|Vulnerable a correo falsificado|30/30 en casos sintéticos|30/30|
|Módulos de negocio que consultan BD académica|Prohibido por drivers|0, si se respeta la regla estructural|0|

## 5\. Instanciar elementos

El módulo Autenticación exige un token OIDC validado en servidor; únicamente Integración académica puede llamar a la API externa. El prototipo ilustra la decisión, no despliega un proveedor real.

## 6\. Vistas

El C4 marcará los módulos Autenticación e Integración con QA-08-03 y QA-08-07. La política de aislamiento se protege mediante contratos de imports en E5.

## 7\. Verificación

La prueba de calidad de E5 rechazará los 30 intentos simulados y aceptará solo identidades institucionales verificadas. 

