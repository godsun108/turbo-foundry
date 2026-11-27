# WP-33 — Chronograph Architecture Decision and Prototype Mechanism Definition

- Document ID: SEB-C01-WP-33
- Revision: A — initial controlled issue
- Status: Candidate architecture and decision framework; no winner selected
- Branch: steward/c-01-movement-foundation
- Software: tools/c01_chrono_architecture.py
- Verification: tools/test_c01_chrono_architecture.py
- Predecessors: WP-11, WP-16, WP-17, WP-19, WP-20, WP-25, WP-28, WP-29, WP-30, WP-32

## 1. Purpose and design boundary

The chronograph is the defining complication of STEWARD C-01. WP-33 advances its architecture decision and prototype definition without claiming that a physical mechanism, gear schedule or package has been selected.

This issue formalizes the four combinations already defined by WP-16:
- A: vertical friction clutch + column-wheel control
- B: vertical friction clutch + cam/lever control
- C: horizontal/lateral gear coupling + column-wheel control
- D: horizontal/lateral gear coupling + cam/lever control

All four remain candidates. No winner is selected by convention, popularity, aesthetic preference or software score. Selection requires approved requirements, comparable evidence, geometry and energy analysis, and design-authority approval.

## 2. Controlled functional requirements

The mechanism shall provide:
- central chronograph seconds indication;
- elapsed-minute and elapsed-hour indications;
- start, stop and retained elapsed-time behavior;
- reset to a defined zero datum while stopped;
- positive prevention of reset while running;
- repeatable state transitions without partial engagement;
- acceptable base-timekeeping impact, energy demand and serviceability.

The 4 Hz / 28,800 vph movement target remains preliminary. The 60–70 hour reserve remains an aspiration and must not be represented as demonstrated performance.

Flyback is excluded unless added through formal requirements change control. Counter behavior (continuous or jumping) remains an explicit decision. This package does not resolve the month-window scope or dial arrangement.

## 3. Candidate architecture definitions

### 3.1 Vertical friction clutch

A drive member and chronograph member are coupled by controlled axial contact. Required design evidence includes axial stack, engagement travel, preload strategy, disengaged clearance, friction material and surface compatibility, residual drag, slip capacity, runout, wear and service adjustment. A vertical clutch may avoid lateral tooth entry, but that does not prove low hand jump or low running load.

### 3.2 Horizontal/lateral coupling

A driven chronograph wheel is brought into toothed engagement with a drive wheel by controlled lateral motion. Required evidence includes tooth form, engagement depth, center distance, backlash, travel stops, partial-engagement prevention, tooth-entry impact, wear and service adjustment. Positive toothed engagement does not prove acceptable start shock or packaging.

### 3.3 Column-wheel control

An indexed wheel and operating levers sequence start, stop and reset. The detailed definition must include indexing, state phasing, column/follower geometry, jumper retention, lever travel, pusher transmission, interrupted actuation behavior, wear and adjustment.

### 3.4 Cam/lever control

One or more cam profiles and followers sequence operating levers. The detailed definition must include dwell/state retention, follower contact, detent or jumper strategy, lever travel, pusher transmission, interrupted actuation behavior, wear and adjustment.

The control choice is independent of clutch choice at the trade-study level, but the final geometry and motion directions must be mutually compatible.

## 4. Trade-study criteria and calculations

Compare candidates using the same eight criteria:
1. start disturbance, including hand jump and engagement transient;
2. steady running energy and off-state drag;
3. packaging, including axial/radial envelopes and tolerance stack;
4. state reliability, including interrupted and repeated actuation;
5. reset repeatability and zero alignment;
6. wear life under an approved endurance protocol;
7. serviceability, including inspection and adjustment repeatability;
8. manufacturability, inspection capability and supplier evidence.

For each candidate and criterion, assign a 1–5 score only after the criterion definition, measurement method, acceptance range and evidence record are approved. The score scale must be documented by the review team; this package does not invent a universal meaning for a score of 1 or 5.

Weighted score:
  
    S(candidate) = sum(weight_i * score_i)

Weights are non-negative and sum exactly to 1. Scores and evidence IDs are required for every criterion. The executable model uses exact rational arithmetic for the weight sum and weighted totals. It returns a provisional ranking only; it cannot authorize a decision. A tie remains a tie, not an excuse to select arbitrarily.

No weights, scores or measurement results are populated for C-01 in this issue.

## 5. Physical state sequence and interlocks

Required state sequence:

| Current state | Command | Required state | Physical requirement |
|---|---|---|---|
| Stopped at zero | Start | Running | Couple drive, clear stop element, keep reset hammer clear |
| Running | Stop | Stopped, value retained | Decouple drive and positively retain elapsed position |
| Stopped, value retained | Start | Running | Resume from retained elapsed position |
| Stopped, value retained | Reset | Stopped at zero | Release hammer, return all hearts, withdraw hammer |
| Running | Reset | Running; reset blocked | Positive mechanical interlock; no partial reset |

The mechanism must define the stopped-train restraint (brake, detent or equivalent), coupling return behavior, hammer clearance, lever sequencing and state retention. The exact brake topology remains open until candidate geometry is developed.

The software state-transition validator is a logical requirement checker. A reset-while-running transition is accepted only when a physical interlock evidence reference is supplied, and it must leave the chronograph running. This is not proof that a real mechanism contains or passes that interlock.

## 6. Reset-to-zero mechanism

WP-16 identifies heart cams and a hammer as the preliminary reset concept. WP-33 retains that concept for investigation, not as a fully dimensioned design.

The detailed prototype definition must specify:
- zero datum for each hand and arbor;
- heart-cam concentricity/profile and attachment;
- hammer face, contact sequence and simultaneous return strategy;
- hammer travel, force path, spring return and withdrawal;
- hand/arbor retention against slip;
- counter jumper and indexing phase;
- tolerance stack and hand-height clearances;
- optical zero-error measurement method.

Acceptance limits remain open until dial scale/readability, hand geometry, manufacturing capability and measurement uncertainty are approved. Do not assign arbitrary angular tolerances.

## 7. Counter train and kinematic closure

Retain WP-17's conditional continuous-indication conventions:
- central chronograph seconds: 1 revolution/minute;
- 30-minute totalizer: 1/30 revolution/minute if continuous;
- 12-hour totalizer: 1/720 revolution/minute if continuous.

These are display-speed conventions, not selected gear ratios. A jumping counter requires a separate indexing/carry analysis, including event timing, energy impulse, backlash, jumper force, phase and reset behavior.

The source arbor, drive take-off, tooth counts, module, gear direction, compound arbors, counter cadence and hand inertia remain unselected. Kinematic closure must use an approved source speed and explicit candidate gear data, then pass WP-19 geometry and WP-24 support checks. Tooth-count synthesis from WP-18/WP-26 is a candidate-generation tool, not a design approval.

## 8. Prototype measurement programme

Each candidate must be tested under matched, documented conditions. The measurement plan shall include:

| Measurement | Purpose | Evidence method |
|---|---|---|
| Start hand jump | Quantify engagement disturbance | High-speed optical angle/time capture |
| Steady running load | Compare power demand | Matched torque/speed or energy measurement at declared boundary |
| Off-state drag | Quantify stopped-state losses | Calibrated torque/load measurement |
| Pusher force/travel | Compare control feel and actuation margin | Force-displacement instrumentation |
| Reset zero error | Quantify return repeatability | Optical angular measurement |
| Repeated-cycle reliability | Detect incomplete states and failures | Controlled start/stop/reset cycling |
| Wear inspection | Identify contact degradation | Defined microscopy/inspection before and after endurance |
| Assembly/service time | Assess repeatability and access | Recorded timed service trial |
| Base rate delta | Assess chronograph interaction | Matched WP-09/WP-28 timing test |

Record instrument IDs, calibration status, sampling method, uncertainty budget, movement state, reserve state, temperature, orientation, lubrication condition, operator and configuration revision. Compare candidates only when their test conditions and measurement boundaries are materially comparable.

The actual acceptance limits, cycle counts, sampling frequencies and environmental conditions require approved WP-30 procedures; none are fabricated here.

## 9. Required prototype mechanism deliverables

Before selecting a candidate for P0:
1. candidate assembly schematic with all moving members and states;
2. clutch/control interface-control definition;
3. source drive and counter kinematic diagram;
4. reset hammer/heart-cam arrangement and zero datum definition;
5. stopped-train retention and reset interlock concept;
6. candidate-specific 2D/3D envelope and axial stack;
7. tolerance and dynamic-clearance review;
8. energy/load measurement boundary and test plan;
9. service access and assembly sequence;
10. risk assessment and documented decision record.

## 10. Software and acceptance

The validator checks the four controlled combinations, complete evidence-backed trade scores, exact weight sum, required measurement domains and state-transition logic. It deliberately does not calculate physical forces, torque, tooth geometry, contact stress, wear, power reserve or timing performance.

Run from the tools directory:

    python -m unittest test_c01_chrono_architecture.py

Tests use synthetic records only. They are not C-01 measurements or a physical mechanism test.

Acceptance criteria:
- WP33-AC-01: all four combinations are represented exactly and consistently.
- WP33-AC-02: no score is accepted without criterion-specific evidence.
- WP33-AC-03: approved weights sum exactly to 1.
- WP33-AC-04: trade-study output is advisory and cannot authorize a winner.
- WP33-AC-05: reset while running is prohibited in the state model and requires physical interlock evidence.
- WP33-AC-06: all nine measurement domains are included in the comparison plan.
- WP33-AC-07: counter conventions are distinguished from selected gear ratios.
- WP33-AC-08: no dimensions, materials, tooth counts or performance limits are invented.

## 11. Revision control and disposition

Revision A is the initial controlled issue. Any change to requirements, candidate definitions, criteria, weights, evidence or mechanism interfaces requires revision-controlled review and impact assessment against WP-11, WP-16, WP-17, WP-19, WP-20, WP-25 and WP-30.

**Disposition:** WP-33 advances the chronograph toward a prototype mechanism decision. All four clutch/control combinations remain candidates. No physical design, gear schedule, tolerance, supplier or architecture winner is released.
