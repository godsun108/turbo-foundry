# Foundry Autopilot — Missed-Call Recovery v0.1

Status: **design only; not deployed or connected to telephony**.

## Goal
Recover legitimate inbound business inquiries by offering a timely, consent-aware text reply when an incoming call is missed. The same tenant-isolated engine will eventually serve Foundry internally and external customers.

## Trigger and workflow
1. Receive a signed missed-call event from an approved telephony provider.
2. Validate signature, tenant, destination number, event age, and idempotency key.
3. Confirm SMS eligibility, applicable consent, local quiet hours, and opt-out state.
4. Queue at most one reply per eligible missed-call event, with per-contact frequency caps.
5. Use a tenant-approved deterministic template initially; optional AI drafting requires review, limits, and fallback.
6. Dispatch through a configured SMS provider; record delivery status, cost, and error.
7. If the customer replies, route to the business inbox or human handoff. STOP requests immediately suppress future texts.
8. Record aggregate outcomes without storing unnecessary sensitive conversation data.

## Minimum data model
- Tenant: id, business name, timezone, approved sending number, policy version
- Contact: tenant id, normalized phone, consent evidence, suppression status
- Event: provider event id, tenant id, timestamp, caller, called number, type
- Workflow run: idempotency key, eligibility decision, template version, status
- Message: provider id, delivery status, sent timestamp, cost
- Audit record: actor, action, time, minimal metadata

## Safety and operational requirements
- Fail closed on missing consent evidence, unverifiable provider events, or unknown tenant.
- Support TCPA and state-law review before production use; do not assume an inbound call authorizes marketing texts.
- Respect STOP/HELP, suppression lists, frequency caps, quiet hours, and provider requirements.
- Encrypt secrets; segregate tenants; implement RBAC and retention/deletion policies.
- Avoid claims that an AI is human. Do not send health, financial, or other sensitive details in SMS.
- Do not automatically purchase phone numbers, send live messages, or enroll paying customers without explicit approval.

## Acceptance tests
- Duplicate webhook creates one workflow run and no duplicate SMS.
- Invalid signature, unknown tenant, and stale event are rejected.
- Suppressed, ineligible, and quiet-hour contacts receive no immediate message.
- STOP blocks all future automated sends for the contact.
- Provider failure retries with bounded backoff and no duplicate send.
- Tenant A cannot read or send through tenant B.
- A human can disable a tenant or the entire automation immediately.
- A sandbox end-to-end test demonstrates an eligible event, a queued response, and a delivery callback.

## Metrics
Eligible missed calls, messages attempted/delivered, replies, qualified leads, booked appointments, attributed revenue, SMS/AI cost, complaint rate, and unsubscribes. No invented conversion or revenue claims.

## Rollout gates
1. Mock provider and unit tests.
2. Provider sandbox and consent/opt-out verification.
3. Internal controlled pilot with approved numbers.
4. Measured pilot with one external business and signed agreement.
5. Stripe subscription checkout and tenant provisioning, with payment settlement reconciled through MINT.

## Integrations
- **Foundry:** module registry, deployment templates, CI, documentation.
- **MINT:** sales opportunity pipeline, invoices/payment event reconciliation, settled-cash accounting.
- **Future modules:** lead follow-up, reminders, estimate follow-up, receptionist, CRM, onboarding.

## Open decisions
Select SMS/telephony provider, consent capture and proof model, tenancy/storage backend, initial vertical, and pricing after cost measurement.
