# Foundry Standard v0.1

## Required principles

### Reproducibility
A result should identify the code, inputs, assumptions, and configuration that produced it.

### Separation of research and production
Experiments may fail. Production behavior should not silently change because an experiment looked promising.

### Frozen benchmarks
Once a benchmark is declared frozen, changes require an explicit new version. Negative results are retained.

### Testing
Core calculations receive deterministic unit tests. CI runs on pushes and pull requests.

### Provenance
Generated outputs should record timestamps, configuration/version identifiers, and source provenance where practical.

### Safety
Never commit credentials, API keys, private keys, tokens, personal secrets, or sensitive raw data.

### Promotion
A candidate becomes production only when its acceptance criteria are stated before evaluation and the evidence supports promotion.

## Project states

- CONCEPT
- EXPERIMENTAL
- VALIDATED
- PRODUCTION
- DEPRECATED

Every repository README should state its current status.
