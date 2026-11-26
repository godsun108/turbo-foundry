# STEWARD C-01 — WP-09 Balance and Escapement Engineering Definition

**Document ID:** C01-WP-09  
**Revision:** 0.1  
**Status:** Preliminary engineering basis and verification plan  
**Branch:** `steward/c-01-movement-foundation`  
**Predecessor:** WP-08 Automatic Winding Architecture  
**Next gate:** architecture trade study, instrumented escapement prototype, and controlled verification

## 1. Purpose and scope

Define the balance, hairspring, escapement, shock protection, regulation, and timekeeping verification work required for C-01. The package establishes calculations, measurement definitions, decision gates, acceptance logic, and service requirements. It does not claim a validated escapement or production-ready movement.

The C-01 functional scope remains automatic mechanical chronograph with day-of-week and day-of-month indications. The balance/escapement must be evaluated in the complete movement, including automatic winding, barrel, gear train, chronograph, and calendar loads.

## 2. Controlled design basis

| Parameter | Basis | Status |
|---|---|---|
| Nominal balance frequency | 4 Hz | Project target |
| Vibrations per hour | 28,800 vph | Derived from 4 Hz × 2 beats/cycle × 3,600 s/h |
| Full oscillation period | 0.250 s at exactly 4 Hz | Derived target |
| Beat interval | 0.125 s at exactly 4 Hz | Derived target |
| Proposed rate goal | −4/+6 s/day | Preliminary project target from C-01 baseline; not validated |
| Balance inertia | Measured / supplier-confirmed | TBD |
| Hairspring stiffness | Measured / supplier-confirmed | TBD |
| Balance amplitude limits | Approved test-method-specific limits | TBD |
| Beat-error limit | Approved test-method-specific limit | TBD |
| Positional spread limit | Approved test-method-specific limit | TBD |
| Chronograph rate-delta limit | Approved system requirement | TBD |
| Power-reserve target | 60–70 h aspirational | Not validated by WP-09 |

The frequency conversion is a kinematic definition, not a rate-accuracy claim. A 4 Hz oscillator can still run fast or slow if its effective period differs from nominal.

## 3. Functional architecture

Energy path:

**Mainspring barrel → going train → escapement wheel → pallet fork → balance impulse jewels → balance wheel / hairspring oscillator.**

The escapement alternately locks and releases the escape wheel and supplies timed impulses to compensate for losses. The balance/hairspring provides the oscillator reference. The final architecture must establish pallet geometry, lock, draw, impulse, drop, safety action, lubrication points, and adjustment access.

Candidate escapement architecture remains open pending a documented trade study. Evaluate service history, energy demand, shock behavior, manufacturing tolerance, lubrication stability, adjustment burden, and long-term parts availability. Do not declare a proprietary or superior escapement without comparative evidence.

## 4. First-order oscillator calculations

For an ideal small-angle torsional oscillator:

- Angular natural frequency: `ω₀ = √(κ / I)`
- Natural frequency: `f₀ = ω₀ / (2π)`
- Full oscillation period: `T = 1 / f₀`
- Beat interval: `T / 2`

Where:
- `I` = measured balance assembly moment of inertia (kg·m²)
- `κ` = measured hairspring torsional stiffness (N·m/rad)

At the 4 Hz target, the ideal period is 0.25 s and the half-period is 0.125 s. These values are derived from the target only. The ideal oscillator equation excludes escapement impulse, amplitude dependence, hairspring nonlinearity, pivot losses, air resistance, positional effects, temperature, and shock.

The executable model `tools/c01_balance_escapement.py` calculates the ideal natural frequency from supplied inertia and stiffness. It does not invent either input or claim the real escapement will operate at that calculated frequency.

## 5. Balance and hairspring engineering

Characterize, then select:
- balance wheel material, geometry, inertia distribution, poising method, and adjustment strategy;
- hairspring material, geometry, terminal curve, stud/collet attachment, active length, and breathing concentricity;
- balance staff, pivots, endshake, side shake, and jewel interfaces;
- regulator architecture or free-sprung alternative;
- thermal sensitivity, magnetism susceptibility, shock response, and service replacement method.

Required evidence:
1. Balance inertia measurement and repeatability.
2. Static and dynamic poise assessment in defined orientations.
3. Hairspring stiffness and rate response over the working amplitude range.
4. Hairspring concentric breathing and clearance checks.
5. Temperature and magnetic exposure screening using an approved protocol.
6. Repeatability after disassembly/reassembly and regulation.

No balance diameter, mass, inertia, hairspring alloy, stiffness, terminal curve, regulator type, or manufacturing tolerance is frozen in WP-09.

## 6. Escapement engineering and losses

The escapement study must document:
- escape-wheel tooth count, tooth form, material, hardness, and finish;
- pallet material, jewel geometry, pallet angle, lock, drop, draw, and impulse;
- fork banking, guard pin, safety roller, impulse jewel, and roller-table geometry;
- friction and lubrication locations, lubricant specification, application quantity, and aging;
- energy delivered per cycle and energy lost through locking, unlocking, sliding, impact, and friction;
- tolerance stack-up and sensitivity to wear, contamination, and shock.

Measure the complete escapement's operating behavior on a calibrated fixture. Any analytical model must state assumptions and be reconciled against measured torque/energy and timing behavior before it is used for design release.

## 7. Shock protection

Compare available shock-protection architectures against the actual balance-staff and jewel geometry. Verify:
- radial and axial displacement under the specified shock protocol;
- jewel seating and retention after shock;
- staff/pivot integrity and permanent deformation;
- endshake and side-shake before and after shock;
- amplitude and rate recovery after shock;
- repeatability after multiple orientations and service cycles.

The shock pulse, acceleration, duration, direction, number of impacts, and pass/fail limits must be defined by an approved standard or controlled project requirement before testing. WP-09 assigns no arbitrary shock rating.

## 8. Regulation and beat-error adjustment

Provide a documented procedure for:
1. demagnetization screening and instrument zero/reference checks;
2. full-wind and defined reserve-state stabilization;
3. beat-rate and beat-error measurement;
4. rate measurement in each specified position;
5. regulator or free-sprung adjustment method;
6. repeat measurement after each adjustment;
7. recording environmental conditions, lift angle setting, instrument identity, operator, and movement revision.

Beat error must be measured using a calibrated timing instrument with the correct lift-angle and escapement settings. The lift angle is a measurement-instrument parameter, not a value to guess. Record it with every amplitude result.

If a regulator is selected, document index movement, effective hairspring length change, adjustment sensitivity, and anti-shock retention. If free-sprung regulation is selected, document mass adjustment increments, tool access, balance poise impact, and service repeatability. Selection remains open.

## 9. Verification matrix and acceptance logic

All numerical acceptance limits except the 4 Hz nominal target and the previously recorded preliminary rate goal require formal approval before test release.

| Test | Measurements | Acceptance basis |
|---|---|---|
| Frequency | Measured beat frequency | 4 Hz nominal with approved measurement tolerance |
| Rate | s/day in each defined position | Approved rate limits; preliminary project goal −4/+6 s/day |
| Amplitude | Degrees, instrument lift angle, position, reserve state | Approved position- and reserve-specific envelope |
| Beat error | ms | Approved maximum |
| Positional variation | Rate spread across defined positions | Approved maximum |
| Reserve sweep | Amplitude and rate at measured states of wind | Every point within approved envelope |
| Chronograph interaction | Matched chrono-off and chrono-on rate/amplitude | Difference within approved system limits |
| Calendar interaction | Timing before/during/after changeover | No stoppage, interference, or unacceptable disturbance |
| Automatic winding interaction | Timing and amplitude during controlled rotor input | No unacceptable disturbance or loss of escapement function |
| Shock | Pre/post rate, amplitude, geometry, jewel retention | Approved shock protocol and recovery criteria |
| Temperature | Rate/amplitude across defined temperature points | Approved environmental specification |
| Service repeatability | Before/after service measurements | Within approved limits and documented adjustment range |

The executable evaluator requires the test record and all applicable limits explicitly. Missing limits cause an error; the program does not substitute guessed thresholds.

## 10. Power-reserve and load-state protocol

Use the actual barrel/mainspring torque curve when available. Test at measured states of wind, not inferred clock time alone. At each state record:
- reserve-state descriptor and elapsed time from a defined start;
- barrel torque or validated proxy;
- amplitude and rate in each required position;
- beat error;
- chronograph state;
- calendar state;
- temperature and instrument configuration.

Include full-wind, intermediate, and low-reserve conditions. The 60–70-hour objective remains aspirational until a complete movement demonstrates it under a controlled protocol. Confirm that the escapement remains within its approved amplitude/rate envelope throughout the usable reserve.

## 11. Chronograph-on versus chronograph-off test

Run paired tests on the same movement, at matched reserve state, position, temperature, and stabilization interval:
1. Record baseline rate and amplitude with chronograph stopped.
2. Start chronograph and record rate/amplitude after the defined stabilization interval.
3. Record central seconds, minute/hour counter operation, clutch state, and any hand jump.
4. Stop and reset; record transient disturbance and recovery.
5. Repeat across multiple reserve states and positions.
6. Compare paired results; preserve raw observations and calculate the absolute rate delta.

Do not attribute a rate shift to the escapement alone until gear-train loading, clutch drag, coupling alignment, and chronograph train friction have been isolated.

## 12. Service and calibration requirements

The service manual must include:
- balance complete removal/installation and handling precautions;
- hairspring protection, centering, and concentricity inspection;
- pallet fork and escape-wheel inspection criteria;
- jewel, pivot, banking, lock, and endshake checks;
- approved lubricant locations and quantities from validated supplier/process data;
- timing-machine setup, lift-angle record, positional sequence, and regulation workflow;
- post-service shock, timing, amplitude, and reserve checks;
- replaceable wear-part list, tool list, and inspection intervals established from life testing.

Service acceptance must be repeatable by a qualified watchmaker using documented tools and calibrated equipment.

## 13. Failure modes and controls

| Failure mode | Effect | Detection / control |
|---|---|---|
| Hairspring deformation or contact | Rate instability / stoppage | Clearance inspection, poise and timing checks |
| Magnetization | Rate error / hairspring interaction | Magnetic screening and approved demagnetization process |
| Pivot or jewel damage | Amplitude loss / stoppage | Microscopic inspection, amplitude and rate comparison |
| Escapement contamination or lubricant migration | Locking/impulse instability | Inspection, controlled lubrication, endurance testing |
| Incorrect lock/drop/draw | Unlocking failure or excess loss | Fixture measurement and tolerance verification |
| Shock displacement | Stoppage or rate shift | Defined shock protocol and post-test geometry/timing |
| Chronograph load interaction | Rate/amplitude disturbance | Matched chrono-on/off test |
| Low-reserve amplitude collapse | Loss of timekeeping stability | Reserve sweep with measured barrel state |
| Adjustment drift after service | Poor repeatability | Retention and post-service calibration tests |

## 14. Revision and decision register

| Item | WP-09 status |
|---|---|
| Nominal frequency | 4 Hz project target |
| Balance inertia / hairspring stiffness | TBD; measure or obtain supplier data |
| Balance geometry/material | Open |
| Hairspring material/geometry | Open |
| Escapement type | Open pending trade study |
| Shock-protection architecture | Open pending geometry and test protocol |
| Regulator vs free-sprung | Open |
| Lift angle | TBD from selected escapement and instrument setup |
| Amplitude envelope | TBD; approve by position and reserve state |
| Beat-error limit | TBD |
| Positional rate-spread limit | TBD |
| Chronograph rate-delta limit | TBD |
| Shock/environmental criteria | TBD from approved standard/specification |
| Production/service tolerances | Not released |

## 15. Release gate

WP-09 may advance to preliminary design release only when:
1. escapement and balance architecture trade study is documented;
2. balance inertia and hairspring stiffness are measured or supplier-confirmed;
3. dimensional interfaces and tolerance stack are defined;
4. shock-protection architecture is selected against a specified test protocol;
5. numerical acceptance limits are approved and traceable;
6. instrumented prototype results support timing, reserve-sweep, and chronograph interaction claims;
7. service and calibration procedure is reviewed.

**Current disposition:** engineering definition and measurement framework only. No production geometry, measured performance, validated accuracy, shock rating, or prototype pass is claimed.
