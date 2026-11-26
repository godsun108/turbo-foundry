# STEWARD C-01 — WP-08 Automatic Winding Architecture and Measurement Plan

**Revision:** 0.1  
**Status:** Candidate architecture and executable measurement model; no winding geometry selected  
**Branch:** `steward/c-01-movement-foundation`

## 1. Objective

Define the automatic-winding subsystem needed to replenish the mainspring while preserving the C-01 timekeeping, chronograph and calendar functions. The winding system must be evaluated as part of the complete energy system, not as an isolated rotor assembly.

The 60–70-hour reserve remains an aspirational objective. WP-08 does not claim that any winding architecture achieves it.

## 2. Functional chain

**Wrist motion → oscillating rotor → rotor support/bearing → winding transmission → reversing or direction-selection works → reduction gearing → barrel arbor → mainspring.**

The barrel's slipping bridle or other approved over-wind protection limits the maximum spring winding state. Manual winding, if retained, must enter the winding path without creating a damaging back-drive or interference condition.

The rotor is an energy collector, not an energy source. Actual energy captured depends on wearer motion, rotor inertia, winding geometry, losses, friction, and the state of wind.

## 3. Architecture candidates

### 3.1 Winding direction

| Candidate | Potential advantages | Risks / evidence required |
|---|---|---|
| Bidirectional winding | Can harvest useful rotor motion in either direction | Reversing works add parts, backlash, friction and service complexity |
| Unidirectional winding | Simpler transmission path may reduce component count | One rotor direction does not wind; actual wrist-motion capture may be lower |

Do not select by reputation or nominal simplicity. Instrument both directions under repeatable motion profiles and compare net barrel energy gain, noise, wear and winding response.

### 3.2 Reversing transmission

Candidate mechanisms include paired reversing wheels, pawl-based direction selection or another validated reversing arrangement. Exact tooth counts, ratios, tooth form and component arrangement remain open until a rotor envelope and barrel arbor interface are established.

The transmission must be evaluated for:
- deadband and lost motion;
- backlash and impact during direction reversal;
- friction and lubrication sensitivity;
- tooth/pawl contact stress and wear;
- contamination sensitivity;
- assembly phasing and service access.

### 3.3 Rotor support and geometry

Compare a central bearing/support arrangement with a peripheral support only if packaging and measured loads justify the additional complexity. For each candidate determine:
- rotor mass, polar inertia and center of mass;
- sweep radius and axial envelope;
- bearing type, radial/axial load capacity and shock response;
- rotor-to-bridge and rotor-to-caseback clearance;
- endshake, runout and balance;
- acoustic behavior and lubricant retention;
- removal and replacement procedure.

No rotor material, mass, diameter, bearing or clearance is frozen.

### 3.4 Barrel and slipping protection

The bridle/slipping interface must prevent excessive mainspring winding while minimizing unnecessary drag and energy loss. The correct slip behavior depends on the actual spring, barrel wall, lubricant, surface finish and winding torque.

Measure slip onset and repeatability across:
- new and run-in condition;
- temperature range;
- lubricant condition and aging;
- repeated full-wind cycles;
- shock and service cycles.

The approved maximum barrel torque must be defined from the selected spring/barrel design. A generic torque threshold is not assigned here.

## 4. Manual winding and setting integration

Manual winding remains a desired requirement in the current system requirements. Retain it only after verifying:
- crown/stem input torque and tactile behavior;
- winding direction and reduction ratio;
- interaction with the automatic reversers;
- back-drive and rotor motion during manual winding;
- bridle slip behavior at full wind;
- stem sealing and service access;
- no conflict with hacking or calendar correction positions.

Stem positions and winding directions are not selected in WP-08.

## 5. Measurement model

`tools/c01_automatic_winding.py` accepts measured rotor-side input energy, measured barrel stored-energy gain, rotor revolutions and elapsed time. It reports:
- winding efficiency = barrel energy gain / rotor-side input energy;
- barrel energy gain per rotor revolution;
- average barrel energy gain over the trial;
- aggregate efficiency and trial-to-trial range.

It also compares measured bridle slip-onset torque against an externally approved maximum barrel torque. That check does not design or validate a bridle.

The model intentionally has no default values. It does not simulate wrist motion, rotor dynamics, reversing geometry, winding ratios, mainspring torque curves, or real-world reserve. Inputs must be measured at documented reference planes and under matched test conditions.

Run from the tools directory:

```bash
python -m unittest test_c01_automatic_winding.py
```

## 6. Required prototype instrumentation and protocol

1. Define rotor-side and barrel-side measurement planes.
2. Calibrate torque, angular displacement and time instrumentation.
3. Measure rotor input energy over repeatable bidirectional motion profiles.
4. Measure barrel stored-energy gain over the same trial interval using the measured torque-versus-winding-angle curve.
5. Repeat with the rotor moving clockwise, counter-clockwise and through representative reversals.
6. Test multiple states of wind: low, intermediate and near full wind.
7. Compare candidate winding architectures using the same motion profile, case orientation, temperature and lubrication condition.
8. Record rotor revolutions, elapsed time, input energy, barrel energy gain, noise, missed engagement and abnormal impacts.
9. Measure bridle slip onset and repeatability against the approved spring/barrel torque limit.
10. Repeat after wear, shock, temperature and service-cycle tests.

A wrist-motion simulator may provide repeatability, but it must be supplemented by human-use trials before claiming practical winding performance.

## 7. Integration test matrix

| System condition | Required observation |
|---|---|
| Chronograph stopped / running | Winding does not create unacceptable rate or amplitude disturbance |
| Calendar changeover | No winding-train interference or missed calendar index |
| Rotor direction reversal | No damaging impact, jam or loss of winding engagement |
| Manual winding | No back-drive or reverser damage |
| Near full wind | Bridle slips within approved torque envelope |
| Low reserve | Winding restores reserve predictably without disturbing the escapement |
| Shock / case movement | Rotor remains captured, clear and functional |
| Service / reassembly | Rotor and reversers can be removed, inspected and reinstalled correctly |

## 8. Serviceability and failure controls

Inspect and document:
- rotor bearing wear, contamination and lubricant migration;
- reversing wheel/pawl wear and spring fatigue;
- gear tooth wear, backlash growth and lost motion;
- rotor screw/retention security;
- rotor contact with bridge, dial-side components or caseback;
- bridle glazing, lubricant change and slip instability;
- winding noise and intermittent engagement.

Provide a replaceable rotor/bearing assembly where practical, accessible reverser components, assembly alignment references and a post-service winding-efficiency check.

## 9. Decisions intentionally left open

| Decision | Status |
|---|---|
| Bidirectional vs unidirectional | Compare on instrumented trials |
| Reversing mechanism | Open |
| Rotor bearing/support | Open |
| Rotor geometry/material/mass | TBD |
| Winding reduction ratio | TBD |
| Barrel arbor interface | Must match barrel design |
| Slipping bridle | Candidate; torque behavior unmeasured |
| Manual winding | Desired; interface study required |
| Winding efficiency | Not measured |
| Reserve performance | Not validated |

**Next gate:** establish a physical envelope and instrumented test fixture, then compare winding candidates using matched energy measurements. Do not freeze rotor dimensions or winding ratios before barrel, bridge, caseback and service-clearance studies converge.
