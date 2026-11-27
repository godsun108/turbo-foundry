# WP-50 — Chronograph Control Test Data Analysis and Comparative Performance Dashboard

**Document ID:** SEB-C01-WP-50  
**Revision:** A  
**Status:** Engineering analysis framework — review pending  
**Repository:** `godsun108/turbo-foundry`  
**Branch:** `steward/c-01-movement-foundation`  
**Date:** 2026-11-27  
**Predecessors:** WP-45 architecture trade framework; WP-46 control test bench; WP-47 fixture mechanical design; WP-48 structural/metrology qualification; WP-49 instrumentation and data acquisition  
**Companion software:** `tools/c01_control_analysis.py`  
**Regression tests:** `tools/test_c01_control_analysis.py`

## 1. Purpose and scope

WP-50 defines a reproducible analysis layer for transforming controlled WP-49 acquisition records into engineering evidence suitable for review of the column-wheel (CW) and cam/lever (CL) chronograph control candidates.

The dashboard is a presentation and traceability layer, not an instrument controller or design authority. It organizes:
- force-versus-travel observations and signed path work;
- start/stop event-latency distributions;
- reset-to-zero error and repeatability;
- state-transition success/failure counts and interval estimates;
- run history, candidate revisions, procedure revisions, fixture revisions and evidence lineage;
- measurement uncertainty records supplied under WP-48/WP-49.

No actual C-01 test data is present in this work package. Synthetic values in regression tests are software fixtures only.

## 2. Design principles

1. **Raw evidence is immutable.** WP-50 consumes exported observations and never edits or replaces native WP-49 files.
2. **Every result is traceable.** Each run carries run ID, candidate ID, procedure revision, test-condition ID, fixture revision, evidence ID and source revision.
3. **No hidden defaults.** Analysis parameters such as coverage factor and Wilson interval z-value are supplied explicitly by the caller.
4. **Comparability is gated.** Procedure revision, test condition and fixture revision are checked; passing metadata checks does not prove experimental equivalence.
5. **Uncertainty is visible.** An interval is calculated only from supplied uncertainty inputs and explicit confirmation that the combination assumptions are appropriate.
6. **No aesthetic winner.** Graphs and summary metrics do not select CW or CL, determine weights, or substitute for the WP-45 decision process.
7. **Fail visibly.** Missing provenance, invalid numeric values and non-monotonic time samples are rejected rather than silently repaired.

## 3. Input data contract

Each analysis run must identify:
- `run_id`, `candidate_id`, `procedure_revision`, `test_condition_id`, `fixture_revision`;
- `evidence_id` and `source_revision`;
- optional measured channels/derived observations with explicit units;
- zero datum and reset observations where reset analysis is requested;
- state trials with expected and observed physical/logical states clearly identified by the upstream procedure.

The production adapter must retain the full WP-49 manifest, instrument IDs, calibration IDs/status, article and carrier revisions, operator, UTC start time, raw-file hashes, synchronization evidence, sample method, filter metadata and deviations. The WP-50 minimal analysis record does not replace the WP-49 manifest.

## 4. Analysis methods

### 4.1 Force-versus-travel

The model preserves every supplied `(time, travel, force)` point for chart rendering and calculates sampled peak force, travel range and signed work:

[
W = sum_i rac{F_i+F_{i+1}}{2}(x_{i+1}-x_i)
]

For force in N and travel in mm, divide N·mm by 1000 to report joules. Because travel reverses on a return stroke, the signed integral can cancel loading work. WP-50 does not automatically segment loading/return branches or label the resulting signed integral as dissipated hysteresis energy. A future approved analysis method must define branch segmentation, dwell treatment, filtering and compliance correction before reporting loop loss.

The sampled maximum is not a guaranteed transient maximum. Native acquisition bandwidth and sampling adequacy remain WP-49/WP-48 responsibilities.

### 4.2 Start/stop latency

The dashboard summarizes supplied event-latency observations in seconds using count, mean, median, minimum, maximum, range and sample standard deviation where defined. The event-detection rule, source/target event definitions, timebase correction and uncertainty must remain linked to the WP-49 run record.

Do not pool different event definitions, procedures, test conditions, fixture revisions or candidate configurations merely because the units match.

### 4.3 Reset accuracy and repeatability

For each measured angle and calibrated zero datum:

[
e_i = ((	heta_i-	heta_0+180^circ)mod 360^circ)-180^circ
]

The analysis reports each signed wrapped error, circular mean error, maximum absolute error and sample standard deviation. The zero datum must be calibrated and its uncertainty retained in the measurement record. The calculated statistics do not include optical scale, alignment, parallax, hand width, backlash, settling or calibration uncertainty unless these are separately propagated by an approved uncertainty model.

### 4.4 State-transition reliability

Each trial compares an expected state with an observed state. The software reports successful/failed counts, observed success fraction and a Wilson score interval. The caller must supply the z-value; the interval's confidence interpretation depends on that value and the sampling assumptions.

Trials must be defined by an approved protocol, including the transition sequence, cycle selection, failure definition, exclusions and independence assumptions. Repeated cycles on one article may be correlated; the simple Wilson interval does not model clustering, wear drift or article-to-article variation.

A state-label match is not proof of a physical running-reset interlock. WP-46 requires a physical test with appropriate evidence and review.

### 4.5 Uncertainty overlays

A supplied value and combined standard uncertainty may be represented as:

[
[x-ku_c,;x+ku_c]
]

The function requires an explicit positive coverage factor and explicit confirmation that the supplied combined standard uncertainty is valid for the stated combination method. This is not a full uncertainty budget, does not establish a confidence level by itself and does not handle covariance. Use WP-48's uncertainty budget and correlation treatment. If independence is not justified, do not use independent RSS.

### 4.6 Candidate comparison and run history

The comparison helper checks candidate identity and selected metadata: procedure revision, test-condition ID and fixture revision. A metadata match is necessary but insufficient. Engineering review must assess article configuration, calibration, conditioning, lubrication, assembly, operator, cycle history, environmental conditions, acquisition bandwidth, synchronization and other confounders.

Dashboard run history retains each run separately. Candidate-level aggregation across unmatched conditions is intentionally not performed. Any pooled estimate requires a separately approved statistical analysis plan and a defined experimental design.

## 5. Dashboard presentation requirements

A future user interface should provide:
- **Run selector/history:** run ID, date/time, candidate and configuration revisions, procedure, fixture, article, evidence and disposition.
- **Force/travel panel:** raw point trace, loading and return branches only when a reviewed segmentation rule exists, sampled peak, signed work and uncertainty annotations.
- **Timing panel:** individual observations, distribution summary and uncertainty/timebase notes.
- **Reset panel:** per-cycle signed error, circular mean, maximum absolute error and measurement uncertainty.
- **Reliability panel:** successes, failures, denominator, Wilson interval and any excluded trials with disposition.
- **Comparability panel:** matched/mismatched metadata and a separate human-reviewed confounder checklist.
- **Decision panel:** evidence completeness, unresolved issues and WP-45 gate status. It must display `NO ARCHITECTURE SELECTED` until the formal design-authority decision process is completed.

Charts must show units, sample counts, run IDs, candidate revisions and uncertainty definitions. Do not visually imply precision beyond the underlying instrument and analysis capability. No graph color, ranking or composite score may imply a design winner.

## 6. Equations and statistical assumptions

Descriptive statistics use the arithmetic mean, median, extrema, range and sample standard deviation. A standard deviation is undefined for a single observation and is returned as null.

The Wilson interval for observed proportion (hat p), sample count (n) and caller-supplied (z) is:

[
rac{hat p+rac{z^2}{2n} pm zsqrt{rac{hat p(1-hat p)}{n}+rac{z^2}{4n^2}}}{1+rac{z^2}{n}}
]

The interval is bounded to [0,1]. Its suitability depends on the test design; repeated dependent cycles require a more appropriate model.

## 7. Acceptance criteria

Software framework acceptance:
- Reject missing required run provenance.
- Reject non-finite values and non-monotonic force/travel timestamps.
- Preserve source points and return chart-ready data.
- Calculate signed work with correct unit conversion.
- Calculate event-latency descriptive statistics without inventing samples.
- Handle angular wrap at the 0°/360° boundary.
- Report transition denominators, failures and supplied-z Wilson intervals.
- Reject uncertainty interval calculation unless independence/combination assumptions are explicitly confirmed.
- Flag metadata mismatches and never select a candidate.
- Preserve run and evidence identifiers in dashboard output.

Engineering acceptance before any architecture recommendation:
- WP-49 raw files and hashes are archived and verified.
- WP-48 calibration, fixture qualification and uncertainty records are approved.
- Test procedures and acceptance criteria are approved before data collection.
- CW/CL configurations are controlled and comparable, or confounders are explicitly addressed.
- Physical interlock test evidence is independently reviewed.
- Statistical analysis plan, exclusions and pooling rules are approved.
- WP-45 decision gates and independent design-authority review are complete.

No numerical acceptance threshold is assigned by WP-50.

## 8. Verification and execution

Synthetic regression tests cover descriptive statistics, uncertainty gating, signed force/travel integration, timestamp validation, latency summaries, angular wrap, state reliability, matched-run metadata, dashboard provenance and neutral decision status.

From the tools directory:

    python -m unittest test_c01_control_analysis.py

All test inputs are synthetic. Passing software tests would establish only the implemented calculation behavior; it would not establish instrument validity, physical mechanism performance or C-01 acceptance.

## 9. Revision control

| Revision | Date | Change | Approval |
|---|---|---|---|
| A | 2026-11-27 | Initial analysis and dashboard data contract, calculations, traceability and synthetic regression suite | Pending engineering review |

## 10. Release statement

WP-50 establishes a traceable analysis framework downstream of WP-49. It does not contain actual C-01 measurements, approve test procedures, select a control architecture, select a clutch architecture, freeze the movement, authorize prototype construction or establish production readiness.
