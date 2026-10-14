"""Offline persisted bounded operator attempt gate; no external services.

A fixed-window quota limits attempts per known operator ID. This is only a
local defense-in-depth control, not IP throttling, MFA, or an auth service.
"""
import sqlite3
from datetime import datetime, timezone


class OperatorAttemptLimiter:
    def __init__(self, db_path):
        self.db_path = db_path
        with sqlite3.connect(db_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS operator_attempt_windows (
                operator_id TEXT NOT NULL,
                window_start INTEGER NOT NULL,
                attempts INTEGER NOT NULL,
                PRIMARY KEY (operator_id,window_start)
            )""")

    def allow(self, operator_id, *, now=None, max_attempts=5, window_seconds=300):
        if (not isinstance(operator_id,str) or not operator_id.strip()
                or not isinstance(max_attempts,int) or isinstance(max_attempts,bool)
                or not 1<=max_attempts<=100
                or not isinstance(window_seconds,int) or isinstance(window_seconds,bool)
                or not 1<=window_seconds<=86400):
            return False
        if now is None:
            now=datetime.now(timezone.utc)
        if (not isinstance(now,datetime) or now.tzinfo is None
                or now.utcoffset() is None):
            return False
        bucket=int(now.timestamp())//window_seconds*window_seconds
        try:
            with sqlite3.connect(self.db_path,timeout=10) as db:
                db.execute("BEGIN IMMEDIATE")
                row=db.execute("""SELECT attempts FROM operator_attempt_windows
                    WHERE operator_id=? AND window_start=?""",
                    (operator_id,bucket)).fetchone()
                if row is not None and row[0]>=max_attempts:
                    return False
                db.execute("""INSERT INTO operator_attempt_windows
                    (operator_id,window_start,attempts) VALUES (?,?,1)
                    ON CONFLICT(operator_id,window_start)
                    DO UPDATE SET attempts=attempts+1""",(operator_id,bucket))
            return True
        except (sqlite3.Error,OSError,OverflowError,ValueError):
            return False
