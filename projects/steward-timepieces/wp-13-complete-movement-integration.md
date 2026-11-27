# STEWARD C-01 — WP-13 Complete Movement Integration

**Document ID:** C01-WP-13  
**Revision:** 0.1  
**Status:** Preliminary system integration definition; architecture not frozen  
**Branch:** `steward/c-01-movement-foundation`  
**Predecessors:** WP-08 Automatic Winding; WP-09 Balance and Escapement; WP-10 Gear Train and Energy Transmission; WP-11 Chronograph; WP-12 Integrated Calendar  
**Next gate:** measured subsystem interfaces, integrated CAD envelope, and instrumented complete-movement prototype

## 1. Purpose and release boundary

WP-13 joins the five subsystem work packages into one controlled system model. It defines energy and functional interfaces, simultaneous operating states, integration risks, dimensional data requirements, and verification evidence needed before C-01 architecture freeze.

This is a preliminary engineering integration package. It is not a completed movement design, production drawing set, validated prototype, supplier commitment, or proof of the 60–70-hour reserve. The calculation module is a transparent arithmetic aid; it does not simulate a physical movement.

## 2. Controlled system baseline

C-01 remains an automatic mechanical chronograph with:
- hours and minutes;
- running seconds;
- central chronograph seconds;
- elapsed-minute and elapsed-hour counters;
- day-of-week;
- day-of-month (1–31);
- automatic winding.

Hand winding and hacking seconds remain desired features pending compatibility verification. The project frequency target remains 4 Hz / 28,800 vph. The preliminary rate goal of −4/+6 seconds per day remains unvalidated. The 60–70-hour reserve is aspirational and is not an acceptance result.

**Scope control:** the current C-01 baseline is chronograph + weekday + date. The user's requested month window remains an explicit open scope decision against the separate LUNAR concept; it is not silently treated as included in this integration baseline. Moon phase and planetary indications are outside this package.

## 3. Integrated functional architecture

### 3.1 Energy and indication paths

```text
Wrist motion
  -> oscillating rotor / support
  -> winding transmission and direction selection
  -> barrel arbor / mainspring / slipping protection
  -> barrel output
      -> going train
          -> escapement
              -> balance + hairspring timebase
          -> hour / minute / running-seconds indications
          -> calendar drive
              -> weekday indication
              -> date indication
          -> chronograph drive and coupling
              -> central chrono seconds
              -> elapsed-minute / elapsed-hour counters

Crown / stem -> manual winding (if retained) and setting/correction
Pushers -> chronograph control works -> clutch, brake, hammer and reset hearts
Calendar correction controls -> independent day/date correction (if retained)
```

This is a functional allocation, not a selected gear topology. Exact drive take-off points, wheel counts, ratios, clutch placement, and coaxial arrangements remain open until the dial-side and movement-side CAD studies are reconciled.

### 3.2 System ownership and interfaces

| Subsystem | Inputs | Outputs | Integration dependency / evidence |
|---|---|---|---|
| WP-08 winding | Wrist motion, rotor support, barrel state | Stored mainspring energy | Rotor envelope, reverser losses, bridle torque, winding under all states |
| Barrel / power source | Winding input, spring state | Torque versus angle and usable energy | Measured torque curve, usable energy limits, slip repeatability |
| WP-10 going train | Barrel torque, gear geometry | Wheel speeds, torque at branches, escapement supply | Tooth geometry, losses, endshake, wheel/pinion interfaces |
| WP-09 oscillator | Escapement impulses | Timebase and regulated release | Balance/hairspring data, amplitude, rate, beat error, positional behavior |
| WP-11 chronograph | Timed drive, pusher commands | Elapsed-time outputs and incremental load | Clutch engagement, hand jump, reset, load and rate delta |
| WP-12 calendar | Daily drive and correction commands | Weekday/date display and changeover load | Date/weekday indexing, correction safety, month-end manual correction |
| Plates / bridges / case | All component datums and loads | Alignment, retention, shock and service envelope | Controlled CAD, tolerance stack, clearances, assembly access |

Interfaces are not accepted merely because a subsystem model runs. Each interface needs a controlled drawing or data record, a named reference datum or measurement plane, units, revision, and verification evidence.

## 4. Energy accounting and no-double-counting rule

### 4.1 Required measurement discipline

The complete movement energy audit must use a common, documented measurement boundary and common test interval. Record:
- boundary identifier and physical measurement plane;
- interval identifier, start/end definition, and elapsed seconds;
- barrel usable stored energy measured over an approved wind-state range;
- measured energy or power for each non-overlapping load crossing the selected boundary;
- operating state: chronograph stopped/running, calendar idle/changeover, winding state, orientation, temperature, lubrication condition, and sample count;
- instrument identity, calibration status, uncertainty, raw data location, operator, date, and movement revision.

Do not add subsystem values if one value already includes another. For example, do not sum a measured complete going-train-plus-escapement load with a separate escapement load. Do not add chronograph/calendar incremental demand to a total system load that already includes those functions. WP-11 and WP-12 incremental comparisons must be taken at compatible boundaries and matched conditions before they can be included as increments.

### 4.2 Calculation model

`tools/c01_system_integration.py` implements two calculations:

1. **Integrated energy:** sums explicitly listed, non-overlapping measured loads only when each load declares the same `boundary_id` and `interval_id`. Duplicate component identifiers are rejected as a basic double-counting guard. The result reports energy margin, average measured power, and an idealized reserve extrapolation.
2. **Axial stack:** sums supplied nominal dimensions and worst-case plus/minus tolerances. It rejects incomplete or negative data. It is a simple arithmetic stack only, not a geometric datum model, thermal model, deformation model, or statistical RSS analysis.

The energy calculation uses:
- total measured load energy (E_L = sum E_i);
- energy margin (M = E_U - E_L), where (E_U) is measured usable barrel energy;
- average measured load power (P = E_L / Delta t);
- idealized reserve extrapolation (t_R = E_U / P), converted to hours.

The reserve extrapolation is valid only as a first-order comparison if the measured average load represents the intended complete operating profile. Real reserve depends on changing barrel torque, amplitude, escapement behavior, orientation, winding state, chronograph duty cycle, calendar events, and rate limits. It is not a substitute for a full unwind test.

### 4.3 Required energy test cases

- baseline timekeeping, chronograph stopped, calendar idle;
- chronograph running continuously for a defined test window;
- calendar changeover captured with sufficient temporal resolution;
- chronograph running during calendar changeover;
- winding input and barrel energy gain measured separately;
- reserve sweep from full wind through the approved end-of-reserve criterion;
- matched repeats at defined orientations and temperatures.

The test plan must distinguish continuous loads from event loads and avoid multiplying a brief calendar event by an arbitrary daily duty factor without a controlled usage profile.

## 5. Dimensional envelope and axial stack

No movement diameter, thickness, plate spacing, rotor clearance, hand height, dial height, stem height, pusher location, or component tolerance is frozen by WP-13.

The CAD/interface register must capture, for every critical component:
- part number and revision;
- nominal dimension and units;
- tolerance plus/minus and tolerance type;
- datum scheme and inspection method;
- source: controlled CAD, supplier drawing, or calibrated measurement;
- material/thermal condition where relevant;
- mating component and required functional clearance;
- assembly direction, tool access, and service-removal path.

Perform separate analyses for axial stack, radial envelope, hand/dial clearance, rotor/caseback clearance, gear endshake, pivot side-shake, clutch engagement, calendar hand/disc clearance, and pusher/stem travel. A simple sum of axial dimensions cannot prove radial clearance or geometric fit. Worst-case arithmetic and statistical tolerance analysis must not be conflated.

The WP-13 axial-stack helper is a placeholder for measured/CAD inputs. Synthetic unit-test values are not C-01 dimensions.

## 6. Integrated functional-state matrix

| State / transition | Required system behavior | Evidence required |
|---|---|---|
| Normal timekeeping | Stable going train and oscillator; indications advance correctly | Rate, amplitude, power, display indexing |
| Automatic winding | Rotor replenishes barrel without interference or unacceptable disturbance | Rotor/barrel energy, slip behavior, rate/amplitude |
| Manual winding (if retained) | Crown input winds safely without harmful back-drive | Crown torque, reverser interaction, full-wind behavior |
| Chronograph start | Coupling engages and central hand starts without unacceptable jump | High-speed observation, hand jump, rate/load |
| Chronograph running | Elapsed counters advance; timekeeping remains within approved limits | Counter timing, rate delta, energy demand |
| Chronograph stop | Counters hold indicated elapsed time | Stop repeatability and hand stability |
| Chronograph reset | Reset only from stopped state; hands return to zero | Zero-return error, hammer/heart wear, repeated cycles |
| Calendar changeover | Day/date index once per day without stall or partial engagement | Changeover timing, indexing, peak load |
| Chronograph + calendar | Both functions operate concurrently without missed index or unacceptable rate loss | Combined-load and interaction test |
| Date/weekday correction | Independent corrections, if designed, do not damage drive works | Quickset engagement window and misuse tests |
| Low reserve | Rate and amplitude behavior remain within approved criteria until declared end point | Full reserve sweep and stop criterion |
| Shock / recovery | No dislodgement or persistent functional damage | Approved shock protocol, post-shock rate and function |

No numerical acceptance limits are invented here. Each test requires an approved requirement, instrument uncertainty allowance, sample size, conditioning procedure, and pass/fail rule before execution.

## 7. Verification and acceptance matrix

| ID | Verification | Method / recorded evidence | Acceptance status |
|---|---|---|---|
| INT-001 | Subsystem interface closure | Approved interface register and released drawings | TBD |
| INT-002 | Complete movement energy audit | Calibrated energy/torque measurements at controlled planes | TBD |
| INT-003 | Reserve and low-reserve performance | Full unwind test with rate/amplitude logging | 60–70 h aspiration; acceptance TBD |
| INT-004 | Chronograph load and rate interaction | Matched stopped/running trials | Limit TBD |
| INT-005 | Calendar event and combined operation | Instrumented changeover, including chrono-running case | Limit TBD |
| INT-006 | Functional sequencing | Repeated start/stop/reset/correction cycles | Requirements TBD |
| INT-007 | Dimensional fit and tolerance | Released CAD, inspection, stack analysis | Drawings and limits TBD |
| INT-008 | Rotor, hand, dial and case clearance | Worst-case tolerance and physical inspection | Limits TBD |
| INT-009 | Positional, temperature and shock behavior | Approved controlled protocols | Limits TBD |
| INT-010 | Serviceability | Timed disassembly/assembly and documented service trial | Policy and criteria TBD |
| INT-011 | Wear and lubrication stability | Defined cycle-life and aging tests | Duration/criteria TBD |
| INT-012 | Production repeatability | Multiple prototype/build samples and measurement system analysis | Sample plan TBD |

A result is accepted only when linked to raw data, instrument calibration, procedure revision, sample identity, movement configuration, reviewer, and disposition of deviations.

## 8. Interface-control register

The following interfaces are mandatory open records:

| Interface ID | From → To | Controlled items | Closure evidence |
|---|---|---|---|
| IF-01 | Rotor → winding works | Axis, bearing, torque, sweep, clearance | Rotor/winding CAD and measured input profile |
| IF-02 | Winding works → barrel | Arbor geometry, direction, ratio, torque, slip | Interface drawing and full-wind test |
| IF-03 | Barrel → going train | Arbor/pivot, torque-angle envelope, endshake | Barrel output curve and gear mesh drawing |
| IF-04 | Going train → escapement | Escape-wheel interface, impulse energy, rate | Released geometry and escapement test |
| IF-05 | Going train → chronograph | Take-off point, clutch geometry, drive ratio | Kinematic layout and load test |
| IF-06 | Going train → calendar | Daily drive, indexing phase, available torque | Changeover prototype test |
| IF-07 | Chronograph → dial display | Hand axes, counter ratios, zero positions, heights | Dial-side CAD and hand-clearance inspection |
| IF-08 | Calendar → dial display | Weekday/date windows, disc/ring position, correction | Dial-side CAD and correction test |
| IF-09 | Stem/pushers → control works | Travel, force, sealing, positions, interlocks | Case/control drawing and misuse test |
| IF-10 | Plates/bridges → all assemblies | Datums, screws, pivots, endshake, service access | Assembly drawing, tolerance analysis, service trial |

## 9. Critical integration risks

| Risk | Consequence | Mitigation / evidence gate |
|---|---|---|
| Energy budget double-counts or omits loads | False reserve prediction | Common boundary/interval, unique load register, independent audit |
| Chronograph and calendar loads coincide | Amplitude loss, missed indexing, rate disturbance | Combined worst-case operating test |
| Calendar quickset conflicts with changeover | Damaged teeth, jumper or correction works | Mechanically defined safe window and misuse test |
| Rotor or winding works collide with bridges/caseback | Interference, wear, noise | Full tolerance envelope and shock/deflection check |
| Display stack conflicts with hands/dial/crystal | Contact or poor legibility | Dial-side dimensional closure and physical gauge |
| Clutch engagement causes hand jump or high load | Poor timing indication and rate loss | Candidate clutch comparison under measured load |
| Service access compromises robustness | Damage or high service cost | Tool access, modularity, service trial, spare-parts plan |
| Lubricant migration/aging affects multiple systems | Timing, clutch, calendar or winding failure | Lubrication map, aging and contamination testing |
| Supplier substitutions change interfaces | Nonconforming assemblies | Approved supplier drawing and change-control process |

## 10. Open architecture decisions

No architecture freeze is authorized by this document. Open decisions include:
- rotor support, geometry, material, winding direction and reverser;
- mainspring/barrel geometry, usable energy, torque curve and bridle;
- gear-train topology, tooth counts, modules, materials and lubrication;
- balance/hairspring and escapement architecture;
- vertical versus horizontal/lateral chronograph clutch;
- column wheel versus alternative control mechanism;
- counter ratios, hand geometry and dial-side arrangement;
- weekday/date mechanism and correction strategy;
- whether a month window belongs in C-01 or remains in LUNAR;
- case, stem, pusher, plate and bridge envelope;
- hand winding and hacking compatibility.

Every decision must cite alternatives, evidence, consequences, approval owner, and revision.

## 11. Configuration, traceability and engineering change

Use the repository branch and commit history as the configuration record for this preliminary package. Every controlled document and calculation shall carry an ID, revision, status, author/reviewer, date, change summary, and predecessor references.

For each requirement, maintain traceability to:
1. source requirement and rationale;
2. responsible subsystem and interface;
3. analysis or drawing;
4. verification procedure and acceptance criterion;
5. raw evidence and result;
6. review disposition and approved revision.

An engineering change request must identify the initiating issue, affected parts/documents/interfaces, safety and reliability impact, energy and dimensional impact, test regression required, approval, and implementation commit. Do not revise a released interface implicitly through an unrelated subsystem change.

## 12. Architecture-freeze exit gate

C-01 may enter detailed architecture freeze only when all of the following are reviewed and approved:
- complete requirements baseline, including explicit month-window scope decision;
- selected subsystem architectures with documented trade studies;
- measured barrel torque-angle curve and usable stored energy;
- reconciled gear ratios and complete kinematic path;
- complete energy budget with common measurement boundaries and uncertainty;
- demonstrated reserve and low-reserve timekeeping against approved criteria;
- integrated chronograph/calendar concurrent-operation evidence;
- controlled movement, dial-side and case envelope CAD;
- axial and radial tolerance/clearance analyses;
- released interface-control register;
- assembly, lubrication, adjustment and service procedures;
- supplier capability and critical-part sourcing review;
- verification matrix with approved limits and evidence ownership;
- independent engineering review and signed configuration baseline.

A missing item is an open gate, not an assumed pass.

## 13. Revision history

| Revision | Date | Change |
|---|---|---|
| 0.1 | 2026-11-26 | Initial integrated architecture, interfaces, energy-accounting rules, dimensional data schema, verification matrix and release gate |

## 14. Limitations and execution

Run the synthetic unit tests from the tools directory:

```bash
python -m unittest test_c01_system_integration.py
```

The tests validate arithmetic and input rejection only. They do not verify the physical movement, measured energy, dimensions, gear geometry, reserve, accuracy, durability, or manufacturability. Test execution and CI status must be reported separately from the existence of committed test files.
