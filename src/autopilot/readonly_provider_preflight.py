"""Fail-closed offline preflight for an eventual read-only provider test.

This checks explicit *claimed* operator/provider authorization and resource
bounds. It does NOT authenticate the claims, connect to a provider, or permit
production operations. A privileged service must independently verify every
claim and bind account/tenant/parent from trusted records.
"""
from dataclasses import dataclass
from datetime import datetime, timezone

from .worker_control import WorkerControl


@dataclass(frozen=True)
class ReadonlyProbePermit:
    tenant_id: str
    provider_account_sid: str
    parent_call_sid: str
    authorized_by: str
    approval_reference: str
    expires_at: datetime
    read_only: bool
    max_pages: int = 2
    max_legs: int = 20
    page_size: int = 10


@dataclass(frozen=True)
class ProbeDecision:
    allowed: bool
    reason: str


def _sid(value, prefix):
    return (isinstance(value, str) and len(value) == 34 and value.startswith(prefix)
            and all(c in "0123456789abcdefABCDEF" for c in value[2:]))


def preflight_readonly_probe(
    permit: ReadonlyProbePermit | None, *,
    expected_tenant_id: str,
    trusted_provider_account_sid: str,
    trusted_parent_sid: str,
    now: datetime,
    control: WorkerControl | None,
    operator_authorization_verified: bool = False,
    provider_ownership_verified: bool = False,
    zero_charge_verified: bool = False,
) -> ProbeDecision:
    """Only check local policy. Never accept request-supplied 'trusted' values.

    The verified Booleans are placeholders for future *independent*, trusted
    service attestations and MUST NOT be accepted from HTTP/user input.
    """
    if not isinstance(permit, ReadonlyProbePermit):
        return ProbeDecision(False, "missing_permit")
    if not (operator_authorization_verified is True
            and provider_ownership_verified is True
            and zero_charge_verified is True):
        return ProbeDecision(False, "independent_approval_missing")
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        return ProbeDecision(False, "invalid_clock")
    if (not isinstance(permit.expires_at, datetime)
            or permit.expires_at.tzinfo is None
            or permit.expires_at.utcoffset() is None
            or not now < permit.expires_at
            or (permit.expires_at - now).total_seconds() > 3600):
        return ProbeDecision(False, "expired_or_oversized_permit")
    if (permit.read_only is not True
            or any(type(v) is not int for v in
                   (permit.page_size, permit.max_pages, permit.max_legs))
            or not 1 <= permit.page_size <= 10
            or not 1 <= permit.max_pages <= 2
            or not 1 <= permit.max_legs <= 20):
        return ProbeDecision(False, "unsafe_probe_scope")
    if (not isinstance(permit.tenant_id, str)
            or not permit.tenant_id.strip()
            or permit.tenant_id != expected_tenant_id
            or not _sid(permit.provider_account_sid, "AC")
            or not _sid(trusted_provider_account_sid, "AC")
            or permit.provider_account_sid != trusted_provider_account_sid
            or not _sid(permit.parent_call_sid, "CA")
            or not _sid(trusted_parent_sid, "CA")
            or permit.parent_call_sid != trusted_parent_sid):
        return ProbeDecision(False, "unbound_tenant_or_provider_record")
    if (not isinstance(permit.authorized_by, str)
            or not permit.authorized_by.strip()
            or not isinstance(permit.approval_reference, str)
            or not permit.approval_reference.strip()):
        return ProbeDecision(False, "missing_approval_evidence")
    if not isinstance(control, WorkerControl):
        return ProbeDecision(False, "operator_stop_unavailable")
    try:
        if not control.is_enabled():
            return ProbeDecision(False, "operator_stop_active")
    except Exception:
        return ProbeDecision(False, "operator_stop_unavailable")
    return ProbeDecision(True, "policy_preflight_passed_not_live_authorization")
