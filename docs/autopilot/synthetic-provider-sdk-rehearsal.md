# Foundry synthetic provider SDK rehearsal

**Mode: offline fictional data only.** No phone service, Twilio account connection, HTTP request, API key, SMS, deployment, customer data or billing is involved.

`src/autopilot/synthetic_provider_sdk.py` is a deterministic Twilio-shaped SDK *test double* wired to the existing `TwilioCallPager`. It verifies that the production-facing pager reads a multi-page result via SDK `next_page()`, refuses child records bound to the wrong account, fails closed on unknown call parents, handles 429/403/503 interruptions without claiming page exhaustion, and obeys page bounds.

`tests/test_autopilot_synthetic_provider_sdk.py` also integrates the sandbox SDK with the real SQLite-backed `RecheckQueue`, `RecheckLeases`, `WorkerControl`, `ObservationStore`, and `run_recheck` codepaths: a synthetic authorized offline read produces review-only data; a persisted operator stop prevents another SDK request; synthetic rate limits do not create successful observations.

Run with:
```bash
python -m unittest discover -s tests -p 'test_autopilot_synthetic_provider_sdk.py' -v
```

**Explicit remaining NO-GO conditions:** This is neither the official Twilio sandbox nor evidence of authenticated customer/provider authorization, live pagination compatibility, Twilio signature validation against their service, reliable 24/7 operations, delivery reconciliation, message legality/consent, actual SMS delivery, or a customer-ready deployment. The injected test account SID does not constitute independently verified tenant identity. Do not use this test double as a live provider adapter. The commercial evidence gate remains separate and blocked.

Next qualified milestone: human-authorized, credentials-safe **read-only** provider test with a real sandbox/account and bound ownership in a properly authenticated runtime, plus logging and teardown procedures, subject to zero-new-spend constraints.
