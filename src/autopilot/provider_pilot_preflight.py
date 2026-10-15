"""Offline preflight for a future, approved read-only provider pilot.

This module NEVER touches a provider, provisions credentials or declares
customer service active. It rejects invalid deployment requests and produces
a bounded, redacted, human-review-only staging plan.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import re

_ALLOWED = frozenset({"twilio"})
_SID = re.compile(r"^AC[a-fA-F0-9]{32}$")
_TENANT = re.compile(r"^[A-Za-z0-9_-]{1,100}$")


class ProviderPreflightDenied(ValueError):
    pass


@dataclass(frozen=True)
class ProviderPilotRequest:
    tenant_id: str
    provider: str
    provider_account_id: str
    written_authorization_reference: str
    operator_review_reference: str
    max_pages: int = 2
    max_legs: int = 20


def inspect_provider_pilot(request: ProviderPilotRequest) -> dict:
    """Validate planning metadata, not the authenticity of supplied evidence.

    A request passing shape checks DOES NOT authorize a provider call.
    Never include access tokens, customer numbers or call identifiers.
    """
    if not isinstance(request, ProviderPilotRequest):
        raise ProviderPreflightDenied("typed request required")
    if (not _TENANT.fullmatch(request.tenant_id)
            or request.provider not in _ALLOWED
            or not isinstance(request.provider_account_id, str)
            or not _SID.fullmatch(request.provider_account_id)
            or type(request.max_pages) is not int
            or type(request.max_legs) is not int
            or not 1 <= request.max_pages <= 2
            or not 1 <= request.max_legs <= 20):
        raise ProviderPreflightDenied("unsupported or unbounded provider request")
    for value in (request.written_authorization_reference,
                  request.operator_review_reference):
        if (not isinstance(value, str) or not 3 <= len(value) <= 120
                or not _TENANT.fullmatch(value)):
            raise ProviderPreflightDenied("non-sensitive review reference required")
    if request.written_authorization_reference == request.operator_review_reference:
        raise ProviderPreflightDenied("distinct customer and operator references required")
    return {
        "schema_version": 1,
        "tenant_id": request.tenant_id,
        "provider": request.provider,
        "provider_account_fingerprint": request.provider_account_id[:2]
                                        + "..." + request.provider_account_id[-4:],
        "claimed_authorization_reference": request.written_authorization_reference,
        "claimed_operator_review_reference": request.operator_review_reference,
        "allowed_operation": "bounded_read_only_call_history",
        "max_pages": request.max_pages,
        "max_legs": request.max_legs,
        "authorization_independently_verified": False,
        "provider_account_ownership_verified": False,
        "provider_called": False,
        "network_calls": 0,
        "cost_approved": False,
        "production_ready": False,
        "connected_staging_approved": False,
        "next_action": "Independent human verification of written consent, provider ownership, account billing and runtime controls",
    }
