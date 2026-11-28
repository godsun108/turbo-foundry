# WP-56 — Chronograph Control Mechanism Optimization and Architecture Selection

- **Document ID:** SEB-C01-WP-56
- **Revision:** A — initial controlled issue
- **Status:** Evidence-gated decision framework; no architecture selected
- **Branch:** \`steward/c-01-movement-foundation\`
- **Software:** \`tools/c01_control_architecture_selection.py\`
- **Verification:** \`tools/test_c01_control_architecture_selection.py\`
- **Dependencies:** WP-30, WP-33, WP-41 through WP-55

## 1. Purpose and decision boundary

WP-56 consolidates the control architecture engineering program into a controlled decision packet for the two candidates:
- **CW:** indexed column-wheel control.
- **CL:** cam/lever control.

It defines approved criteria, evidence-linked scores, uncertainty-aware measured comparisons, configuration comparability, release gates, decision-authority record and an explicit compatibility matrix with the separate clutch decision.

The software calculates transparent weighted score summaries and pairwise measurement interval comparisons. It never automatically selects a winner, freezes C-01, approves a prototype, or authorizes manufacturing. A completed packet can become ready for design-authority review; only the formally authorized design process can make the decision.

## 2. Architecture boundary: control and clutch remain separate

WP-33's four integrated combinations remain:

| Combination | Clutch candidate | Control candidate |
|---|---|---|
| A | Vertical friction clutch | Column wheel |
| B | Vertical friction clutch | Cam/lever |
| C | Horizontal/lateral gear coupling | Column wheel |
| D | Horizontal/lateral gear coupling | Cam/lever |

WP-56 evaluates control architecture. It requires a separate compatibility review reference for each candidate/clutch pairing. It does not infer that the preferred control mechanism automatically determines the clutch.

## 3. Decision principles

1. Requirements and acceptance references are approved before scoring.
2. CW and CL are separately identified configurations with controlled revisions.
3. Test comparisons use matched procedures, conditions and fixture revisions.
4. Raw evidence remains immutable and traceable to WP-49 acquisition.
5. WP-50 derived metrics retain run-level provenance and uncertainty context.
6. WP-52's paired-block protocol governs physical comparison design.
7. WP-54 component definitions and WP-55 motion/contact analysis are reviewed alongside bench results.
8. A weighted score is a decision aid, not proof of engineering superiority.
9. Conflicting, incomplete or uncertainty-overlapping evidence remains indeterminate.
10. Design-authority approval, design freeze and manufacturing release are separate controlled gates.

## 4. Required decision criteria

The WP-45 ten-criterion set is retained. Each criterion must have a definition, measurement method, acceptance reference, evidence ID, source revision, direction, approval ID and approved status. Weights are positive rational values and must sum exactly to one.

| Criterion ID | Engineering question |
|---|---|
| \`actuation_force_travel\` | What input force, travel, work and return behavior are required? |
| \`state_repeatability\` | Are start/stop/resume transitions repeatable without ambiguous states? |
| \`partial_actuation\` | What happens during interrupted, incomplete or repeated pusher strokes? |
| \`clutch_phase\` | Can the control deliver the required command timing for each clutch candidate? |
| \`retention_phase\` | Is elapsed time securely retained when stopped? |
| \`reset_interlock\` | Is reset positively blocked while running, with physical evidence? |
| \`wear_inspection\` | Are contact interfaces inspectable and durability evidence acceptable? |
| \`serviceability\` | Can the mechanism be assembled, adjusted, inspected and serviced? |
| \`manufacturability\` | Can controlled geometry and process capability support repeatable production? |
| \`packaging\` | Does the mechanism fit the approved movement envelope and service-access boundary? |

Direction is criterion-specific. The decision team must not assume that lower is always better; for example, a metric may be a target range rather than a simple minimization. Where a target band is needed, its scoring transformation must be documented in the approved criterion definition before data are scored.

## 5. Candidate configuration baseline

Both candidate records require:
- candidate ID and configuration revision;
- article identity and physical article status;
- requirements revision;
- evidence ID and source revision;
- approved configuration status;
- clutch-compatibility review reference.

A comparison is invalid if configuration revisions, procedure revisions, test conditions, fixture revisions, units, instrumentation, or relevant environmental and lubrication conditions are not comparable. Metadata checks do not prove physical equivalence; engineering review must confirm the complete comparison boundary.

## 6. Measured comparison and uncertainty

For a measured value \(x\) and expanded uncertainty \(U\), the comparison interval is:

\[
I=[x-U,\;x+U]
\]

For a lower-is-better criterion, CW is demonstrably better in a pairwise comparison only if its interval is wholly below the CL interval. For higher-is-better, CW is demonstrably better only if its interval is wholly above the CL interval. If intervals overlap, the result is indeterminate under this screening rule.

This interval rule is not a substitute for the approved WP-48/49 uncertainty model, paired experimental design, distribution analysis, or a formal statistical method. Every comparison must identify both run IDs, procedure revision, test condition, fixture revision, units, evidence and source revision. Do not compare unmatched test conditions or pool raw observations across unrelated runs.

## 7. Weighted score summary

For approved weights \(w_i\) and reviewed scores \(s_i\), the tool calculates:

\[
S=\sum_i w_i s_i,\qquad \sum_i w_i=1
\]

Scores are constrained to the declared 1–5 scale and require evidence, source revision, rationale and review approval per criterion. The resulting values are transparent summaries only. They are not an optimization proof, uncertainty-adjusted ranking, automatic recommendation, or architecture selection. A single high aggregate score cannot override a failed safety gate or unresolved critical risk.

## 8. Mandatory decision gates

The decision packet requires explicit disposition for all gates:

1. requirements baseline;
2. candidate configuration baseline;
3. comparable test conditions;
4. approved measurement procedures;
5. instrument calibration and uncertainty;
6. physical running-reset interlock;
7. motion and contact review;
8. energy and timekeeping impact review;
9. risk disposition;
10. independent design review.

A gate may be open, pass, fail or not applicable. Not-applicable requires a documented rationale and approval reference. Only a complete set of passing gates can make the packet ready for design-authority review. The software does not treat a not-applicable disposition as a pass.

## 9. Decision-authority record

The packet may carry a proposed decision-authority record with selected control, rationale, signatory, date and approval ID. The evaluator reports that record separately and does not treat it as a software-controlled freeze.

The actual decision must be recorded in the controlled design baseline and traceable to:
- approved requirements revision;
- candidate configuration revisions;
- evidence index and raw test records;
- analysis and uncertainty reports;
- all gate dispositions;
- independent review comments and closure;
- signed design-authority decision.

Control selection does not decide the clutch. The four WP-33 combinations require their own compatibility and integrated architecture review. A design freeze under WP-32 and first-article release under WP-53 remain separate approvals.

## 10. Evidence package required

The decision packet should index, at minimum:
- WP-46 control test procedures and results;
- WP-47/48 fixture and metrology qualification;
- WP-49 immutable raw acquisition records and calibration;
- WP-50 analysis exports and uncertainty;
- WP-51 dashboard export for review convenience;
- WP-52 paired campaign protocol, deviations and run dispositions;
- WP-53 candidate article configuration, BOM, drawings and inspections;
- WP-54 component geometry and interface records;
- WP-55 motion/contact analysis and physical correlation;
- WP-27 through WP-29 energy and rate-impact evidence;
- risk register and independent design review.

The dashboard is not primary evidence. Preserve raw measurement files and their hashes in the controlled evidence index.

## 11. Executable model and verification

Files:
- \`tools/c01_control_architecture_selection.py\`
- \`tools/test_c01_control_architecture_selection.py\`

The model validates criteria and rational weights, candidate configuration records, evidence-linked scores, uncertainty intervals, mandatory gates and decision packet completeness. It reports weighted summaries and review readiness while keeping architecture selection and design freeze false.

Run from the tools directory:

\`\`\`sh
python -m unittest test_c01_control_architecture_selection.py
\`\`\`

All regression fixtures are synthetic software test data. They are not C-01 measurements, approved weights, actual article records, gate approvals, or a design decision.

## 12. Current C-01 decision status

No actual CW or CL physical test campaign data has been supplied in this work package. No approved criteria weights, candidate scores, measured comparisons, completed gate evidence or signed design-authority decision are populated. Therefore:
- no control architecture is selected;
- no clutch architecture is selected;
- none of combinations A–D is selected;
- C-01 is not design-frozen;
- no prototype build or manufacturing release is authorized.

## 13. Acceptance criteria

| ID | Acceptance criterion | Required evidence |
|---|---|---|
| WP56-AC-01 | Complete approved criteria and weights | Requirements/criteria approval |
| WP56-AC-02 | Controlled CW and CL configuration baselines | Approved article/configuration records |
| WP56-AC-03 | Comparable measured runs for each required criterion | WP-49 raw data and WP-52 campaign records |
| WP56-AC-04 | Uncertainty and interval interpretation reviewed | WP-48/49 metrology report |
| WP56-AC-05 | Component, motion, contact and energy reviews complete | WP-27–29, WP-54 and WP-55 evidence |
| WP56-AC-06 | Physical running-reset interlock passes | Actual-article inspection/test |
| WP56-AC-07 | All risks have approved dispositions | Controlled risk register |
| WP56-AC-08 | Independent review complete | Signed review record |
| WP56-AC-09 | Decision authority issues explicit control decision | Signed decision record |
| WP56-AC-10 | Clutch compatibility remains separately reviewed | Four-combination compatibility matrix |

## 14. Revision history

| Revision | Description | Status |
|---|---|---|
| A | Initial evidence-gated optimization and architecture decision framework | Issued for engineering development |
