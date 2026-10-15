"""Local offline credential check -> opaque session -> audited gateway.

This facade accepts test credentials only, never exposes issue() to an HTTP
endpoint, and does not provide genuine production identity verification.
A privileged local provisioning process supplies credentials. Re-use of
static credentials and bearer tokens is NOT phishing/replay resistant.
"""
import hashlib
import hmac
import secrets

from .gateway_audited_reads import _key
from .gateway_local_sessions import LocalGatewaySessions
from .operator_attempt_limiter import OperatorAttemptLimiter
from .universal_gateway import GatewayResult


class OfflineIdentityGateway:
    """Synthetic credential-to-session boundary; no public login/service."""

    def __init__(self, sessions: LocalGatewaySessions,
                 test_credentials: dict[str, str]):
        if not isinstance(sessions, LocalGatewaySessions) or type(test_credentials) is not dict:
            raise ValueError("privileged session store and test credentials required")
        self._sessions = sessions
        self._secrets = {}
        for name, credential in test_credentials.items():
            if (not _key(name) or not isinstance(credential, str)
                    or len(credential) < 32 or len(credential) > 1024
                    or name not in sessions._reads._operator_tenants):
                raise ValueError("invalid local test identity")
            salt = secrets.token_bytes(16)
            # Synthetic only. Do not use source-embedded secrets in real deployments.
            key = hashlib.scrypt(credential.encode("utf-8"), salt=salt,
                                 n=2**14, r=8, p=1, dklen=32)
            self._secrets[name] = (salt, key)

    def login(self, *, operator_id: str, credential: str, now,
              ttl_seconds: int = 600) -> str | None:
        if (not _key(operator_id) or not isinstance(credential, str)
                or not 1 <= len(credential) <= 1024):
            return None
        # Attempt storage errors and quota exhaustion fail closed.
        try:
            if not OperatorAttemptLimiter(self._sessions.db_path).allow(
                    operator_id, now=now, max_attempts=5,
                    window_seconds=300):
                return None
        except Exception:  # SQLite failures must never grant a session.
            return None
        record = self._secrets.get(operator_id)
        if record is None:
            return None
        salt, expected = record
        submitted = hashlib.scrypt(credential.encode("utf-8"), salt=salt,
                                   n=2**14, r=8, p=1, dklen=32)
        if not hmac.compare_digest(submitted, expected):
            return None
        try:
            return self._sessions.issue(operator_id, now=now,
                                        ttl_seconds=ttl_seconds)
        except (OSError, ValueError):
            return None

    def observe(self, *, token: str, tenant_id: str, provider: str,
                parent_id: str, now) -> GatewayResult:
        return self._sessions.observe(
            token=token, tenant_id=tenant_id, provider=provider,
            parent_id=parent_id, now=now)

    def logout(self, token: str) -> bool:
        try:
            return self._sessions.revoke(token)
        except (OSError, ValueError):
            return False
