# Documentación - DevOps Automation

Documentación técnica de la plataforma centralizada de automatización DevOps basada en GitHub Actions.

## Índice general

### 1. Fundamentos y arquitectura

| Documento | Descripción | Estado |
|---|---|---|
| `01-arquitectura-general.md` | Diseño, componentes y flujo de la plataforma | Planificado |
| `02-estructura-y-estandares.md` | Organización, convenciones, ramas y ambientes | Planificado |

### 2. Autenticación y recepción de eventos

| Documento | Descripción | Estado |
|---|---|---|
| [03 - GitHub App](03-github-app.md) | Configuración, permisos e instalación | Completado |
| [04 - Autenticación GitHub App](04-autenticacion-github-app.md) | JWT, RS256 y tokens de instalación | Completado |
| [05 - Webhook Receiver](05-webhook-receiver.md) | FastAPI, HMAC, SQLite, worker y reintentos | Validado localmente; integración real pendiente |
| `06-publicacion-y-seguridad.md` | HTTPS, URL pública y configuración del webhook | Planificado |
| `07-integracion-y-pruebas.md` | Integración real y pruebas end-to-end | Planificado |

### 3. Automatización centralizada

| Documento | Descripción | Estado |
|---|---|---|
| `08-workflows-centrales.md` | Orquestación con GitHub Actions | Planificado |
| `09-scripts-compartidos.md` | Biblioteca de scripts Shell reutilizables | Planificado |
| `10-repositorios-aplicaciones.md` | Integración de repositorios de aplicaciones | Planificado |
| `11-pipeline-ci-java.md` | Compilación, pruebas y calidad de aplicaciones Java | Planificado |
| `12-docker-y-harbor.md` | Construcción y publicación de imágenes | Planificado |

### 4. Despliegue y operación

| Documento | Descripción | Estado |
|---|---|---|
| `13-promocion-artefactos.md` | Promoción de imágenes entre ambientes | Planificado |
| `14-helm-y-kubernetes.md` | Despliegues mediante Helm y Kubernetes | Planificado |
| `15-seguridad-y-aprobaciones.md` | Secretos, permisos y aprobaciones de producción | Planificado |
| `16-observabilidad.md` | Métricas, logs y monitorización | Planificado |
| `17-operacion-y-troubleshooting.md` | Mantenimiento, errores y recuperación | Planificado |

## Criterios para completar cada documento

Un componente se considera documentado y completado cuando:

1. Su implementación está terminada.
2. Se han ejecutado y validado las pruebas correspondientes.
3. Se explica su arquitectura y funcionamiento.
4. Se documentan los requisitos y parámetros de configuración.
5. Se explican sus controles de seguridad.
6. Se incluyen procedimientos de validación y troubleshooting.
7. Se registran los resultados reales y las limitaciones conocidas.

## Estándares de documentación

- Idioma: español.
- Los documentos deben reflejar el estado real de la implementación.
- No se marcarán componentes como completados antes de validar su funcionamiento.
- Los cambios relevantes de arquitectura y configuración deben quedar registrados.
- La documentación se actualizará junto con la implementación de cada componente.
