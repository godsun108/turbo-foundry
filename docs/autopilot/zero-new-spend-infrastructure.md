# Foundry Zero-New-Spend Infrastructure Strategy

**Decision:** do not provision Railway, purchase domains, subscribe to a service, publish a checkout link, send paid customer messages, or incur new bills without a separate decision. This is a **no-new-spend engineering plan**, not a claim that public infrastructure has zero marginal costs or unlimited quotas.

## What is possible now for $0 additional cash

- Build and test with Python standard library, SQLite and GitHub repository CI, **subject to GitHub plan/runner limits and quotas**.
- Generate a self-contained static Foundry discovery preview via `python -m src.autopilot.static_preview_build`. It writes `outputs/foundry-static-preview/` with `index.html`, `offers.json`, `readiness.json`, `robots.txt` and `.nojekyll`; no internet or service account is required. It does **not** collect or transmit data; checkout is disabled.
- Open the generated `index.html` locally or host it later on an appropriate free static platform **after verifying account eligibility, bandwidth/quota, public visibility and terms**. GitHub Pages may be viable if project/repo visibility and plan allow; no Pages deployment has been enabled here.
- Run a **manual, human-reviewed** discovery effort using an already functioning email account, after fulfilling truthful sender identity and applicable commercial-email requirements. Do not generate unsolicited mass messages or post prospect private details into GitHub.
- Continue building portable application code, isolated from any particular hosting vendor, with CI tests covering security boundaries and replay prevention.

## The costs software cannot wish away

Public HTTPS connectivity requires an externally reachable network service and reliable DNS/TLS or a supported platform-provided subdomain. Hosting reliability, outbound email/SMS termination, payment processing, data storage and support have real infrastructure and operational costs—even with open-source software. Stripe's use typically carries processing fees on real payments. Running a self-hosted mail server does not guarantee receiving-provider deliverability, and public mobile networks may block inbound hosting.

**Do not pretend we can accept money and service customers 24/7 with only a static site.** A static preview cannot authenticate customers, protect personal onboarding data, verify live payments, deliver SMS or operate persistent jobs. Building our own free code is distinct from operating an internet service free of third-party dependencies.

## Engineering roadmap without new spending

1. **Static preview**: phone-friendly discover/demo experience and accurate availability labels. No unapproved data collection or checkout. CI builds/validates its artifact locally.
2. **Local simulated customer portal**: use the WSGI preview and isolated SQLite for synthetic checkout, invite, ownership and fulfillment tests. Test denial conditions, crashes, backup and replay.
3. **Production-independent interfaces**: explicit boundary contracts for identity provider, payment gateway, message gateway, durable state, audit and outbound delivery; fail closed when unconfigured.
4. **Portable hardened web app**: safe deployment manifest, TLS proxy architecture and secure session system; keep untrusted interfaces disabled until authentication and threat review.
5. **Free-tier staging evaluation**: compare truly available quotas, cold starts, storage durability, costs and data policies before choosing any external hosting. Stay within $0 authorized cash spend; require consent to provision new resources even on free tier.
6. **First paid delivery gate**: identify one viable automation, scope/pricing, signed terms, refund/service commitments, verified consent, integration tests, webhook/identity auth, support process and a real hosted runtime. Activate **only when evidence supports fulfillment**.

## Policy and costs

- CI jobs and static publication may count against provider quotas. Review quota dashboards and configure budgets/alerts before enabling automatic deployments. “Free tier” does not always mean “never bills.”
- No domain exists for Foundry today. A vendor-assigned subdomain can be used for a trial if available, but brand DNS/email requires later domain ownership or a carefully scoped alternative.
- **Zero new spend = reuse resources and stay offline by default.** Never create hosting projects, start a paid runner or activate metered APIs just to demonstrate progress.
- Existing Stripe integration may be connected for *planning only*. Do not create live products, links, subscriptions or charges until approved. The offline signed-event fixture is not a Stripe sandbox transaction.

## Completion proof

A verified no-new-spend milestone requires: deterministic generated static bundle; no network requests or checkout; catalog and readiness truth; tests on the exact commit; no resource provisioning or spend. Proof of a live service is a separate milestone.
