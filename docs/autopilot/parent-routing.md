# Parent-based tenant routing (offline)

The routing registry associates an authenticated inbound parent CallSid with a
provisioned business number, then associates authenticated child callbacks
with that parent's tenant even if the child destination is an agent's number.

It rejects invalid signatures, unknown parents, parent route conflicts, and
child CallSid conflicts. All records are stored in SQLite.

**Production gaps:** registration currently trusts the calling code's tenant
and provisioned-number assignment. A real server must look up ownership in
an authenticated provisioning registry and reject unowned numbers. The
current implementation does not verify provider-side parent/child linkage
via REST or reconcile transfers across nested call legs. It is not a
complete call-history proof or authorization to send SMS.

The callback journal's direct destination check is still separate and
must be updated before routed child callbacks can be journaled.
No outbound messaging or billing enabled.
