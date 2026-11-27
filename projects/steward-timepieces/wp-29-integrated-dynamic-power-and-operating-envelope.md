# WP-29 — Integrated Dynamic Power and Operating Envelope

- **Document ID:** SEB-C01-WP-29
- **Project:** STEWARD C-01
- **Revision:** A (initial controlled issue)
- **Status:** Measurement-driven analysis framework; no virtual C-01 movement or physical performance claim
- **Branch:** `steward/c-01-movement-foundation`
- **Software:** `tools/c01_dynamic_power_envelope.py`
- **Verification:** `tools/test_c01_dynamic_power_envelope.py`
- **Dependencies:** WP-09, WP-10, WP-13, WP-16, WP-27 and WP-28

## 1. Purpose

WP-29 provides a common analysis layer for measured operating states and load events. It connects the measured mainspring/barrel energy work in WP-27 with the escapement supply, amplitude and rate measurements in WP-28. It is an evidence aggregator and reducer, not a continuous physical simulation.

The intended outputs are:
- a traceable reserve-state profile;
- a same-boundary operating-load ledger;
- measured incremental energy for complete calendar or other events;
- measured before/during/after chronograph or calendar transition deltas;
- explicitly parameterized friction-loss sensitivity scenarios;
- a controlled join between measured reserve states and load measurements.

## 2. Model boundary and evidence classes

Every reserve profile identifies movement revision, physical measurement boundary and test-condition identifier. Every sample carries a unique state ID, reserve-state fraction and source-record ID. Optional measured fields include elapsed time, barrel torque/speed, amplitude, rate, beat error and power.

The normalized reserve-state fraction is a test descriptor only. It is not remaining-hours data. WP-29 sorts measured points for presentation but does not interpolate, extrapolate or infer a reserve duration.

Every load record identifies the same movement revision, boundary, test condition, interval and duration. The allowed load categories are:
- baseline;
- chronograph incremental;
- calendar incremental;
- other incremental.

The baseline must exclude the incremental loads listed separately. Each category appears at most once in a ledger and each record must explicitly state whether it is incremental. A record flagged as already including another load is rejected. This conservative rule prevents obvious overlap; the test engineer must still establish the physical measurement boundary and prove that records are truly disjoint.

## 3. Calculations

### 3.1 Measured load energy and average power

For non-overlapping energy records measured over a common interval:

\[
E_{total}=\sum_i E_i
\]

\[
P_{avg}=\frac{E_{total}}{\Delta t}
\]

This is an interval average. It does not describe torque ripple, peak power, impulse waveform or transient response.

### 3.2 Event incremental energy

For a complete event-window trial and a matched baseline trial:

\[
\Delta E_{event}=E_{event\ window}-E_{baseline}
\]

Both trials must use the same movement revision, measurement boundary, test condition, interval definition and duration. The event trial must explicitly confirm complete event capture. The signed result is preserved; it is not forced positive. The method is suitable for a calendar advance or a defined operating event only when the entire event and a valid baseline are captured.

### 3.3 Transition measurements

Chronograph start/stop and calendar transitions should be instrumented as synchronized before/during/after samples. WP-29 reports signed differences in measured power, amplitude and rate. It does not fit a transient curve, infer an impulse, or claim that three samples characterize a high-bandwidth event. For true transient analysis, a synchronized high-rate trace, instrument bandwidth and uncertainty budget are required.

### 3.4 Friction sensitivity

For an explicitly supplied scenario loss fraction \(f\):

\[
E_{loss,scenario}=E_{input}f
\qquad
E_{downstream,scenario}=E_{input}(1-f)
\]

The fraction must be supplied with an evidence identifier. The result is labeled a scenario, not a measured C-01 efficiency or selected friction coefficient. No default friction value exists.

## 4. Required measurement programme

| Measurement | Method / evidence | Acceptance evidence |
|---|---|---|
| Reserve-state profile | Repeated measured states across controlled unwind | Traceable source records, movement revision and condition |
| Barrel torque/speed | Synchronized calibrated transducer and encoder | Same physical interface and time base |
| Amplitude/rate/beat error | Timing instrument using approved method | Approved limits, positions and uncertainty |
| Baseline load | Instrumented complete movement, defined subsystem boundary | Explicitly excludes separately listed increments |
| Chronograph increment | Matched chrono-off/on trials | Same interval, boundary, revision and condition |
| Calendar event increment | Complete advance event and matched baseline window | Event capture confirmed; same duration and condition |
| Start/stop transient | Synchronized high-rate measurement | Sample rate, bandwidth, trigger and calibration documented |
| Friction/loss sensitivity | Measured loss or explicitly approved scenario parameter | Evidence ID and uncertainty / scenario designation |
| Full reserve | Controlled full-wind run-down to approved stop criterion | Complete trace, repeat trials and end criterion |

## 5. Acceptance criteria

1. All measurements identify the movement revision, test condition, boundary and source record.
2. Reserve-state identifiers and reserve fractions are unique; measured states span the required approved operating window.
3. No remaining-hours value is inferred from normalized reserve fraction.
4. Every load ledger uses one boundary, interval, duration, movement revision and test condition.
5. Baseline and incremental loads are demonstrably non-overlapping; duplicate categories and records that include another listed load are rejected.
6. Calendar event energy is accepted only when the entire event is captured and a matched baseline trial exists.
7. Chronograph and calendar transition results preserve signed measured deltas; no unmeasured transient response is synthesized.
8. Friction sensitivity uses explicit evidence or scenario inputs and is never presented as a measured design value without supporting test records.
9. Amplitude, rate and beat error are evaluated against separately approved WP-09/WP-28 limits; WP-29 does not create those limits.
10. The 60–70-hour aspiration remains unproven until a complete movement run-down test passes the approved stop criteria in required operating/duty-cycle cases.

## 6. Assumptions and limitations

- Energy records are in joules, time in seconds, power in watts, torque in N·m, angular speed in rad/s, amplitude in degrees, rate in seconds/day and beat error in milliseconds.
- Input measurements are assumed to be calibrated and correctly synchronized; the software does not perform uncertainty propagation or calibration correction.
- Normalized reserve fractions are supplied by the test protocol; the model does not define their physical derivation.
- The arithmetic sum is valid only for non-overlapping measurements referred to a common energy boundary. Measurements taken at different shaft planes cannot be added without a separately documented energy-transfer model.
- Event subtraction is meaningful only for matched test conditions and complete capture.
- Friction sensitivity is a simple scenario calculation, not a tribological model.
- Synthetic test fixtures are software fixtures only and are not C-01 design or measured hardware data.

## 7. Verification

Run from the tools directory:

```sh
python -m unittest test_c01_dynamic_power_envelope.py
```

Tests cover reserve-state ordering and uniqueness, load aggregation, overlap rejection, complete event capture, matched event windows, transition deltas, friction scenario bounds, common-basis joining and mismatch rejection. Tests do not establish physical movement performance.

## 8. Revision control

| Revision | Date | Change | Approval |
|---|---|---|---|
| A | 2026-11-26 | Initial integrated measured dynamic-power and operating-envelope framework | Pending engineering review |

**Release gate:** WP-29 selects no spring, barrel, gear ratio, escapement, friction coefficient, operating limit or reserve result. No physical C-01 validation, merge or deployment is authorized by this work package.
