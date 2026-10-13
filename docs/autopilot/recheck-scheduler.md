# Durable bounded provider recheck queue

`RecheckQueue` persists per-tenant, per-parent scheduled rechecks. It limits attempts to 1–10 (default four), exposes due work in bounded batches, and applies capped exponential delays after unsuccessful checks. Complete and exhausted work does not reappear in due queries.

This is a scheduling **data primitive**, not an autonomous worker. It does not contact Twilio, persist provider snapshots, send SMS, or initiate billing. Worker ownership/leases, crash recovery, jitter, Retry-After support, secure provider account binding, and atomic observation-to-attempt commits remain to be engineered. Live SMS and billing remain disabled.
