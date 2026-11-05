import os
from pathlib import Path


def required_env(name):
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"Falta la variable de entorno: {name}"
        )

    return value.strip()


def csv_env(name, default=""):
    value = os.getenv(name, default)

    return {
        item.strip().lower()
        for item in value.split(",")
        if item.strip()
    }


def positive_int(name, default):
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError as error:
        raise RuntimeError(
            f"La variable {name} debe ser un entero"
        ) from error

    if value <= 0:
        raise RuntimeError(
            f"La variable {name} debe ser mayor que cero"
        )

    return value


GITHUB_APP_ID = required_env("GITHUB_APP_ID")
GITHUB_INSTALLATION_ID = required_env(
    "GITHUB_INSTALLATION_ID"
)

GITHUB_PRIVATE_KEY = Path(
    os.path.expanduser(
        required_env("GITHUB_PRIVATE_KEY")
    )
)

GITHUB_WEBHOOK_SECRET = required_env(
    "GITHUB_WEBHOOK_SECRET"
)

if len(GITHUB_WEBHOOK_SECRET) < 32:
    raise RuntimeError(
        "GITHUB_WEBHOOK_SECRET debe tener al menos 32 caracteres"
    )

if not GITHUB_PRIVATE_KEY.is_file():
    raise RuntimeError(
        "No existe el archivo de clave privada de GitHub App"
    )

CENTRAL_REPOSITORY = required_env(
    "CENTRAL_REPOSITORY"
).lower()

if CENTRAL_REPOSITORY.count("/") != 1:
    raise RuntimeError(
        "CENTRAL_REPOSITORY debe tener formato propietario/repositorio"
    )

ALLOWED_REPOSITORIES = csv_env(
    "ALLOWED_REPOSITORIES"
)

if not ALLOWED_REPOSITORIES:
    raise RuntimeError(
        "ALLOWED_REPOSITORIES no puede estar vacío"
    )

ALLOWED_BRANCHES = csv_env(
    "ALLOWED_BRANCHES",
    "develop,qa,uat,prod",
)

MAX_WEBHOOK_BODY_BYTES = positive_int(
    "MAX_WEBHOOK_BODY_BYTES",
    1048576,
)

MAX_DELIVERY_ATTEMPTS = positive_int(
    "MAX_DELIVERY_ATTEMPTS",
    5,
)

WORKER_POLL_SECONDS = positive_int(
    "WORKER_POLL_SECONDS",
    2,
)

DATABASE_PATH = Path(
    os.path.expanduser(
        os.getenv(
            "WEBHOOK_DATABASE_PATH",
            "~/.local/share/devops-automation/webhook/events.db",
        )
    )
)
