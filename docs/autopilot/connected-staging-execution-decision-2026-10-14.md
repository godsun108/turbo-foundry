# Foundry — connected read-only staging decision (2026-10-14)

## Status

**NO-GO for live provider access, public hosting or customer messages.** This is an inspected-resource deployment plan, not a deployed environment.

## Actual connected-resource inventory

- Railway connected workspace includes multiple separate named ventures (Oracle Paper Laboratory, Genesis First Contact Alpha, EarthChain Preview, Alchemy Kitchen, Dreams to Reality, Virtual Human Engine, Command Center, WINDOW Earth, MINT Capital Engine, Portal Intelligence).
- **No project named Foundry** appears in the accessible Railway project inventory. Avoid deploying Foundry into another venture's project or reusing its environment, volumes or credentials.
- One Stripe business account is accessible in **live mode**. No Foundry product checkout, metered billing or live-mode settlement is authorized by this fact. Do not touch production Stripe payments.
- Foundry GitHub repo includes `TwilioHistoryAdapter`, provider-neutral `ReadOnlyGateway`, local session/audit harness, stop control, synthetic fulfillment, and read-only customer-status facade. No production hosting recipe or real provider identity evidence was verified.
- Foundry Pages currently hosts a static research showcase, **not** a safe API runtime.

## Next meaningful checkpoint — nonpublic provider-read staging

1. **Choose and approve hosting account / budget:** confirm actual Railway workspace plan, consumption limits, target region and source repository; create a **dedicated** Foundry project rather than attaching to an unrelated venture. An empty project is not a running service. No project/service should be created or deployed before an explicit, amount-bounded infrastructure approval.
2. **Provide lawful provider ownership evidence:** a consenting business or explicitly designated development account; verify the owner, legitimate purpose, least-privilege call-history permissions, and data-handling authority privately. Do not place credentials, phone numbers, full Call SIDs or customer identities in GitHub or CI.
3. **Deploy an isolated nonpublic runtime:** reviewed, pinned runtime/dependencies, no public ingress, no auto-PR previews, persistent encrypted store/backup strategy, restricted administrative access, secrets manager, authentication and operator controls. Current `wsgiref` app is loopback development-only; never expose it through Railway public ingress/tunnel.
4. **Dry-run before network calls:** verify no outbound traffic on startup, worker default-off, defined tenant+provider binding, exact path restrictions, bounded page/leg count, timeout/retry ceiling, audit failure deny, read-only GET methods only, restart disabled, and an independent stop test. Check that a direct adapter call cannot bypass the authorization boundary in the deployed architecture.
5. **Limited provider observation:** execute only after separately documented customer authorization, exact provider-account validation, cost limits, approved data minimization, private retention and a named human operator. Compare returned call-history counts to provider console under controlled scope; store only minimal evidence privately.
6. **Stop and review:** collect test date, operator, non-sensitive tenant alias, observed read count, errors, latency, spending, stop response, and deletion proof. Any mismatch or excessive usage fails the pilot. No SMS, outbound calls, customer signup or payment.

## Distinct commercial gates

A read-only call-history observation does **not** establish missed-call recovery. Live SMS requires a separate legitimate consent/opt-out design, messaging registration where applicable, lawful content/quiet hours, delivery receipts, suppression, reconciliation, service terms and ongoing support. Successful connected reads must not unlock checkout.

## Spending

Railway documentation: https://docs.railway.com/pricing/plans and https://docs.railway.com/pricing/cost-control . Free availability and included credits depend on account tier. Hosted workloads can incur usage charges. Never promise an exact zero bill without verifying current plan limits and preventing all billable resources.

## Immediate explicit approvals needed

- A provider test account or written authorization from a real business, with the owner confirmed by a private channel.
- Confirmation that the connected Railway workspace may host an isolated Foundry staging project, and an explicit maximum permissible cost (including $0).
- If live data are involved: reviewed privacy, retention and incident handling before any staging observation.

**Current outcome:** connected staging **NOT RUN**; real provider reads **0**; sent SMS **0**; production activation **NO**; new infrastructure deployment **NONE**.
