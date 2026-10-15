"""Locally controlled authorization and audit for provider-neutral history reads.

NOT an authentication server, HTTP endpoint, or trusted production boundary.
The operator identity and fixture bindings must be injected by a privileged,
separately authenticated runtime. All records here are synthetic/offline.
A direct ReadOnlyGateway.observe() call bypasses this facade entirely.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import sqlite3

from .universal_gateway import GatewayResult, ReadOnlyGateway


@dataclass(frozen=True)
class TrustedReader:
    identity: str


def _key(value):
    return (isinstance(value, str) and 1 <= len(value) <= 100
            and all(c.isascii() and (c.isalnum() or c in "_-") for c in value))


class AuditedGatewayReads:
    """Privileged local binding registry; fail closed when audit unavailable."""

    def __init__(self, db_path: str, gateway: ReadOnlyGateway,
                 operator_tenants: dict[str, frozenset[str]]):
        if not isinstance(gateway, ReadOnlyGateway) or not isinstance(operator_tenants, dict):
            raise ValueError("trusted gateway and operator mapping required")
        for identity, tenants in operator_tenants.items():
            if (not _key(identity) or not isinstance(tenants, frozenset)
                    or any(not _key(t) for t in tenants)):
                raise ValueError("invalid operator tenant mapping")
        self.db_path = db_path
        self.gateway = gateway
        self._operator_tenants = dict(operator_tenants)
        with sqlite3.connect(db_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS gateway_read_bindings (
                tenant_id TEXT NOT NULL, provider TEXT NOT NULL,
                parent_id TEXT NOT NULL,
                PRIMARY KEY (tenant_id,provider,parent_id))""")
            db.execute("""CREATE TABLE IF NOT EXISTS gateway_read_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                at_utc TEXT NOT NULL, actor TEXT NOT NULL, tenant_id TEXT NOT NULL,
                provider TEXT NOT NULL, parent_id TEXT NOT NULL,
                allowed INTEGER NOT NULL CHECK(allowed IN (0,1)),
                reason TEXT NOT NULL)""")

    def bind_parent(self, *, tenant_id: str, provider: str, parent_id: str):
        """Privileged local provisioning only; not callable by users."""
        if not (_key(tenant_id) and _key(provider) and _key(parent_id)):
            raise ValueError("invalid binding")
        with sqlite3.connect(self.db_path, timeout=10) as db:
            db.execute("""INSERT INTO gateway_read_bindings
                (tenant_id, provider, parent_id) VALUES (?,?,?)""",
                (tenant_id, provider, parent_id))

    def _audit(self, *, actor, tenant, provider, parent, allowed, reason):
        with sqlite3.connect(self.db_path, timeout=10) as db:
            db.execute("""INSERT INTO gateway_read_audit
                (at_utc, actor, tenant_id, provider, parent_id, allowed, reason)
                VALUES (?,?,?,?,?,?,?)""",
                (datetime.now(timezone.utc).isoformat(), actor, tenant,
                 provider, parent, int(allowed), reason))

    def observe(self, *, principal: TrustedReader, tenant_id: str,
                provider: str, parent_id: str) -> GatewayResult:
        # Do not accept claimed role sets; resolve permissions from mapping.
        actor = principal.identity if isinstance(principal, TrustedReader) else ""
        if not (_key(actor) and _key(tenant_id) and _key(provider) and _key(parent_id)):
            return GatewayResult(False, "invalid_principal_or_request")
        authorized = tenant_id in self._operator_tenants.get(actor, frozenset())
        try:
            with sqlite3.connect(self.db_path, timeout=10) as db:
                bound = db.execute("""SELECT 1 FROM gateway_read_bindings
                    WHERE tenant_id=? AND provider=? AND parent_id=?""",
                    (tenant_id, provider, parent_id)).fetchone() is not None
        except sqlite3.Error:
            return GatewayResult(False, "binding_store_unavailable")
        if not authorized or not bound:
            try:
                self._audit(actor=actor, tenant=tenant_id, provider=provider,
                            parent=parent_id, allowed=False,
                            reason="permission_or_binding_denied")
            except sqlite3.Error:
                return GatewayResult(False, "audit_store_unavailable")
            return GatewayResult(False, "permission_or_binding_denied")
        # Record intent before any adapter invocation; if storage is unavailable,
        # no provider read occurs. This is not an immutable or completion audit.
        try:
            self._audit(actor=actor, tenant=tenant_id, provider=provider,
                        parent=parent_id, allowed=True,
                        reason="read_requested")
        except sqlite3.Error:
            return GatewayResult(False, "audit_store_unavailable")
        return self.gateway.observe(trusted_tenant=tenant_id,
                                    provider=provider, parent_id=parent_id)

    def audit_records(self):
        with sqlite3.connect(self.db_path) as db:
            return db.execute("""SELECT actor,tenant_id,provider,parent_id,allowed,reason
                FROM gateway_read_audit ORDER BY id""").fetchall()
