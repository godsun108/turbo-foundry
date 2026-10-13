"""Durable simulated delivery attempts; no network calls.

An atomic claim prevents concurrent workers from sending the same message.
Production providers must support idempotency or reconciliation after crashes.
"""
import sqlite3
from datetime import datetime, timezone, timedelta
from .queue import MessageQueue

class MockDelivery:
    def __init__(self, queue: MessageQueue):
        self.queue = queue
        with self.queue._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS delivery_attempts (
                key TEXT PRIMARY KEY, tenant_id TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                last_attempt TEXT, state TEXT NOT NULL DEFAULT 'pending'
            )""")

    def attempt(self, key: str, tenant_id: str, *, simulate_failure: bool = False, max_attempts: int = 3) -> str:
        """Mock-only delivery with bounded retries and atomic claim."""
        if max_attempts < 1:
            return "invalid_policy"
        with self.queue._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT recipient FROM messages WHERE key=? AND tenant_id=? AND status='queued'",
                (key, tenant_id),
            ).fetchone()
            if row is None:
                return "not_queued"
            if db.execute("SELECT 1 FROM suppression WHERE tenant_id=? AND recipient=?", (tenant_id, row[0])).fetchone():
                db.execute("UPDATE messages SET status='suppressed' WHERE key=? AND tenant_id=?", (key, tenant_id))
                return "suppressed"
            db.execute("INSERT OR IGNORE INTO delivery_attempts(key,tenant_id) VALUES (?,?)", (key, tenant_id))
            record = db.execute("SELECT attempts,state FROM delivery_attempts WHERE key=? AND tenant_id=?", (key, tenant_id)).fetchone()
            attempts, state = record
            if state in ("simulated", "exhausted") or attempts >= max_attempts:
                return "exhausted" if state != "simulated" else "already_simulated"
            attempts += 1
            status = "failed" if simulate_failure else "simulated"
            if simulate_failure and attempts >= max_attempts:
                status = "exhausted"
            db.execute(
                "UPDATE delivery_attempts SET attempts=?,last_attempt=?,state=? WHERE key=? AND tenant_id=?",
                (attempts, datetime.now(timezone.utc).isoformat(), status, key, tenant_id),
            )
            if status == "simulated":
                db.execute("UPDATE messages SET status='simulated' WHERE key=? AND tenant_id=? AND status='queued'", (key, tenant_id))
            if status == "exhausted":
                db.execute("UPDATE messages SET status='failed' WHERE key=? AND tenant_id=? AND status='queued'", (key, tenant_id))
            return status
