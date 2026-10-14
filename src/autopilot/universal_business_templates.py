"""Reusable offline business configurations across service industries.

No provider access, external calls, messages, payments or customer records.
Templates describe *proposed* workflows, never verified capabilities.
"""
from dataclasses import dataclass

ALLOWED_AUTOMATIONS = frozenset({
    "missed-call-recovery", "appointment-follow-up", "lead-intake",
    "review-requests", "support-triage",
})


@dataclass(frozen=True)
class IndustryTemplate:
    slug: str
    label: str
    example_workflows: tuple[str, ...]
    qualifying_question: str
    operational_notes: str
    status: str = "discovery_only"


TEMPLATES = (
    IndustryTemplate("automotive", "Automotive repair & detailing",
                     ("missed-call-recovery", "appointment-follow-up", "lead-intake"),
                     "How do you follow up when someone calls for a quote while the shop is busy?",
                     "Estimates and vehicle details need human verification."),
    IndustryTemplate("hvac", "HVAC & climate services",
                     ("missed-call-recovery", "lead-intake", "appointment-follow-up"),
                     "Who handles missed calls during peak or after-hours service?",
                     "Emergency jobs need immediate human escalation."),
    IndustryTemplate("plumbing", "Plumbing & electrical services",
                     ("missed-call-recovery", "lead-intake", "appointment-follow-up"),
                     "How are urgent requests distinguished from routine estimates?",
                     "Safety-critical work requires human review."),
    IndustryTemplate("landscaping", "Landscaping & lawn care",
                     ("lead-intake", "appointment-follow-up", "review-requests"),
                     "How do you handle quote requests during scheduled jobs?",
                     "Service areas and recurring jobs vary by business."),
    IndustryTemplate("cleaning", "Cleaning & property services",
                     ("lead-intake", "appointment-follow-up", "review-requests"),
                     "What takes the most time when scheduling and confirming visits?",
                     "Property-access details must not enter public demos."),
    IndustryTemplate("general", "Other service businesses",
                     ("lead-intake", "support-triage", "appointment-follow-up"),
                     "Which repetitive customer-facing task costs the team the most time?",
                     "Require individual review for sensitive or regulated industries."),
)


@dataclass(frozen=True)
class BusinessProfile:
    """Local fictional configuration only; never a customer enrollment."""
    profile_id: str
    template_slug: str
    workflows: tuple[str, ...]
    status: str = "discovery_only"


def get_template(slug: str) -> IndustryTemplate:
    for template in TEMPLATES:
        if template.slug == slug:
            return template
    raise ValueError("unknown industry template")


def configure_business(profile_id: str, template_slug: str,
                       workflows: tuple[str, ...] | None = None) -> BusinessProfile:
    """Validate a proposed profile against the universal automation catalog.

    No enable/activate flag exists: profile creation cannot turn on a service.
    """
    if (not isinstance(profile_id, str) or not 1 <= len(profile_id) <= 80
            or not all(ch.isascii() and (ch.isalnum() or ch in "-_")
                       for ch in profile_id)):
        raise ValueError("invalid fictional profile ID")
    template = get_template(template_slug)
    selected = template.example_workflows if workflows is None else workflows
    if (not isinstance(selected, tuple) or not selected
            or len(selected) > len(ALLOWED_AUTOMATIONS)
            or len(set(selected)) != len(selected)
            or not all(isinstance(item, str) and item in ALLOWED_AUTOMATIONS
                       and item in template.example_workflows for item in selected)):
        raise ValueError("unapproved workflow selection")
    from .commercial_catalog import OFFERS
    offered = {offer.slug for offer in OFFERS}
    if any(item not in offered for item in selected):
        raise ValueError("unknown catalog workflow")
    return BusinessProfile(profile_id, template.slug, selected)
