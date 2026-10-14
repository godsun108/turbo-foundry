"""Persistent worker stop gate with local transactional operator audit.

Actor strings are caller claims, NOT authenticated operator identities.
No live deployment, provider access, or customer messaging is authorized.
"""
import sqlite3
from datetime import datetime, timezone


class WorkerControl:
    def __init__(self, db_path: str):
        self.db_path = db_path
        with sqlite3.connect(db_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS worker_control (
                name TEXT PRIMARY KEY,
                enabled INTEGER NOT NULL CHECK (enabled IN (0,1))
            )""")
            db.execute("""CREATE TABLE IF NOT EXISTS worker_control_audit (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                occurred_at TEXT NOT NULL,
                actor TEXT NOT NULL,
                reason TEXT NOT NULL,
                previous_enabled INTEGER,
                new_enabled INTEGER NOT NULL CHECK(new_enabled IN (0,1))
            )""")

    def set_enabled(self, enabled: bool, *, actor="unattributed_local_caller",
                    reason="legacy_local_call", now=None):
        """Persist the transition and its claimed provenance in one transaction.

        Legacy callers get an explicit unattributed marker; production requires
        an independent authenticated operator boundary.
        """
        if type(enabled) is not bool:
            raise ValueError("enabled must be boolean")
        if (not isinstance(actor, str) or not actor.strip() or len(actor)>128
                or not isinstance(reason, str) or not reason.strip() or len(reason)>512):
            raise ValueError("operator actor/reason required")
        if now is None:
            now = datetime.now(timezone.utc)
        if not isinstance(now,datetime) or now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("timezone-aware audit timestamp required")
        stamp = now.astimezone(timezone.utc).isoformat()
        with sqlite3.connect(self.db_path, timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute(
                "SELECT enabled FROM worker_control WHERE name='read_only_recheck'"
            ).fetchone()
            db.execute("""INSERT INTO worker_control(name,enabled)
                VALUES ('read_only_recheck',?)
                ON CONFLICT(name) DO UPDATE SET enabled=excluded.enabled""",
                (int(enabled),))
            db.execute("""INSERT INTO worker_control_audit
                (occurred_at,actor,reason,previous_enabled,new_enabled)
                VALUES (?,?,?,?,?)""",
                (stamp,actor,reason,None if prior is None else prior[0],int(enabled)))

    def audit_events(self, *, limit=50):
        """Read local audit records, newest first; not tamper-proof."""
        if type(limit) is not int or not 1<=limit<=100:
            raise ValueError("invalid limit")
        with sqlite3.connect(self.db_path) as db:
            return db.execute("""SELECT event_id,occurred_at,actor,reason,
                previous_enabled,new_enabled FROM worker_control_audit
                ORDER BY event_id DESC LIMIT ?""",(limit,)).fetchall()

    def is_enabled(self) -> bool:
        try:
            with sqlite3.connect(self.db_path) as db:
                row = db.execute(
                    "SELECT enabled FROM worker_control WHERE name='read_only_recheck'"
                ).fetchone()
                return row is not None and row[0] == 1
        except (sqlite3.Error, OSError):
            return False
