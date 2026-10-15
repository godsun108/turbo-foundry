# Foundry Railway staging — deployment preparation only

Project: **Foundry Staging** (Railway project ID `a08e3701-1f77-4028-bf5b-ef077a638004`)
Environment: **staging** (ID `869d25e4-1ab7-452c-9dc9-f10901046607`)

The dedicated Railway project was created by explicit user approval, privately, with PR deployments disabled. At creation its inventory had **0 services, 0 volumes, 0 buckets, no shared variable names, and no pending patch**. This document does not claim the Railway account is free to run or that any deployed workload has been tested.

## Source available

`src/autopilot/staging_health_app.py` is a deliberately **non-deployable-as-public-app** stdlib-only *local* health service: no provider credentials, customer API, payment, signup, SMS, hosted database, network clients, or operator enable route. A trusted developer may locally run:

```sh
python -m src.autopilot.staging_health_app
# only localhost:8094, GET /healthz; worker and live features absent
python -m unittest discover -s tests -p 'test_autopilot_staging_health_app.py' -v
```

The service strictly binds to `127.0.0.1` even when `HOST` or `PORT` are configured by an external platform, refusing remote/proxied requests. It is **not** designed to satisfy Railway's public health probes; do not open a public domain or relay it through an ingress just to make the check green. A successful local health response is not production-service readiness.

## Before deploying any application

- Obtain explicit approval of a hosting cost ceiling and check actual Railway workspace plan, billing notifications, service resource limits and PR deployment settings. An empty Railway project and passing GitHub CI do not guarantee zero ongoing charges once services launch.
- Agree on the operational architecture: private network path for operator access, trusted authentication, managed secrets, tenant isolation, no public listener, approved secret lifecycle, backups and logs. Do not convert the current loopback WSGI fixture into a public HTTP service.
- Select and validate a narrow first use case. The provider adapter is read-only, and an approved, lawfully authorized owner of a development/provider account is a separate prerequisite to call-history observation.
- Ensure release gates block read calls before provider credentials are injected; test default-off restart and operator shutdown in the *actual* isolated runtime. No live SMS until a separate lawful messaging and opt-out review.
- Confirm host cost, confidentiality, deletion/retention, incident ownership and rollback criteria before acceptance.

## State at handoff

Dedicated Railway project: created. Railway service deployment: **not performed**. Provider account: **not connected**. Database: **not provisioned**. Human/provider authorization: **not verified**. Checkout: **disabled**. SMS: **disabled**. Production-ready: **false**.

No ongoing service was created in this sprint; all changes remain in experimental draft GitHub branch.
