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
