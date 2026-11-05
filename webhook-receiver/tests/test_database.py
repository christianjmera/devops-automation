import sqlite3
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from app import config, database


class DatabaseTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_database_path = config.DATABASE_PATH
        self.original_max_attempts = config.MAX_DELIVERY_ATTEMPTS

        config.DATABASE_PATH = Path(self.temp_dir.name) / "events.db"
        config.MAX_DELIVERY_ATTEMPTS = 5

        database.initialize_database()

        self.delivery = {
            "delivery_id": "test-delivery-001",
            "repository": "christianjmera/devops-java-demo",
            "branch": "develop",
            "commit_sha": "a" * 40,
        }

    def tearDown(self):
        config.DATABASE_PATH = self.original_database_path
        config.MAX_DELIVERY_ATTEMPTS = self.original_max_attempts
        self.temp_dir.cleanup()

    def get_delivery(self):
        with sqlite3.connect(config.DATABASE_PATH) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                "SELECT * FROM deliveries WHERE delivery_id = ?",
                (self.delivery["delivery_id"],)
            ).fetchone()

        return dict(row) if row else None

    def test_delivery_persists_in_sqlite(self):
        database.enqueue_delivery(self.delivery)

        result = self.get_delivery()

        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "pending")
        self.assertEqual(result["attempts"], 0)

    def test_processing_delivery_is_recovered(self):
        database.enqueue_delivery(self.delivery)

        claimed = database.claim_next_delivery()
        self.assertEqual(claimed["status"], "processing")
        self.assertEqual(claimed["attempts"], 1)

        database.recover_processing()

        recovered = self.get_delivery()
        self.assertEqual(recovered["status"], "pending")
        self.assertEqual(recovered["attempts"], 1)

        claimed_again = database.claim_next_delivery()
        self.assertEqual(claimed_again["attempts"], 2)

    def test_delivery_cannot_be_claimed_twice(self):
        database.enqueue_delivery(self.delivery)

        first = database.claim_next_delivery()
        second = database.claim_next_delivery()

        self.assertIsNotNone(first)
        self.assertIsNone(second)

    def test_retry_uses_exponential_backoff(self):
        database.enqueue_delivery(self.delivery)
        claimed = database.claim_next_delivery()

        with patch("app.database.time.time", return_value=1000):
            database.mark_failed(
                self.delivery["delivery_id"],
                claimed["attempts"],
                "RuntimeError",
            )

        result = self.get_delivery()

        self.assertEqual(result["status"], "pending")
        self.assertEqual(result["next_attempt_at"], 1030)

        with patch("app.database.time.time", return_value=1029):
            self.assertIsNone(database.claim_next_delivery())

        with patch("app.database.time.time", return_value=1030):
            retry = database.claim_next_delivery()

        self.assertIsNotNone(retry)
        self.assertEqual(retry["attempts"], 2)

    def test_second_retry_uses_sixty_seconds(self):
        database.enqueue_delivery(self.delivery)

        with patch("app.database.time.time", return_value=1000):
            database.mark_failed(
                self.delivery["delivery_id"],
                2,
                "RuntimeError",
            )

        result = self.get_delivery()
        self.assertEqual(result["next_attempt_at"], 1060)

    def test_delivery_fails_after_maximum_attempts(self):
        database.enqueue_delivery(self.delivery)

        with patch("app.database.time.time", return_value=1000):
            database.mark_failed(
                self.delivery["delivery_id"],
                config.MAX_DELIVERY_ATTEMPTS,
                "RuntimeError",
            )

        result = self.get_delivery()

        self.assertEqual(result["status"], "failed")

        with patch("app.database.time.time", return_value=2000):
            self.assertIsNone(database.claim_next_delivery())

    def test_successful_delivery_clears_previous_error(self):
        database.enqueue_delivery(self.delivery)

        with patch("app.database.time.time", return_value=1000):
            database.mark_failed(
                self.delivery["delivery_id"],
                1,
                "RuntimeError",
            )

        database.mark_succeeded(self.delivery["delivery_id"])

        result = self.get_delivery()

        self.assertEqual(result["status"], "succeeded")
        self.assertIsNone(result["last_error"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
