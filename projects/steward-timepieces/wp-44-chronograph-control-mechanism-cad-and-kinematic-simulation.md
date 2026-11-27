# WP-44 — Chronograph Control Mechanism CAD and Kinematic Simulation

- **Document ID:** SEB-C01-WP-44
- **Revision:** A — initial controlled issue
- **Status:** Evidence-gated sampled kinematic/CAD framework; no C-01 control geometry approved
- **Branch:** `steward/c-01-movement-foundation`
- **Software:** `tools/c01_control_kinematics.py`
- **Verification:** `tools/test_c01_control_kinematics.py`
- **Dependencies:** WP-21, WP-22, WP-30, WP-32, WP-35, WP-36, WP-40 through WP-43

## 1. Purpose and scope

WP-44 establishes a controlled engineering data path for the chronograph control mechanism: candidate member definitions, sampled planar poses, fixed-pivot/linkage point constraints, axial-aware envelope clearance, operating-state sequence checks and a neutral OpenSCAD preview.

It carries forward the WP-42 column-wheel (CW) and cam/lever (CL) alternatives without selecting either. It does not select a clutch/control combination, dimensions, pivot coordinates, lever arms, wheel or cam profiles, spring rates, force, travel, materials, tolerances or acceptance limits.

The model is a deterministic sampled-geometry validator. It is not a rigid-body dynamics solver, contact solver, constraint solver, CAD feature-tree generator or physical mechanism verification.

## 2. Design basis and units

- XY follows the movement-centred WP-14/WP-20 convention.
- Z is referenced to the WP-21 M0 realization.
- Length is millimetres; time is seconds; angular pose is degrees.
- Every candidate, member, interface, constraint and motion package requires evidence ID and source revision.
- All sampled members use one common, strictly increasing time vector.
- Every member pose contains XY translation, angular orientation and an axial interval.

A local point on a planar rigid member is transformed by:

`x_g=x_0+x_l\cos\theta-y_l\sin\theta`

`y_g=y_0+x_l\sin\theta+y_l\cos\theta`

The evaluator compares transformed point pairs against an explicitly supplied target distance. This supports a measured or drawing-derived linkage closure check; it does not solve unknown member positions or infer pivot locations.

## 3. Candidate architecture contract

Two candidate IDs are recognized:

| ID | Architecture | Status |
|---|---|---|
| CW | Indexed column wheel | Open |
| CL | Cam/lever | Open |

Each candidate must identify members and the seven WP-42 control interfaces: pusher input, index/state retention, clutch command, stopped-retention command, reset-hammer command, running-reset interlock, and return/reset. Member and interface IDs must be unique; endpoints must reference declared members. Candidate completeness is not evidence of physical operation or approval.

## 4. Motion input and kinematic constraints

A motion package contains:
- candidate ID, package evidence and source revision;
- a common list of time samples;
- each member's role, envelope type, radius, evidence and source revision;
- one pose per time sample, with x/y, angle and z-min/z-max;
- optional point-to-point fixed-distance constraints with local attachment-point coordinates, target distance and tolerance.

For each constraint and time sample, the evaluator transforms the two local attachment points into global XY and computes:

`e(k)=|d(k)-d_{target}|`

The reported maximum absolute error is compared with the explicitly supplied tolerance. The result is a sampled kinematic consistency screen only. A fixed-distance relation is not a full revolute, slider, cam-follower or gear constraint and the model does not integrate forces or solve mechanism motion.

## 5. Sampled envelope clearance

For two supplied circular envelope radii whose Z intervals overlap at a sample:

`c(k)=\sqrt{(x_A-x_B)^2+(y_A-y_B)^2}-r_A-r_B`

Negative clearance indicates sampled overlap. Axially separated envelopes are not treated as planar collisions. The result is limited to the supplied circular envelopes and sample instants; it does not prove continuous swept-solid clearance, actual tooth/contact geometry, tolerance clearance, deflection, shock, wear or lubrication adequacy.

## 6. CAD handoff

The OpenSCAD exporter emits a simple cylindrical envelope preview at the first supplied sample, with evidence and source-revision comments. It is intended for rapid orientation and data review. It is not an animated assembly, detailed part model, manufacturing drawing or fit certification.

Detailed CAD must eventually represent the actual column-wheel columns/indexer/jumper or cam/follower/detent, pusher linkage, clutch lever, stopped-retention lever, reset lever, hammer, interlock, return elements, pivots and supports. Non-circular contact profiles and swept volumes require a suitable CAD system and engineer-reviewed solids.

## 7. Operating sequence and safety-critical interlock

The logical state path remains:
- stopped_zero + start → running;
- running + stop → stopped_retained;
- stopped_retained + resume → running;
- stopped_retained + reset → stopped_zero;
- running + reset → running, with reset-hammer contact positively blocked.

The sequence validator requires a physical interlock test-record ID for a running-reset attempt and insists that the chronograph remains running. This is a record-reference gate, not proof that the interlock exists or passed. WP-30 physical inspection and test evidence remains mandatory.

## 8. Acceptance criteria

| ID | Acceptance criterion |
|---|---|
| AC-01 | Candidate ID/type, member IDs and required control interfaces validate without ambiguity |
| AC-02 | Motion samples use seconds/mm, strictly increasing common timestamps and complete per-member poses |
| AC-03 | Every declared linkage point constraint reports maximum sampled error against its explicit tolerance |
| AC-04 | Every axial-overlapping envelope pair reports minimum sampled clearance and any sampled overlap |
| AC-05 | Invalid IDs, missing poses, unsupported constraints and invalid numeric values fail closed |
| AC-06 | Start/stop/resume/reset logical sequence is valid; running reset remains running and references a physical test record |
| AC-07 | CAD source preserves evidence/provenance and labels the preview as an envelope-only first-pose representation |
| AC-08 | Review output never declares architecture winner, design freeze or prototype release |

No numeric C-01 acceptance limit is assigned in this package. Tolerances must be approved and sourced before they are used for design acceptance.

## 9. Verification plan

The accompanying synthetic regression suite covers candidate completeness and mismatch, monotonic time, pose completeness, fixed-distance constraint pass/fail, sampled overlap, axial separation, reset interlock sequence, OpenSCAD provenance and fail-closed release status. Synthetic fixtures validate software behavior only; they are not C-01 dimensions or test results.

Before physical design acceptance, engineers must independently verify the detailed CAD assembly, actual pivot and contact geometry, full-stroke swept volumes, partial-pusher behavior, state retention, reset interlock under adverse conditions, force/travel, wear, serviceability and timekeeping impact under approved WP-30 procedures.

## 10. Open decisions preserved

- Vertical friction clutch vs horizontal/lateral coupling.
- Column wheel vs cam/lever control.
- Column-wheel indexing geometry or cam count/profile/dwell.
- Pusher linkage topology, pivots, lever arms and travel.
- Stopped-retention element and phase.
- Reset hammer arrangement and sequencing.
- Positive running-reset interlock geometry.
- Return springs/detents and preload.
- Continuous vs jumping counter architecture.
- Detailed CAD environment and neutral-solid exchange format.
- All component geometry, tolerances, materials and acceptance limits.

## 11. Revision control and release status

Revision A introduces the WP-44 model, synthetic tests and this controlled engineering definition. Subsequent revisions must identify changed equations, schemas, interfaces, evidence and verification coverage.

**WP-44 does not select an architecture, freeze C-01, certify physical fit, or authorize prototype manufacture.** All C-01 geometry and performance claims remain evidence-gated.
