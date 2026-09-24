# Scout v0.2 — Scheduled Runner

Scout now has a scheduled execution path, persistent snapshot format, change artifacts, and CI-testable runner.

The included GitHub Actions schedule runs once daily. The bundled source remains **synthetic example data**, deliberately: scheduling a fake source is safe, while pretending it is live property discovery is not.

## Live-source gate

A source adapter can be promoted to live discovery when it has:

1. a permitted/API/public-record access method,
2. documented provenance and retrieval time,
3. a stable normalized mapping into `Candidate`,
4. tests for missing/malformed fields, and
5. credentials stored in GitHub Secrets when required.

Until a live adapter passes that gate, Scout's automation validates the pipeline but does not claim to discover current listings.
