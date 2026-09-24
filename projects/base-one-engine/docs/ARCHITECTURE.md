# Architecture

Base One Engine begins as a deterministic calculation core.

**Inputs → validation → calculation engine → structured outputs**

Property acquisition data, financing adapters, listing ingestion, sensitivity analysis, and user interfaces should remain outside the calculation core so the formulas can be tested independently.

No external listing source is authoritative by default. Source provenance and retrieval timestamps should accompany imported data.
