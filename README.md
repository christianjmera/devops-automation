# Automatización DevOps

Plataforma centralizada para la automatización de procesos CI/CD.

## Componentes

- `.github/workflows/`: flujos de trabajo centrales de GitHub Actions.
- `devops-files/sh-files/`: scripts compartidos para los procesos CI/CD.
- `webhook-receiver/`: servicio encargado de recibir y procesar eventos de GitHub.

## Arquitectura objetivo

- Repositorios de aplicaciones privados.
- Autenticación mediante GitHub App.
- Orquestación centralizada de pipelines.
- Ejecución mediante un runner local autogestionado.
- Construcción de imágenes Docker y promoción del mismo artefacto entre ambientes.
- Separación de los ambientes DEV, TEST, UAT y PROD.

## Documentación técnica

La documentación del proyecto está organizada por componentes y fases de implementación.

Consulta el [índice general de documentación](docs/README.md) para acceder a:

- Arquitectura general de la plataforma.
- Configuración y autenticación de GitHub App.
- Recepción y procesamiento de webhooks.
- Workflows centrales y scripts compartidos.
- Integración CI/CD de aplicaciones.
- Docker, Harbor, Helm y Kubernetes.
- Seguridad, observabilidad y operación.
