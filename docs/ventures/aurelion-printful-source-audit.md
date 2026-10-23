# AURELION — current MINT Printful source audit

2026-10-23, static source review only. Repo: https://github.com/godsun108/Mint-capital-engine

### Read-only adapter verified in source
`automation/providers/printful-readonly.mjs`: all network requests use `fetch(API + path, {headers})` without method override (GET). Public functions: `catalogProducts`, `catalogProduct`, `layoutTemplates`, `mockupStyles`, `productTemplates`, `variantPrices`, `mockupPreflight`, `tokenScopes`. Token/store ID loaded from environment, not source. Capability flags mark orders/productWrites/listingWrites/mockupWrites/spend false.

`automation/providers/printful-readonly.test.mjs`: assertions check static capability flags **only**; they do not intercept `fetch` or prove no hidden writes across all scripts.

`automation/printful-discover-orbital-garden.mjs`: GET catalog and mockup metadata; writes local evidence JSON. Has 30-page bound and saves snapshot on no match. Network read-only, not filesystem read-only.

`automation/orbital-garden-mockup-preflight.mjs`: calls GET metadata for product 274, writes local evidence. No mockup submission.

`automation/orbital-garden-mockup-request-contract.mjs`: constructs fixed request for product 274, variant 9039, style 16394 and fixed artwork URL, writes local JSON. **Orbital-specific; do not reuse its hard-coded IDs for Aurelion.**

### Write path: exclude from automated reuse
`automation/orbital-garden-submit-mockup.mjs` performs actual `POST /v2/mockup-tasks` if credentials are present. It checks a JSON status/flags but does not independently require a fresh human approval token. It should be considered a live external write even though no order is created. Do not call `npm run orbital-garden:submit-mockup` for Aurelion.

### Economics caveat
`automation/orbital-garden-economics.mjs` reads variant price from Printful but defaults fee rate 2.9% + $0.30, shipping subsidy $4.69, returns reserve $2.45. These are **assumptions** for an Orbital Garden tote, not verified for Aurelion; don't transplant or label as confirmed Aurelion margin. `automation/orbital-garden-readiness.mjs` contains static gate labels including `supplierMockup: PASS_TASK_979593343`; labels alone do not prove current supplier state. Publication explicitly BLOCKED.

### Safe next steps
1. Inspect workflow YAML and existing tests; do not dispatch Actions.
2. Design Aurelion-specific offline adapter tests with mocked `fetch` that fail on non-GET and test missing credentials, invalid IDs and cross-brand isolation.
3. Require explicit approval separate from configuration JSON for any supplier POST; no account changes or products.
4. Read-only catalog verification of organic garments only after confirming current token and correct store scope, without exposing secrets.
