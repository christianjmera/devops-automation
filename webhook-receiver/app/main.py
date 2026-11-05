import asyncio
import json
import logging
import re
import uuid

from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI, HTTPException, Request
from starlette.responses import JSONResponse

from app import config, database
from app.security import verify_signature
from app.worker import run_worker


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger("webhook.receiver")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.to_thread(
        database.initialize_database
    )

    await asyncio.to_thread(
        database.recover_processing
    )

    worker_task = asyncio.create_task(
        run_worker()
    )

    logger.info("Webhook receiver iniciado")

    yield

    worker_task.cancel()

    with suppress(asyncio.CancelledError):
        await worker_task

    logger.info("Webhook receiver detenido")


app = FastAPI(
    title="DevOps Automation Webhook Receiver",
    description="Receptor centralizado de eventos GitHub",
    version="2.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    try:
        database.database_health()

        return {
            "status": "healthy",
            "database": "available",
        }

    except Exception:
        logger.exception("Error comprobando la base de datos")

        raise HTTPException(
            status_code=503,
            detail="Servicio no disponible",
        )


@app.post("/webhook")
async def receive_webhook(request: Request):
    content_length = request.headers.get("content-length")

    if content_length:
        try:
            declared_size = int(content_length)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Content-Length inválido",
            )

        if declared_size < 0:
            raise HTTPException(
                status_code=400,
                detail="Content-Length inválido",
            )

        if declared_size > config.MAX_WEBHOOK_BODY_BYTES:
            raise HTTPException(
                status_code=413,
                detail="Payload demasiado grande",
            )

    chunks = []
    total_size = 0

    async for chunk in request.stream():
        total_size += len(chunk)

        if total_size > config.MAX_WEBHOOK_BODY_BYTES:
            raise HTTPException(
                status_code=413,
                detail="Payload demasiado grande",
            )

        chunks.append(chunk)

    body = b"".join(chunks)

    signature = request.headers.get(
        "X-Hub-Signature-256"
    )

    if not verify_signature(body, signature):
        raise HTTPException(
            status_code=401,
            detail="Firma del webhook inválida",
        )

    event = request.headers.get("X-GitHub-Event")
    delivery_id = request.headers.get("X-GitHub-Delivery")

    if not event or not delivery_id:
        raise HTTPException(
            status_code=400,
            detail="Faltan cabeceras obligatorias de GitHub",
        )

    try:
        delivery_id = str(uuid.UUID(delivery_id))
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=400,
            detail="Identificador de entrega inválido",
        )

    if event == "ping":
        return {"status": "pong"}

    if event != "push":
        return {
            "status": "ignored",
            "event": event,
        }

    try:
        data = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(
            status_code=400,
            detail="Payload JSON inválido",
        )

    if not isinstance(data, dict):
        raise HTTPException(
            status_code=400,
            detail="El payload debe ser un objeto JSON",
        )

    repository_data = data.get("repository")

    if not isinstance(repository_data, dict):
        raise HTTPException(
            status_code=400,
            detail="Información del repositorio inválida",
        )

    repository = repository_data.get("full_name")

    if not isinstance(repository, str):
        raise HTTPException(
            status_code=400,
            detail="Nombre del repositorio inválido",
        )

    repository = repository.lower()

    if repository not in config.ALLOWED_REPOSITORIES:
        raise HTTPException(
            status_code=403,
            detail="Repositorio no autorizado",
        )

    ref = data.get("ref")

    if not isinstance(ref, str) or not ref.startswith(
        "refs/heads/"
    ):
        raise HTTPException(
            status_code=400,
            detail="Referencia Git no válida",
        )

    branch = ref.removeprefix("refs/heads/")

    if branch.lower() not in config.ALLOWED_BRANCHES:
        return {
            "status": "ignored",
            "reason": "branch_not_allowed",
            "branch": branch,
        }

    commit_sha = data.get("after")

    if (
        not isinstance(commit_sha, str)
        or not re.fullmatch(r"[0-9a-fA-F]{40}", commit_sha)
    ):
        raise HTTPException(
            status_code=400,
            detail="Identificador de commit inválido",
        )

    sender_data = data.get("sender")
    sender = (
        sender_data.get("login")
        if isinstance(sender_data, dict)
        else None
    )

    delivery = {
        "delivery_id": delivery_id,
        "repository": repository,
        "branch": branch,
        "ref": ref,
        "commit_sha": commit_sha,
        "sender": sender,
    }

    inserted = await asyncio.to_thread(
        database.enqueue_delivery,
        delivery,
    )

    if not inserted:
        logger.info(
            "Entrega duplicada ignorada: %s",
            delivery_id,
        )

        return JSONResponse(
            status_code=202,
            content={
                "status": "duplicate",
                "delivery_id": delivery_id,
            },
        )

    logger.info(
        "Entrega almacenada: %s, repositorio: %s, rama: %s",
        delivery_id,
        repository,
        branch,
    )

    return JSONResponse(
        status_code=202,
        content={
            "status": "accepted",
            "delivery_id": delivery_id,
        },
    )
