# Routed call-event journal

`record_routed_callback` composes the authenticated parent-call registry
with the SQLite event journal. An authenticated child callback can now be
journaled under the parent business tenant even when `To` is a forwarded
agent's number. Duplicate event keys are rejected.

**Trust limitations:** the test harness still supplies the parent tenant
and provisioned number. Production must resolve ownership from a secured
number-provisioning registry, and verify parent-child linkage against the
provider before accepting the relationship as authoritative. A signed
callback does not itself prove that all call legs are known.

This helper performs two database operations without a shared transaction.
A process interruption can leave a route registered without a journal
entry. Future work must provide atomic persistence and collision detection
for event keys whose payload changes.

The replay engine still produces manual-review candidates only. No live
SMS, provider calls, or billing.
