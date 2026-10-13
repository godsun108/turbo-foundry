"""Persistent, fail-closed mock delivery reconciliation; no provider calls."""
from datetime import datetime, timezone
from .queue import MessageQueue
from .recovery import Outcome, decide_recovery

class ReconciliationStore:
    def __init__(self, queue: MessageQueue):
        self.queue = queue
        with queue._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS reconciliation (
                key TEXT NOT NULL, tenant_id TEXT NOT NULL,
                outcome TEXT NOT NULL, action TEXT NOT NULL,
                reason TEXT NOT NULL, updated_at TEXT NOT NULL,
                PRIMARY KEY(key,tenant_id)
            )""")

    def record(self, key: str, tenant_id: str, outcome: Outcome,
               *, provider_supports_idempotency: bool,
               lookup_confirms_absence: bool = False) -> str:
        decision = decide_recovery(outcome, provider_supports_idempotency=provider_supports_idempotency,
                                   lookup_confirms_absence=lookup_confirms_absence)
        with self.queue._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            message = db.execute("SELECT status FROM messages WHERE key=? AND tenant_id=?", (key, tenant_id)).fetchone()
            if message is None:
                return "unknown_message"
            existing = db.execute("SELECT action FROM reconciliation WHERE key=? AND tenant_id=?", (key, tenant_id)).fetchone()
            if existing and existing[0] in ("close", "stop"):
                return existing[0]
            db.execute("""INSERT INTO reconciliation(key,tenant_id,outcome,action,reason,updated_at)
                VALUES (?,?,?,?,?,?)
                ON CONFLICT(key,tenant_id) DO UPDATE SET outcome=excluded.outcome,
                action=excluded.action,reason=excluded.reason,updated_at=excluded.updated_at""",
                (key,tenant_id,outcome.value,decision.action,decision.reason,datetime.now(timezone.utc).isoformat()))
            return decision.action

    def action(self, key: str, tenant_id: str) -> str | None:
        with self.queue._connect() as db:
            row = db.execute("SELECT action FROM reconciliation WHERE key=? AND tenant_id=?", (key,tenant_id)).fetchone()
            return row[0] if row else None
