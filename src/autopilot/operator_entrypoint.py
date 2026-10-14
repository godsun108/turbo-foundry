"""Offline authenticated operator entrypoint; never expose through HTTP directly.

Trusted caller supplies a server-held mapping of operator ID to secret.
No identity or role from an untrusted payload authorizes a control change.
This helper is not a production login service or a deployable API.
"""
from dataclasses import dataclass
import hashlib
import hmac

from .operator_authorization import OperatorAuthorization, OperatorPrincipal
from .worker_control import WorkerControl


@dataclass(frozen=True)
class OperatorCommand:
    # Operator ID is used only as a lookup key, not proof of identity.
    operator_id: str
    credential: str
    enabled: bool
    reason: str


class OfflineOperatorEntrypoint:
    def __init__(self, trusted_credentials: dict[str, str],
                 authorization: OperatorAuthorization):
        if not isinstance(trusted_credentials, dict) or not isinstance(
                authorization, OperatorAuthorization):
            raise ValueError("trusted credentials and authorization required")
        if any(not isinstance(k, str) or not k.strip()
               or not isinstance(v, str) or len(v) < 32
               for k, v in trusted_credentials.items()):
            raise ValueError("invalid server-side credentials")
        # Store only digests in the local object, never accept trusted
        # permissions or signing keys from the submitted command.
        self._digests = {
            k: hashlib.sha256(v.encode("utf-8")).digest()
            for k, v in trusted_credentials.items()
        }
        self._authorization = authorization

    def apply(self, command: OperatorCommand, control: WorkerControl, *,
              now=None) -> bool:
        if not isinstance(command, OperatorCommand):
            return False
        if (not isinstance(command.operator_id, str)
                or not isinstance(command.credential, str)
                or type(command.enabled) is not bool
                or not isinstance(command.reason, str)):
            return False
        expected = self._digests.get(command.operator_id)
        if expected is None:
            return False
        submitted = hashlib.sha256(command.credential.encode("utf-8")).digest()
        if not hmac.compare_digest(submitted, expected):
            return False
        principal = OperatorPrincipal(command.operator_id, frozenset())
        return self._authorization.set_worker_enabled(
            principal=principal, control=control, enabled=command.enabled,
            reason=command.reason, now=now,
        )
