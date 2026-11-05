import asyncio
import hashlib
import hmac
import json
import tempfile
import unittest
import uuid

from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import config, main


async def idle_worker():
    """Mantiene el worker inactivo durante las pruebas."""
    await asyncio.Event().wait()


class WebhookReceiverTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_database_path = config.DATABASE_PATH
        config.DATABASE_PATH = Path(self.temp_dir.name) / "events.db"

        self.worker_patch = patch(
            "app.main.run_worker",
            new=idle_worker
        )
        self.worker_patch.start()

        self.client_context = TestClient(main.app)
        self.client = self.client_context.__enter__()

        self.delivery_id = str(uuid.uuid4())

        self.payload = {
            "ref": "refs/heads/develop",
            "after": "a" * 40,
            "repository": {
                "full_name": next(iter(config.ALLOWED_REPOSITORIES))
            },
            "sender": {
                "login": "test-user"
            }
        }

    def tearDown(self):
        self.client_context.__exit__(None, None, None)
        self.worker_patch.stop()
        config.DATABASE_PATH = self.original_database_path
        self.temp_dir.cleanup()

    def post_webhook(self, payload=None, delivery_id=None,
                     event="push", secret=None):

        body = json.dumps(
            payload if payload is not None else self.payload
        ).encode()

        signing_secret = (
            secret if secret is not None
            else config.GITHUB_WEBHOOK_SECRET
        )

        signature = hmac.new(
            signing_secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()

        return self.client.post(
            "/webhook",
            content=body,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": f"sha256={signature}",
                "X-GitHub-Event": event,
                "X-GitHub-Delivery": delivery_id or self.delivery_id
            }
        )

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)

    def test_invalid_signature_is_rejected(self):
        response = self.post_webhook(secret="invalid-secret")
        self.assertEqual(response.status_code, 401)

    def test_unauthorized_repository_is_rejected(self):
        payload = dict(self.payload)
        payload["repository"] = {
            "full_name": "otro-usuario/repositorio-no-autorizado"
        }

        response = self.post_webhook(payload=payload)
        self.assertEqual(response.status_code, 403)

    def test_unauthorized_branch_is_rejected(self):
        payload = dict(self.payload)
        payload["ref"] = "refs/heads/main"

        response = self.post_webhook(payload=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ignored")
        self.assertEqual(response.json()["reason"], "branch_not_allowed")

    def test_valid_push_is_accepted(self):
        response = self.post_webhook()

        self.assertEqual(response.status_code, 202)

        import sqlite3
        with sqlite3.connect(config.DATABASE_PATH) as connection:
            count = connection.execute(
                "SELECT COUNT(*) FROM deliveries"
            ).fetchone()[0]

        self.assertEqual(count, 1)

    def test_duplicate_delivery_is_not_inserted_twice(self):
        first = self.post_webhook()
        second = self.post_webhook()

        self.assertEqual(first.status_code, 202)
        self.assertEqual(second.status_code, 202)

        import sqlite3
        with sqlite3.connect(config.DATABASE_PATH) as connection:
            count = connection.execute(
                "SELECT COUNT(*) FROM deliveries"
            ).fetchone()[0]

        self.assertEqual(count, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
