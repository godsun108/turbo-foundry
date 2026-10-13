# Worker lease coordination

`RecheckLeases` adds atomic SQLite claims over scheduled rechecks, using `BEGIN IMMEDIATE`, expiring lease tokens, and token-checked release. Workers cannot claim work that is not pending and due. Expired leases can be reclaimed after a crash.

**Important integration boundary:** the existing `RecheckQueue.record_attempt` does not yet require a lease token; worker code must not call it without verifying lease ownership. The next sprint should implement a token-fenced atomic completion method so stale workers cannot update jobs after lease expiry. Leases alone do not guarantee exactly-once provider calls or SMS. No network, live SMS, or billing is enabled.
