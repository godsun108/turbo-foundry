# WP-45 — Chronograph Control Architecture Optimization and Evidence-Based Selection

- **Document ID:** SEB-C01-WP-45
- **Revision:** A — initial controlled issue
- **Status:** Evidence-gated trade-study framework; no control architecture selected
- **Branch:** `steward/c-01-movement-foundation`
- **Software:** `tools/c01_architecture_trade.py`
- **Verification:** `tools/test_c01_architecture_trade.py`
- **Dependencies:** WP-16, WP-30, WP-32, WP-33, WP-41 through WP-44

## 1. Purpose and decision boundary

WP-45 establishes a disciplined comparison of the two C-01 chronograph control candidates: indexed column wheel (CW) and cam/lever (CL). It combines approved criteria, comparable measured evidence, uncertainty-aware pairwise comparison, evidence-linked scoring, decision gates and design-authority review.

The decision in this package is the **control architecture only**. Clutch selection remains a separate decision. All four WP-33 combinations remain open:
- A — vertical friction clutch + column wheel;
- B — vertical friction clutch + cam/lever;
- C — horizontal/lateral coupling + column wheel;
- D — horizontal/lateral coupling + cam/lever.

The compatibility matrix is retained so the control candidate can be assessed against both clutch families. No architecture is selected by convention, popularity, assumed quality or software output.

## 2. Controlled requirements and decision principles

The comparison shall preserve the C-01 functional baseline: start, stop, resume, retained elapsed indication, reset while stopped, and positive prevention of reset-hammer contact while running. Partial or interrupted pusher actuation must not leave an unsafe or ambiguous mechanism state.

A valid comparison requires:
1. the same approved requirements revision;
2. separately identified CW and CL configurations;
3. approved criterion definitions, directions, measurement methods and acceptance references;
4. matched test procedures, boundary conditions and calibrated instruments;
5. traceable raw data and uncertainty;
6. physical interlock evidence;
7. independent review and design-authority disposition.

Missing, incomparable or uncertain evidence is reported as open/indeterminate, not converted to a favorable score.

## 3. Required comparison criteria

Ten criteria are mandatory. The review authority must approve each criterion's detailed rubric, measurement method, direction, acceptance reference and rational weight before scoring.

| Criterion | Required evidence domains |
|---|---|
| Actuation force and travel | Loading/unloading force-travel curves, peak force, travel, hysteresis, work |
| State repeatability | Start/stop/resume/reset cycle success, state retention, repeatability |
| Partial actuation | Interrupted strokes, rebound, double-step, ambiguous intermediate states |
| Clutch phase | Relative timing and clearance to clutch command for each compatible clutch candidate |
| Stopped-retention phase | Brake/detent engagement and release sequencing, retained-value disturbance |
| Reset interlock | Physical attempt to reset while running, no hammer contact and no reset motion |
| Wear and inspection | Contact wear, deformation, lubrication condition, inspection criteria |
| Serviceability | Disassembly, inspection, adjustment, reassembly time and repeatability |
| Manufacturability | Process capability, critical feature inspection, supplier/process evidence |
| Packaging | Axial/radial envelope, motion clearance, tolerance stack and service access |

The criteria list does not assign a numerical limit or imply equal importance. The weights are project decisions and must sum exactly to one. The score scale is 1–5 only after the review team approves a common rubric; the software does not define what a score means.

## 4. Measurement and uncertainty method

For every measured result, record:
- candidate and configuration revision;
- test procedure and revision;
- test condition and measurement boundary;
- instrument ID, calibration status and uncertainty;
- raw data location and evidence ID;
- value, unit, expanded uncertainty and coverage factor/confidence;
- repeat count and data-reduction method;
- operator/reviewer and date.

A pairwise metric comparison is permitted only when both candidates share the same unit, procedure revision and condition ID. The evaluator forms intervals:

`I_A=[x_A-U_A, x_A+U_A]`

`I_B=[x_B-U_B, x_B+U_B]`

If intervals overlap, the comparison is reported as indeterminate at the supplied uncertainty. Non-overlap can indicate a provisional direction only; the uncertainty model, coverage and test adequacy remain subject to engineering review. This interval check is not a substitute for a formal statistical analysis or a correlated uncertainty budget.

## 5. Evidence-linked weighted scoring

For each candidate:

`S=\sum_i w_i s_i`

where approved weights `w_i` are non-negative rational values summing exactly to 1, and scores `s_i` are integers from 1 through 5 with evidence and review-record references.

The evaluator uses exact rational arithmetic for the weight sum and weighted total. It reports a provisional score comparison only. A higher weighted score is not an automatic selection, and close scores or contradictory safety evidence must remain visible to the review authority.

No C-01 weights, scores or measurement values are populated in this issue. Synthetic values appear only in software regression fixtures and are not engineering results.

## 6. Mandatory decision gates

| Gate | Required closure evidence |
|---|---|
| Requirements baseline | Approved controlled C-01 requirements revision |
| Comparable configuration | Reviewed CW and CL assemblies/interfaces with traceable revisions |
| Measurement procedures | Approved matched procedures and acceptance references |
| Instrument calibration | Current calibration and uncertainty records |
| Physical reset interlock | Actual mechanism test showing reset-hammer contact is blocked while running |
| Independent review | Signed technical review, deviations and disposition |

The evaluator reports whether all gate records are present and marked pass. A pass requires non-placeholder evidence and review references. This is administrative evidence completeness, not independent proof of the underlying physical claim.

Even when all gates and study review are marked approved, software reports only that the package is ready for design-authority review. It never selects the architecture, freezes C-01 or authorizes manufacture.

## 7. Clutch/control compatibility

Control architecture must be compared with the vertical and horizontal/lateral clutch families because lever timing, actuation travel, retention sequence, packaging and start disturbance may differ by combination.

The four combinations remain separate configuration candidates. A control-only preference must not be interpreted as proof that its corresponding clutch combination is best. Each combination requires compatible geometry, phase, force/travel, clearance and physical verification.

## 8. Executable model and acceptance criteria

The WP-45 model validates:
- complete ten-criterion register and exact rational weight sum;
- approved criteria before scoring;
- CW/CL identity and distinct configuration revisions;
- complete score coverage, 1–5 integer scores and evidence/review references;
- measurement comparability and uncertainty interval overlap;
- complete mandatory gate register and non-placeholder evidence on passed gates;
- provisional-only scoring and non-authorizing review output;
- preservation of all four clutch/control combinations.

Acceptance criteria:
- AC-01 incomplete or unapproved criteria are rejected;
- AC-02 weights not summing exactly to one are rejected;
- AC-03 missing candidate score/evidence is rejected;
- AC-04 incomparable measurement conditions are rejected;
- AC-05 overlapping uncertainty intervals are labeled indeterminate;
- AC-06 missing or unsupported gate closure is not treated as passed;
- AC-07 the software never selects an architecture, freezes design or authorizes manufacture.

## 9. Verification plan

The accompanying regression tests use explicitly synthetic fixtures to exercise criteria completeness, rational weights, uncertainty overlap, mismatched test conditions, evidence requirements, gate closure, provisional scoring and four-combination preservation.

These tests validate software behavior only. No physical mechanism, instrument, test campaign, statistical analysis or C-01 performance result is represented as completed by this package.

## 10. Open engineering decisions

- Approved weights and score rubric.
- Acceptance limits and test conditions for each criterion.
- Final CW and CL member geometry and detailed assemblies.
- Column-wheel indexing/jumper geometry versus cam/follower/detent geometry.
- Pusher linkage and force/travel envelope.
- Clutch and stopped-retention phase margins for each combination.
- Positive physical running-reset interlock design and test.
- Material, surface finish, lubrication and wear limits.
- Manufacturing process capability and supplier qualification.
- Independent design-authority decision and approved configuration baseline.

## 11. Revision control and release status

Revision A establishes the evidence-gated trade-study model, synthetic regression suite and controlled decision framework. Later revisions shall record changed criteria, methods, evidence, requirements/configuration revisions and approvals.

**WP-45 does not select CW or CL, does not select a clutch, does not freeze C-01 and does not authorize prototype manufacture.**
