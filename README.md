# Turbo Foundry

**Build → measure → learn → preserve → compound.**

Turbo Foundry is the production standard and repository factory for projects in the Turbo ecosystem.

## Doctrine

1. Build the smallest useful system.
2. Make assumptions explicit.
3. Test before trusting.
4. Preserve reproducible evidence.
5. Never rewrite a benchmark to flatter a result.
6. Version meaningful changes.
7. Promote experiments only after they earn it.

## Standard project lifecycle

`idea → specification → implementation → tests → experiment → evidence → release → iteration`

## Repository standard

New projects should normally contain:

- `README.md` — purpose, status, usage, limitations.
- `docs/` — architecture and decisions.
- `src/` — production code.
- `tests/` — automated verification.
- `experiments/` — hypotheses and reproducible research.
- `outputs/` — generated summaries; large/raw data stays out of Git.
- `.github/workflows/` — CI.
- `CHANGELOG.md` — meaningful releases.
- `SECURITY.md` — responsible handling of secrets/issues.

## First targets

Turbo Foundry will become the scaffold used for Oracle-related research, Base One analysis, cacao-shell operations, restoration research, VictoryChain tooling, and future projects.

The Foundry itself should remain simple, inspectable, and tested.
