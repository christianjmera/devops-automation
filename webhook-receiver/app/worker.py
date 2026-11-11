import asyncio
import json
import logging
import urllib.error
import urllib.request

from app import config, database
from github_app_auth import get_installation_token


logger = logging.getLogger("webhook.worker")


def send_repository_dispatch(token, payload):
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
        with urllib.request.urlopen(
            request,
            timeout=20,
        ) as response:
            return response.status

    except urllib.error.HTTPError as error:
        raise RuntimeError(
            f"GitHub API respondió HTTP {error.code}"
        ) from error

    except urllib.error.URLError as error:
        raise RuntimeError(
            "No se pudo conectar con GitHub API"
        ) from error

async def process_delivery(delivery):
    token = await asyncio.to_thread(
        get_installation_token,
        config.GITHUB_APP_ID,
        config.GITHUB_INSTALLATION_ID,
        str(config.GITHUB_PRIVATE_KEY),
        repositories=[
            config.CENTRAL_REPOSITORY.split("/", 1)[1]
        ],
        permissions={
            "contents": "write"
        },
    )

    payload = json.loads(delivery["payload_json"])

    status = await asyncio.to_thread(
        send_repository_dispatch,
        token,
        payload,
    )

    if status != 204:
        raise RuntimeError(
            f"Respuesta inesperada de GitHub: HTTP {status}"
        )

async def run_worker():
    logger.info("Procesador de eventos iniciado")

    while True:
        delivery = await asyncio.to_thread(
            database.claim_next_delivery
        )

        if delivery is None:
            await asyncio.sleep(
                config.WORKER_POLL_SECONDS
            )
            continue

        delivery_id = delivery["delivery_id"]

        try:
            await process_delivery(delivery)

            await asyncio.to_thread(
                database.mark_succeeded,
                delivery_id,
            )

            logger.info(
                "Entrega procesada correctamente: %s",
                delivery_id,
            )

        except asyncio.CancelledError:
            raise

        except Exception as error:
            logger.error(
                "Error procesando entrega %s: %s",
                delivery_id,
                type(error).__name__,
            )

            await asyncio.to_thread(
                database.mark_failed,
                delivery_id,
                delivery["attempts"],
                type(error).__name__,
            )
