# 05 - Webhook Receiver

**Fecha de actualización:** 5 de noviembre de 2026.

**Estado:** implementado y validado mediante pruebas locales.

## 1. Objetivo

El Webhook Receiver recibe eventos de GitHub procedentes de los repositorios de aplicaciones. Valida su autenticidad, comprueba el repositorio y la rama, almacena el evento y solicita la ejecución del workflow central mediante GitHub Actions.

Los repositorios de aplicaciones no necesitan contener Jenkinsfiles, workflows propios ni scripts de automatización centralizada.

## 2. Arquitectura y flujo

1. Un desarrollador realiza un push en un repositorio de aplicaciones.
2. GitHub envía un webhook al receptor.
3. FastAPI recibe la petición.
4. Se valida la firma HMAC-SHA256.
5. Se comprueba el tipo de evento y el identificador de entrega.
6. Se valida el repositorio y la rama.
7. SQLite almacena el evento con estado `pending`.
8. El receptor responde HTTP 202 Accepted.
9. El worker reclama el evento y cambia su estado a `processing`.
10. El worker obtiene un token temporal de instalación de GitHub App.
11. Se envía un evento `repository_dispatch` al repositorio central.
12. GitHub Actions recibe el evento y ejecuta el workflow correspondiente.
13. El evento se marca como `succeeded` o se programa un reintento.

El receptor y el worker son independientes de la lógica de compilación, pruebas, análisis de seguridad y despliegue.

## 3. Estructura de archivos

```text
webhook-receiver/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   └── worker.py
├── tests/
│   ├── test_webhook.py
│   └── test_database.py
├── github_app_auth.py
├── requirements.txt
└── run.sh
```

### Responsabilidades

| Archivo | Responsabilidad |
|---|---|
| `app/config.py` | Carga y valida la configuración. |
| `app/database.py` | Gestiona SQLite, persistencia y estados. |
| `app/main.py` | Expone FastAPI y valida los webhooks. |
| `app/worker.py` | Procesa eventos y solicita `repository_dispatch`. |
| `github_app_auth.py` | Genera JWT y obtiene tokens temporales de GitHub App. |
| `requirements.txt` | Declara dependencias Python. |
| `run.sh` | Carga la configuración e inicia el servicio. |
| `tests/` | Contiene las pruebas automatizadas. |

## 4. Configuración

Los archivos sensibles se mantienen fuera del repositorio:

- `~/.config/devops-automation/github-app/app.env`
- `~/.config/devops-automation/github-app/webhook.env`

La configuración contempla:

- Identificador e instalación de GitHub App.
- Ruta de la clave privada PEM.
- Secreto HMAC.
- Repositorio central.
- Repositorios y ramas permitidos.
- Ruta de la base de datos SQLite.
- Tamaño máximo del webhook.
- Número máximo de intentos.
- Intervalo de consulta del worker.

Los archivos de configuración y la clave privada tienen permisos restringidos y están excluidos del control de versiones.

## 5. Seguridad

El receptor implementa:

- Validación de firma `X-Hub-Signature-256` mediante HMAC-SHA256.
- Comparación segura de firmas.
- Límite configurable del tamaño del cuerpo.
- Validación del identificador de entrega.
- Comprobación del tipo de evento.
- Lista permitida de repositorios.
- Lista permitida de ramas.
- Validación del formato del commit SHA.
- Uso de tokens temporales de instalación de GitHub App.
- Exclusión de credenciales y claves privadas del repositorio.
- Manejo de errores sin registrar tokens ni secretos.

## 6. Persistencia y procesamiento

SQLite conserva los eventos aunque el receptor se reinicie.

La tabla `deliveries` almacena:

- Identificador de entrega.
- Repositorio y rama.
- Commit SHA.
- Payload recibido.
- Estado de procesamiento.
- Número de intentos.
- Fecha del siguiente intento.
- Último error.

### Estados

| Estado | Descripción |
|---|---|
| `pending` | Evento pendiente de procesamiento. |
| `processing` | Evento reservado por el worker. |
| `succeeded` | Dispatch enviado correctamente. |
| `failed` | Se agotaron los intentos configurados. |

El identificador de entrega evita almacenar dos veces el mismo webhook.

Al iniciar el servicio, los eventos que quedaron en `processing` se recuperan como `pending`.

### Reintentos

Cuando falla la comunicación con GitHub, se programa una espera incremental:

- Primer reintento: 30 segundos.
- Segundo reintento: 60 segundos.
- Los siguientes intervalos aumentan exponencialmente.
- El máximo es de 30 minutos.
- Al agotar los intentos configurados, el evento pasa a `failed`.

El procesamiento ofrece entrega al menos una vez. Si GitHub acepta el dispatch y el proceso falla antes de guardar `succeeded`, puede producirse un envío duplicado. Los workflows centrales deberán contemplar esta posibilidad.

## 7. Ejecución local

Desde la raíz del repositorio:

```bash
./webhook-receiver/run.sh
```

El servicio escucha inicialmente en `127.0.0.1:8000`.

Comprobación:

```bash
curl http://127.0.0.1:8000/health
```

El endpoint `/health` comprueba la disponibilidad de SQLite.

## 8. Pruebas automatizadas

Para ejecutar las pruebas:

```bash
source .venv/bin/activate

set -a
source "$HOME/.config/devops-automation/github-app/app.env"
source "$HOME/.config/devops-automation/github-app/webhook.env"
set +a

export PYTHONPATH="$PWD/webhook-receiver"

python -m unittest discover -s webhook-receiver/tests -p "test_*.py" -v

deactivate
```

Cobertura validada:

- Endpoint de salud.
- Firmas HMAC incorrectas.
- Repositorios no autorizados.
- Ramas no permitidas.
- Push autorizado.
- Entregas duplicadas.
- Persistencia SQLite.
- Recuperación de eventos interrumpidos.
- Reserva de eventos.
- Reintentos y espera incremental.
- Agotamiento de intentos.
- Entregas completadas.

**Resultado de la última ejecución:** 13 pruebas locales superadas.

Las pruebas simulan las comunicaciones con GitHub. No representan todavía una integración real ni una ejecución de GitHub Actions.

## 9. Limitaciones actuales

- El endpoint todavía no está expuesto públicamente.
- La GitHub App aún no tiene configurada la URL real del webhook.
- No se ha validado un evento enviado directamente por GitHub.
- No se ha ejecutado un `repository_dispatch` real.
- El worker está diseñado para una única instancia.
- SQLite es adecuado para esta fase local; una evolución productiva podrá requerir una base de datos y una estrategia de ejecución más robustas.
- No se han ejecutado pipelines ni despliegues de aplicaciones.

## 10. Estado de implementación

El receptor dispone de API, validación de seguridad, persistencia, procesamiento asíncrono, control de duplicados y reintentos.

La validación local ha superado las 13 pruebas automatizadas.

La integración real con GitHub y la exposición segura del endpoint quedan pendientes para una fase posterior.
