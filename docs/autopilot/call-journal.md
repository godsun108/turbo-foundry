# Durable authenticated callback journal

The SQLite journal records signature-validated Twilio **form** callbacks with
tenant, CallSid, optional ParentCallSid, status and receipt time. It deduplicates
by tenant and externally supplied event key. No SMS is sent.

**Limitations and required hardening:**
- This journal does not prove a complete call lifecycle or whether a human
  answered; never promote journal entries to `TrustedCallRecord.authoritative`
  based only on a `no-answer` status.
- `event_key` is supplied by the trusted caller of this module; production
  code must derive a stable key from authenticated provider fields and ensure
  event collision/conflict detection.
- A child-leg callback's `To` is often the dialed agent number rather than
  the business's provisioned inbound number. Production tenant routing must
  correlate the parent CallSid to the provisioned inbound number; this initial
  journal currently rejects such child callbacks when the destination differs.
- A production endpoint needs bounded request size, URL reconstruction,
  timestamp/replay strategy, encrypted storage, retention controls, and
  authorization for journal reads.
- Twilio documents that a `<Dial>` action callback may be absent if the
  caller disconnects first; prefer child-leg status callbacks for reliable
  call tracking. See https://help.twilio.com/articles/55048623661851

This is an offline journal and test harness, not a deployed webhook server.
