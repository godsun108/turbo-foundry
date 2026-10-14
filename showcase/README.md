# Foundry Public Showcase — no-new-spend publishing

**Status: independent minimal publishing change, separate from the large draft Autopilot PR.** The showcase is pure HTML/CSS in `showcase/index.html`; no backend, cookies, third-party JS/assets, email collection, customer onboarding or checkout.

## Why this approach

The repository is currently public, and GitHub Pages can serve static files for supported repositories. Pages is subject to GitHub's current service policies, limits and eligibility. No new domain or Railway project is necessary. This workflow uses existing GitHub Actions capacity, which may have plan-dependent limits.

## Steps after code review

1. Review the PR containing `showcase/index.html` and `.github/workflows/foundry-public-showcase.yml`. Pull request checks validate the static site and upload an artifact but **do not deploy**.
2. After human review, merge this **small PR only** to `main`; **do not merge the broad unfinished Autopilot PR**.
3. In GitHub repository **Settings → Pages → Build and deployment**, choose **GitHub Actions** as the source. This account-level setting might require manual administrator action; the GitHub connector used for this change cannot confirm or set it.
4. Under **Actions → Foundry Public Showcase**, inspect the main-branch run and its `deploy` job. It must succeed and show the actual `page_url` output before announcing any public URL.
5. Review the live page in Safari on iPhone and desktop. Confirm HTTP 200, no form, disabled purchasing by absence of checkout, five accurately labeled offers and no unexpected tracking.
6. If the Pages publishing job fails due to permissions or Pages not being enabled, **do not claim a deployed site**. Fix the repository setting and rerun through GitHub as supported.

A likely standard Pages URL for a public repository would follow `https://godsun108.github.io/turbo-foundry/`, but that is a **pattern, not a verified live link**. Only share it as live once deployment and HTTP checks confirm it. Hosting location/path may vary.

## Commercial boundaries

- The website advertises discovery conversations and fictional offline demonstrations only; it is *not* a ready-to-buy offering.
- No valid official public business email address or postal contact identity has yet been established, so it does not advertise contact addresses or collect lead details.
- A static host cannot securely verify Stripe webhooks, authenticate clients, store private onboarding data, schedule work or send customer messages.
- Revisit sender identity, business policies, support, consent, billing and technical production gates before taking payments.
- A public GitHub repository means **all showcase source is publicly viewable**. Never commit prospects' private details, API credentials or personal customer records.

No paid service has been provisioned by this change.

## Pages 404 recovery

GitHub Pages being enabled *after* a previous merge may not replay an old `push` workflow. A new push to `main` touching `showcase/**` triggers fresh validation and deploy. The workflow also has an explicit manual **Run workflow** option on `main`.

If the site returns 404:

1. Check repository **Settings → Pages**: Source **GitHub Actions** (not Deploy from a branch).
2. Go to **Actions → Foundry Public Showcase** and inspect the newest **main** run. It should include **validate** and **deploy** jobs. The prior PR runs validate only.
3. If no main run appears, select **Run workflow → Branch: main → Run workflow**. Do not re-run an old PR validation job expecting publication.
4. If deploy fails, inspect the failed job (especially Pages permissions/environment configuration). Fix it before retrying; don't assume the site is live.
5. After deploy succeeds, use the exact deployment URL shown in the successful job. Allow a little time for public CDN propagation, then check that actual path in Safari.

A static HTML file by itself is not evidence of a live Pages website.
