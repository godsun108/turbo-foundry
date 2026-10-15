"""Explicit read-only view of operator state, for offline trust-boundary tests.

This view opens the existing SQLite database in mode=ro and exposes no
mutation methods. Deployment must also enforce filesystem/process isolation:
Python modules alone do not establish an OS security boundary.
"""
from dataclasses import dataclass
from pathlib import Path
import sqlite3
from urllib.parse import quote


@dataclass(frozen=True)
class OperatorState:
    enabled: bool
    audit_events: int


class ReadOnlyOperatorView:
    def __init__(self, db_path: str):
        if not isinstance(db_path, str) or not db_path.strip():
            raise ValueError("database path required")
        self.db_path = db_path

    def connect(self):
        path = Path(self.db_path).resolve()
        return sqlite3.connect(
            "file:" + quote(path.as_posix(), safe="/") + "?mode=ro",
            uri=True,
        )

    def snapshot(self) -> OperatorState:
        """Fail closed on missing/corrupted schema instead of creating one."""
        with self.connect() as db:
            row = db.execute("""SELECT enabled FROM worker_control
                WHERE name='read_only_recheck'""").fetchone()
            count = db.execute(
                "SELECT COUNT(*) FROM worker_control_audit"
            ).fetchone()[0]
            return OperatorState(enabled=row is not None and row[0] == 1,
                                 audit_events=count)
