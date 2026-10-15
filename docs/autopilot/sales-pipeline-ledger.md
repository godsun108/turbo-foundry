# Foundry — Offline Sales Pipeline Ledger

**Status:** Local research-stage ledger. No prospect contacted, pilot authorized, payment independently verified, customer SMS sent, or billing integration enabled by this implementation.

## Purpose

`src/autopilot/sales_ledger.py` persists business-level opportunity stages in a local SQLite database. Its totals are deliberately separate from hypothetical bookings, estimated pricing, invoices, and uncollected payments.

Stages: `researched → contacted → replied → interviewed → qualified → demoed → proposal_requested → pilot_authorized → paying → retained`.

Each stage change requires a human-supplied evidence note and can advance only one stage at a time. The `paying` stage requires an existing collected-payment record. These are **workflow checks**, not independent verification of truth. The software cannot validate that a conversation happened, a signature is genuine, or funds settled. An operator must review external evidence before recording it. Records can be edited directly by someone with database access, so this is not an immutable financial journal.

## Example with fictional offline data — not actual customers

```python
from src.autopilot.sales_ledger import SalesLedger

ledger = SalesLedger("local-sales.sqlite")
ledger.add_prospect("synthetic-demo-001", "HVAC", "Fictional offline example")
print(ledger.summary())  # researched=1; collected_revenue_usd=0
```

The example is **synthetic only**. Do not put real names, phone numbers, emails, payment account details, customer call logs, or secrets in repository issues, CI logs or source-controlled databases.

## How actual collected revenue can eventually be recorded

1. A paid pilot must separately clear all authorization, safety, contractual, integration and billing gates. The ledger does not supply or bypass those gates.
2. Confirm the prospect stage was genuinely achieved, with documented evidence held in private approved records.
3. Independently verify settlement/receipt in the authorized payment provider or bank; never count an invoice, pledge, promise or estimated recovery as collected revenue.
4. Enter only an opaque unique settlement reference, positive exact USD amount and short verification note. The code prevents duplicate references but cannot confirm settlement on its own.
5. Periodically reconcile the ledger against the authoritative payment system; refunds, disputes, taxes, fees and partial settlements require additional implementation before financial accounting use.

**Important:** The summary is a simple cumulative internal collection tally, *not net profit, recurring revenue, recognized accounting revenue or a substitute for the payment provider*. It currently does not model refunds/chargebacks; do not use it for financial reporting.

## Near-term human work

- Verify CI for the current commit.
- Identify and contact three relevant businesses individually after reviewing the outreach drafts.
- Record real replies and interviews based on evidence, not hypothetical sales.
- Prepare one narrow scope and business-specific unit economics before proposing any paid pilot.

Product and messaging operations remain disabled until independently approved.
