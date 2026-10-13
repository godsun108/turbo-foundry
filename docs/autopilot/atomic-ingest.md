# Atomic callback ingest

`AtomicCallIngest` combines signed callback validation with tenant routing,
event fingerprinting and journal insertion in one SQLite `BEGIN IMMEDIATE`
transaction. A successful new callback commits all three records together.
Exact replays do not create additional events; changed payloads under the
same event key are rejected and audited.

The existing non-atomic helper remains for comparison and must not be used
in production.

**Not production-ready:** parent provisioning still trusts the caller's
tenant and number; event identifiers must be stable and provider-derived;
callback arrival can be out of order; provider-side call-leg reconciliation
and a complete-call evidence boundary remain outstanding. The transaction
only protects one SQLite database, not external services.

No live messaging or billing is enabled.
