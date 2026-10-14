# Foundry Universal Gateway v0 — provider-neutral read-only core

**Status:** offline engineering only. Not deployed, no live provider connection, no phone-number inventory, no messaging, no billing and no new hosting costs.

The first provider-neutral interface is `src/autopilot/universal_gateway.py`:
- `CallHistory` holds a normalized read-only result (provider, trusted tenant, parent, children, completeness and reason).
- `CallHistoryAdapter` defines `enumerate_children` without requiring Twilio fields in the business-facing interface.
- `ReadOnlyGateway` maps a trusted tenant/provider pair to a locally registered adapter and refuses unknown routes, out-of-bounds reads, malformed or cross-tenant responses, and incomplete provider results. Exceptions are converted to non-accepting outcomes without leaking raw provider errors.
- `TwilioHistoryAdapter` wraps the existing `TwilioCallPager`. Its current SDK behavior is not independently verified against Twilio.
- `FictionalHistoryAdapter` provides a second provider-shaped contract entirely offline, without Twilio identifiers; this is a simulator, **not another real telecom integration**.

Run regression tests with:
```sh
python -m unittest discover -s tests -p 'test_autopilot_universal_gateway.py' -v
```

## Security architecture and next steps

The gateway is **read-only** and intentionally has no send/dial/payment interface. The caller's `trusted_tenant` parameter **must be supplied from verified server-side authentication**, not user input. A Python process holding the gateway can create adapters and choose tenant strings, so local tests are not evidence of a secure hosted multi-tenant service.

A service-side authorization facade, provider account ownership binding, independently authenticated operator session, durable audit records and denial for disabled customer/provider connections are still missing. A real messaging adapter would require separate consent, opt-out, legal review, idempotency, rate limits, billing safeguards and approved provider access. Do not add live messaging to this gateway as a shortcut.

No synthetic provider or passing test proves real network delivery, customer value, regulatory readiness, payment processing, or production safety. Customer-facing readiness stays NO-GO. The broad Autopilot pull request remains draft.

**Doctrine:** Truth before theater. Evidence before confidence. Operational before victory.
