# Token-fenced recheck completion

`RecheckLeases.finish` checks lease token, expiry, job state, and due timestamp inside a single SQLite `BEGIN IMMEDIATE` transaction. It advances attempts and retry schedule, then removes the lease atomically. Expired or replaced workers cannot commit job state. Completing work is idempotent at the state boundary: a second finish with the same token is rejected.

This does not yet atomically commit provider observations alongside job completion. A worker integration must ensure that observations are persisted only by the active lease owner, preferably in the same database transaction. No provider network requests, live SMS, or billing are enabled.
