# Durable provider observations

`ObservationStore` persists tenant- and parent-scoped complete child-call SID sets with UTC timestamps in SQLite. Repeated identical observations at the same instant are idempotent; conflicting payloads at the same timestamp fail closed. A reloaded history can be passed to `assess_settlement`.

Only the trusted provider audit worker should append observations. The store currently does not authenticate the caller or verify the provider; that trust boundary must be enforced by the integrating service. No scheduler, retry queue, or production storage migration has been wired yet. Stable observations are review-only and never SMS authorization. Live SMS and billing remain disabled.
