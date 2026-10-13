"""Tenant-scoped consent ledger for offline simulations.

Only authorized application code should write verified consent evidence.
This is not a public consent-capture API and does not establish legal compliance.
"""
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class ConsentState:
    permitted: bool
    opted_out: bool
    evidence_reference: str = ""

class ConsentStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS consent_records(
                tenant_id TEXT NOT NULL, phone TEXT NOT NULL,
                evidence_reference TEXT NOT NULL, source TEXT NOT NULL,
                granted_at TEXT NOT NULL, opted_out INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY(tenant_id, phone))""")

    def _connect(self):
        return sqlite3.connect(self.db_path, timeout=10)

    def grant_verified(self, tenant_id: str, phone: str, evidence_reference: str, source: str, granted_at: datetime) -> bool:
        """Internal trusted-write operation. Never accept webhook-claimed opt-ins."""
        if not all((tenant_id, phone, evidence_reference, source)) or not phone.startswith("+"):
            return False
        if granted_at.tzinfo is None:
            return False
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            current = db.execute("SELECT opted_out FROM consent_records WHERE tenant_id=? AND phone=?",(tenant_id,phone)).fetchone()
            if current and current[0]:
                return False  # sticky opt-out until a separately verified re-subscription process
            db.execute("""INSERT INTO consent_records(tenant_id,phone,evidence_reference,source,granted_at,opted_out)
                VALUES(?,?,?,?,?,0) ON CONFLICT(tenant_id,phone) DO UPDATE SET
                evidence_reference=excluded.evidence_reference,source=excluded.source,
                granted_at=excluded.granted_at""",
                (tenant_id,phone,evidence_reference,source,granted_at.isoformat()))
            return True

    def revoke(self, tenant_id: str, phone: str) -> None:
        if not tenant_id or not phone:
            raise ValueError("tenant and phone required")
        with self._connect() as db:
            db.execute("""INSERT INTO consent_records(tenant_id,phone,evidence_reference,source,granted_at,opted_out)
                VALUES(?,?,?,?,?,1) ON CONFLICT(tenant_id,phone) DO UPDATE SET opted_out=1""",
                (tenant_id,phone,"","opt_out",datetime.now(timezone.utc).isoformat()))

    def lookup(self, tenant_id: str, phone: str) -> ConsentState:
        with self._connect() as db:
            row = db.execute("SELECT evidence_reference,opted_out FROM consent_records WHERE tenant_id=? AND phone=?",
                             (tenant_id,phone)).fetchone()
        if not row:
            return ConsentState(False, False)
        return ConsentState(bool(row[0]) and not bool(row[1]), bool(row[1]), row[0])
