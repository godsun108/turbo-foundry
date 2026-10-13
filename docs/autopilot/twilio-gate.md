# Twilio authenticated classification gate

`src/autopilot/twilio_gate.py` combines signature-authenticated webhook parsing
with a conservative call-status classifier and provisioned destination check.

For the offline integration test, trusted_inbound and
trusted_answered_elsewhere are injected by the test harness. **Do not derive
these from unverified user input.** A production call-record lookup must
establish actual direction, parent/child leg relationship, answer history,
and the final authoritative call outcome before any SMS is considered.

The gate does not enqueue or send a message. It does not resolve customer
consent or infer that a rejected event is a real missed call.

CI installs the official Twilio Python SDK and uses its RequestValidator
to compute and validate genuine signatures. This validates algorithm
compatibility, not real webhooks, customer phone numbers, carrier delivery,
or provider-account configuration.

Required next steps:
- trusted call lifecycle/state reconciliation, including transfers
- provider-hosted callback endpoint and exact URL reconstruction
- provisioned sender and destination mapping, strict tenant boundaries
- persisted server-side consent and suppression
- explicit sandbox messaging mode and provider delivery reconciliation
- compliance approval and authorized live activation

No live phone calls, SMS messages, or billing are enabled.
