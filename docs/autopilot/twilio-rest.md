# Twilio REST read-only adapter

`TwilioRestCallClient` accepts an authenticated `twilio.rest.Client` and
fetches a Call resource by SID. Credentials are not stored in this repository.

The official Twilio Call resource includes status, direction, parent SID,
and timestamps. Its `answered_by` field relates to answering-machine
detection; absence does not establish that nobody answered. A `completed`
call can include voicemail or an IVR. Child calls have distinct SIDs.
The API is eventually consistent. See:
https://www.twilio.com/docs/voice/api/call-resource

Consequently the adapter sets `answered=None`,
`child_legs_complete=False`, and `any_child_answered=None`. The
existing resolver **correctly rejects** these snapshots. This is a
genuine REST read boundary, not a functioning missed-call detector.

Next: correlate complete provider call-leg events and obtain authoritative
answer/no-answer evidence, with bounded retries and durable reconciliation.
Do not enable outbound SMS until this is proven and consent controls are
audited.
