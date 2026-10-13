# Authenticated provider pipeline — offline prototype

`provider_pipeline.py` joins Twilio SDK signature validation, conservative
call-outcome screening, a trusted call record, tenant-scoped stored consent,
and the simulated message queue.

It fails closed when call records are missing, not authoritative, or disagree
with the authenticated CallSid. It rejects answered calls, opted-out callers,
missing consent, and duplicate callbacks.

**Trust boundary:** `TrustedCallRecord` is currently supplied by test fixtures.
It is not proof of a real provider lookup. Production code must fetch and
reconcile provider call records using authenticated server-side credentials,
validate direction and all call legs, and confirm that no leg was answered.
Never construct authoritative=True from untrusted callback fields.

The provider event pipeline only simulates delivery. No real Twilio account,
HTTP endpoint, customer opt-in capture, SMS sending, or billing is enabled.
