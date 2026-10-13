# Foundry Autopilot — Missed-Call Recovery Pilot

## Customer-facing promise
Help service businesses follow up on missed inbound calls faster, subject to verified consent and business-hours controls.

## Current readiness
Offline simulation validated in CI. No real telephony, SMS, customer accounts, or billing enabled. This is **not** a live service offer yet.

## Suggested pilot structure (proposal, not a published price)
- Discovery: review the business's missed-call volume, existing phone provider, opt-in process, and CRM workflow.
- Sandbox demonstration: run provider test events without real outbound messaging.
- Controlled live pilot only after provider integration, consent compliance review, operational approval, and explicit customer authorization.
- Evaluate over an agreed pilot period; report eligible missed calls, permitted messages, replies, booked appointments, opt-outs, failures, and attributable sales.

## Definitions
- Missed call: inbound call not answered, according to the provider's authoritative status.
- Eligible recovery: verified missed call passing tenant, consent, suppression, timing, and frequency policies.
- Message sent: provider accepted a real outbound message (not a simulation).
- Reply: inbound response associated with a sent recovery message.
- Booking: confirmed appointment with an auditable reference.
- Recovered revenue: actual collected revenue reasonably attributable to a recovered lead; never inferred from messages alone.

## Pilot success gates
1. Zero unauthorized outbound messages.
2. Correct tenant separation and suppression.
3. Provider callbacks and delivery reconciliation tested.
4. Duplicate-event replay produces at most one intended outbound message.
5. Customer can inspect counts and event-level audit records.
6. Customer agrees to the metrics, retention policy, pricing, and cancellation terms before billing.

## Positioning
Sell measurable follow-up operations, not guaranteed sales or guaranteed ROI. Pricing and terms require approval and actual cost data.
