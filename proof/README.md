# PROOF RECEIPTS v1

A proof receipt is an **evidence submission**, not a maturity promotion.

## Authority boundary

A producing system may say:

> “I ran this bounded procedure; this was the result; these immutable evidence fingerprints support it.”

It may **not** say:

> “Therefore I have promoted myself to DEMONSTRATED.”

Only the canonical Foundry North Star registry may change maturity/proof state, through a separate reviewed commit.

## Receipt rules

1. Use schema `turbo.proof-receipt.v1`.
2. Target an existing `north_star_id` from `NORTH_STARS.json`.
3. The producer must be the target's canonical owner or an explicitly allowed evidence producer.
4. Preserve an ISO-8601 observation time.
5. Label the environment honestly: simulation, synthetic, historical, paper-forward, local, testnet, live, settled, or recovery.
6. Result is PASS, FAIL, or INCONCLUSIVE. Failure is evidence and must not be deleted merely because it is disappointing.
7. Every evidence reference carries a SHA-256 fingerprint.
8. A receipt must not contain credentials, private keys, personal secrets, or sensitive raw data.
9. A receipt proves only its written claim. It does not imply profitability, safety, identity, causality, production readiness, or authorization beyond that claim.
10. “paid” and “settled” remain distinct; “paper-forward” and “live” remain distinct; “testnet” and production remain distinct.

## Storage

Reviewed receipts live under:

`proof/receipts/<north_star-id>/<receipt-id>.json`

The receipt ID must match the filename stem.

## Review flow

```text
producer experiment/run
      ↓
proof receipt + fingerprints
      ↓
Foundry structural validation
      ↓
human/reviewer checks evidence and claim boundary
      ↓
optional separate NORTH_STARS.json update
      ↓
Mission Command regeneration
```

Structural validation deliberately does **not** fetch arbitrary external URLs or infer that a referenced artifact is true. It establishes that the evidence package is well-formed, targeted, truth-labeled and fingerprinted. Review establishes whether it is persuasive enough to change a proof state.
