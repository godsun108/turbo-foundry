# Foundry Customer Account Ownership — offline boundary

**Status: source-only, offline.** No hosted authentication, real signup, Stripe sandbox Checkout Session creation, deployed database, email verification, or public onboarding exists. Feature branch remains a draft PR.

`src/autopilot/account_ownership.py` records an opaque customer account ID and binds each registered test Checkout order to one account in SQLite. Read and onboarding-invite wrappers require a matching `authenticated_account_id`. Tests cover account A being unable to read or request onboarding for account B, persistence across reopen, and refusal to rebind orders. Correct ownership does **not** override the separate verified-payment requirement.

## Security boundary and limitations

- The `authenticated_account_id` parameter is **not itself authentication**. A malicious client able to supply another customer's account ID could impersonate that customer. It must be derived from a verified server-side session by a separate, production-grade identity component, not request parameters, headers, or form data.
- `register_account` and `bind_order` are currently directly callable. Future deployment must isolate them in privileged code with write permissions unavailable to customers.
- This helper is not a tenant-isolated database architecture. Any process with direct SQLite access can bypass the wrapper, and `OnboardingInvites.submit` still authenticates by bearer token only. Protect invite delivery, token exposure and independent account ownership when building the actual hosted intake.
- No real customer PII, financial information or provider credentials belong in synthetic fixtures. Production requires encryption, audit and retention policies, per-tenant database authorization, independent penetration/security review, and operational procedures.
- Account creation, verified email ownership, MFA, passwordless login/session issuance, CSRF protection, abuse prevention and secure OAuth integrations are future work.

## Next meaningful milestone

Build a real HTTPS app in a staging environment with customer identity, managed key storage and encrypted tenant-isolated data. Create Stripe **test-mode only** sessions server-side; map webhook-verified payments to the authenticated account and approved offer; send the one-time onboarding invitation to the verified buyer. Then validate end-to-end in sandbox and document remaining production NO-GO gates.

Do not connect live payment or SMS or call this a secure public sign-up service merely because offline tests pass.
