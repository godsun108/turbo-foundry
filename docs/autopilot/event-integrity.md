# Callback event integrity

The `EventIntegrity` ledger stores a SHA-256 fingerprint of canonicalized,
authenticated event fields for each (tenant,event_key). Exact replays are
recognized; changed payloads under the same event key are rejected and
recorded in a persistent conflict table. Cross-tenant keys are isolated.

This is an offline building block. **It is not yet atomically integrated**
with parent routing or callback journaling. A crash between writes could
still leave inconsistent state. Before production, unify route registration,
fingerprinting and event insertion in one database transaction, and require
stable provider-derived event identifiers. Fingerprints are not substitutes
for provider signatures or consent records.

No live provider traffic or SMS.
