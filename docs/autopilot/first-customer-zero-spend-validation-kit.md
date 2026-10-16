# Foundry — first-customer zero-spend validation kit

**Status: discovery-ready; not a live or paid service.** This is a manual, human-led research procedure. It does not activate phone service, AI voice, SMS, billing, customer onboarding, or access to customer data.

## Narrow hypothesis
An owner-operated service business misses inbound calls and loses time following up. We need to learn whether this is a real, frequent, costly problem *before* buying provider services or building another integration.

## One-session interview (15 minutes)
1. Ask permission to discuss their existing missed-call handling. Do not record or collect callers' personal information.
2. Ask for a **rough weekly count** of missed inbound calls and where that estimate comes from; label unverified estimates.
3. Ask what happens now: voicemail, callbacks, manual notes, existing CRM, or no follow-up.
4. Ask how much **staff time** one callback typically takes and how they estimate it.
5. Ask whether the business already has lawful permission to contact its callers, and who controls the phone system.
6. Show the **fictional offline** Foundry missed-call demo only if the owner wants to see it. Explain that no messages are sent.
7. Ask: "Would a measured, permission-aware follow-up workflow solve a problem worth paying to fix?" Do not suggest an available live subscription.
8. Agree on **one** next step: no follow-up, another conversation, or permission to prepare a written scope.

## What to hand the business after the meeting
A one-page, human-reviewed **workflow assessment** describing: (a) their stated bottleneck, (b) the current manual process, (c) a simple process map, (d) assumptions and unverified estimates, (e) a possible future automation concept, and (f) dependencies, consent and limitations. Deliver it through a private channel the business chooses. **No customer records or identities in GitHub.**

## Internal evaluation (anonymized only)
| Field | Record |
| --- | --- |
| Industry | Generic category only |
| Voluntary interview completed? | Yes / No |
| Approximate missed calls per week | Estimate + source, or unknown |
| Approximate minutes per manual follow-up | Estimate + source, or unknown |
| Existing provider and permission process | General description, no credentials |
| Business-confirmed pain point | Yes / No / unclear |
| Business wants another step? | Yes / No / unclear |
| Live messaging / payment requested? | Note privately; **NO-GO** pending release gate |

**Illustrative arithmetic, not revenue proof:** estimated weekly manual minutes = estimated missed calls × estimated minutes per follow-up. This does not prove all calls are eligible, recoverable, or monetizable.

## Decision gate
- **GO to scope review** only if a willing business confirms a meaningful bottleneck, consents to follow-up, and the proposed work has a clearly bounded, lawful path.
- **NO-GO** if there is no real pain point, no permission to follow up, unverified claims, or unresolved safety/provider requirements.
- **No paid pilot, live SMS, autonomous outreach, or billing** until independent operational, consent, cost, terms, and human approval gates in `docs/autopilot/pilot-offer.md` and `commercial_release_gate.py` are satisfied.

## Immediate operator action
Find **one willing business owner** through a personal connection or other expressly approved, respectful channel; request a 15-minute interview. No prospect has been contacted or validated by creating this document.

References: `docs/first-customer-discovery-operations.md`, `docs/autopilot/customer-discovery-sales-kit.md`, `docs/autopilot/commercial-readiness-audit-2026-10-14.md`.
