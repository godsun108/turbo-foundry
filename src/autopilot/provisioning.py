"""Offline provisioned-number ownership registry; no provider account mutations."""
import sqlite3
from dataclasses import dataclass

@dataclass(frozen=True)
class ProvisioningResult:
    accepted: bool
    reason: str

class NumberProvisioning:
    def __init__(self,db_path: str):
        self.db_path=db_path
        with sqlite3.connect(db_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS provisioned_numbers (
                phone_number TEXT PRIMARY KEY, tenant_id TEXT NOT NULL,
                provider_account_sid TEXT NOT NULL, enabled INTEGER NOT NULL
            )""")

    def provision(self, *, phone_number: str, tenant_id: str,
                  provider_account_sid: str) -> ProvisioningResult:
        """Administrative offline fixture only; must be access-controlled in production."""
        if not phone_number.startswith("+") or not phone_number[1:].isdigit() or not tenant_id or not provider_account_sid:
            return ProvisioningResult(False,"invalid_provisioning")
        with sqlite3.connect(self.db_path,timeout=10) as db:
            db.execute("BEGIN IMMEDIATE")
            existing=db.execute("SELECT tenant_id,provider_account_sid FROM provisioned_numbers WHERE phone_number=?",
                                (phone_number,)).fetchone()
            if existing:
                return ProvisioningResult(existing==(tenant_id,provider_account_sid),
                    "already_provisioned" if existing==(tenant_id,provider_account_sid) else "number_owned_by_other_account")
            db.execute("INSERT INTO provisioned_numbers VALUES(?,?,?,1)",
                       (phone_number,tenant_id,provider_account_sid))
        return ProvisioningResult(True,"provisioned")

    def verify(self, *, phone_number: str, tenant_id: str,
               provider_account_sid: str) -> bool:
        with sqlite3.connect(self.db_path,timeout=10) as db:
            return db.execute("""SELECT 1 FROM provisioned_numbers WHERE
                phone_number=? AND tenant_id=? AND provider_account_sid=? AND enabled=1""",
                (phone_number,tenant_id,provider_account_sid)).fetchone() is not None

    def disable(self,phone_number: str):
        with sqlite3.connect(self.db_path,timeout=10) as db:
            db.execute("UPDATE provisioned_numbers SET enabled=0 WHERE phone_number=?",(phone_number,))
