# Foundry First-Customer Pilot — Evidence Report (Offline)

The new `src/autopilot/pilot_readiness_report.py` generates a reproducible report from the commercial release gate. It operates entirely offline, uses only Python's standard library and **never** sends SMS, requests payments, deploys infrastructure, or transmits a customer record.

## Run locally

```bash
python -m src.autopilot.pilot_readiness_report --markdown /tmp/foundry-pilot.md --json /tmp/foundry-pilot.json
# Expected without evidence: exit status 2, live pilot NO-GO
```

An optional trusted local JSON register may contain evidence keys listed in `src/autopilot/commercial_release_gate.py`. Each entry must have:
```json
{
  "honest_readiness_disclosure": {
    "passed": true,
    "reference": "reviewed-document-reference",
    "verified_by": "human-reviewer"
  }
}
```

To supply local evidence, use `--evidence /path/to/local-evidence.json`. Do **not** put private customer data, credentials, phone numbers or confidential contracts in the GitHub repository or generated reports.

## Release interpretation

- **NO-GO** (exit 2): at least one required proof is missing. This is the expected result before a real service is validated.
- **READY FOR INDEPENDENT APPROVAL REVIEW** (exit 0): all listed evidence fields have been *asserted*. This is **not authorization** or independent validation; a human must check provenance and completeness. Local files can be fabricated.
- Bad input or inaccessible files produce an error and do not grant approval.
- Discovery eligibility and customer paid-pilot readiness are separate assessments. Passing unit tests is not sufficient to verify customer consent, lawful SMS, provider ownership, authenticated runtime, billing or service delivery.

## Highest-value next evidence

Prioritize proving one realistic, tenant-bound workflow with permission-aware provider sandbox connectivity in a secure runtime, then delivery reconciliation and support response. These require a separate explicit approval for any real provider access or spending. Public marketing availability alone does not count as deliverability proof.

The commercial readiness gate deliberately does **not** activate an automation on successful report output.
