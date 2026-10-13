# Atomic observation + recheck completion

`commit_observation` requires the `ObservationStore`, `RecheckQueue`, and `RecheckLeases` tables to live in the same SQLite database. Under one `BEGIN IMMEDIATE` transaction it validates the current lease, checks for observation conflicts, inserts complete provider evidence, advances the bounded retry job, and releases the lease. A conflict rolls back the whole transaction; expired or replaced leases cannot write.

This is an offline persistence primitive, not a Twilio worker. Caller/provider authentication, observation scheduling, rate-limit Retry-After handling, settlement orchestration, and production database migrations remain pending. A completed recheck is **not** permission to send an SMS. No live SMS or billing is enabled.
