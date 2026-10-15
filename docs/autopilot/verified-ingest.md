# Verified atomic ingestion (offline)

`VerifiedAtomicIngest` composes trusted token lookup, signed callback verification, provisioned-number checks and atomic SQLite event storage. Unknown accounts and failed signatures are rejected before persistence.

The validator is instantiated twice in the current implementation, once during account verification and once during atomic ingestion. This is redundant but both checks use the same trusted token. Production should avoid repeated validation while preserving the trust boundary.

**Not a deployed webhook:** production still needs secure token storage, exact public URL reconstruction, Twilio account/number verification, provider-side parent-child reconciliation, bounded request handling, retention policy, and verified opt-in/opt-out. Test validators are injected fixtures. No live SMS or billing.
