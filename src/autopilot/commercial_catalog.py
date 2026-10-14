"""Foundry AI automation commercial catalog, explicitly separated from readiness.

All offerings are proposals. This is neither a live checkout nor authority
to collect payments, contact prospects or enable customer automations.
"""
from dataclasses import dataclass
from typing import Literal

Status = Literal["offline_demo", "concept", "validated_live"]


@dataclass(frozen=True)
class AutomationOffer:
    slug: str
    title: str
    buyer: str
    problem: str
    proposed_outcome: str
    qualifying_question: str
    proof_required: str
    status: Status


OFFERS: tuple[AutomationOffer, ...] = (
    AutomationOffer(
        "missed-call-recovery", "Missed-call lead recovery",
        "Home-service contractors and repair businesses",
        "Inbound calls go unanswered and leads are lost",
        "Permission-based response workflow with observable outcomes",
        "How many inbound sales calls go unanswered each week?",
        "Provider-bound consent, safe SMS delivery, real lead conversion and support",
        "offline_demo",
    ),
    AutomationOffer(
        "appointment-follow-up", "Appointment follow-up automation",
        "Appointment-based local services",
        "Manual scheduling, confirmations and follow-up consume staff time",
        "Auditable reminders and human handoff",
        "What scheduling system do you use, and where do no-shows occur?",
        "Approved scheduling integration, permission checks, suppression and no-show measurement",
        "concept",
    ),
    AutomationOffer(
        "lead-intake", "AI lead intake and routing",
        "Service businesses with website or form inquiries",
        "Inbound questions wait for manual sorting",
        "Structured lead qualification and supervised assignment",
        "How are new form inquiries routed to the right person today?",
        "Verified data access, redaction, human escalation and routing accuracy",
        "concept",
    ),
    AutomationOffer(
        "review-requests", "Customer feedback and review follow-up",
        "Local businesses with completed jobs",
        "Feedback arrives inconsistently and problems are missed",
        "Permission-based feedback collection and issue escalation",
        "How do you ask customers for feedback after finishing work?",
        "Platform-policy compliant outreach, consent, unbiased request design and opt-outs",
        "concept",
    ),
    AutomationOffer(
        "support-triage", "Customer support triage assistant",
        "Small teams handling repetitive requests",
        "Frequently asked questions overwhelm available staff",
        "Grounded answers and reliable escalation to people",
        "Which five questions take the most staff time?",
        "Approved knowledge sources, privacy review, response accuracy and escalation testing",
        "concept",
    ),
)


def public_offers(*, include_concepts: bool = False) -> tuple[AutomationOffer, ...]:
    """Conservative public display: concepts require an explicit qualifier."""
    allowed = {"offline_demo", "validated_live"}
    if include_concepts:
        allowed.add("concept")
    return tuple(offer for offer in OFFERS if offer.status in allowed)


def can_claim_live(offer: AutomationOffer) -> bool:
    return offer.status == "validated_live"
