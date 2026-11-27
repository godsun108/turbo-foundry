# WP-42 — Chronograph Control System: Column Wheel vs Cam/Lever Detailed Engineering

- **Document ID:** SEB-C01-WP-42
- **Revision:** A — initial controlled issue
- **Status:** Comparative engineering definition; neither control architecture selected
- **Branch:** `steward/c-01-movement-foundation`
- **Software:** `tools/c01_chrono_control.py`
- **Verification:** `tools/test_c01_chrono_control.py`
- **Dependencies:** WP-16, WP-30, WP-32, WP-33, WP-34, WP-41

## 1. Purpose and boundary

WP-42 develops the two control-system candidates that sequence the C-01 chronograph: indexed column-wheel control (CW) and cam/lever control (CL). It defines member functions, interfaces, operating states, timing relationships, failure modes, measurement plans and selection evidence.

The control system must coordinate the clutch/coupling, stopped-train retention and reset hammer. It must not permit reset-hammer contact while the chronograph is running. WP-42 does not select a control architecture or a clutch architecture. The four combinations in WP-33 remain open.

No dimensions, tooth counts, cam profiles, column counts, angular indexing, lever ratios, spring rates, forces, materials, tolerances, wear limits or acceptance thresholds are assigned without source evidence.

## 2. Functional requirements

The control system shall:
1. accept distinct start, stop/resume and reset commands;
2. establish a stable, unambiguous operating state after each completed actuation;
3. sequence clutch engagement/disengagement and stopped-train retention;
4. keep the reset hammer clear during running and normal timing operation;
5. permit reset only from the stopped-retained state;
6. positively block reset-hammer contact while running;
7. tolerate defined partial or interrupted pusher strokes without an unsafe intermediate state;
8. return levers and followers to controlled positions after release;
9. provide inspectable, adjustable and serviceable interfaces;
10. demonstrate repeatability, acceptable actuation force/travel, wear and timekeeping impact under approved WP-30 procedures.

The required logical states are `stopped_zero`, `running` and `stopped_retained`. A reset while running is a blocked command, not a fourth state.

## 3. Candidate CW — indexed column-wheel control

### 3.1 Functional concept

A column wheel provides discrete indexed control positions. A pusher and transmission lever actuate an indexing element; a jumper or equivalent retention feature maintains the selected index. Control levers/followers interact with the wheel's columns and gaps to command the clutch, stopped-train restraint and reset mechanism.

This is a functional concept only. Column count, column shape, wheel diameter, index pitch, jumper geometry, tooth/indexing arrangement and lever layout are not specified.

### 3.2 Required member definition

| Member function | Required engineering definition |
|---|---|
| Column wheel | Index positions, columns/gaps, datum and support |
| Indexing element | Drive interface, stroke, engagement and anti-double-step behavior |
| Jumper/retainer | Stable state retention, preload source, wear/contact inspection |
| Pusher transmission | Input travel, lost motion, return and overload behavior |
| Clutch lever | Engagement/disengagement command and phase |
| Retention lever | Brake/detent command and phase |
| Reset lever | Hammer actuation and positive running-state block |
| Return elements | Return path, preload evidence and failure-safe behavior |

### 3.3 Engineering questions

- Can a partial pusher stroke leave the index between stable positions?
- What prevents double indexing or rebound?
- Is the jumper securely seated at every intended state?
- What is the phase margin between clutch release, retention engagement and state indexing?
- How are reset and hammer withdrawal sequenced relative to retention release?
- Can a worn or contaminated index/follower create an ambiguous state?
- Can the wheel, jumper and levers be inspected and adjusted without disturbing adjacent chronograph geometry?

## 4. Candidate CL — cam/lever control

### 4.1 Functional concept

One or more profiled cams act on followers and levers to sequence clutch, stopped-train retention and reset. Stable dwell regions and a detent, spring or equivalent state-retention mechanism maintain the selected state. The cam profile and follower arrangement must ensure the required order of events and avoid unintended intermediate commands.

The number of cams, profiles, dwell angles, follower type, detent strategy and lever geometry remain open. A cam/lever candidate may use more than one cam; this document does not presume a single-piece control cam.

### 4.2 Required member definition

| Member function | Required engineering definition |
|---|---|
| Control cam(s) | State profile, dwell regions, transitions and angular datum |
| Follower(s) | Contact geometry, constraint, preload and wear surfaces |
| Detent/state retention | Stable state positions and resistance to unintended motion |
| Pusher transmission | Input travel, lost motion, return and overload behavior |
| Clutch lever | Engagement/disengagement command and phase |
| Retention lever | Brake/detent command and phase |
| Reset lever | Hammer actuation and positive running-state block |
| Return elements | Return path, preload evidence and failure-safe behavior |

### 4.3 Engineering questions

- Are dwell regions sufficient to retain each state under measured disturbance?
- Does follower contact remain controlled through each transition?
- Can interrupted pusher travel stop on a ramp and leave a partially commanded mechanism?
- Is the detent positive and repeatable without excessive actuation force?
- Are cam/follower contact loads, lubrication and wear measurable and serviceable?
- Does the control profile maintain correct phase with clutch and stopped-retention elements over tolerance and wear?

## 5. Common interface-control requirements

Both candidates shall implement the same functional interface set:

| Interface | Required boundary |
|---|---|
| pusher_input | Case pusher to control transmission |
| index_or_state_retention | State-setting member to retention feature |
| clutch_command | Control member to selected clutch/coupling |
| stopped_retention_command | Control member to brake/detent/equivalent |
| reset_hammer_command | Control member to reset hammer |
| running_reset_interlock | Running state to positive reset block |
| return_or_reset | Release/return path to stable state |

Every interface record must identify its two members, motion direction, allowed degrees of freedom, contact mode, datum, travel, force boundary, return behavior, evidence ID and source revision. Numeric data remain TBD until measured or specified.

## 6. Required operating sequence and event ordering

| Command | Initial state | Required final state | Functional ordering |
|---|---|---|---|
| Start | stopped_zero | running | Reset hammer confirmed clear; retention released; clutch engaged; state retained |
| Stop | running | stopped_retained | Clutch disengaged; elapsed train retained; control reaches stable stop state |
| Resume | stopped_retained | running | Retention released and clutch engaged in controlled sequence; elapsed value preserved |
| Reset | stopped_retained | stopped_zero | Hammer enabled only while stopped; hearts returned; hammer withdrawn; stopped state restored |
| Reset attempt | running | running | Positive interlock blocks hammer contact; chronograph continues running |

Exact overlap, deadband and phase margins must be established from candidate geometry and tolerance analysis. This document does not assign an arbitrary sequence timing or angular phase.

## 7. Comparative trade study — no assumed winner

| Criterion | Column wheel evidence | Cam/lever evidence |
|---|---|---|
| State definition | Index position and jumper seating | Cam dwell and detent stability |
| Pusher actuation | Indexing force/travel, step completion | Follower/cam force/travel through profile |
| Partial actuation | No half-index or double-step | No unsafe follower/lever intermediate state |
| Clutch timing | Lever phase against index position | Cam profile and follower phase |
| Retention timing | Brake/detent sequence through index | Brake/detent sequence through cam dwell |
| Reset interlock | Mechanical block at running index | Mechanical block over full running cam dwell |
| Wear | Index, column/follower and jumper contact | Cam/follower and detent contact |
| Packaging | Wheel, indexer, jumper and lever envelopes | Cam(s), followers, detent and lever envelopes |
| Serviceability | Index phase and jumper adjustment | Cam phase, follower and detent adjustment |
| Manufacturability | Index/column geometry and repeatable finishing | Cam profile, follower geometry and contact finishing |

Neither traditional familiarity nor theoretical part count is sufficient to select a winner. Each candidate must be evaluated with equivalent requirements, measurement boundaries and prototype conditions.

## 8. Failure-mode review

The following are required failure scenarios, not claims that either candidate has experienced them:

| Failure mode | Potential effect | Required design response / verification |
|---|---|---|
| Incomplete pusher stroke | Ambiguous state or partial engagement | Defined interrupted-actuation behavior and cycling test |
| Double index / cam overshoot | Wrong command state | Positive state retention and rebound test |
| Jumper/detent fails to seat | State drift | Retention margin evidence and inspection |
| Clutch command mistimed | Hand jump, drag or failed drive | Phase tolerance analysis and high-speed observation |
| Stopped restraint mistimed | Elapsed indication drift or shock | Matched stop/resume tests |
| Reset interlock failure | Reset contact while running | Physical interlock proof test; fail-safe design review |
| Hammer fails to withdraw | Drag or hand interference | Clearance inspection through full stroke |
| Return spring failure | Control remains partially actuated | Failure analysis and return-path test |
| Wear/contamination | Rising force or unreliable state | Endurance, lubrication and inspection programme |

## 9. Verification and acceptance plan

Both candidates must use matched configuration, movement state, reserve state, temperature, orientation, lubrication, measurement boundary and calibrated instrumentation. Required measurements:

1. Pusher force versus travel, including hysteresis and return.
2. State transition success and repeatability over approved cycle protocol.
3. Partial-stroke and interrupted-actuation behavior.
4. Clutch engagement/disengagement phase and repeatability.
5. Stopped-retention engagement timing and elapsed-value stability.
6. Reset interlock proof: running reset attempts must not contact any heart cam.
7. Reset hammer actuation and withdrawal clearance.
8. Wear and contact inspection before/after endurance.
9. Assembly, adjustment and service repeatability.
10. Chronograph-on/off rate and amplitude comparison under WP-09/WP-28 methods.

Numeric limits, cycle counts and sampling requirements must come from approved WP-30 procedures. A successful software validation or a single bench demonstration is not sufficient for architecture release.

## 10. Executable engineering model

Files:
- `tools/c01_chrono_control.py`
- `tools/test_c01_chrono_control.py`

The model validates candidate identity/type, unique member and interface records, required functional interfaces, four-state-command definitions, reset-interlock definition completeness, candidate comparison and measurement-review coverage. It explicitly does not certify the physical interlock or select a winner.

Run from the tools directory:

```sh
python -m unittest test_c01_chrono_control.py
```

Tests use synthetic records only. They do not represent measured C-01 geometry, force, travel, wear or reliability.

## 11. Acceptance criteria

| ID | Criterion | Evidence required |
|---|---|---|
| WP42-AC-01 | CW and CL each have complete member and interface registers | Reviewed candidate definitions |
| WP42-AC-02 | Both implement the same four commands and state transitions | Approved state tables |
| WP42-AC-03 | Partial/interrupted actuation behavior is safe and repeatable | Instrumented prototype tests |
| WP42-AC-04 | Clutch and stopped-retention phase are controlled | Candidate drawings and tolerance analysis |
| WP42-AC-05 | Reset is positively blocked while running | Physical interlock proof test |
| WP42-AC-06 | Force/travel and return behavior meet approved limits | Calibrated measurement records |
| WP42-AC-07 | Wear, lubrication, assembly and serviceability are assessed | Endurance and service reports |
| WP42-AC-08 | Comparative evidence is matched and traceable | Approved trade-study package |
| WP42-AC-09 | No candidate is selected by this validator | Design-authority decision record required |
| WP42-AC-10 | C-01 configuration and release gates are satisfied | WP-32 approval |

## 12. Revision control and disposition

| Revision | Date | Change | Approval |
|---|---|---|---|
| A | 2026-11-27 | Initial controlled column-wheel and cam/lever candidate engineering definition | Pending independent engineering review |

**Disposition:** WP-42 defines comparable control-system engineering work for CW and CL. Neither is selected. All four clutch/control combinations remain open under WP-33. C-01 remains unfrozen and is not released for manufacture. No merge or deployment is authorized.
