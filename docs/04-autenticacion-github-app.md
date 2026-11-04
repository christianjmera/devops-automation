# 04 - Autenticación de GitHub App

## 1. Objetivo

Implementar la autenticación de la plataforma centralizada mediante
GitHub App, evitando el uso de credenciales personales.

## 2. Componentes

- App ID: identifica la GitHub App.
- Installation ID: identifica su instalación.
- Clave privada PEM: permite firmar el JWT.
- JWT: acredita la identidad de la aplicación.
- Installation Access Token: permite realizar operaciones autorizadas
  mediante un token temporal.

## 3. Configuración local

Los datos de configuración se almacenan fuera del repositorio:

`~/.config/devops-automation/github-app/app.env`

La clave privada se encuentra en:

`~/.config/devops-automation/github-app/private-key.pem`

Ambos archivos tienen permisos 600.

## 4. Implementación

Script: `webhook-receiver/github_app_auth.py`

Flujo de autenticación:

1. Lee las variables de configuración.
2. Genera un JWT firmado mediante RSA SHA-256.
3. Solicita un Installation Access Token a GitHub.
4. Utiliza el token para consultar el contenido del repositorio central.
5. No imprime ni almacena el token.

## 5. Validación realizada

La autenticación se ejecutó correctamente:

- [x] Generación del JWT.
- [x] Intercambio por token de instalación.
- [x] Acceso autenticado al repositorio privado.
- [x] Token no expuesto en pantalla.
- [x] Token no almacenado en archivos.

Repositorio validado: `christianjmera/devops-automation`

## 6. Seguridad

- No versionar claves privadas ni tokens.
- No imprimir credenciales en logs.
- Mantener los archivos de configuración fuera del repositorio.
- Utilizar tokens temporales con los permisos mínimos necesarios.
