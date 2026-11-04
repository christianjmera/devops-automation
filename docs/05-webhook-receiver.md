
##  Validación local del receptor

Fecha: 4 de noviembre de 2026.

Se realizaron pruebas automatizadas utilizando FastAPI TestClient.

### Resultados

| Prueba | Resultado esperado | Resultado obtenido |
|---|---|---|
| Endpoint GET /health | HTTP 200 | HTTP 200 |
| Firma HMAC inválida | HTTP 401 | HTTP 401 |
| Firma válida y repositorio no autorizado | HTTP 403 | HTTP 403 |
| Push autorizado simulado | HTTP 200 | HTTP 200 |
| Envío repository_dispatch simulado | HTTP 204 | HTTP 204 |

### Seguridad y alcance

- La firma HMAC-SHA256 se valida correctamente.
- Los repositorios se comprueban contra la lista de permitidos.
- La obtención del token de GitHub App y el envío del evento se simularon durante la prueba del push autorizado.
- No se realizaron llamadas reales a GitHub durante estas pruebas.
- No se ejecutaron pipelines ni despliegues.

### Estado

El receptor está implementado y sus principales controles de seguridad y procesamiento han superado las pruebas locales.

Queda pendiente la integración mediante webhook real, que se realizará en una fase posterior.
