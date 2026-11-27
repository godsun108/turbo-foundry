# WP-46 — Chronograph Control Prototype Test Bench

- **Document ID:** SEB-C01-WP-46
- **Revision:** A — initial controlled issue
- **Status:** Preliminary test-bench engineering plan; fixture design and procedures pending approval
- **Project:** STEWARD C-01
- **Branch:** `steward/c-01-movement-foundation`
- **Software model:** `tools/c01_control_test_bench.py`
- **Synthetic regression tests:** `tools/test_c01_control_test_bench.py`
- **Dependencies:** WP-30, WP-31, WP-33, WP-42, WP-43, WP-44, WP-45

## 1. Purpose and release boundary

WP-46 defines a controlled physical test-bench architecture for generating comparable evidence on the two unresolved chronograph control candidates:

- **CW:** column-wheel control.
- **CL:** cam/lever control.

The objective is to measure actuation, state changes, partial strokes, reset behavior, running-reset interlock behavior, wear and serviceability using matched methods and traceable configurations. WP-46 does not select CW or CL, select one of the four clutch/control combinations, freeze C-01, authorize a prototype build, or authorize operation of a physical movement.

No physical bench, instrument, prototype, measured result, approved limit, fixture dimension, cycle count, test speed, pusher force, or procurement selection is asserted to exist. All numeric limits and test quantities must be established from approved requirements, risk review, instrument capability and prototype configuration.

A software validation result means only that a record is structurally complete. It is not a safety approval or permission to operate hardware.

## 2. Candidate configurations and comparability

Each candidate shall have its own immutable configuration identity and revision. The comparison package must identify:
- control architecture and candidate revision;
- clutch architecture and revision, even if held common;
- movement/fixture serial or article ID;
- component and spring revisions;
- lubrication and assembly state;
- pusher/case interface configuration;
- procedure and measurement-method revisions;
- test-condition ID, including applicable temperature, orientation, power state and elapsed conditioning;
- deviations and prior cycle history.

A comparison is valid only when procedure revision, test condition, measurement method, units and acceptance requirement are matched. Candidate-specific geometry may differ, but the test fixture interface and measurement boundary must be controlled. Where a common movement baseline cannot be held, the difference must be recorded as a confounding variable rather than silently attributed to the control architecture.

## 3. Test-bench architecture

The proposed bench is modular and should comprise the following subsystems. Final mechanical design, ranges and instrument models remain open.

### 3.1 Structural fixture and movement restraint
- Rigid base with a documented datum scheme and repeatable mounting interface.
- Interchangeable movement nest or subassembly carrier for CW and CL articles.
- Controlled support that does not distort the plate or bridge.
- Guarding and access controls appropriate to the approved test hazards.
- Alignment references and a documented installation/inspection procedure.
- Replaceable sacrificial contact elements where repeated pusher or lever contact could damage a development article.

Fixture stiffness, resonance, mounting torque, thermal behavior and loading influence must be evaluated before measurement use. The fixture must not impose unmeasured side load on the pusher stem, lever or movement structure.

### 3.2 Pusher force and travel measurement
Measure input force and displacement synchronously through the full approved stroke and return. Candidate measurement methods include a calibrated force transducer/load cell and a displacement sensor or encoder, mounted through a low-friction, aligned actuator. A motorized actuator is optional; if used, its speed profile and compliance must be controlled and recorded.

Record force-versus-travel on both actuation and return. Derive peak force, force at defined state transitions, total travel, lost motion, hysteresis-loop area/work and repeatability. Do not reduce the result to a single peak-force value: the complete trace is needed to identify detents, friction, partial engagement and return behavior.

The actuator and sensor fixture must be characterized for compliance, friction, alignment, bandwidth, sampling and parasitic force. An actuator must not drive beyond a mechanically approved travel stop. No target force or travel is assigned here.

### 3.3 State and motion observation
Use synchronized optical observation, encoder data or other approved non-invasive sensing to record:
- pusher input onset and release;
- control-member/indexing motion;
- clutch command and engagement state;
- stopped-retention behavior;
- chronograph seconds motion;
- reset-hammer and heart-cam motion where visible;
- timing of state transition and settling.

High-speed imaging is a candidate method, not a selected instrument. Frame rate, exposure, magnification, illumination and time synchronization must be chosen from the fastest event to be resolved and documented. Sensor targets or markers must not add meaningful inertia or interfere with the mechanism.

### 3.4 Data acquisition and synchronization
All channels must share a traceable time base or have a measured synchronization correction. Record raw force, travel, optical/encoder channels, environmental channels and operator event markers. Preserve native raw files unchanged; derived CSV files are separate controlled outputs. Record instrument asset IDs, calibration references, firmware/software versions, sampling configuration, filtering and data-reduction revision.

### 3.5 Wear and inspection station
Provide repeatable pre/post inspection using suitable optical microscopy, dimensional metrology and image capture. Inspect contact surfaces, pivots, teeth, detents, springs, hammer/heart interfaces and any observed debris. A wear claim requires baseline and post-test images/measurements with matched magnification, lighting, datum and calibration. No wear limit is assigned in WP-46.

## 4. Instrument and calibration requirements

Instrument selection is measurand-driven. Candidate classes include:
- force transducer or load cell for pusher force;
- linear displacement sensor or encoder for pusher travel;
- optical encoder or calibrated video/vision system for angular motion and event timing;
- synchronized data acquisition for analog/digital channels;
- calibrated timebase for synchronization;
- microscope/vision metrology for wear and reset-zero inspection;
- temperature sensor and environmental monitor where required by the approved test condition.

For every instrument, the controlled register shall include instrument ID, asset/serial, measurand, unit, range, resolution, calibration record/status/due date, evidence ID and any approved deviation or exemption. Confirm calibration is current for the actual test date. Calibration status alone does not prove suitability: range, resolution, bandwidth, dynamic response, loading effect and uncertainty must meet the measurement requirement.

The uncertainty budget shall account for relevant calibration, repeatability, resolution, alignment, fixture compliance, hysteresis, sampling, synchronization, image scale, environmental drift and data reduction. Combine independent standard contributions by RSS only where justified; correlated contributions require covariance treatment. Apply an approved coverage factor and decision rule. Do not infer uncertainty from display resolution alone.

## 5. Controlled test procedures

Each procedure shall identify preconditions, candidate configuration, approved sample plan, instrument setup, calibration status, raw-data schema, safety controls, stop conditions, acceptance requirement, uncertainty method, operator and independent reviewer. The procedure must be approved before hardware operation.

### TP-46-01 — Pusher force/travel characterization
1. Inspect the article, fixture and pusher path; confirm approved configuration and travel stop.
2. Verify alignment and zero the force/travel channels using the approved method.
3. Execute the approved actuation and return profile without exceeding the approved mechanical envelope.
4. Capture synchronized force/travel/time data for each prescribed stroke.
5. Derive force at transition points, peak force, total travel, lost motion, hysteresis and work.
6. Repeat only according to the approved sample plan; preserve every trace and outlier.

Acceptance requires approved force/travel envelopes and guard-banded uncertainty. No values are supplied in WP-46.

### TP-46-02 — Start/stop/resume observation
1. Establish the declared running and stopped baseline.
2. Record pusher input and synchronized control, clutch, retention and chronograph output motion.
3. Verify state transitions against the approved sequence and identify delay, bounce, incomplete engagement or unintended motion.
4. Record start disturbance and any measured change in movement rate/amplitude using the separately approved method.
5. Repeat for the approved sample plan and compare CW/CL under matched conditions.

Acceptance limits for transition reliability, delay, disturbance and unintended motion remain TBD pending approved requirements.

### TP-46-03 — State-transition repeatability
Exercise start, stop, resume and reset only in the approved sequence and sample plan. Record every command, observed physical state, transition time, failure, double-step, missed index and recovery. Report numerator/denominator and confidence method for reliability claims; do not report a pass rate without the full sample history and approved acceptance plan.

### TP-46-04 — Partial-stroke and interrupted-input behavior
Use a controlled actuator or approved manual fixture to interrupt pusher travel at defined positions derived from the actual mechanism geometry and approved procedure. Map input position against control-member state and output state. Include actuation interruption, release, rebound and re-application cases where the hazard review permits.

The procedure must identify safe interruption positions and avoid forcing the mechanism through a jam or overtravel. Record incomplete indexing, ambiguous state, double actuation, clutch conflict and recovery. Do not invent partial-stroke positions before geometry and safe limits are approved.

### TP-46-05 — Reset-to-zero repeatability
With the chronograph stopped and in each approved counter state, command reset and measure the final hand/counter angular position relative to a calibrated zero datum. Capture each reset image or encoder record, direction of approach, hammer/heart contact behavior, settling and any bounce. Report signed zero error and repeatability with uncertainty. Minute/hour counter indication methods remain unresolved; procedure branches must match the selected mechanism rather than assume continuous or jumping counters.

### TP-46-06 — Physical running-reset interlock proof
This is a safety-critical functional verification, not a software state-machine test.

- Use a separately approved, guarded test fixture and a development article specifically released for this test.
- Establish and independently observe a stable running chronograph state.
- Apply the reset input only through the approved instrumented actuator and within the approved force/travel envelope.
- Observe whether the physical interlock blocks reset-hammer engagement or otherwise prevents reset while preserving the running state.
- Record pusher force/travel, control-member motion, chronograph output and synchronized video/encoder evidence.
- Stop immediately on unexpected reset, loss of retention, jamming, abnormal force, component displacement or any stop condition in the approved risk assessment.
- Inspect the article after the test and document any damage or permanent set.

A logical model, drawing, inferred linkage, or statement that reset is “not commanded” is not proof. Proof applies only to the tested configuration and procedure. A failed or ambiguous result blocks further running-reset testing until engineering disposition. Do not repeat a failed test on a valuable or production-intent article without explicit review and authorization.

### TP-46-07 — Wear/endurance and post-test inspection
Only after functional and safety procedures are approved, define a cycle profile from intended use and the reliability requirement. Specify dwell, actuation profile, environmental condition, inspection intervals, lubrication state and stop criteria. No cycle count, frequency or endurance target is assigned here.

Record each cycle or validated event count, interruptions, force/travel drift, transition anomalies, reset-zero drift, visible wear, debris and post-test functional status. Inspect matched surfaces before and after using the same method and calibration. A cycle count without a controlled actuation profile and configuration history is not endurance evidence.

## 6. Test matrix and evidence package

Both CW and CL shall be assessed against the same seven test families:

| Test family | Primary outputs | Key controls |
|---|---|---|
| Pusher force/travel | Force curves, travel, hysteresis, work | Alignment, fixture compliance, calibration |
| Start/stop observation | Transition sequence, timing, disturbance | Common timebase, matched power state |
| State repeatability | Complete transition history, failures | Approved sample plan |
| Partial stroke | Input-position/state map, recovery | Safe positions, no forced jam |
| Reset-to-zero | Signed zero error, repeatability | Datum, imaging/encoder calibration |
| Running-reset interlock | Physical block/disengagement evidence | Guarded approved test, independent witness |
| Wear/endurance | Drift, inspection evidence, anomalies | Controlled cycle profile and baseline |

Every test record shall include:
- unique record ID and candidate architecture;
- procedure ID/revision and test-method revision;
- configuration revision, movement/fixture serial and test-condition ID;
- timestamp, operator and independent reviewer;
- instrument IDs, calibration record IDs and uncertainty budget;
- immutable raw-source URI and cryptographic checksum;
- data-schema and analysis-software revision;
- derived outputs, units, acceptance requirement ID and guard-band result;
- deviations, anomalies, retests and disposition references.

Raw evidence must never be overwritten. Corrections create a new derived record with an explicit link to the original. Synthetic software fixtures must be labeled synthetic and must never enter the physical C-01 evidence register.

## 7. Comparative decision method

For each measurand, compare CW and CL only when the measurement procedure, revision, condition, unit, measurement method and acceptance requirement match. Report each candidate's measured value, expanded uncertainty and interval. If intervals overlap, report the comparison as indeterminate unless a separately approved statistical method is defined. If they do not overlap, report only the supported directional result; do not automatically convert it into an architecture selection.

WP-45 remains the governing evidence-based architecture trade framework. WP-46 supplies physical evidence inputs; it does not set weights, scores, acceptance limits or a winner. A final decision must include all required criteria, approved evidence, independent review and design-authority disposition.

## 8. Stop conditions and safety controls

Before any physical test, the responsible engineering authority and safety reviewer must approve a test-specific hazard assessment and stop-condition list. At minimum, stop for:
- unexpected reset while running;
- jam, binding, abnormal force or overtravel;
- loss of chronograph retention or uncontrolled hand motion;
- movement/fixture loosening or displacement;
- sensor/actuator misalignment or data loss;
- instrument range/bandwidth exceedance;
- abnormal noise, debris, visible damage or unexpected heating;
- any condition outside the approved procedure.

The bench must include guarding and a safe means to remove actuator input. Do not energize or wind an unapproved article. Do not bypass a mechanical stop or interlock to “see what happens.” Any deviation requires stop, preservation of evidence and documented disposition.

## 9. Acceptance criteria and hold points

No numerical acceptance limits are invented. Before execution, approve:
- pusher force, travel, hysteresis and return requirements;
- state transition sequence and repeatability criteria;
- partial-stroke behavior and safe recovery criteria;
- reset-zero error and repeatability limits;
- physical running-reset interlock proof criteria;
- wear/endurance cycle profile and allowable drift;
- measurement uncertainty and guard-band decision rules;
- candidate comparability and independent-review requirements.

Hold points:
- **H0:** approved requirements and architecture candidate definitions.
- **H1:** fixture design, risk assessment, guarding and safety approval.
- **H2:** instrument selection, calibration, synchronization and uncertainty review.
- **H3:** procedure, sample plan, stop conditions and data schema approval.
- **H4:** article/configuration inspection and authorization for the specific test.
- **H5:** execution complete, raw data checksummed and deviations recorded.
- **H6:** independent analysis review and WP-45 evidence handoff.

Passing a software validator does not pass a hold point. No physical test is authorized by this document.

## 10. Software support and verification

`tools/c01_control_test_bench.py` provides evidence-record validators, instrument/procedure completeness checks, a simple independent-uncertainty RSS calculator, guard-banded two-sided acceptance evaluation, matched CW/CL result comparability and a physical-interlock evidence checklist.

Run from the tools directory:

```sh
python -m unittest test_c01_control_test_bench.py
```

Regression fixtures are synthetic. They test software logic only and are not C-01 measurements, acceptance limits, or proof of physical behavior. The model deliberately returns `hardware_test_authorized: False` and `architecture_selected: False`.

## 11. Revision control

| Revision | Date | Change | Approval |
|---|---|---|---|
| A | 2026-11-27 | Initial controlled test-bench architecture, procedure framework and evidence model | Pending engineering review |

**Release statement:** WP-46 is a planning and evidence-control document only. It does not establish that a test bench or prototype exists, certify a physical interlock, approve numerical limits, select CW/CL, freeze C-01, authorize manufacture, or authorize physical testing.
