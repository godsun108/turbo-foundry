# Callback history replay

`assess_call_history` groups recorded parent and direct-child callbacks
by tenant and CallSid. It blocks absent parent/child evidence, active child
calls, completed parent calls, and completed or in-progress child calls.

A positive result means **candidate for manual review only**. It is not a
trusted provider call record, proof of complete child-leg enumeration,
proof that nobody answered, or authorization to send SMS.

The current journal only accepts child callbacks when their `To` matches
the provisioned destination. Twilio dialed child legs may target other
numbers. Production work must implement authenticated parent-based tenant
routing before this replay can represent ordinary forwarded calls.

The journal also cannot distinguish provider event versions or verify that
all expected legs and final callbacks have arrived. Introduce trusted REST
reconciliation, timeouts, and explicit unresolved status before promoting
any assessment to actionable eligibility. Never infer completeness solely
from the presence of one child leg.

No real messages are sent.
