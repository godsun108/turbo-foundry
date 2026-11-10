# AURELION — MINT/Orbital Garden reuse matrix

Date: 2026-10-23. Evidence: GitHub commit messages only; file-level code and live workflow execution still unverified.

| Existing capability | Historical commit | Aurelion reuse decision | Gate |
|---|---|---|---|
| Printful adapter safety contract | c9c4cd0c7c5bede5b557916edc26b4442b8259c8 | Inspect first; reuse authorization boundaries | Confirm actual current source |
| Catalog discovery | 0e3ae1e02e58af2cf4ecf743acbabe371c1fe7cb | Adapt to organic garments | Verify catalog/variant support |
| Variant economics | 59d059bb6d4c9dd861726365c662d6d2f3a02060 | Reuse price evidence method | No assumed shipping or fees |
| Artwork QA | fa0d481f181bc40e2270a66f0b419f1bdc5fa048 | Reuse for original logo files | Preserve original assets |
| Production raster build | 675e1676688da8423d73a79921d7eac4a4193f94 | Reuse sizing/print-quality gates | Supplier template-specific |
| Mockup preflight | 283ac55b23514e5ce967cf257b42fa112faafcb1 | Reuse zero-write checks | Do not submit mockup requests |
| Mockup result poller | 388d6de86095ff31954c3011563c96f4566f9b67 | Future option only | No workflow dispatch |
| Zero-spend order simulation | be143c6f9bf864df9e6e2addc4221bdc0ba60973 | Inspect offline simulation | No live order |
| Guarded draft order adapter | 9cd30819064ecaf7156adb6cfac040574f9594d2 | Not required at this stage | Explicit approval for any writes |

Commit browser prefix: https://github.com/godsun108/Mint-capital-engine/commit/

**Architecture:** Aurelion branding and product specifications remain in turbo-foundry; MINT remains the shared provider adapter and evidence engine. Orbital Garden is preserved as its own store/product context. Never share product IDs or design assets implicitly between brands.

**Critical financial caveat:** Printful integration does not by itself remove advance fulfillment costs. Printify Pop-Up is a separate unverified channel. Do not launch without an approved cash-flow path.

**Next evidence task:** locate actual source paths and test commands from current MINT tree or a local checkout; inspect fail-closed authorization, no-write defaults, and prior CI before running anything. No new credentials, store creation, publication, order, deployment or spend.
