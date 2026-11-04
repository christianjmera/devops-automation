# 03 - Configuración de GitHub App

## 1. Objetivo

Crear una identidad de aplicación que permita conectar nuestra plataforma
centralizada de automatización DevOps con los repositorios privados de GitHub.

La GitHub App será utilizada por el Webhook Receiver para autenticarse
ante GitHub y solicitar tokens temporales.

## 2. Aplicación creada

- Nombre: christian-devops-automation-app
- Tipo: GitHub App
- Instalación: únicamente en nuestra cuenta personal.

## 3. Permisos configurados

| Permiso | Nivel | Uso |
|---|---|---|
| Contents | Read and write | Acceso al contenido de los repositorios y envío de eventos al repositorio central. |
| Metadata | Read-only | Consulta de metadatos básicos. |
| Otros permisos | No access | No se conceden permisos innecesarios. |

Los permisos efectivos se limitarán posteriormente a los repositorios
que necesite cada operación.

## 4. Clave privada

Se generó una clave privada desde la configuración de la GitHub App.

La clave se almacena fuera del repositorio Git, en:

`~/.config/devops-automation/github-app/private-key.pem`

## 5. Protección de la clave

El directorio tiene permisos `700` y el archivo tiene permisos `600`.

Esto restringe el acceso al usuario propietario del entorno Linux.

La clave privada:

- No debe subirse a GitHub.
- No debe incluirse en archivos de configuración versionados.
- No debe compartirse por correo, chat o capturas.
- No debe imprimirse en logs.

## 6. Arquitectura de autenticación prevista

1. El Webhook Receiver obtiene el App ID y utiliza la clave privada.
2. Genera un JWT firmado.
3. Solicita a GitHub un token de instalación.
4. Utiliza el token temporal para realizar operaciones autorizadas.

## 7. Estado actual

- [x] GitHub App creada.
- [x] Permisos iniciales configurados.
- [x] Clave privada generada.
- [x] Clave privada almacenada en WSL2.
- [x] Permisos del directorio y archivo verificados.
- [ ] GitHub App instalada en la cuenta.
- [ ] Acceso limitado a los repositorios necesarios.
- [ ] Autenticación mediante JWT validada.
- [ ] Token de instalación validado.

## 8. Consideraciones de seguridad

Nunca almacenar claves privadas, JWT o tokens de instalación
en el repositorio.

Las credenciales deben mantenerse fuera del código fuente y utilizarse
mediante mecanismos seguros de gestión de secretos.
