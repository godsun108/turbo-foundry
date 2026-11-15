# SFTI ecosystem integration map

This is a target architecture and repository ownership map, not evidence that connections are already implemented.

| System | Proposed responsibility | First integration | Boundary |
|---|---|---|---|
| Turbo Foundry | Research portfolio, project lifecycle, experiments, test evidence | Owns SFTI source of truth and review process | No assumption of physical device control |
| Sovereign-Core | Shared contracts, provenance, identity, policy and evaluation interfaces | Review observation schema and tool permission contract | Keep provider-neutral; no product UI or deployment ownership |
| Genesis | Engineering research copilot | Read-only ingest of versioned experiment records and sensor exports | May propose; cannot grant itself authority or bypass approvals |
| Alfred | Human-facing operator | Present device health and request explicit confirmation for approved actions | No autonomous hazardous actuation |
| Sovereign Offline | Local-first interface | Local viewing/export of instrument records | Core instrument functions must survive network loss |
| Sovereign Online | Optional remote dashboard | Authenticated, read-only telemetry view | Remote access is optional and least-privilege |
| EarthChain | Optional lifecycle/provenance attestations | Record selected build, calibration, maintenance, and ownership attestations | Ledger availability never gates safety or real-time control |

## Integration sequence
1. Stabilize a versioned observation record and experiment record.
2. Add read-only import/export in the local toolchain.
3. Review the data contract in Sovereign-Core before adding shared interfaces.
4. Add Genesis retrieval with source provenance and uncertainty preservation.
5. Add Alfred presentation and confirmation only after policy review.
6. Consider EarthChain attestations only after there is a real provenance use case.

## Security principles
- Device identity is distinct from user identity.
- Default device permissions are read-only.
- Secrets never enter Git.
- Local safe-state behavior does not depend on an AI model or remote service.
- Physical control commands require explicit capability grants, bounded operating envelopes, and human approval.
- Every command and device response is auditable.
