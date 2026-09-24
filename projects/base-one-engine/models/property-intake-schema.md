# Property Intake Schema v0.1

Property facts and analytical assumptions are intentionally separated.

## Property fields

Address, asking price, property type, beds, baths, square feet, annual property tax, annual insurance estimate, monthly rent estimate, and rehab estimate.

Unknown values remain null. Base One must not silently invent them.

## Provenance

Every deal record requires at least one source with:

- source kind
- source reference
- retrieval timestamp
- optional notes

A deterministic SHA-256 fingerprint is generated from the normalized property facts, sources, and assumptions. This lets later analyses identify exactly which intake record they used.

## Source hierarchy

A source being recorded does not make it correct. Listing data, public records, inspections, insurance quotes, lender quotes, owner statements, and analyst estimates should remain distinguishable.
