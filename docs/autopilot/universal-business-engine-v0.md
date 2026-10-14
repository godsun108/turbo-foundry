# Foundry Universal Business Engine — first multi-industry foundation

**Goal:** one configurable Foundry automation company serving many business categories, not separately built products for every industry.

## Implemented offline

- `src/autopilot/universal_business_templates.py` defines common fictional business profiles and discovery templates for automotive, HVAC, plumbing/electrical, landscaping, cleaning/property services and general service businesses.
- Each template selects approved workflow concepts from the same `commercial_catalog.py` (missed calls, appointments, intake, feedback and support). No workflow runner, live account, separate vendor or paid infrastructure is created.
- `configure_business()` validates identifiers and prevents unsupported, duplicate, mismatched or malformed automation selections. Outputs always remain `discovery_only`; configuration has no activation switch or payment details.
- Existing preview-only `portal_app.py` exposes `GET /api/industries` for truthful concept discovery. It does not receive business information, send messages, subscribe anyone or grant access to provider records.
- Unit tests verify reuse of one catalog, tenant-profile separation, invalid selection refusal, safe public preview output and denied write/activation routes.

## Customer-facing approach

Market the **universal platform** to multiple sectors with tailored landing-page language, but do not represent proposed templates as deployed. Use the same discovery interview across industries, supplemented by the template-specific qualifying question. Start with a low-cost organic campaign using existing channels and the static showcase; verify each claim before advertising. Do not automate unsolicited outreach. Paid ads are not approved by this sprint.

## Still missing — customer deployment NO-GO

Templates do **not** implement actual phone call ingestion, SMS delivery, booked appointments, payment collection, AI answer quality, customer login or secure multi-tenant hosting. A business choosing an industry isn't evidence of an available service. Real-world integrations, written business permission, telecom consent, review of regulated sectors, pricing, contractual terms, audit assurance and independent operational verification remain separate release gates.

No new hosted service or payment was initiated. The experimental branch is intentionally not merged into main. Evaluate the safe public messaging separately from experimental provider integration.
