# Conservative missed-call policy

For the current prototype, only an authenticated inbound terminal
`no-answer` outcome may be classified as a missed call. `completed`
does not mean missed. Busy, failed, canceled, ringing, and unknown statuses
fail closed. A call answered elsewhere is not missed.

This pure function does **not** establish that a Twilio callback is for the
parent inbound call, nor that a dialed child leg's status represents the
customer's experience. Production integration must correlate CallSid,
ParentCallSid, Direction, dial legs, transfers, and authoritative call records
as applicable. Call direction and answered-elsewhere evidence must be sourced
from trusted provider state, not arbitrary user-controlled request fields.

No live messaging is enabled.
