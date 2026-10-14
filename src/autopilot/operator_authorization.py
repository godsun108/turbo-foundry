"""Offline trusted-context authorization boundary for worker control changes.

Not a login, network API, or deployed identity provider. The identity value
must originate from a separately authenticated trusted runtime, never a user
request or unverified HTTP header.
"""
from dataclasses import dataclass
from .worker_control import WorkerControl


@dataclass(frozen=True)
class OperatorPrincipal:
    operator_id: str
    roles: frozenset[str]


class OperatorAuthorization:
    """Allowlisted, runtime-injected operator principals; deny by default."""

    def __init__(self, permitted_operators: dict[str, frozenset[str]]):
        if not isinstance(permitted_operators, dict):
            raise ValueError("trusted operator mapping required")
        self._permissions = {}
        for key, roles in permitted_operators.items():
            if (not isinstance(key, str) or not key.strip()
                    or not isinstance(roles, frozenset)
                    or any(not isinstance(role, str) for role in roles)):
                raise ValueError("invalid operator mapping")
            self._permissions[key] = roles

    def set_worker_enabled(self, *, principal: OperatorPrincipal,
                           control: WorkerControl, enabled: bool,
                           reason: str, now=None) -> bool:
        if type(enabled) is not bool:
            raise ValueError("enabled must be boolean")
        if not isinstance(principal, OperatorPrincipal):
            return False
        if not isinstance(control, WorkerControl):
            return False
        # Do not trust the roles declared on a principal. Validate against the
        # server-side mapping; this still assumes trusted principal injection.
        trusted_roles = self._permissions.get(principal.operator_id, frozenset())
        if "autopilot.worker.admin" not in trusted_roles:
            return False
        control.set_enabled(enabled, actor=principal.operator_id,
                            reason=reason, now=now)
        return True
