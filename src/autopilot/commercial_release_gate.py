"""Evidence-only commercial release gate for Foundry automation offerings.

A human-reviewed evidence register is required. No code-only test may mark
provider integration, consent compliance, or real-money collection complete.
"""
from dataclasses import dataclass
from typing import Mapping

REQUIRED_FOR_DISCOVERY = (
    "honest_readiness_disclosure",
    "fictional_demo_data",
    "manual_outreach_review",
    "business_contact_opt_out_process",
)
REQUIRED_FOR_LIVE_PILOT = (
    "customer_written_authorization",
    "provider_account_binding",
    "authenticated_operator_service",
    "hosting_backup_recovery",
    "tenant_isolation_review",
    "consent_and_optout_review",
    "messaging_regulatory_review",
    "delivery_reconciliation_test",
    "incident_response_owner",
    "support_and_cancellation_terms",
    "costs_and_price_approved",
    "customer_data_processing_terms",
)


@dataclass(frozen=True)
class EvidenceItem:
    passed: bool
    reference: str
    verified_by: str


@dataclass(frozen=True)
class ReleaseAssessment:
    discovery_ready: bool
    live_pilot_ready: bool
    missing_discovery: tuple[str, ...]
    missing_live_pilot: tuple[str, ...]


def assess_release(evidence: Mapping[str, EvidenceItem]) -> ReleaseAssessment:
    """No silent defaults to True; only explicit, attributable proof passes."""
    def verified(key: str) -> bool:
        item = evidence.get(key)
        return (
            isinstance(item, EvidenceItem)
            and item.passed is True
            and isinstance(item.reference, str) and bool(item.reference.strip())
            and isinstance(item.verified_by, str) and bool(item.verified_by.strip())
        )
    missing_disc = tuple(k for k in REQUIRED_FOR_DISCOVERY if not verified(k))
    missing_live = tuple(k for k in REQUIRED_FOR_LIVE_PILOT if not verified(k))
    return ReleaseAssessment(
        discovery_ready=not missing_disc,
        live_pilot_ready=not missing_disc and not missing_live,
        missing_discovery=missing_disc,
        missing_live_pilot=missing_live,
    )
