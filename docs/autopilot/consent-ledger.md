# Stored consent gate — offline prototype

`ConsentStore` records tenant-scoped opt-in evidence reference, source,
timestamp, and sticky opt-outs in SQLite. `trusted_ingest.py` uses signed
mock callbacks, then looks up consent in the server-side ledger before
simulating a response. Webhook-supplied consent assertions are ignored.

The `grant_verified` API is an **internal trust-boundary stub** and does not
verify the underlying evidence by itself. Do not expose it directly to a
public API. Production integration needs authenticated administrators,
verifiable opt-in records, purpose-specific consent language, tamper-evident
audit history, atomic coordination with the delivery queue, and verified
re-subscription procedures. Synchronize STOP and opt-outs with the provider,
and enforce opt-outs again at send time. SQLite is for prototype usage;
multi-worker deployment needs transaction and access-control hardening.

This integration is only for signed mock events. Do NOT pass live Twilio
callbacks into the mock HMAC webhook parser. The Twilio gate still requires
trusted direction and call-leg outcome evidence.

No customer messages or billing enabled.
