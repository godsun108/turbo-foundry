# Foundry Gateway — release-candidate synthetic evidence

The release-candidate exercise is **not a public deployment, customer pilot, nor evidence of production security**. It is an in-process WSGI rehearsal using fictional records and a disposable SQLite database. It opens **no network socket** and has no provider, messaging or payment access.

Run locally:

```sh
python -m src.autopilot.gateway_release_rehearsal --json gateway-release-evidence.json
python -m unittest discover -s tests -p 'test_autopilot_gateway_release_rehearsal.py' -v
```

The report has individually named pass/fail checks for default-disabled startup, one authorized synthetic observation, operator shutdown, an enabled-state crash/restart with a default-off recovery, successful manually reenabled read, session revocation, and fail-closed audit-storage failure. It explicitly records `production_ready: false`, `live_provider_connected: false`, zero messages, zero payments and no public deployment. A failed scenario exits nonzero.

The dedicated GitHub Actions workflow **Foundry Gateway Release Rehearsal** executes the report on eligible pull requests and pushes, verifies its no-go flags, and publishes a short-lived `foundry-synthetic-gateway-evidence` JSON artifact for review. This is self-reported test evidence, not independently witnessed field behavior.

The local service factory now resets the persistent stop switch to **off** at startup, rather than only in its command-line entrypoint. This reduces accidental restart-resumption in test service construction. It cannot atomically cancel a provider call already underway; any privileged process with direct database or Python access can bypass the boundary.

**Commercial decision remains NO-GO** until verified secure deployment, operator authentication and isolation, account ownership, real provider compatibility, consent/opt-out, incident response, backup/restore and real delivery validation are independently documented. Neither GitHub Actions nor public GitHub Pages provides a production runtime for this feature. No hosting cost or telecom commitment was incurred.
