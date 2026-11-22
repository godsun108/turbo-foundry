# STEWARD C-01 — Preliminary System Requirements

**Revision:** 0.1  
**Status:** Draft for engineering review  
**Classification:** Design intent, not a released specification

## 1. Product intent

A mechanically driven automatic wristwatch movement combining a practical day/date calendar with a mechanically actuated chronograph. Precision and durability have equal priority. The movement must be designed for competent long-term maintenance.

## 2. Required indications and functions

| ID | Requirement | Priority | Verification |
|---|---|---|---|
| FUNC-001 | Display hours and minutes | Must | Functional test |
| FUNC-002 | Display day of week | Must | Calendar cycle test |
| FUNC-003 | Display day of month, 1–31 | Must | Calendar cycle test |
| FUNC-004 | Central chronograph seconds | Must | Timing comparison |
| FUNC-005 | Chronograph elapsed minutes | Must | Timing comparison |
| FUNC-006 | Chronograph elapsed hours | Must | Timing comparison |
| FUNC-007 | Continuous running seconds | Desired | Functional test |
| FUNC-008 | Automatic winding | Must | Winding efficiency test |
| FUNC-009 | Manual winding | Desired | Functional test |
| FUNC-010 | Hacking seconds | Desired | Functional test |
| CAL-001 | Day and date correction without damaging calendar train | Must | Misuse/setting test |
| CAL-002 | Clear setting instructions and restricted-setting guidance | Must | Service/document review |

Calendar architecture must define month-end behavior. A conventional 1–31 date mechanism will require manual correction for months shorter than 31 days; do not describe it as an annual or perpetual calendar.

## 3. Performance objectives

| ID | Objective | Preliminary target | Notes |
|---|---|---:|---|
| PERF-001 | Oscillator frequency | 4 Hz / 28,800 vph | Confirm balance and escapement design |
| PERF-002 | Power reserve | 60–70 hours | Aspirational; requires energy budget |
| PERF-003 | Rate performance | −4/+6 s/day | Define positions, temperature, state of wind, and test duration |
| PERF-004 | Chronograph engagement | Low disturbance to timekeeping | Quantify amplitude and rate change |
| PERF-005 | Chronograph reset | Repeatable, centered reset | Measure hand return error |
| PERF-006 | Shock robustness | Set after applicable test-standard review | No unsupported rating |
| PERF-007 | Water resistance | Watch-case requirement, not movement-only claim | Validate complete cased watch |

## 4. Durability and serviceability requirements

- Identify expected wear parts and establish replacement procedures.
- Minimize inaccessible fasteners and destructive disassembly.
- Specify lubrication points and approved lubricants.
- Define inspection intervals only after testing and supplier input.
- Provide exploded views, parts lists, tolerances, assembly sequence, regulation instructions, and troubleshooting guidance.
- Design a spare-parts inventory and last-time-buy policy.
- Evaluate whether critical parts can be manufactured by more than one qualified supplier.
- Establish corrosion, shock, temperature, magnetism, and chronograph-cycle tests appropriate to the final design.

The proposed 25-year post-production service-support objective requires a funded parts-retention and supply plan. It is not a guarantee until the company can operationalize it.

## 5. Accuracy test definition required

The −4/+6 s/day target is incomplete until the project specifies:
- Number and orientation of test positions.
- Temperature conditions.
- Fully wound and partially wound conditions.
- Chronograph stopped versus running.
- Measurement duration and instrument calibration.
- Acceptance sampling and treatment of outliers.

A test matrix must include chronograph off/on comparisons and repeated start-stop-reset cycles.

## 6. Architecture candidates to investigate

- Integrated versus modular chronograph.
- Column wheel versus cam switching.
- Vertical clutch versus horizontal coupling.
- Automatic winding system and rotor bearing.
- Day/date drive and correction mechanism.
- Shared versus independent calendar correction.
- Gear-train layout and barrel strategy.

No candidate is approved solely by reputation or marketing claims. Compare actual service manuals, parts availability, dimensions, technical data, and teardown evidence.

## 7. Required engineering artifacts

- Architecture trade study.
- Functional block diagram.
- Gear-train and ratio calculations.
- Mainspring/barrel energy budget.
- Oscillator and escapement specification.
- Chronograph torque and engagement analysis.
- Calendar mechanism design and setting logic.
- Tolerance stack-ups.
- Lubrication and wear analysis.
- Failure Mode and Effects Analysis (FMEA).
- Prototype test plan and test reports.
- Service manual and parts catalog.

## 8. Release gates

**Gate A — Requirements baseline:** requirements reviewed and ambiguities resolved.  
**Gate B — Architecture selection:** comparative evidence and feasibility calculations complete.  
**Gate C — Preliminary design:** layouts, ratios, energy budget, interfaces, and FMEA reviewed.  
**Gate D — Prototype readiness:** drawings, tolerances, supplier capability, assembly and test plans released.  
**Gate E — Validation:** measured results meet approved acceptance criteria.

No claim that C-01 is more accurate, more durable, or better than an existing movement may be made before Gate E and a fair comparative test.
