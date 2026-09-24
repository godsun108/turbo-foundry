# Base One Engine

Status: EXPERIMENTAL  
Project type: business

## Purpose

A reproducible real-estate deal analysis engine for evaluating candidate properties and financing structures without changing assumptions after seeing the result.

## Initial scope

Analyze a property using purchase price, financing, cash required, rehab, carrying costs, rent, operating expenses, vacancy, and exit assumptions.

Supported scenario families will include conventional/cash purchase, FHA-style financing, seller financing, and subject-to modeling where legally and contractually applicable.

## Core outputs

- Monthly cash flow
- NOI
- Cap rate
- Cash-on-cash return
- Estimated cash required
- Debt service
- Break-even occupancy
- Scenario sensitivity
- Explicit assumptions and provenance

## Acceptance criteria — v0.1

1. Same inputs always produce the same outputs.
2. Every calculated metric has a unit test.
3. Missing assumptions are surfaced rather than silently invented.
4. Financing scenarios remain separately identifiable.
5. Outputs preserve the assumptions used to produce them.

## Limitations

This is an analytical tool, not an appraisal, lending approval, legal opinion, tax opinion, or guarantee of investment performance.
