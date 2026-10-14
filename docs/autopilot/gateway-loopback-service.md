# Foundry loopback-only synthetic gateway service (v0)

**No deployment. No live customers. No telecom provider connection. No payment or outbound messaging.**

`src/autopilot/gateway_loopback_app.py` adds an intentionally restricted HTTP-shaped *integration harness* using only Python's standard library. It binds to `127.0.0.1` on a nonprivileged port when manually started. A caller must already hold a token issued out-of-band by privileged local code. There is **no HTTP login, registration, token issuance, SMS, payment, tenant selection or provider selection** route.

The fixed synthetic tenant `synthetic-a` and fictional provider use `call-a` with two fictional legs. A read can proceed only if the persisted `WorkerControl` gate was locally enabled by the test operator, the session is valid, the tenant/parent binding matches, and the existing audit records the read intent. Only a count is returned. HEAD never returns body content. All writes are rejected and only localhost requests are accepted at the WSGI layer. Even this restricted design is **not appropriate for internet exposure**.

## Offline verification

```sh
python -m unittest discover -s tests -p 'test_autopilot_gateway_loopback_app.py' -v
python -m src.autopilot.gateway_loopback_app
```

The program leaves its gate **OFF** and does not issue sessions. For automated checks use the unittest harness, which creates disposable databases and sessions; do not put tokens in URLs, shell history, public issues or CI logs.

## Security limitations and launch blockers

- Python `wsgiref.simple_server` is a development server, not production hosting. **Never use a public bind address, tunnel, reverse proxy or remote access** for this harness. The loopback restriction is not a complete sandbox if untrusted local processes exist.
- A local process with DB/Python access can bypass the application layer, issue sessions or flip `WorkerControl`. The stop check is not atomically fenced with actual adapter work. No secure OS isolation, MFA, TLS, CSRF-resistant session cookies, independently authenticated human identity, secret lifecycle, immutable audit, concurrency controls or mature HTTP request hardening is provided.
- HTTP `Authorization: Bearer` tokens are appropriate only for this simulated local test. Production sessions need independent security review, safer transport and access controls.
- The `/healthz` response proves only that the fictional service is responding. It is **not customer fulfillment readiness**.
- The existing public GitHub Pages showcase is static and remains separate. Customer signup, payment, consent, provider ownership, SMS and real activation are still **NO-GO**.
- No new money, hosting project, metered provider API, SMS or customer data was used.

**Next:** establish an isolated runtime security boundary before contemplating any real provider access; verify stop fencing at adapter entry, service logs/monitoring and threat-model tests.

## October 14 hardening verification

The loopback harness now rejects nonlocal Host headers (a basic DNS-rebinding defense), rechecks its default-off operator gate after a fictional adapter call before returning results, and explicitly disables the gate when the standalone server starts even if a prior SQLite database had been enabled. Regression tests simulate stopping a read after the underlying synthetic observation and require that no child count is returned. These are defense-in-depth checks, **not** cancellation or atomic fencing for a real provider request: already-running work may finish and privileged local code can bypass the HTTP layer. Never expose this development service beyond localhost.
