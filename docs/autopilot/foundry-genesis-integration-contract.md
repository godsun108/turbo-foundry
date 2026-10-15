# Foundry ↔ Sovereign Genesis intelligence boundary (v0)

**Status:** architectural contract only; not a working Genesis integration. Zero new spend, no live customers, no new services.

## Ownership

- Sovereign Core / Genesis: provider-neutral model adapter, language reasoning, bounded session context, evaluations, provenance.
- Foundry: tenant authorization, approved business facts, service policies, safe intake, consent, workflow state, authoritative booking/payment/notification receipts.
- Voice Lab: microphone/speech recognition, speech synthesis, turn-taking, interruption/cancellation, explicit synthetic-agent disclosure.
- VHE: optional speech/character adapters; narration does not imply real-time audio readiness.

The verified `godsun108/Sovereign-Core/README.md` describes shared protocols, identities, model-adapter contracts, provenance, tool boundaries, memory interfaces, and evaluations. It does **not** establish a deployed, available, low-latency Genesis chat endpoint.

## Contract proposal

Input (trusted server-side gateway only, never a browser-held provider credential):

```json
{
  "schema": "foundry.genesis.turn.v0",
  "tenant": "fictional_shop",
  "session": "fictional_session",
  "industry": "automotive",
  "utterance": "Can I bring my car Friday?",
  "context": [{"role": "assistant", "content": "What service do you need?"}],
  "verified_business_facts": {"services": ["inspection"]},
  "permitted_actions": []
}
```

Output (untrusted suggestion until independently validated):

```json
{
  "schema": "foundry.genesis.reply.v0",
  "reply": "What would you like inspected?",
  "intent": "appointment_request",
  "disposition": "collect_details",
  "proposed_actions": [],
  "evidence": [],
  "verified_booking": false,
  "real_message_sent": false
}
```

## Non-negotiable enforcement

1. Authenticate tenant and session outside the model; ignore tenant identifiers supplied by a customer transcript.
2. Treat model replies and tool proposals as untrusted; validate against allowlisted schemas and business policy.
3. No model-supplied prices, availability, emergency dispatch, completed bookings, or sent messages without authoritative business-system evidence.
4. Separate conversation memory by tenant and session; bound retention, context length, and sensitive data exposure.
5. Respect opt-out and explicit human escalation; provide text fallback when audio fails.
6. Log synthetic evaluation outcomes without recording real voice/customer PII; disclose AI identity.
7. Fail closed when Genesis is unavailable: a truthful, deterministic Foundry intake fallback may operate, but cannot claim an AI answer.
8. Never put Genesis API credentials in GitHub Pages JavaScript.

## Readiness gates

- Discover and verify the actual Genesis inference entry point and deployment status.
- Add an isolated server-side adapter with timeouts, output schema validation and tenant/session authorization.
- Test prompt injection, cross-tenant leakage, hallucinated prices/bookings, emergency escalation, latency, cancellation and provider failure.
- Demonstrate a browser voice conversation on iPhone with an explicitly configured, reachable Genesis endpoint.
- Obtain separate authorization before hosting a new service, processing customer audio, enabling real phone numbers, or spending money.

**Current demo:** `voice-lab/index.html` is a scripted browser rehearsal with local conversational state. It does not connect to Genesis.
