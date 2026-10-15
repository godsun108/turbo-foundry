# Zero-new-spend prospect preview — iPhone review path

**This is a static discovery prototype, not a real sign-up form or payable product.** The preview can be saved as a GitHub Actions artifact; it is not deployed, public or connected to payments.

## Automatic packaging

The `Foundry Static Preview Artifact` workflow runs preview-specific tests, builds `outputs/foundry-static-preview` with only Python's standard library, and uploads a `foundry-static-preview` artifact retained for **7 days**. This reuses existing GitHub Actions quota, which is subject to provider plan restrictions. No hosting project, domain, emails, server, DNS or Stripe checkout is provisioned.

On iPhone: open the repository → **Actions** → **Foundry Static Preview Artifact** → latest successful run → download `foundry-static-preview` artifact → unzip using Files → open `index.html` in a supported browser or file viewer. Some iPhone file viewers restrict scripts from local HTML; if the worksheet download is unsupported locally, preview on a suitable local browser later, rather than putting sensitive content in GitHub. No live URL has been deployed.

## Prospect experience

The browser-only page offers a catalogue, basic business/workflow questions, a local summary and a **Save discovery worksheet (.txt)** action. The worksheet is created in the browser and only downloaded to the current device, not sent to Foundry. No contact details, payment credentials, customer lists, API passwords or financial information should be entered. Do not represent a download as a submitted lead. It is only shared if the person deliberately transmits it by their own means, after agreeing to that exchange.

Checkout remains disabled. Four catalogue items are concepts; the missed-call offering is an offline demo only. Avoid sending prospects a checkout or asking them to purchase until one offer is genuinely deliverable.

## Limits and next real milestones

- A downloadable static page **cannot** persist a customer account, secure an upload, conduct identity verification, receive payment webhooks, deliver SMS, schedule services or operate a 24/7 fulfillment queue.
- If GitHub Pages or another no-new-cost public static site is later used, confirm current eligibility and terms before publication. Public repo visibility may reveal source; no private customer records should ever be checked into GitHub.
- Before real onboarding: find an authenticated hosting option with durable protected data, verified Stripe *sandbox* backend, and reviewed business contract. Production requires support, privacy, consent, service delivery and payment readiness, not only passing CI.
- The shared email and phone channels for live outreach must be properly established and reviewed; no outreach is automatically sent.

**No additional service or charges were created by this sprint.**
