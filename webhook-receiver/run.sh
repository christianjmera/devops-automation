#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"

CONFIG_DIR="$HOME/.config/devops-automation/github-app"

APP_ENV="$CONFIG_DIR/app.env"
WEBHOOK_ENV="$CONFIG_DIR/webhook.env"

if [[ ! -x "$VENV_DIR/bin/uvicorn" ]]; then
    echo "ERROR: No se encontró Uvicorn en $VENV_DIR/bin/uvicorn"
    echo "Comprueba que el entorno virtual esté creado y las dependencias instaladas."
    exit 1
fi

if [[ ! -f "$APP_ENV" || ! -f "$WEBHOOK_ENV" ]]; then
    echo "ERROR: No se encontraron los archivos de configuración."
    exit 1
fi

set -a
source "$APP_ENV"
source "$WEBHOOK_ENV"
set +a

cd "$SCRIPT_DIR"

exec "$VENV_DIR/bin/uvicorn" app.main:app \
    --app-dir "$SCRIPT_DIR" \
    --host 127.0.0.1 \
    --port 8000
