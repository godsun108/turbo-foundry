# Scout v0.6 — Enrichment + Shortlist

The post-ingestion layer is now ready before credentials arrive.

- Active-listing candidates can be joined to public-record candidates using conservative normalized-address matching.
- Only a unique exact normalized-address match is accepted automatically; ambiguous matches are flagged rather than guessed.
- An explainable shortlist orders candidates using the existing transparent triage components.
- Triage remains discovery prioritization, not a purchase recommendation.

## Next runtime gate

Live RentCast execution still requires `RENTCAST_API_KEY` in GitHub Secrets. Once present, the workflow can retrieve actual active candidates; enrichment can then be applied against the St. Lucie public-record adapter.
