import os


def required_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Falta la variable de entorno: {name}")
    return value


GITHUB_APP_ID = required_env("GITHUB_APP_ID")
GITHUB_INSTALLATION_ID = required_env("GITHUB_INSTALLATION_ID")
GITHUB_PRIVATE_KEY = os.path.expanduser(
    required_env("GITHUB_PRIVATE_KEY")
)
GITHUB_WEBHOOK_SECRET = required_env("GITHUB_WEBHOOK_SECRET")

CENTRAL_REPOSITORY = required_env("CENTRAL_REPOSITORY")

ALLOWED_REPOSITORIES = {
    repo.strip().lower()
    for repo in required_env("ALLOWED_REPOSITORIES").split(",")
    if repo.strip()
}

