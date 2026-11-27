# WP-52 — Chronograph Control Experimental Data Protocol and First Comparative Test Campaign

- **Document ID:** SEB-C01-WP-52
- **Revision:** A — initial controlled issue
- **Status:** Experimental protocol framework; campaign not approved or executed
- **Project:** STEWARD C-01
- **Repository:** `godsun108/turbo-foundry`
- **Branch:** `steward/c-01-movement-foundation`
- **Companion model:** `tools/c01_experimental_protocol.py`
- **Synthetic regression tests:** `tools/test_c01_experimental_protocol.py`
- **Predecessors:** WP-30, WP-33, WP-42 through WP-51
- **Date:** 2026-11-27

## 1. Purpose and release boundary

WP-52 establishes the controlled experimental protocol for the first physical comparison of the unresolved chronograph-control candidates:

- **CW:** column-wheel control.
- **CL:** cam/lever control.

It connects the WP-46 test families, WP-47/48 fixture and metrology requirements, WP-49 acquisition records, WP-50 analysis methods and WP-51 evidence dashboard into one campaign governance framework.

The campaign is intended to generate comparable, traceable evidence for engineering review. It is not a design selection, design freeze, manufacturing release, or permission to operate a physical article.

**No physical campaign is represented as approved or completed.** No actual C-01 prototype article, test result, sample size, cycle count, acceptance limit, instrument, supplier, or measured performance is asserted. Numeric values in software regression fixtures are synthetic examples only.

The protocol validator deliberately never authorizes hardware testing and never selects an architecture.

## 2. Experimental objectives

The first campaign shall answer, with controlled observations rather than assumptions:

1. What force and travel are required to actuate each candidate, including return behavior and hysteresis?
2. Are start, stop and resume transitions complete, repeatable and free of unintended output motion?
3. How often do missed, double, delayed or incomplete transitions occur under the approved test conditions?
4. How does each mechanism behave during controlled partial strokes, interruptions, release and re-application?
5. How repeatably does the stopped chronograph return to its defined zero datum?
6. Does a physical mechanism prevent reset while the chronograph is running, with the running state preserved?
7. How do force, timing, reset behavior and inspected condition change over a separately approved endurance exposure?

The campaign compares only the control candidates under identified configuration conditions. It does not automatically establish the best of the four combinations previously defined in WP-33 (vertical or horizontal/lateral clutch paired with column wheel or cam/lever).

## 3. Candidate article definition and comparison controls

### 3.1 Immutable candidate identity

Before testing, create a configuration record for each candidate containing at minimum:

- candidate ID and revision;
- unique physical article ID and serial/asset identity;
- control mechanism drawing/BOM and component revisions;
- clutch configuration and revision;
- movement and chronograph train configuration;
- assembly and inspection record;
- spring and component state;
- lubrication specification, batch/record and application history;
- pusher/case-interface configuration;
- fixture/carrier identity and revision;
- procedure and data-schema revisions;
- prior actuation, conditioning, repair and test history;
- deviations and approved dispositions.

A candidate article shall not silently change during a campaign. Any repair, adjustment, lubrication change, part replacement or reassembly creates a new configuration revision or a formally approved controlled deviation. Preserve the original record and link the new state.

### 3.2 Matched comparison conditions

Use the same qualified fixture datum scheme, measurement boundary, procedure revision, instrument method, calibration status, data reduction and declared test condition for CW and CL wherever technically possible.

Record, rather than assume equivalent:

- article orientation and mounting;
- temperature and environmental condition where relevant;
- movement power/winding state and conditioning;
- elapsed time since assembly, lubrication or conditioning;
- pusher actuator alignment, speed profile and contact interface;
- operator, setup sequence and fixture installation;
- instrument configuration, bandwidth, sampling and synchronization;
- prior cycle count and any interruptions.

If the two candidates cannot share a common baseline or fixture interface, identify the difference as a confounding variable and obtain engineering review before interpreting a candidate effect.

Metadata agreement is necessary but not sufficient to establish experimental equivalence.

## 4. Campaign structure and run sequencing

### 4.1 Paired-block design

Organize the campaign into predeclared blocks. A block is one matched comparison unit for a specified test family and test condition. Each block contains:

- one CW run;
- one CL run;
- a common procedure revision;
- a common fixture revision or documented equivalence basis;
- a common test-condition ID;
- a documented order assignment;
- linked calibration, raw evidence and analysis records.

The order within each block shall be randomized or counterbalanced using a method selected and recorded in the approved statistical plan. Do not always test one architecture first: order can confound conditioning, operator learning, temperature drift, instrument drift or wear.

Where practical, use balanced order assignments across blocks. The randomization seed or method, generated schedule, person generating it, date and approved schedule revision must be retained. Do not reshuffle order after observing results.

### 4.2 Sample size is an approved input, not a software default

No universal sample count is assigned in WP-52. A qualified statistician or responsible engineering authority shall approve a separate sample plan for each test family and intended inference.

The sample-size rationale should consider, as applicable:

- the engineering question and primary measurand;
- whether the objective is characterization, repeatability, reliability demonstration or comparative inference;
- expected variability from pilot evidence or a justified prior source;
- smallest practically meaningful difference, if a comparative claim is intended;
- confidence level, power and statistical method where inferential claims are intended;
- repeated observations within one article versus independent articles;
- clustering by article, assembly, operator, fixture or test day;
- censoring, missing observations and planned exclusions;
- wear/endurance exposure and whether the test is destructive;
- instrument uncertainty relative to the effect being resolved.

Repeated strokes on one article are not automatically independent samples. The plan must identify the experimental unit, observation unit, independence assumptions and any hierarchical or repeated-measures treatment. A sample count without this definition is not an adequate sample plan.

Every sample plan must specify the number of observations/articles per candidate, population definition, rationale, statistical or engineering basis, acceptance-plan reference and approval record. The software validates that a value and approval reference exist; it does not recommend or calculate the value.

### 4.3 Campaign phases

| Phase | Work | Release condition |
|---|---|---|
| A — readiness | Requirements, candidate configuration, risk assessment, fixture qualification, calibration, uncertainty and sample plans | All pre-test hold points approved |
| B — baseline | Incoming inspection, configuration audit, zero/reference checks and conditioning | Article accepted for the named procedure |
| C — functional characterization | Force/travel, start/stop, state repeatability and partial-stroke procedures | Raw records complete; anomalies dispositioned |
| D — reset/interlock | Reset-to-zero and separately authorized physical running-reset interlock test | Dedicated article/procedure release and independent witness |
| E — endurance | Approved cycle profile, interim inspections and drift measurements | Separate endurance authorization and stop criteria |
| F — analysis | WP-49 reduction, WP-50 analysis and WP-51 review | Independent data and comparability review |
| G — design review | WP-45 evidence handoff and design-authority decision | Formal decision record; no automatic software selection |

The order of test procedures may be changed only by an approved campaign revision. Wear-sensitive procedures may affect later measurements; define sequencing and baseline restoration before the campaign begins.

## 5. Procedure-level experimental protocol

The detailed execution steps and safety requirements remain governed by the approved WP-46 procedure. WP-52 adds the campaign controls below.

### 5.1 Pusher force and travel

For every prescribed stroke, preserve synchronized time, force and displacement observations from initial contact through actuation and return. Capture complete loading and unloading traces.

Record:
- peak sampled force and its time/travel coordinate;
- force at each defined transition event;
- total travel, lost motion and return position;
- loading and return branches;
- hysteresis/work calculation method;
- actuator speed profile and compliance characterization;
- abnormal peaks, stick-slip, incomplete return or contact anomalies.

Do not pool force traces across different actuator profiles, fixture revisions or conditioning states without an approved analysis method. Sampled peak force may miss a transient peak; bandwidth and sampling adequacy must be justified.

### 5.2 Start, stop and resume

Record the input event and observed mechanism/output events on a common corrected timebase. Identify command onset, control movement, clutch response, retention response, chronograph output and settling.

Classify every event as complete, delayed, missed, duplicated, incomplete, unintended or indeterminate using definitions approved before execution. Retain event-level traces and video/encoder records; do not retain only average latency.

### 5.3 State-transition repeatability

Use the approved state sequence and record each commanded transition and independently observed physical state. Preserve the denominator, successes, failures, interruptions and recovery actions.

A success fraction alone is not sufficient. Report the interval method and assumptions specified by the approved sample/analysis plan. Repeated trials on the same physical article must not be represented as independent article-level reliability evidence.

### 5.4 Partial-stroke and interrupted-input behavior

Define safe interruption positions only after the actual mechanism geometry, safe travel envelope and risk assessment are approved. For each planned position, record input position, physical control state, output state, release behavior, rebound and recovery.

Do not force a jam, drive past a stop or use arbitrary partial-stroke coordinates. A position map must identify its coordinate datum and uncertainty.

### 5.5 Reset-to-zero repeatability

Define and calibrate the zero datum before the run. Record each stopped-state reset observation, direction of approach, settling time, hand/counter indication method and any bounce or rebound.

Retain signed angular errors and source images or encoder records. The analysis must state whether the reported spread is within-run, between-run or between-article. Counter branches must follow the actual selected indication mechanism; continuous and jumping counters remain unresolved until separately decided.

### 5.6 Physical running-reset interlock

The running-reset interlock is a dedicated physical safety/function test. It is not satisfied by a state-machine model, a CAD constraint, a drawing, an uncommanded reset, or a software validator.

Before execution, require:
- a specifically identified development article and configuration revision;
- an approved test-specific procedure and risk assessment;
- article release record for this test;
- qualified, guarded fixture and approved actuator envelope;
- current instruments and synchronized observation;
- independent observer;
- explicit stop conditions and post-test inspection method.

During the test, attempt reset only while the chronograph is independently observed running. Record pusher input, force/travel, physical control/interlock motion, reset-hammer behavior where observable, chronograph output and synchronized raw video/encoder evidence.

A positive result requires direct observation that the physical mechanism blocks reset-hammer engagement or otherwise prevents reset while the chronograph remains running, followed by post-test inspection and independent approval. Proof applies only to the exact article, configuration, procedure and conditions tested.

Unexpected reset, loss of running state, jamming, abnormal force, damage or ambiguous observation is a failure/stop condition. Preserve evidence and obtain engineering disposition. Do not repeat a failed test on a valuable article without explicit authorization.

### 5.7 Wear and endurance

Define cycle profile, actuation speed, dwell, environmental conditions, lubrication state, inspection intervals and cycle count from the approved use/reliability requirement. No cycle count is prescribed here.

Capture baseline and interval inspections using matched methods, magnification, lighting, datums and calibration. Record every interruption, abnormal event, force/travel drift, transition anomaly, reset drift, debris and component replacement. A repair or replacement changes the tested configuration and must be recorded; do not continue a cumulative-life claim as if the article were unchanged.

## 6. Failure, anomaly and deviation management

Record every unexpected or nonconforming observation, including events that do not immediately cause a stop. Use the controlled initial taxonomy in the companion model:

- missed transition;
- double transition;
- incomplete engagement;
- unexpected output motion;
- reset-zero error;
- running-reset interlock failure;
- ambiguous partial-stroke state;
- abnormal force or travel;
- jam or binding;
- retention loss;
- fixture or instrument fault;
- data-integrity failure;
- visible damage or wear;
- other (with explanation).

Each failure record shall include a unique ID, run ID, event time, class, factual description, raw evidence URI and checksum, immediate containment, disposition status, responsible reviewer and disposition record. Separate observed facts from suspected cause. Do not silently delete outliers or reclassify failures as operator error without evidence and approval.

A failed or invalid run remains in the campaign ledger. Retests receive new run IDs and link to the original; the original raw evidence is retained. A retest does not erase the original failure.

Stop the affected test when any WP-46 stop condition occurs, including unexpected reset while running, jam/binding, abnormal force, overtravel, retention loss, fixture displacement, sensor/actuator misalignment, data loss, instrument range exceedance, visible damage or any unanticipated unsafe condition. Resume only after documented engineering disposition and required re-authorization.

## 7. Raw data, traceability and chain of custody

### 7.1 Immutable raw evidence

For each run, retain native instrument files and original video/image evidence in their native form. Compute and record a SHA-256 checksum at acquisition or controlled transfer. Preserve file name, byte size, acquisition timestamp, source device, transfer history and storage location.

Never overwrite native raw evidence. Corrections, clock alignment, filtering, calibration conversion and derived exports create new files with new identifiers and explicit links to source files and software revisions.

A checksum supports integrity checking; it does not independently establish authenticity, calibration or correctness.

### 7.2 Run manifest

Every run record must identify at minimum:
- run ID, candidate ID/revision, article ID and configuration revision;
- fixture ID/revision;
- procedure ID/revision and test family;
- test-condition ID;
- operator and UTC start time;
- channel/instrument/calibration references;
- raw evidence URI and SHA-256 digest;
- evidence ID and source revision;
- deviations, failure IDs and linked approval records.

Use WP-49's channel-level manifest for measurand, unit, instrument, calibration status, sampling method, sample rate where applicable and provenance.

### 7.3 Data governance

Maintain access control and backup appropriate to controlled engineering records. Preserve raw and derived records separately. Any correction must be attributable, dated and reviewable. Do not place synthetic regression fixtures or generated sample values in the physical C-01 evidence store.

## 8. Analysis and comparative interpretation

WP-49 remains the measurement/acquisition basis. WP-50 remains the numerical analysis layer. WP-51 remains the local interactive evidence viewer. WP-52 governs the experimental design and campaign record that make their outputs interpretable.

For each measurand:
1. Verify source checksum, manifest completeness, calibration status and procedure revision.
2. Confirm the run meets predeclared validity criteria; retain invalid runs and reasons.
3. Apply only the approved clock, calibration and data-reduction transformations.
4. Report individual observations and distributions, not only a mean.
5. Include uncertainty, interval method and assumptions.
6. Compare CW and CL only within matched blocks or a preapproved model that accounts for differences.
7. Report missing data, exclusions, failures, retests and deviations.
8. Separate engineering acceptance from comparative preference.

Overlapping uncertainty intervals may make a simple directional comparison indeterminate; non-overlap alone does not prove practical significance or select an architecture. Use the approved statistical method and engineering relevance criterion.

Do not pool across unmatched conditions. Do not treat repeated strokes as independent articles. Do not infer physical interlock performance from dashboard status. Do not infer wear life beyond the observed exposure.

The final evidence package is an input to WP-45. The design authority, not the software, decides whether the evidence is sufficient and whether any architecture should be selected.

## 9. Hold points and approval matrix

| Hold point | Required evidence | Approval authority |
|---|---|---|
| H0 — requirements | Requirements baseline, candidate definitions, primary measurands and acceptance plan | Design authority |
| H1 — safety/fixture | Risk assessment, fixture qualification, guarding, stop conditions | Responsible engineer and safety reviewer |
| H2 — metrology | Instrument suitability, calibration, timebase, uncertainty budget | Metrology authority |
| H3 — experimental design | Sample plans, experimental units, analysis method, randomized/counterbalanced schedule | Responsible engineer and statistical reviewer |
| H4 — article release | Configuration audit, incoming inspection, conditioning and procedure-specific release | Article/configuration authority |
| H5 — run completion | Raw files, checksums, manifests, deviations, failure records | Test lead |
| H6 — analysis review | WP-49/50 outputs, matched-block assessment, uncertainty and independent review | Independent reviewer |
| H7 — architecture disposition | WP-45 trade evidence and formal decision record | Design authority |

No software output satisfies an approval hold point. The validator's `complete_for_independent_review` result means only that required planning fields are present. It does not mean the plan is approved, safe or ready to execute.

## 10. Companion software and verification

`tools/c01_experimental_protocol.py` provides structural checks for:
- explicit approved sample plans with no default sample count;
- distinct CW/CL configuration records and common comparison controls;
- paired run blocks containing one run per candidate;
- recorded randomized/counterbalanced order assignments;
- campaign coverage of all seven WP-46 test families;
- immutable raw-evidence run records and SHA-256 syntax;
- controlled failure taxonomy and disposition references;
- duplicate run IDs and failure-to-run links;
- physical interlock evidence completeness.

Run the synthetic regression tests from the tools directory:

```sh
python -m unittest test_c01_experimental_protocol.py
```

The regression fixtures are synthetic software tests. They are not C-01 sample-size recommendations, physical measurements, acceptance limits, or evidence of prototype behavior. The validator does not operate a test bench, validate a real checksum against a file, calculate statistical power, determine sample size, approve a safety case, or authorize testing.

## 11. Open decisions and required inputs

The following remain open and must be resolved through controlled review before campaign execution:

- final CW and CL prototype article configurations;
- whether a common clutch configuration can be maintained for the first comparison;
- fixture qualification and article-specific release;
- approved test conditions and conditioning sequence;
- measurands and primary endpoints for each test family;
- sample size, experimental unit and statistical analysis plan;
- numerical acceptance limits and uncertainty/guard-band rules;
- randomization/counterbalancing method and schedule;
- partial-stroke safe positions and procedure-specific limits;
- reset indication/counter configuration;
- running-reset interlock proof method and independent witness;
- endurance cycle profile, inspection intervals and stop limits;
- storage, retention and access-control location for raw evidence.

No control architecture is selected. No prototype is released for manufacture. No physical test is authorized by WP-52.

## 12. Revision control

| Revision | Date | Change | Approval |
|---|---|---|---|
| A | 2026-11-27 | Initial controlled experimental campaign protocol and evidence-governance framework | Pending engineering review |

**Release statement:** WP-52 is a planning and evidence-control document only. It defines how a first CW/CL campaign should be designed and governed after required approvals. It does not claim the campaign has been approved, a prototype exists, physical testing has occurred, the interlock has been proven, or a design decision has been made.
