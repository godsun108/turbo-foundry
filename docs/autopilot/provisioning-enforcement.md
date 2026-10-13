# Provisioning enforcement in atomic ingest

Parent-call registration now requires an active entry matching
`phone_number`, `tenant_id`, and `provider_account_sid` in the
SQLite provisioning registry. Disabled numbers and mismatched accounts
are rejected before any route, fingerprint or journal insertion.

**Remaining trust boundaries:** `provider_account_sid` is currently
supplied by the trusted caller of this offline method. A production
webhook must obtain AccountSid from a signature-validated Twilio
callback, bind it to the correct account credential, and independently
verify that the configured number belongs to that Twilio account.
The administrative provisioning method is not a public endpoint.

Existing child routes inherit the tenant from a previously verified
parent. This does not prove provider-side parent/child linkage or
complete call history. No live SMS or billing.
