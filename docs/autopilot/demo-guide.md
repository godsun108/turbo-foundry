# Foundry Autopilot — Offline demonstration

Run from the repository root:

```sh
python -m src.autopilot.demo
python -m unittest discover -s tests -p 'test_*.py' -v
```

The demo uses fictional example telephone numbers and a temporary SQLite database.
It illustrates one eligible missed call, a duplicate callback, a missing-consent
case, an opted-out caller, and a second eligible missed call.

Expected output: five scenarios, two simulated messages, three rejected events,
zero actual SMS, zero real recovered leads, and zero revenue.

This is a product behavior demonstration, not proof of demand or profitability.
The simulated delivery engine is not connected to a telecom provider.
Before live use, complete docs/autopilot/provider-readiness.md.
