# Zero-spend read-only provider test preflight

**State: offline policy code and tests only. No provider has been contacted.**

The `readonly_provider_preflight.py` module refuses read-only provider probes until all claims and scope checks succeed. Its explicit boundaries are:
- Default-deny unless trusted independent checks assert operator authorization, provider account ownership and no-charge scope.
- Permit must bind exactly to the trusted tenant, account SID and parent-call SID, contain approval reference and an unexpired approval window no longer than one hour.
- At most two pages, 10 records per page, 20 child legs; no write or messaging permission.
- Persisted operator stop must be enabled, or the check rejects.
- No provider API calls, tokens, phone numbers, customer messages or HTTP endpoints are supplied by this module.

Run offline tests:
```
python -m unittest discover -s tests -p 'test_autopilot_readonly_provider_preflight.py' -v
```

**Important security boundary:** The three `*_verified` booleans, `expected_tenant_id`, provider identifiers and `ReadonlyProbePermit` are *claims supplied by calling code*, **not independently authenticated**. A malicious client could manufacture them. Passing this function **does not authorize** a real provider request. Never expose these arguments in a public endpoint, trust request input, treat synthetic test results as live authorization or deploy it as an operator approval server.

## What is required before a real read-only provider test

1. Explicit human authorization to access a particular verified owned test provider account; scope and test window recorded separately from code. No credentials, auth tokens or customer PII committed to GitHub.
2. Independently authenticated operator identity and secure retrieval of the provider account binding from a trusted server-side record, not an HTTP parameter or self-attested flag.
3. Provider SDK behavior and TLS/timeouts checked against official SDK and provider account in a safe isolated runtime. Ensure no calls, SMS or paid operations occur. Provider read API access may be billable depending on terms; validate zero charges before accessing.
4. Restrict to safe fabricated identifiers and a disposable test account. Verify logs exclude numbers, access tokens and PII; implement cost stop, audit and teardown.
5. Have separate independent human review of the test plan, plus a persisted kill switch and rollback, before execution.

No external account, cost, phone-number, subscription, hosting service or deployment was created during this sprint. Customer automation remains **NO-GO**.
