# Foundry: First operational missed-call service — provider pilot gate

Status: **Offline planning only; connected provider staging NO-GO.**

The existing `TwilioHistoryAdapter` and `ReadOnlyGateway` support bounded, read-only call-history observation using a trusted, injected SDK pager. They cannot establish actual account ownership, permission to access call records, consent to message someone, or verified SMS delivery.

`src/autopilot/provider_pilot_preflight.py` introduces a strictly limited *planning metadata* validator for the first proposed provider pilot. It accepts a fictional tenant reference, a Twilio account SID-shaped value, separate **claimed** written-authorization and operator-review references, and maximum two pages/twenty legs. It rejects unsupported providers, invalid metadata or excessive limits, and emits only a redacted account fingerprint with explicit `false` declarations for provider ownership, independent authorization, cost approval and connected staging. The submitted reference strings are **not** independent proof. The validator NEVER creates SDK clients, issues requests, starts a server, sends SMS or pays any bill.

## Operator review before any connection

1. Select a real business that has voluntarily agreed to a narrowly scoped pilot. Store its identifying information privately, not in this public repository.
2. Obtain signed authority from the appropriate business representative; independently verify their provider account ownership and read permissions, subject to legal/privacy obligations.
3. Review whether provider call history contains personal data, define minimization, retention, access restrictions and secure handling. No customer data in public GitHub Actions artifacts.
4. Document provider-specific cost and metering risks, exact spending ceiling and the account that pays; seek explicit user approval before a metered test.
5. Establish trusted authentication, secret manager, TLS, tenant binding, connection timeouts, rate limits, logs, storage encryption, recovery and operational incident ownership. Test shutdown and stop-versus-inflight races; never claim stop cancels in-flight requests.
6. Execute a least-privilege, read-only **separately authorized** staging trial with bounded inputs, then independently reconcile observed provider results and record evidence in an access-controlled location.
7. Treat live messaging as a separate project needing consent/opt-out controls, legal review, deliverability monitoring, onboarding and support. A missed call alone is not consent to SMS.
8. Validate fulfillment outcomes before enabling checkout or offering a paid subscription.

## Verification

```sh
python -m unittest discover -s tests -p 'test_autopilot_provider_pilot_preflight.py' -v
```

**Release decision remains NO-GO.** No domain, mailbox, provider credential, charge, customer enrollment or public service is created by this module. This is a narrow gating improvement, not real provider integration.
