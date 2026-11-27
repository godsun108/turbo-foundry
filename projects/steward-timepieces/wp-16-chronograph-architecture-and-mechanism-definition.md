# STEWARD C-01 — WP-16 Chronograph Architecture Selection and Detailed Mechanism Definition

**Document ID:** C01-WP-16  
**Revision:** 0.1  
**Status:** Preliminary engineering definition and evidence-gated trade study; no architecture selected  
**Branch:** `steward/c-01-movement-foundation`  
**Predecessors:** WP-10 Gear Train; WP-11 Chronograph Mechanism; WP-13 System Integration; WP-14 Movement Architecture; WP-15 Gear-Train Topology and Placement  
**Next gate:** approved dial candidate, movement envelope, measured drive/load inputs, and documented architecture review

## 1. Purpose

WP-16 advances the chronograph from functional concept to a detailed architecture decision package. It separates the two major independent choices—**coupling/clutch architecture** and **operating-control architecture**—then defines the interfaces, reset mechanism, counters, energy measurements, tolerance work, and prototype tests required to select and detail them.

The chronograph remains the defining C-01 complication. It must provide central elapsed seconds, elapsed minutes, and elapsed hours while preserving base timekeeping and serviceability.

This is not a completed mechanism design. No physical geometry, tooth count, spring force, friction coefficient, material, tolerance, pusher force, or performance result is assigned.

## 2. Controlled baseline

The current C-01 requirement set includes:
- central chronograph seconds;
- elapsed-minute counter;
- elapsed-hour counter;
- start, stop and reset;
- reset prohibited while running;
- automatic mechanical movement;
- day and date;
- 4 Hz / 28,800 vph target (preliminary);
- 60–70-hour reserve aspiration (unvalidated).

WP-11 already defines the logical state machine and initial vertical/horizontal clutch and column-wheel/cam alternatives. WP-16 refines the comparison; it does not overwrite WP-11 or claim that its state model proves physical interlocking.

Flyback is excluded from the baseline unless formally added through requirements change control. Month display remains outside C-01's current requirements boundary; the project README places month and moon-phase features in the separate LUNAR concept.

## 3. Architecture decomposition

Treat the chronograph as five interacting mechanisms:

1. **Drive take-off:** derives motion from an approved going-train member.
2. **Coupling and running train:** transmits drive to central chronograph seconds and counter mechanisms only when commanded.
3. **Control and braking:** sequences start, stop, coupling, and stopped-train restraint.
4. **Reset and zeroing:** returns all elapsed-time indications to a repeatable zero datum.
5. **Totalizers:** converts continuous chronograph motion into elapsed-minute and elapsed-hour indications.

The control system must have a positive mechanical state definition. Software state logic is a verification aid only.

## 4. Coupling architecture trade study

### 4.1 Candidate C-V — vertical friction clutch

Functional principle: drive and chronograph members remain in the designed axial relationship; a controlled axial engagement brings friction surfaces into torque-transmitting contact.

**Potential advantages to verify**
- Avoids lateral tooth entry at the instant of start.
- Can reduce start-hand jump if drag, runout, friction and train compliance are controlled.
- May allow continuously meshed downstream chronograph gearing.

**Critical risks**
- Axial stack height, endshake, runout and contact-pressure sensitivity.
- Residual drag in the disengaged state.
- Friction material, surface finish, wear, contamination and lubricant migration.
- Clutch slip under counter-indexing or reset-related disturbances.
- Assembly phasing and service adjustment complexity.

**Required design outputs**
- Driven and driving friction member geometry.
- Engagement travel and axial tolerance stack.
- Spring/preload strategy and adjustment method.
- Disengaged clearance and residual-drag limit.
- Torque capacity and slip verification.
- Surface/material/lubricant compatibility evidence.

### 4.2 Candidate C-H — horizontal/lateral gear coupling

Functional principle: a controlled lateral movement engages a chronograph wheel with a continuously driven wheel or pinion.

**Potential advantages to verify**
- Positive toothed drive when fully engaged.
- Direct visual inspection of engagement and wear.
- Potentially straightforward component replacement and diagnosis.

**Critical risks**
- Tooth-to-tooth contact or hand jump at engagement.
- Engagement depth, backlash and center-distance sensitivity.
- Partial engagement, tip interference and tooth wear.
- Lateral control travel, spring forces and packaging demand.

**Required design outputs**
- Gear tooth form and compatible geometry.
- Engagement depth and travel stops.
- Backlash and center-distance tolerance analysis.
- Anti-partial-engagement control geometry.
- Start impact and wear verification.

### 4.3 Coupling comparison matrix

| Criterion | Vertical clutch evidence | Horizontal clutch evidence | Status |
|---|---|---|---|
| Start hand jump | High-speed optical angle capture | High-speed optical angle capture | Open |
| Disengaged drag | Torque/load measurement while stopped | Drag and rubbing measurement | Open |
| Running load | Matched energy and rate tests | Matched energy and rate tests | Open |
| Packaging | Axial stack and rotor/bridge clearance | Radial sweep and control travel | Open |
| Wear | Friction-surface inspection and endurance | Tooth/contact inspection and endurance | Open |
| Adjustment | Axial setting and repeatability trial | Engagement-depth setting trial | Open |
| Service | Timed remove/inspect/reassemble | Timed remove/inspect/reassemble | Open |
| Manufacturing | Supplier process capability | Gear and pivot process capability | Open |

No winner is declared. Neither architecture should be preferred solely because it is common in a particular price class or associated with a known movement family.

## 5. Operating-control architecture trade study

The control architecture is a separate decision from clutch type.

### 5.1 Candidate K-CW — column wheel

A column wheel provides indexed control states through columns and intervening gaps acting on levers.

Define and verify:
- column count and profile;
- indexing finger and jumper geometry;
- column-wheel angular step and state phasing;
- lever contact geometry and travel;
- pusher-to-indexing transmission;
- positive prevention of reset while running;
- spring return, bounce and incomplete indexing;
- assembly datum and adjustment sequence.

Do not assume a column wheel is automatically more precise or more durable. Its suitability depends on geometry, process capability, wear surfaces and service procedures.

### 5.2 Candidate K-CAM — cam/lever control

A shaped cam or coordinated cam surfaces actuate the operating levers through defined positions.

Define and verify:
- cam profile and dwell regions;
- follower geometry and contact stress;
- state retention and detent/jumper method;
- lever sequencing and travel;
- reset interlock;
- pusher force/travel and return;
- wear, lubrication, and tolerance sensitivity.

A cam/lever design may simplify some manufacturing or assembly operations, but must demonstrate equally robust state sequencing and serviceability.

### 5.3 Control comparison matrix

| Criterion | Column wheel | Cam/lever | Status |
|---|---|---|---|
| State determinism | Indexed-state geometry and cycle test | Cam dwell and state-retention test | Open |
| Reset interlock | Mechanical blocking inspection/test | Mechanical blocking inspection/test | Open |
| Pusher feel | Force/travel curve | Force/travel curve | Open |
| Partial actuation | Interrupted-pusher test | Interrupted-pusher test | Open |
| Wear | Contact inspection after endurance | Contact inspection after endurance | Open |
| Tolerance sensitivity | Column/lever stack analysis | Cam/follower stack analysis | Open |
| Service | Phasing and adjustment trial | Phasing and adjustment trial | Open |
| Manufacture | Supplier capability and inspection | Supplier capability and inspection | Open |

## 6. Combined architecture candidates

Keep the design space explicit:

| Candidate | Coupling | Control | Key question |
|---|---|---|---|
| A | Vertical | Column wheel | Can axial clutch stack and indexed controls fit while remaining serviceable? |
| B | Vertical | Cam/lever | Can cam state retention and vertical-clutch adjustment be made robust? |
| C | Horizontal | Column wheel | Can the lateral engagement path be controlled without excessive hand jump? |
| D | Horizontal | Cam/lever | Can the cam deliver reliable engagement depth and reset blocking? |

These are combinations for investigation, not four completed designs. The selected control must be compatible with the selected clutch's travel, engagement direction, timing and return requirements.

## 7. Required mechanical sequence

The detailed mechanism must produce these physical states:

| State | Coupling | Brake/stop | Reset hammer | Allowed transition |
|---|---|---|---|---|
| Stopped at zero | Disengaged | Applied/defined hold | Withdrawn after reset | Start |
| Running | Engaged | Released | Positively clear | Stop |
| Stopped, elapsed value retained | Disengaged | Applied/defined hold | Withdrawn | Start or reset |
| Reset transient | Disengaged | Controlled as required | Contacts all reset hearts | Return to stopped at zero |

The exact brake behavior must be defined for the chosen topology. A stopped chronograph must not creep, and the reset hammer must not obstruct or damage a driven wheel train.

### 7.1 Mechanical interlock requirements

- Reset command while running must be physically blocked.
- Start/stop actuation must not leave the coupling partially engaged.
- Pusher return must not depend on a fragile or ambiguous friction balance.
- Simultaneous or rapid repeated commands must have a defined non-damaging result.
- The stopped state must retain elapsed indication without unintended motion.
- The reset sequence must not begin until drive isolation and required stop conditions are achieved.

Verify these with transparent prototype plates or high-speed observation where practical. A passing software state-machine test is not acceptance evidence for the physical mechanism.

## 8. Reset-to-zero mechanism

### 8.1 Heart cams and reset hammer

WP-11 identifies heart cams as the current concept. WP-16 retains that concept for investigation, not as a frozen design.

Each elapsed-time arbor requiring reset must have:
- a heart-cam profile concentric to its arbor;
- a controlled zero datum aligned to the dial scale;
- a hammer contact surface and defined contact direction;
- sufficient torque to overcome friction and hand inertia;
- retention against hand slip on the arbor;
- clearance from adjacent wheels, bridges and hands.

A common hammer may reset multiple hearts, or separate hammer elements may be used. Compare both approaches for simultaneous contact, tolerance stack, peak force, reset time, service access and risk that one heart reaches zero before another.

### 8.2 Reset design calculations

The detailed design shall calculate or measure:
- hand and arbor rotational inertia;
- friction torque at each pivot and hand fit;
- heart-cam restoring torque versus angular position;
- hammer contact force and lever ratio;
- spring energy and peak reaction load;
- reset time and rebound;
- zero-angle error and repeatability;
- effects of wear, lubrication and temperature.

No values are assigned in this work package because actual hand geometry, materials, pivots and spring design are not available.

### 8.3 Reset acceptance

Use calibrated optical measurement of each hand after repeated reset cycles. Define acceptance limits from scale graduation, hand length, viewing distance, manufacturing capability and project readability requirements. Record all elapsed hands independently; do not hide a poor counter reset behind a good central-seconds result.

## 9. Counter train definition

The 30-minute and 12-hour totalizers must be derived from the selected chronograph seconds train and controlled indexing mechanism.

For each counter, document:
- source wheel and cadence;
- continuous or intermittent transfer;
- gear ratio and direction;
- indexing finger, star, jumper or equivalent;
- carry timing and anti-backlash behavior;
- hand inertia and required torque;
- zero heart/cam and reset interface;
- lost motion and cumulative indication error.

Do not assume the minute/hour totalizers are simple continuously geared outputs. If intermittent indexing is used, model the event timing, impulse, carry load and interaction with the running chronograph separately.

## 10. Drive-point and energy interface

The chronograph drive take-off remains open under WP-15. For each candidate drive point, calculate its available speed and torque from the selected going-train topology and WP-10 measurement inputs.

Measure separately:
1. chronograph stopped residual drag;
2. chronograph running steady load;
3. start engagement transient;
4. stop transient;
5. minute-counter indexing event;
6. hour-counter carry event;
7. reset hammer event;
8. combined worst-case event sequence.

Use identical measurement boundaries, reserve state, temperature, orientation and lubrication conditions when comparing candidates. Capture transient events at adequate sampling rate. Compare chronograph-off/on amplitude and rate using WP-09 protocols at full, intermediate and low reserve.

No generic energy penalty, amplitude drop or rate shift is assumed.

## 11. Preliminary interface-control register

| Interface ID | From | To | Controlled data required | Owner |
|---|---|---|---|---|
| CH-IF-01 | Going train | Chronograph take-off | Source axis, speed, torque curve, mesh geometry | Train |
| CH-IF-02 | Take-off | Clutch | Drive axis, engagement plane, torque capacity | Chronograph |
| CH-IF-03 | Control | Clutch | Travel, state, return, interlock | Chronograph |
| CH-IF-04 | Clutch | Chronograph seconds train | Output cadence, drag, backlash, support | Chronograph |
| CH-IF-05 | Seconds train | Minute totalizer | Index cadence, impulse, phase, reset | Totalizer |
| CH-IF-06 | Minute totalizer | Hour totalizer | Carry cadence, impulse, phase, reset | Totalizer |
| CH-IF-07 | Control | Brake/stop | Stop timing, holding torque, release clearance | Chronograph |
| CH-IF-08 | Reset control | Hammer/hearts | Hammer travel, contact, reset force, zero datum | Reset |
| CH-IF-09 | Chronograph | Dial/hand stack | Axis, hand height, sweep, scale and zero alignment | Display |
| CH-IF-10 | Chronograph bridges | Main plate/case | Pivot support, fastening, access, service envelope | Packaging |

All interface values remain TBD until backed by source drawings, calculations or measurements.

## 12. Evidence-gated decision method

The executable helper `tools/c01_chrono_trade.py` calculates weighted totals only when:
- at least two candidates are compared;
- every criterion has an approved weight and acceptance basis;
- weights sum to 1.0;
- every candidate has a score for every criterion;
- every score is within the declared 1–5 review scale;
- every score has a traceable evidence description.

The helper does not supply weights, scores, acceptance limits or a preferred candidate. Scores remain reviewer judgements unless backed by an identified measurement/test report. Even a calculated ranking is provisional and requires recorded engineering approval.

Run from the tools directory:

```bash
python -m unittest test_c01_chrono_trade.py
```

Synthetic unit-test values are software fixtures only; they are not C-01 test data or architecture evidence.

## 13. Verification and acceptance plan

| ID | Verification | Acceptance criterion |
|---|---|---|
| CH16-01 | Drive-point feasibility | Speed and torque close from controlled going-train data |
| CH16-02 | Clutch engagement | Reliable full engagement; hand jump within approved limit |
| CH16-03 | Disengaged drag | Residual drag within approved energy/timekeeping budget |
| CH16-04 | Control sequencing | All states and transitions mechanically deterministic |
| CH16-05 | Reset interlock | Reset physically impossible while running |
| CH16-06 | Stop retention | No unacceptable creep or elapsed-time loss while stopped |
| CH16-07 | Reset zero | Every elapsed hand returns within approved optical tolerance |
| CH16-08 | Counter cadence | Minute/hour indication correct with no missed/double indexing |
| CH16-09 | Energy/timekeeping | Chronograph-on/off effects within approved WP-09/WP-10 limits |
| CH16-10 | Endurance | No unacceptable wear, drift, partial engagement or failure |
| CH16-11 | Serviceability | Assembly, adjustment, lubrication and replacement demonstrated |
| CH16-12 | Manufacturability | Supplier process capability and inspection method documented |

Numerical limits must be approved before test execution. A test cannot pass against an undefined threshold.

## 14. Failure-mode review inputs

| Failure mode | Effect | Required control |
|---|---|---|
| Clutch drag while stopped | Reduced reserve / timekeeping disturbance | Disengaged-clearance and matched load test |
| Clutch slip while running | Elapsed-time error | Torque-capacity and endurance test |
| Partial engagement | Intermittent drive or damaged teeth | Positive travel stops and engagement inspection |
| Control bounce/double step | Wrong operating state | Jumper/retention and rapid-actuation test |
| Reset while running | Component damage | Positive mechanical interlock |
| Hammer misses one heart | One counter remains offset | Multi-point contact and optical reset verification |
| Hand slips on arbor | Loss of zero alignment | Hand-fit retention and shock/endurance test |
| Counter carry stalls | Incorrect elapsed indication | Carry-event torque and low-reserve test |
| Excessive indexing impulse | Amplitude disturbance | High-rate transient load measurement |
| Poor access | Service damage / high repair cost | Assembly sequence and watchmaker service review |

## 15. Architecture selection gate

No architecture is selected until:
1. The dial candidate and register axes are sufficiently defined to compare layouts.
2. The WP-15 drive-point alternatives are reconciled with going-train kinematics.
3. The case, plate, bridge and rotor envelopes are available.
4. Clutch and control candidates have dimensioned concept layouts.
5. Matched energy, hand-jump, reset and service test methods are approved.
6. Numerical acceptance limits are authorized.
7. Supplier/manufacturing input is recorded.
8. The weighted trade study has traceable evidence and an approved decision record.
9. WP-13 system integration and WP-14/WP-15 placement models are updated to the selected configuration.

## 16. Revision control

| Revision | Change | Status |
|---|---|---|
| 0.1 | Initial detailed clutch/control comparison, combined candidate set, mechanical sequence, reset, totalizer, interfaces and verification definition | Preliminary; review required |

**Release statement:** WP-16 defines the engineering evidence required to select and detail the C-01 chronograph. It does not declare a winning clutch or control architecture, nor claim a completed, dimensioned, tested or production-ready mechanism.
