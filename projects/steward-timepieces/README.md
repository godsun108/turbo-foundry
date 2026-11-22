# STEWARD TIMEPIECES — C-01

**Project status:** Concept / preliminary engineering definition  
**Movement designation:** STEWARD C-01  
**Repository branch:** `steward/c-01-movement-foundation`

## Purpose

Develop a serviceable, accurate, durable automatic mechanical chronograph movement with day-of-week and day-of-month indications.

This repository contains engineering requirements, architecture studies, calculations, verification plans, and design decisions. It does not yet contain a validated movement design, production drawings, or a manufactured prototype.

## Functional requirements

- Automatic mechanical winding.
- Hours and minutes.
- Day-of-week indication.
- Day-of-month indication (1–31).
- Central chronograph seconds.
- Elapsed-minute counter.
- Elapsed-hour counter.
- Running seconds indication.
- Hand winding and hacking seconds are desired; architecture compatibility must be verified.

## Engineering principles

1. Accuracy and durability are co-equal design objectives.
2. Serviceability is a first-order design constraint, not an afterthought.
3. Prefer proven interfaces and replaceable wear components where they do not compromise performance.
4. Do not claim superiority over established calibers without comparative test evidence.
5. Distinguish requirements, proposed targets, calculated values, measured results, and supplier-confirmed facts.
6. Preserve long-term service documentation and a realistic spare-parts strategy.

## Initial proposed targets — not yet validated

| Parameter | Preliminary target | Status |
|---|---:|---|
| Frequency | 28,800 vph (4 Hz) | Proposed |
| Power reserve | 60–70 hours | Aspirational; feasibility study required |
| Rate | −4/+6 s/day | Proposed acceptance goal; test protocol required |
| Chronograph coupling | Vertical clutch candidate | Architecture study |
| Chronograph control | Column wheel candidate | Architecture study |
| Calendar | Independently correctable day and date desired | Mechanism study |
| Service support | 25 years after final production run | Business/parts policy goal |

These targets must be reconciled against movement dimensions, energy budget, component stress, lubrication, manufacturability, and service cost.

## Development sequence

1. Requirements and terminology baseline.
2. Benchmark existing chronograph calibers and calendar solutions.
3. Select architecture based on evidence and component compatibility.
4. Build gear-train, energy, calendar, and chronograph calculations.
5. Create preliminary dimensional envelope and interface control document.
6. Design failure-mode analysis and service procedures.
7. Define prototype build and validation plan.
8. Only then progress to detailed CAD, supplier engagement, and physical prototype.

## Scope boundary

C-01 is specifically **chronograph + day + date**. Month display and moon phase belong to the separate LUNAR concept; planetary indications belong to SOLARIS.

## Current engineering caution

A column wheel and vertical clutch are candidates, not settled decisions. They can offer desirable pusher behavior and reduced chronograph-hand jump, but their actual suitability depends on layout, energy consumption, serviceability, tolerances, and cost. No movement architecture is approved yet.
