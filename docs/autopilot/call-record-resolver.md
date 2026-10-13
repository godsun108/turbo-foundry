# Provider call-history resolver boundary

`CallRecordResolver` accepts a trusted injected provider client with a
`fetch_call_snapshot(CallSid)` method. Its returned `ProviderCallSnapshot`
must be assembled from authenticated provider records, not webhook fields.

The resolver rejects missing records, API errors, SID mismatches, child calls,
outbound calls, answered calls, unknown answer evidence, incomplete child-leg
history, and naive timestamps. It only emits an authoritative record when the
parent call is inbound and terminal no-answer, with no answered child leg.

**Important:** The current provider client is a test double. Twilio REST's
ordinary Call resource does not necessarily prove every leg's answer history,
and its `start_time` may not equal the final missed-call event time. A real
adapter must obtain reliable completion timestamps and correlate all relevant
legs, including forwarding and transfers, before setting
`child_legs_complete=True` or `answered=False`.

This is a conservative contract, not a claim that the Twilio API integration
has been completed. No real messages are sent.
