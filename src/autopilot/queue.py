"""SQLite-backed, idempotent simulated messaging queue. No external delivery."""
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

@dataclass(frozen=True)
class QueuedMessage:
    key: str
    tenant_id: str
    recipient: str
    body: str

class MessageQueue:
    def __init__(self, db_path: str):
        self.db_path = str(db_path)
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS messages (
                key TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                recipient TEXT NOT NULL,
                body TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'queued',
                created_at TEXT NOT NULL
            )""")
            db.execute("""CREATE TABLE IF NOT EXISTS suppression (
                tenant_id TEXT NOT NULL,
                recipient TEXT NOT NULL,
                PRIMARY KEY (tenant_id, recipient)
            )""")

    def _connect(self):
        return sqlite3.connect(self.db_path, timeout=10)

    def suppress(self, tenant_id: str, recipient: str) -> None:
        with self._connect() as db:
            db.execute("INSERT OR IGNORE INTO suppression VALUES (?, ?)", (tenant_id, recipient))
            db.execute("UPDATE messages SET status='suppressed' WHERE tenant_id=? AND recipient=? AND status='queued'", (tenant_id, recipient))

    def enqueue(self, item: QueuedMessage) -> bool:
        """Atomically reject duplicate keys and suppressed contacts."""
        if not item.key.startswith(item.tenant_id + ":") or not item.recipient or not item.body:
            return False
        with self._connect() as db:
            if db.execute("SELECT 1 FROM suppression WHERE tenant_id=? AND recipient=?", (item.tenant_id, item.recipient)).fetchone():
                return False
            cur = db.execute(
                "INSERT OR IGNORE INTO messages(key,tenant_id,recipient,body,status,created_at) VALUES (?,?,?,?,?,?)",
                (item.key, item.tenant_id, item.recipient, item.body, "queued", datetime.now(timezone.utc).isoformat()),
            )
            return cur.rowcount == 1

    def status(self, key: str, tenant_id: str) -> str | None:
        with self._connect() as db:
            row = db.execute("SELECT status FROM messages WHERE key=? AND tenant_id=?", (key, tenant_id)).fetchone()
            return row[0] if row else None

    def simulate_delivery(self, key: str, tenant_id: str) -> bool:
        """Mock delivery only; conditional update prevents repeat processing."""
        with self._connect() as db:
            row = db.execute("SELECT recipient FROM messages WHERE key=? AND tenant_id=? AND status='queued'", (key, tenant_id)).fetchone()
            if not row:
                return False
            if db.execute("SELECT 1 FROM suppression WHERE tenant_id=? AND recipient=?", (tenant_id, row[0])).fetchone():
                db.execute("UPDATE messages SET status='suppressed' WHERE key=? AND tenant_id=?", (key, tenant_id))
                return False
            cur = db.execute("UPDATE messages SET status='simulated' WHERE key=? AND tenant_id=? AND status='queued'", (key, tenant_id))
            return cur.rowcount == 1
