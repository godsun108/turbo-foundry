# TURBO ECOSYSTEM STATUS

> Generated deterministically from `ECOSYSTEM.json`. This is an architecture/contract status surface, not a network uptime claim.

Canonical registry: **20 systems**

| System | Role | Repository | Contracts | Status |
|---|---|---|---:|---|
| `portal` | public-experience | godsun108/The-portal | 0 | registered |
| `earth-now` | earth-observation | godsun108/earth-now | 3 | registered |
| `window` | public-camera-observation | godsun108/window-earth | 4 | registered |
| `edge` | intelligence-console | godsun108/edge-intelligence | 2 | registered |
| `mint` | capital-execution | godsun108/Mint-capital-engine | 2 | registered |
| `oracle-options` | market-research | godsun108/-oracle-options-lab | 1 | registered |
| `seldon` | world-state-research | godsun108/Seldon | 1 | registered |
| `base-one` | property-analysis | godsun108/turbo-foundry | 1 | registered |
| `victory` | identity-governance-impact | godsun108/victorychain_stack | 2 | registered |
| `soul-key` | presence-research | godsun108/soul-key | 0 | registered |
| `turbo-turtle` | game-recovery | not recovered | 0 | source-not-located |
| `ryln-ai` | legacy-ai | godsun108/ryln-ai | 0 | legacy-preserve-review |
| `hemp-token` | legacy-placeholder | godsun108/Hemp-Token | 0 | placeholder |
| `sacredchainx` | legacy-placeholder | godsun108/sacredchainx | 0 | empty-placeholder |
| `victory-trust-registry` | legacy-placeholder | godsun108/victory-trust-registry | 0 | empty-placeholder |
| `mint-placeholder` | legacy-placeholder | godsun108/Mint | 0 | empty-placeholder |
| `turbo-foundry` | ecosystem-governance | godsun108/turbo-foundry | 3 | registered |
| `sovereign-core` | intelligence-kernel | godsun108/Sovereign-Core | 2 | registered |
| `sovereign-online` | online-ai-body | godsun108/Sovereign-Online | 0 | registered |
| `sovereign-offline` | offline-ai-body | godsun108/Sovereign-Offline | 1 | registered |

## Dependency edges

- `portal` → `earth-now` via canonical iframe + EARTH to EYES message handoff
- `portal` → `window` via canonical iframe with query passthrough
- `portal` → `earth-now` via dynamic/latest.json (earth-pulse)
- `portal` → `victory` via Fonzi travel-form experience prototype
- `sovereign-online` → `sovereign-core` via canonical Sovereign Core protocol
- `sovereign-offline` → `sovereign-core` via canonical Sovereign Core protocol

## Recovery / legacy boundaries

- **oracle-options** — registered: research system; no public prediction API is claimed
- **seldon** — registered: research library; no public forecasting service is claimed
- **base-one** — registered: engine/workflows; no public browser API is claimed
- **victory** — registered: legacy trading code is not the canonical Victory protocol
- **soul-key** — registered: research output must never authorize funds
- **turbo-turtle** — source-not-located: Do not treat a new implementation as the recovered original. Locate original source/artifact first, then migrate deliberately.
- **ryln-ai** — legacy-preserve-review: Small older Python implementation. Preserve until functionality is reviewed for deliberate migration; do not assume it is current.
- **hemp-token** — placeholder: README-only in current audit; no substantial implementation established.
- **sacredchainx** — empty-placeholder: Empty in current audit; preserve name/history but do not treat as implemented capability.
- **victory-trust-registry** — empty-placeholder: Empty in current audit; preserve name/history but do not treat as implemented capability.
- **mint-placeholder** — empty-placeholder: Empty placeholder. Canonical implemented capital system is godsun108/Mint-capital-engine.
- **turbo-foundry** — registered: Foundry validates and preserves evidence; it does not manufacture proof for owned systems.
- **sovereign-core** — registered: Core owns intelligence semantics, not deployment bodies or ambient machine authority.
- **sovereign-online** — registered: Body consumes Core semantics; inference provider remains replaceable.
- **sovereign-offline** — registered: No cloud fallback; completion requires reproducible operation with external networking denied.

## Registry checks

- schema recognized
- system IDs unique
- declared dependency targets exist
- status generated without external network assumptions
