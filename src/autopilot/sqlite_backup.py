"""Offline SQLite backup with integrity validation; no network or live provider access."""
import os
import sqlite3
from pathlib import Path


def backup_readonly_state(source: str, destination: str) -> None:
    """Back up an existing SQLite database to a new path, refusing overwrite.

    Callers must quiesce writers for a consistent operational recovery point.
    SQLite's backup API supplies a transactionally consistent copy; the policy
    still requires an operator to validate restore against their RPO/RTO.
    """
    src = Path(source).resolve()
    dst = Path(destination).resolve()
    if src == dst:
        raise ValueError("source and destination must differ")
    if not src.is_file():
        raise FileNotFoundError("source database missing")
    if dst.exists():
        raise FileExistsError("backup destination exists")
    # Exclusive creation ensures we do not clobber any existing backup.
    fd = os.open(dst, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(fd)
    try:
        with sqlite3.connect(f"file:{src.as_posix()}?mode=ro", uri=True) as origin:
            with sqlite3.connect(str(dst)) as target:
                origin.backup(target)
                integrity = target.execute("PRAGMA integrity_check").fetchone()
                if integrity is None or integrity[0] != "ok":
                    raise RuntimeError("backup failed integrity check")
    except BaseException:
        dst.unlink(missing_ok=True)
        raise
