# STEWARD C-01 — WP-67 Integrated Movement Power and Reserve Validation Campaign

- **Document ID:** SEB-C01-WP-67
- **Revision:** A — initial controlled issue
- **Status:** Integrated campaign and evidence-validation definition; no physical test authorized
- **Branch:** `steward/c-01-movement-foundation`
- **Validation model:** `tools/c01_integrated_power_campaign.py`
- **Synthetic regression tests:** `tools/test_c01_integrated_power_campaign.py`
- **Dependencies:** WP-27, WP-28, WP-29, WP-30, WP-64, WP-65 and WP-66

## 1. Purpose

WP-67 joins the C-01 energy-source, transmission, oscillator, chronograph-load and measurement-system work into one controlled campaign definition. Its question is:

**Across approved, directly measured reserve states, does the configured movement deliver sufficient energy and maintain approved timekeeping performance with the chronograph stopped and running?**

The campaign is intended to produce traceable evidence for:
- mainspring/barrel torque-angle behavior and usable energy over approved endpoints;
- barrel and going-train input/output speed and power at named interfaces;
- balance amplitude, rate and beat error across the same reserve-state conditions;
- incremental chronograph demand under matched stopped/running conditions;
- dynamic events and load changes where the approved procedures require them;
- measurement uncertainty, data integrity and guard-banded acceptance.

This is an engineering campaign definition and evidence validator. It does not establish that a physical C-01 movement exists, that any test has been performed, that the power budget closes, or that the reserve target is achieved.

## 2. Controlled campaign architecture

WP-67 composes the prior work rather than replacing it:

| Work package | WP-67 role |
|---|---|
| WP-27 | Measured spring torque-angle integration and usable-energy accounting |
| WP-28 | Supply/demand interface matching and oscillator/timekeeping observations |
| WP-29 | Measured reserve-state and event-window analysis |
| WP-30 | Verification matrix, instrument/evidence controls and guard-banded acceptance |
| WP-64 | Chronograph stopped/running demand and dynamic load comparisons |
| WP-65 | Chronograph power instrumentation and acquisition controls |
| WP-66 | Mainspring, barrel and going-train instrumentation and source-path measurements |

The integrated evidence chain is:

**Mainspring → barrel output → going-train input/output → escapement/balance**, with the chronograph treated as a separately measured demand branch and its stopped/running condition explicitly recorded.

Each result must retain the exact movement revision, campaign/procedure revision, fixture revision, test condition, measurement boundary, timebase, interval, reserve-state identifier and evidence source required by its underlying procedure.

## 3. Campaign matrix

The campaign plan declares, rather than assumes:
- movement and requirements revisions;
- procedure and fixture revisions;
- approved test-condition identifiers;
- approved reserve-state identifiers and their order;
- required chronograph modes (stopped and running);
- release-gate records and evidence references.

The model does not prescribe a sample count, reserve-state fraction, test duration, temperature, winding protocol, cycle count or environmental condition. Those values must come from approved requirements and procedures before test release.

At each approved reserve state, the intended comparison is a matched chronograph-stopped and chronograph-running observation. The matching key includes:
- reserve-state identifier;
- test-condition identifier;
- measurement boundary;
- timebase;
- measurement interval; and
- movement/source revision.

A pair with different intervals, boundaries, timebases, conditions or movement revisions is not treated as a matched comparison. Different raw evidence IDs are expected and are retained independently; they do not invalidate a pair by themselves.

Other operating conditions—calendar advance, winding state, environmental exposure or specific event loads—may be included only when explicitly defined in the approved campaign matrix. They must not be silently pooled with the baseline stopped/running comparison.

## 4. Measurement and evidence contract

Every observation has a unique ID and records:
- reserve-state and chronograph mode;
- test condition and measurement boundary;
- timebase and measurement interval;
- movement/source revision;
- immutable evidence ID;
- named measured quantities and units;
- expanded uncertainty for each reported quantity.

Candidate quantities include barrel torque and angular state, shaft torque/speed, delivered power, balance amplitude, rate, beat error, temperature and event markers. The approved procedure determines which are mandatory for a particular run and how they are acquired.

Raw instrument files remain the authoritative measurement record. WP-67 accepts traceable reduced observation records; it is not a data-acquisition driver and does not replace WP-49/65/66 raw-data, calibration, synchronization or chain-of-custody controls.

No missing value may be filled by interpolation, assumed efficiency, nominal spring curves, simulation, or an unverified model. The validator does not create data or convert a reserve-state fraction into elapsed hours.

## 5. Power and energy evaluation

Use the underlying controlled models and measured inputs:
- Shaft power: (P=T\omega), with torque and angular speed measured at the same declared interface and operating state.
- Measured work: integrate measured power over the approved time interval using the approved sampling and numerical method.
- Spring usable energy: integrate the measured torque-angle curve between explicitly approved operating endpoints.
- Chronograph incremental demand: compare stopped/running measurements at the same measurement boundary, reserve state, test condition, interval and timebase.
- Supply/demand margin: compare values only at a common declared interface and state.

The arithmetic is not a substitute for transient analysis, gear-tooth stress, dynamic torque capacity, friction, amplitude response or physical validation. Do not sum measurements across incompatible boundaries or double-count loads already included in an aggregate channel.

## 6. Timekeeping and reserve-state evaluation

At each declared reserve state, retain measured amplitude, rate and beat error alongside the source and delivered-power observations. Evaluate these against approved limits from the controlled requirements baseline.

WP-67 does not infer amplitude from torque or power. It does not interpolate between reserve states, extrapolate to an empty-barrel endpoint, or estimate hours remaining from a reserve fraction.

A claimed reserve duration must be supported by a directly measured endurance run with a defined start condition, end condition, continuous time record, interruption handling, configuration identity, environmental/test condition and approved acceptance rule. Any duration claim must be independently reviewed against the complete evidence record.

The existing 60–70 hour reserve aspiration remains **unverified** until such a physical result exists and passes the approved acceptance process.

## 7. Guard-banded acceptance

Each acceptance requirement must include:
- unique requirement ID and approved requirements revision;
- approved status;
- referenced observation and measured metric;
- unit;
- lower and upper limits;
- approval evidence ID.

Each observation supplies an expanded uncertainty for the metric. The evaluator forms the interval:

[
[x-U,\;x+U]
]

where (x) is the reported measurement and (U) is the supplied expanded uncertainty. It returns:
- **PASS** only when the complete interval is inside the approved limits;
- **FAIL** when the complete interval lies outside the approved limits;
- **INDETERMINATE** when the interval overlaps a limit.

This is an explicit guard-band rule for the supplied requirement. The user must ensure that uncertainty has been derived under the approved uncertainty budget and that the stated coverage is appropriate. The software does not calculate covariance, select a coverage factor or establish uncertainty independence.

A campaign can be marked evidence-review-ready only when the declared plan gates are approved, matched pairs are complete and every supplied approved acceptance requirement passes. That label means only that the submitted package is ready for engineering review; it is not a product approval or test authorization.

## 8. Fail-closed gates and authority

The campaign gate register requires evidence for:
1. approved requirements;
2. approved movement configuration;
3. qualified test fixture;
4. current instrument calibration;
5. approved measurement boundaries;
6. approved timebase synchronization;
7. approved uncertainty budget;
8. approved test procedure;
9. approved safety review;
10. completed independent review.

A missing, draft or unapproved gate holds the campaign. WP-67 cannot grant authority to perform a test, build hardware, freeze the design, select a chronograph architecture or release manufacture. Those decisions remain with the designated engineering and design authorities.

## 9. Model outputs and limitations

`c01_integrated_power_campaign.py` provides:
- campaign-plan and gate validation;
- observation metadata, numeric-value and uncertainty validation;
- stopped/running matched-pair completeness checks;
- approved-requirement guard-banded acceptance;
- integrated campaign status and explicit release guardrails.

It does not:
- operate instruments or validate calibration certificates;
- acquire or authenticate raw sensor data;
- infer missing measurements or reserve hours;
- simulate physical movement dynamics;
- prove gear strength, efficiency, friction, wear, shock resistance or physical power sufficiency;
- approve test execution, design freeze, prototype manufacture or production release.

The test module contains synthetic regression fixtures only. They are software test data and must never be represented as C-01 measurements or design values.

## 10. Acceptance criteria for WP-67 package

- Campaign plan has unique controlled identifiers and declared reserve states, conditions and both chronograph modes.
- Every release gate has a status and evidence reference.
- Observation IDs are unique and all measurements have explicit expanded uncertainty.
- Stopped/running observations are matched only on identical declared comparison conditions.
- Every acceptance requirement is approved, traceable and references a present observation/metric.
- Guard-banded verdicts are reproducible from supplied values and approved limits.
- No reserve duration is inferred and no 60–70 hour claim is emitted as verified.
- All outputs explicitly preserve the no-test/no-freeze/no-manufacture authority boundary.

## 11. Open inputs before a real campaign

The engineering authority must still supply and approve the actual movement configuration, requirements revision, reserve-state definitions, operating conditions, test durations, procedures, fixtures, instruments, calibration records, measurement boundaries, sampling/timebase plan, uncertainty budget, safety assessment, sample-size rationale and acceptance limits. No such C-01 values are fabricated in this package.

## 12. Revision and release control

This is Revision A, an initial controlled engineering definition. Changes to requirements, movement configuration, fixture, procedure, instrumentation, data schema or acceptance limits require revision traceability and impact review. Raw evidence must remain immutable; corrections are recorded as new controlled records with links to the superseded record.

**Current disposition:** C-01 is not design-frozen. WP-67 defines an evidence campaign and software validation framework only. No physical test, prototype build, merge or deployment is authorized by this document.
