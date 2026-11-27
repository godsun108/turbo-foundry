# WP-30 — Complete Movement Verification and Test Engineering Plan

- **Document ID:** SEB-C01-WP-30
- **Project:** STEWARD C-01
- **Revision:** A (initial controlled issue)
- **Status:** Preliminary test-engineering framework; procedures and limits pending approval
- **Branch:** `steward/c-01-movement-foundation`
- **Software:** `tools/c01_test_engineering.py`
- **Verification:** `tools/test_c01_test_engineering.py`
- **Dependencies:** WP-09, WP-13, WP-16, WP-21 through WP-29

## 1. Purpose and release boundary

WP-30 defines the controlled evidence system required to verify a physical STEWARD C-01 prototype. It establishes test-procedure structure, instrument and calibration traceability, uncertainty-budget bookkeeping, guard-banded acceptance evaluation, and a verification matrix.

This is not a completed test campaign. No physical prototype, instrument, supplier calibration certificate, approved requirement limit, or measured C-01 result is asserted to exist. Software fixtures are not engineering data.

## 2. Verification philosophy

Verification shall be requirement-led and revision-controlled. Each test must identify:
- requirement and design revision under test;
- approved procedure ID and revision;
- movement serial/build configuration and test-condition ID;
- measurement boundary, setup and preconditions;
- instrument asset/serial IDs and calibration records;
- raw data source record and data-reduction method;
- uncertainty budget and acceptance criterion;
- operator, reviewer, approver, date and deviations.

A result without traceable raw evidence is not an accepted result. A procedure in draft status is not authorization to run a hardware test. Safety-critical stop conditions and approved operating limits must be defined before energizing, winding, shocking or cycling a prototype.

## 3. Instrumentation and calibration register

The controlled register requires unique instrument ID, description, asset/serial ID, calibration record, due date, range/resolution, unit and calibration status. A non-calibrated instrument requires a separately approved deviation; a calibration exemption requires a written rationale.

The instrument selection must be based on the measurand, expected range, resolution, bandwidth, loading effect and uncertainty target. Candidate instrument classes include:
- optical encoder or high-resolution angular measurement for arbor/barrel speed;
- torque transducer or calibrated micro-torque fixture for shaft torque;
- timing machine and optical pickup for rate, amplitude and beat error;
- microscope/vision metrology and dimensional gauges for geometry;
- temperature chamber and calibrated temperature sensors for environmental tests;
- synchronized data acquisition for event and transient measurements.

These are instrument classes, not selected models or procurement specifications. Sensor attachment must not materially alter the movement load without that effect being evaluated.

## 4. Measurement uncertainty

The software combines explicitly supplied independent standard uncertainty contributions using root-sum-square:

\[
u_c=\sqrt{\sum_i(c_i u_i)^2}
\]

\[
U=k u_c
\]

where \(u_i\) are standard uncertainty contributions, \(c_i\) are sensitivity coefficients and \(k\) is a supplied coverage factor. This calculation is only valid when the independence/correlation treatment and sensitivity coefficients are justified. Correlated inputs require a covariance treatment and are outside this simple evaluator.

The tool does not derive uncertainty from instrument resolution alone, infer distributions, or choose a coverage factor. The approved uncertainty budget must identify calibration, repeatability, resolution, alignment, environmental, data-acquisition and reduction contributions as applicable.

## 5. Guard-banded acceptance

For a two-sided approved requirement interval \([L,H]\), measured value \(x\), and expanded uncertainty \(U\), WP-30 evaluates the complete interval \([x-U,x+U]\):

- **Pass:** the uncertainty interval lies wholly within the approved limits.
- **Fail:** the uncertainty interval lies wholly outside the approved limits.
- **Indeterminate:** the uncertainty interval overlaps a limit or straddles the acceptance boundary.

Indeterminate results require engineering disposition, improved measurement capability or an approved decision rule. The evaluator does not create requirement limits. One-sided, attribute, reliability and destructive-test acceptance plans require separately defined methods.

## 6. Verification domains and planned procedures

The following coverage register defines required procedure families. Each detailed procedure remains a separately controlled document with approved setup, sequence, sample count, safety controls, acceptance limits and data sheet.

| Domain | Planned evidence |
|---|---|
| Dimensional and geometric inspection | Calibrated dimensional report, datum and CAD revision |
| Gear train kinematics and efficiency | Speed, torque and energy at named interfaces |
| Mainspring torque-angle and barrel output | Loading/unloading curves and approved operating endpoints |
| Automatic winding and bridle | Rotor input, stored-energy gain and slip-onset trials |
| Escapement and balance | Amplitude, rate, beat error, positional and reserve-state data |
| Chronograph start/stop/reset | Functional cycles, hand return, engagement and measured load |
| Chronograph/timekeeping interaction | Matched chrono-off/on timing and power trials |
| Calendar weekday/date | Day transition, month-length rollover and safe correction |
| Power reserve and duty cycle | Full run-down with declared chronograph/calendar duty profiles |
| Environmental and durability | Approved temperature, shock, wear and cycle protocols |
| Serviceability and reassembly | Disassembly/reassembly records and post-service verification |

Calendar coverage must include weekday/date advancement across month boundaries of differing lengths, including February and leap-year behavior if the selected calendar architecture requires it. Month display remains a separate scope decision; WP-30 does not silently add a month indication to C-01.

## 7. Test sequence and hold points

1. **H0 — Requirements baseline:** approve measurable requirements, units, limits, operating states and traceability.
2. **H1 — Design/configuration baseline:** identify prototype revision, drawings, materials, assembly configuration and deviations.
3. **H2 — Instrument readiness:** approve instrument range, calibration, mounting, bandwidth, data acquisition and uncertainty budgets.
4. **H3 — Procedure approval:** approve each procedure, safety/stop conditions, sample count, data fields and acceptance rule.
5. **H4 — Component/subassembly verification:** inspect geometry and verify individual mechanisms before integrated operation.
6. **H5 — Integrated functional verification:** test timekeeping, winding, chronograph and calendar functions in controlled combinations.
7. **H6 — Performance and endurance:** run reserve, positional, environmental and cycle tests using approved duty profiles.
8. **H7 — Independent evidence review:** close deviations, failures, indeterminate results and requirement traceability.
9. **H8 — Prototype release recommendation:** engineering authority reviews the complete evidence package. This document does not grant release authority.

No hold point is considered passed by completion of a software model alone.

## 8. Test data and record control

Raw instrument files shall be retained unchanged with source IDs, timestamps, instrument configuration, calibration references and cryptographic checksums in the controlled project record. Derived data shall identify software version, calculation method, units, input source IDs and reviewer. Corrections shall create a new revision; raw data shall not be silently overwritten.

Every result shall be traceable to a requirement, procedure revision, movement revision, test condition, source record, instruments, calibration records and uncertainty budget. Deviations and retests shall preserve the original result and disposition history.

## 9. Acceptance and release criteria

- All requirements under test have approved numeric or objective acceptance criteria.
- Test procedures and revisions are approved before execution.
- Instruments are in calibration or covered by an approved deviation/exemption.
- Measurement boundaries, sampling rate, bandwidth and synchronization are suitable for the measurand.
- Uncertainty budgets are reviewed and the decision rule is approved.
- Raw data and derived calculations are traceable and reproducible.
- All results pass the approved acceptance rule; failures and indeterminate results have formal dispositions.
- Chronograph operation does not violate approved timekeeping, amplitude or reserve criteria under defined duty cycles.
- Weekday/date behavior passes the complete calendar test matrix for the selected architecture.
- Power reserve is established by full run-down tests, not energy extrapolation.
- Durability, environmental and post-service tests pass their separately approved protocols.
- Independent engineering review authorizes any prototype release recommendation.

No numeric limits are inserted here because they must be derived from the approved C-01 design basis, supplier/component data, intended use and measurement capability.

## 10. Software verification

Run from the tools directory:

```sh
python -m unittest test_c01_test_engineering.py
```

Synthetic tests cover instrument-register completeness, duplicate IDs, uncertainty combination, guard-banded pass/fail/indeterminate states, procedure approval, revision traceability and test-domain coverage. They validate software behavior only, not physical C-01 hardware.

## 11. Revision control

| Revision | Date | Change | Approval |
|---|---|---|---|
| A | 2026-11-26 | Initial controlled verification and test-engineering framework | Pending engineering review |

**Release gate:** WP-30 does not certify a prototype, approve test limits, authorize hardware operation, or authorize merge/deployment. All procedures, requirements, safety controls and acceptance criteria remain subject to engineering approval.
