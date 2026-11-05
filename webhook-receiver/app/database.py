import json
import sqlite3
import time

from app import config


def connect():
    config.DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        config.DATABASE_PATH,
        timeout=30,
    )

    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 30000")

    return connection


def initialize_database():
    with connect() as connection:
        connection.execute("PRAGMA journal_mode = WAL")

        connection.execute("""
            CREATE TABLE IF NOT EXISTS deliveries (
                delivery_id TEXT PRIMARY KEY,
                repository TEXT NOT NULL,
                branch TEXT NOT NULL,
                commit_sha TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                attempts INTEGER NOT NULL DEFAULT 0,
                next_attempt_at REAL NOT NULL DEFAULT 0,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                last_error TEXT
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_deliveries_pending
            ON deliveries(status, next_attempt_at, created_at)
        """)


def recover_processing():
    """
    Recupera eventos que quedaron en procesamiento
    si el servicio se detuvo inesperadamente.
    """
    with connect() as connection:
        connection.execute("""
            UPDATE deliveries
            SET status = 'pending',
                updated_at = ?
            WHERE status = 'processing'
        """, (time.time(),))


def enqueue_delivery(delivery):
    now = time.time()

    with connect() as connection:
        cursor = connection.execute("""
            INSERT OR IGNORE INTO deliveries (
                delivery_id,
                repository,
                branch,
                commit_sha,
                payload_json,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)
        """, (
            delivery["delivery_id"],
            delivery["repository"],
            delivery["branch"],
            delivery["commit_sha"],
            json.dumps(delivery),
            now,
            now,
        ))

        return cursor.rowcount == 1


def claim_next_delivery():
    """
    Reclama atómicamente el siguiente evento pendiente.
    """
    with connect() as connection:
        connection.execute("BEGIN IMMEDIATE")

        row = connection.execute("""
            SELECT delivery_id
            FROM deliveries
            WHERE status = 'pending'
              AND next_attempt_at <= ?
            ORDER BY created_at
            LIMIT 1
        """, (time.time(),)).fetchone()

        if row is None:
            connection.commit()
            return None

        delivery_id = row["delivery_id"]

        connection.execute("""
            UPDATE deliveries
            SET status = 'processing',
                attempts = attempts + 1,
                updated_at = ?
            WHERE delivery_id = ?
              AND status = 'pending'
        """, (time.time(), delivery_id))

        result = connection.execute("""
            SELECT *
            FROM deliveries
            WHERE delivery_id = ?
        """, (delivery_id,)).fetchone()

        connection.commit()

        return dict(result)


def mark_succeeded(delivery_id):
    with connect() as connection:
        connection.execute("""
            UPDATE deliveries
            SET status = 'succeeded',
                updated_at = ?,
                last_error = NULL
            WHERE delivery_id = ?
        """, (time.time(), delivery_id))


def mark_failed(delivery_id, attempts, error):
    now = time.time()

    if attempts >= config.MAX_DELIVERY_ATTEMPTS:
        status = "failed"
        next_attempt = now
    else:
        status = "pending"

        delay = min(
            30 * (2 ** (attempts - 1)),
            1800,
        )

        next_attempt = now + delay

    with connect() as connection:
        connection.execute("""
            UPDATE deliveries
            SET status = ?,
                next_attempt_at = ?,
                updated_at = ?,
                last_error = ?
            WHERE delivery_id = ?
        """, (
            status,
            next_attempt,
            now,
            error[:500],
            delivery_id,
        ))


def database_health():
    with connect() as connection:
        connection.execute("SELECT 1").fetchone()
