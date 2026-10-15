# Foundry Onboarding — Paid-order Invite Boundary

**Status: offline integration component, not a hosted sign-up system.** No real Stripe checkout or payment, customer login, public API, OAuth credential exchange, customer messaging, or activated service has been enabled.

## Implemented

`src/autopilot/onboarding_invites.py` adds a one-time, randomly generated onboarding token for a **previously verified paid test order** in the **same local SQLite database** as `TestCheckoutLedger`. Only SHA-256 token digests are stored. Invites expire after a bounded time, are consumed transactionally, and cannot be replayed. The intake only records a business name, industry and workflow goal, with length controls and no payment card/API credential capture. Regression tests cover unpaid-order rejection, expiry, replay and invalid forms.

## Trust boundary — important

- `issue_for_paid_order` is a trusted-backend-only method. An untrusted customer calling this method or opening the DB directly would bypass real identity authentication. **There is no authenticated HTTPS service yet.**
- `status_for_trusted_operator` requires independent authenticated authorization in a future operator API; it currently returns private submission details without checking operator identity. Never expose it directly.
- The current SQLite record is **not encrypted at rest**. Do not enter real private customer data in test fixtures or deploy this module without tenancy/access/retention/privacy controls.
- A paid test-order flag does not prove money was settled in a real Stripe account. Live receipt verification, refund/chargeback handling, and validated order ownership must precede any production use.
- No customer can activate their own provider messaging. Human review, lawful consent, vendor account ownership, test sends, and an independent deployment gate are still necessary.

## Next implementation priorities

1. Create scoped business accounts with secure hosted authentication (session management, MFA and recovery), tenant-isolated storage and an HTTPS endpoint.
2. Add a backend-only **Stripe sandbox Checkout Session creator** and an official Stripe SDK-verified HTTPS webhook, with secrets in protected deployment configuration.
3. Deliver the one-time invite only to the verified buyer through a validated email inbox, and bind it to the authorized business account. Avoid putting credential tokens in logs, analytics or referrers.
4. Build a protected onboarding wizard and dashboard with upload/OAuth permissions, versioned agreements, status and support handling.
5. Prove real sandbox payment → signed event → owned account invite → secure intake → operator approval end to end, including refund and incomplete-setup cases.
6. Keep live checkout and provider messaging disabled until all commercial-release gates are met.

The `src/autopilot/signup_preview.py` page remains a **local visualization only**; it neither stores submissions nor connects to these offline functions.
