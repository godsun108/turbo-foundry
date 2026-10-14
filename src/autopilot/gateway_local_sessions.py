"""Offline bearer capability sessions for Foundry's read-only gateway.

This is a local, synthetic identity test boundary, not a hosted login service.
Tokens are random, stored only as SHA-256 digests, expire, and can be revoked.
A privileged caller provisions operator-to-tenant permissions separately.
Never use this directly in a public HTTP endpoint.
"""
import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone

from .gateway_audited_reads import AuditedGatewayReads, TrustedReader, _key
from .universal_gateway import GatewayResult


def _stamp(now):
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("timezone-aware clock required")
    return now.astimezone(timezone.utc).isoformat()


def _digest(token):
    if not isinstance(token, str) or len(token) != 64:
        return None
    try:
        bytes.fromhex(token)
    except ValueError:
        return None
    return hashlib.sha256(bytes.fromhex(token)).hexdigest()


class LocalGatewaySessions:
    """Privileged local session issuer; do not expose issue() to customers."""

    def __init__(self, db_path: str, audited_reads: AuditedGatewayReads):
        if (not isinstance(audited_reads, AuditedGatewayReads)
                or db_path != audited_reads.db_path):
            raise ValueError("shared trusted database and gateway required")
        self.db_path = db_path
        self._reads = audited_reads
        with sqlite3.connect(db_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS gateway_sessions (
                token_digest TEXT PRIMARY KEY,
                operator_id TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                revoked INTEGER NOT NULL DEFAULT 0 CHECK(revoked IN (0,1))
            )""")

    def issue(self, operator_id: str, *, now: datetime, ttl_seconds: int = 600) -> str:
        """Privileged use only; issuance alone is NOT proof of authentication."""
        if not _key(operator_id) or operator_id not in self._reads._operator_tenants:
            raise ValueError("unknown trusted operator")
        if type(ttl_seconds) is not int or not 1 <= ttl_seconds <= 900:
            raise ValueError("invalid session duration")
        token = secrets.token_hex(32)
        digest = _digest(token)
        with sqlite3.connect(self.db_path, timeout=10) as db:
            db.execute("""INSERT INTO gateway_sessions
                (token_digest,operator_id,expires_at,revoked)
                VALUES (?,?,?,0)""",
                (digest, operator_id,
                 _stamp(now + timedelta(seconds=ttl_seconds))))
        return token

    def revoke(self, token: str) -> bool:
        digest = _digest(token)
        if digest is None:
            return False
        with sqlite3.connect(self.db_path, timeout=10) as db:
            updated = db.execute("""UPDATE gateway_sessions SET revoked=1
                WHERE token_digest=? AND revoked=0""", (digest,))
            return updated.rowcount == 1

    def observe(self, *, token: str, tenant_id: str,
                provider: str, parent_id: str, now: datetime) -> GatewayResult:
        digest = _digest(token)
        if digest is None:
            return GatewayResult(False, "invalid_session")
        try:
            current = _stamp(now)
            with sqlite3.connect(self.db_path, timeout=10) as db:
                row = db.execute("""SELECT operator_id FROM gateway_sessions
                    WHERE token_digest=? AND revoked=0 AND expires_at>?""",
                    (digest, current)).fetchone()
        except (ValueError, sqlite3.Error, OSError, OverflowError):
            return GatewayResult(False, "session_store_unavailable")
        if row is None:
            return GatewayResult(False, "invalid_or_expired_session")
        # No operator identity/roles from the requester are accepted.
        return self._reads.observe(
            principal=TrustedReader(row[0]), tenant_id=tenant_id,
            provider=provider, parent_id=parent_id)
