import json
import urllib.error
import urllib.request

from fastapi import FastAPI, HTTPException, Request

from app import config
from app.security import verify_signature
from github_app_auth import get_installation_token

app = FastAPI(
    title="DevOps Automation Webhook Receiver",
    description="Receptor centralizado de eventos GitHub",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {"status": "healthy"}


def send_repository_dispatch(token: str, payload: dict):
    owner, repository = config.CENTRAL_REPOSITORY.split("/", 1)

    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repository}/dispatches"
    )

    body = json.dumps({
        "event_type": "application_push",
        "client_payload": payload,
    }).encode()

    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status

    except (urllib.error.HTTPError, urllib.error.URLError) as error:
        raise HTTPException(
            status_code=502,
            detail="No se pudo enviar el evento al repositorio central",
        ) from error


@app.post("/webhook")
async def receive_webhook(request: Request):
    body = await request.body()

    signature = request.headers.get("X-Hub-Signature-256")

    if not verify_signature(body, signature):
        raise HTTPException(
            status_code=401,
            detail="Firma del webhook inválida",
        )

    event = request.headers.get("X-GitHub-Event")
    delivery_id = request.headers.get("X-GitHub-Delivery")

    if event == "ping":
        return {"status": "pong"}

    if event != "push":
        return {
            "status": "ignored",
            "event": event,
        }

    try:
        data = json.loads(body)
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=400,
            detail="Payload JSON inválido",
        ) from error

    repository = data.get("repository", {}).get("full_name", "").lower()

    if repository not in config.ALLOWED_REPOSITORIES:
        raise HTTPException(
            status_code=403,
            detail="Repositorio no autorizado",
        )

    ref = data.get("ref", "")

    if not ref.startswith("refs/heads/"):
        raise HTTPException(
            status_code=400,
            detail="Referencia Git no válida",
        )

    branch = ref.removeprefix("refs/heads/")

    payload = {
        "repository": repository,
        "branch": branch,
        "ref": ref,
        "commit_sha": data.get("after"),
        "delivery_id": delivery_id,
        "sender": data.get("sender", {}).get("login"),
    }

    token = get_installation_token(
        config.GITHUB_APP_ID,
        config.GITHUB_INSTALLATION_ID,
        config.GITHUB_PRIVATE_KEY,
    )

    github_status = send_repository_dispatch(token, payload)

    return {
        "status": "dispatched",
        "repository": repository,
        "branch": branch,
        "github_status": github_status,
    }
