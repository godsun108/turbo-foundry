"""Append-only event fingerprints and conflict detection for offline callbacks."""
import hashlib
import json
import sqlite3
from dataclasses import dataclass

@dataclass(frozen=True)
class IntegrityResult:
    accepted: bool
    reason: str

class EventIntegrity:
    def __init__(self, db_path: str):
        self.db_path=db_path
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS event_fingerprints (
                tenant_id TEXT NOT NULL, event_key TEXT NOT NULL,
                fingerprint TEXT NOT NULL, PRIMARY KEY(tenant_id,event_key))""")
            db.execute("""CREATE TABLE IF NOT EXISTS event_conflicts (
                tenant_id TEXT NOT NULL, event_key TEXT NOT NULL,
                observed_fingerprint TEXT NOT NULL, expected_fingerprint TEXT NOT NULL,
                PRIMARY KEY(tenant_id,event_key,observed_fingerprint))""")

    def _connect(self):
        return sqlite3.connect(self.db_path,timeout=10)

    def register(self, tenant_id: str, event_key: str, authenticated_fields: dict) -> IntegrityResult:
        if not tenant_id or not event_key or not isinstance(authenticated_fields,dict):
            return IntegrityResult(False,"invalid_event")
        canonical=json.dumps(authenticated_fields,sort_keys=True,separators=(",",":"),ensure_ascii=True)
        digest=hashlib.sha256(canonical.encode()).hexdigest()
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            existing=db.execute("SELECT fingerprint FROM event_fingerprints WHERE tenant_id=? AND event_key=?",
                                (tenant_id,event_key)).fetchone()
            if existing:
                if existing[0]==digest:
                    return IntegrityResult(True,"exact_duplicate")
                db.execute("""INSERT OR IGNORE INTO event_conflicts
                    (tenant_id,event_key,observed_fingerprint,expected_fingerprint)
                    VALUES(?,?,?,?)""",(tenant_id,event_key,digest,existing[0]))
                return IntegrityResult(False,"payload_conflict")
            db.execute("INSERT INTO event_fingerprints VALUES(?,?,?)",(tenant_id,event_key,digest))
            return IntegrityResult(True,"new_event")

    def has_conflict(self,tenant_id: str,event_key: str) -> bool:
        with self._connect() as db:
            return db.execute("SELECT 1 FROM event_conflicts WHERE tenant_id=? AND event_key=?",
                              (tenant_id,event_key)).fetchone() is not None
