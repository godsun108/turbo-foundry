"""Persistent fail-closed operator gate for read-only worker invocations.

This does not provide a live remote kill switch or authorize production access.
"""
import sqlite3


class WorkerControl:
    def __init__(self, db_path: str):
        self.db_path = db_path
        with sqlite3.connect(db_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS worker_control (
                name TEXT PRIMARY KEY,
                enabled INTEGER NOT NULL CHECK (enabled IN (0,1))
            )""")

    def set_enabled(self, enabled: bool):
        if type(enabled) is not bool:
            raise ValueError("enabled must be boolean")
        with sqlite3.connect(self.db_path) as db:
            db.execute("""INSERT INTO worker_control(name,enabled)
                VALUES ('read_only_recheck',?)
                ON CONFLICT(name) DO UPDATE SET enabled=excluded.enabled""",
                (int(enabled),))

    def is_enabled(self) -> bool:
        try:
            with sqlite3.connect(self.db_path) as db:
                row = db.execute(
                    "SELECT enabled FROM worker_control WHERE name='read_only_recheck'"
                ).fetchone()
                return row is not None and row[0] == 1
        except (sqlite3.Error, OSError):
            return False
