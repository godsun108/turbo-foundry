# STEWARD C-01 — WP-65 Chronograph Power Test Bench and Instrumentation System

- **Document ID:** SEB-C01-WP-65
- **Revision:** A — initial controlled issue
- **Status:** Measurement-system engineering definition; no instruments selected, no physical test authorized
- **Branch:** `steward/c-01-movement-foundation`
- **Calculation/validation model:** `tools/c01_power_test_bench.py`
- **Synthetic regression tests:** `tools/test_c01_power_test_bench.py`
- **Dependencies:** WP-13, WP-27 through WP-30, WP-46 through WP-49, WP-63 and WP-64

## 1. Purpose

WP-65 defines the bench and instrumentation system required to generate traceable measurements for the WP-64 chronograph power-distribution and dynamic-load analyses. It converts WP-64 measurement questions into a practical measurement architecture, controlled channel register, calibration and timebase requirements, uncertainty plan, raw-data contract, and release-review gates.

The system is intended to support matched evidence for both unresolved control candidates:
- **CW:** column-wheel control.
- **CL:** cam/lever control.

Each candidate retains its own immutable article/configuration identity. A paired stopped/running comparison must use the same movement revision, fixture revision, procedure revision, test condition, reserve state, measurement boundary, interval definition and verified timebase. Different evidence/run IDs are expected and preserved.

WP-65 does not select CW or CL, select a clutch architecture, define a final C-01 gear train, choose instruments, establish numerical acceptance limits, qualify a measurement system, or authorize hardware operation.

## 2. Bench architecture

The proposed bench is a modular, low-parasitic measurement system assembled around the already-defined WP-47 fixture concept and WP-48 structural/metrology qualification.

### 2.1 Mechanical and datum structure
1. A rigid, inspectable base and interchangeable article carrier.
2. A controlled movement/subassembly restraint that avoids plate distortion and unintended bridge loading.
3. A documented fixture datum frame, separate from movement master datum M0 and the movement XY coordinate convention.
4. Traceable carrier-to-movement coordinate transformation for each candidate revision.
5. Instrument mounts and cable routing that do not impose unmeasured force, torque, vibration or thermal load.
6. Guarding and access provisions based on a separately approved hazard review.
7. Repeatable installation, alignment, zeroing and post-installation inspection procedures.

Fixture stiffness, resonance, thermal drift, mounting repeatability, fastener preload, parasitic friction and sensor reaction loads must be characterized using the actual fixture and intended measurement configuration. No fixture dimensions, materials, fasteners or allowable deflections are assigned here.

### 2.2 Functional measurement chain

The measurement chain follows the physical energy path:

**Mainspring/barrel → going train → chronograph take-off/coupling → clutch → central chronograph seconds → minute/hour counter branches.**

The baseline movement load continues through the escapement and balance. The bench must observe both chronograph demand and the effect on timekeeping without assuming that an observed change is caused by a single component.

Torque measurement at a watch-scale arbor is potentially intrusive. Direct inline transducers, reaction-torque fixtures, calibrated micro-torque methods, or indirect measurement may be considered only after a loading study. If the sensor materially changes inertia, friction, alignment, support stiffness or available torque, the result is not representative until that effect is quantified and accepted. A mathematically inferred torque is not a substitute for a measured value unless the inference model and validation are explicitly approved.

## 3. Instrumentation channel architecture

The following register is the minimum planning dictionary. Actual channels are selected by the approved test procedure and measurement boundary; not every channel is required in every test.

| Channel family | Measurand and unit | Intended purpose | Critical qualification |
|---|---|---|---|
| Barrel output | Torque (N·m) and rotational speed (rpm or rad/s) | Source-side power and reserve-state characterization | Sensor loading and barrel boundary |
| Going-train interface | Torque and rotational speed | Baseline supply and transmission observation | Named arbor/interface and parasitic load |
| Chronograph take-off | Torque and rotational speed | Incremental chronograph demand | Must not alter train behavior materially |
| Counter branch | Angular position/speed; optional torque | Continuous/jumping counter load and event behavior | Counter mode remains undecided |
| Balance/escapement | Amplitude (deg), rate (s/day), beat error (ms or approved unit) | Timekeeping interaction | Approved timing method and consistent conditions |
| Chronograph output | Angular position/speed | Central seconds and totalizer response | Optical/encoder target must not add meaningful inertia |
| Event marker | Timestamp (s) and event identity | Clutch, indexing, retention, reset and transition timing | Sensor event distinguished from software command |
| Environment | Temperature (°C), and other justified variables | Test-condition control and drift context | Sensor location and thermal lag recorded |
| Vibration (conditional) | Acceleration (m/s² or g) | Diagnose fixture/motor/sensor disturbance | Include only where the risk assessment requires it |

Every deployed channel must carry: channel ID, measurand, unit, measurement boundary, physical location and axis, sensor/instrument asset IDs, range, resolution, bandwidth, sampling method, timebase, anti-alias disposition, calibration record/status, loading assessment, uncertainty budget reference, evidence ID and source revision.

A sensor's advertised specification is not automatically the uncertainty of the complete measurement chain. Installation, alignment, cable forces, fixture compliance, thermal effects, digitization, timing, calibration and reduction all contribute.

## 4. Measurement-system selection rules

### 4.1 Torque and speed
Select torque and speed instrumentation from the expected operating range established by approved preliminary measurements or a documented engineering estimate. The selection must demonstrate adequate resolution and uncertainty while avoiding overload and excessive sensor loading. The torque and speed measurement planes must be defined at the same physical interface before calculating shaft power.

For measured torque `τ` and speed `n`:

\[
P=\tau\,\omega=\tau\frac{2\pi n}{60}
\]

This calculation is valid only when torque and speed are synchronized and refer to the same shaft, direction, operating state and effective measurement interval. For rapidly varying events, average values may conceal peaks; synchronized time histories and a documented bandwidth/uncertainty treatment are required.

### 4.2 Balance and rate
Use an approved timing instrument and optical pickup appropriate to the movement's escapement and balance. Record amplitude, rate and beat error with instrument configuration, lift-angle setting where applicable, orientation, reserve state, temperature, stabilization period and chronograph state. The correct lift-angle setting and test protocol must be established by the movement/escapement engineering authority; WP-65 does not invent it.

### 4.3 Optical and position sensing
Prefer non-contact observation where practical. Confirm that reflective marks, encoder targets, illumination, camera mounts and optical access do not change component inertia, clearance, friction, temperature or operator access. Resolution, frame/sample timing and exposure must be justified against the event being measured.

### 4.4 Event and timebase measurement
A shared, traceable acquisition clock is preferred. If independent instruments are unavoidable, measure clock offset and drift against a common reference, retain the original timestamps and preserve the correction coefficients and evidence. Do not overwrite native timestamps. Software-issued commands and sensor-observed physical events must be separate channels.

## 5. Bandwidth, sampling and anti-aliasing

The required measurement bandwidth is derived from the fastest physical event and highest meaningful frequency content in the approved test objective. Sampling and filtering must be designed together.

For a declared analog measurement bandwidth (f_B), the ideal Nyquist lower bound is:

\[
f_s \ge 2 f_B
\]

This is a mathematical lower bound, not a recommended practical design margin. The actual sample rate, analog anti-alias filter response, filter transition band, phase delay, sensor response, event timing uncertainty and data volume must be justified in the procedure. A channel that only records quasi-static values may use a different acquisition method if the method is appropriate and traceable.

WP-65's validator checks the declared sample rate against the Nyquist minimum and requires an anti-alias filter reference or documented disposition. It does not design the filter, prove sensor bandwidth, establish event capture adequacy, or qualify the acquisition hardware.

## 6. Calibration, traceability and metrology

Each instrument and sensor shall have:
- unique asset/serial identity;
- manufacturer/model and firmware/configuration where applicable;
- calibration certificate or controlled calibration record;
- calibration status and due date at time of test;
- traceability chain and calibration uncertainty;
- range, resolution, linearity, hysteresis and environmental operating conditions as applicable;
- pre-run and post-run zero/check records where required;
- mounting/alignment and loading assessment;
- approved deviation or documented exemption, if applicable.

Calibration status must be current for the approved procedure unless a separately authorized deviation explicitly permits otherwise. A software validator cannot establish calibration validity; the controlled calibration record must be reviewed.

## 7. Measurement uncertainty

Build a separate uncertainty budget for each critical measurand and derived result, including as applicable:
- calibration uncertainty;
- resolution and quantization;
- repeatability/reproducibility;
- alignment and cosine effects;
- sensor loading and fixture compliance;
- temperature and drift;
- timebase and synchronization;
- bandwidth/filtering and event timing;
- sample processing and numerical integration;
- torque-speed synchronization and derived power.

For independent standard uncertainty contributions:

\[
u_c=\sqrt{\sum_i(c_i u_i)^2}, \qquad U=k u_c
\]

where (c_i) are sensitivity coefficients and (k) is an approved coverage factor. Root-sum-square is permitted only where independence is justified. Correlated components require a covariance treatment; the WP-65 helper intentionally refuses to represent correlation as independence. Instrument resolution alone is not a complete uncertainty budget.

The approved decision rule and acceptance limits come from controlled requirements and procedures, not this work package.

## 8. Data acquisition, integrity and schema

### 8.1 Run manifest
Each run records:
- run ID, candidate architecture and revision;
- movement/article and fixture revisions;
- procedure revision and test-condition ID;
- reserve-state ID, measurement boundary and interval definition;
- timebase synchronization record;
- operator and UTC start time;
- immutable raw-data URI and SHA-256 digest;
- evidence ID, source revision, deviations and calibration references.

### 8.2 Channel record
Each channel record references its channel definition and stores native timestamp/value pairs, unit, scaling, polarity, sensor/instrument identity, calibration, filtering, sample method, dropped/clipped/saturated sample flags and source hash.

### 8.3 Preservation and transformations
Native raw data are immutable. Clock correction, filtering, resampling, event annotation, integration and plotting create separately identified derived datasets with software revision, parameters and links to source evidence. No interpolated or resampled value is to be represented as a new raw measurement. Missing, clipped, saturated, dropped or invalid samples must be flagged and dispositioned, not silently removed.

### 8.4 Matched stopped/running data
For each candidate, acquire separate stopped and running records with matching movement revision, fixture revision, procedure revision, test condition, reserve state, boundary, interval definition and timebase. Retain different run/evidence IDs. The WP-64 reducer then computes paired incremental demand from the matched observations. A metadata match is necessary but does not prove physical equivalence; assembly state, lubrication, temperature, conditioning, operator actions and measurement loading must also be reviewed.

## 9. Test campaign architecture

The campaign is staged and requires independent approval at each hold point.

1. **Bench metrology qualification:** fixture datum realization, stiffness/resonance, alignment, sensor loading, zero stability and environmental sensitivity.
2. **Instrument qualification:** calibration review, range/resolution, bandwidth, anti-alias behavior, timebase verification and channel cross-talk.
3. **Baseline movement characterization:** barrel and going-train state, timing performance, reserve-state descriptors and environmental conditions.
4. **Chronograph stopped characterization:** baseline power and timing under a defined configuration.
5. **Chronograph running characterization:** matched configuration and reserve state, with synchronized source/load/timing observations.
6. **Event characterization:** clutch engagement, counter indexing, stopped retention and reset; transient torque/power capture only with a validated bandwidth and safe operating envelope.
7. **Candidate comparison:** repeat the controlled protocol independently for CW and CL; preserve each configuration and all deviations.
8. **Analysis and review:** WP-64 calculations, uncertainty, data integrity, acceptance decision and independent technical review.

No sample count, cycle count, operating speed, reserve endpoint, temperature, torque, force, bandwidth or acceptance threshold is set in WP-65. Those values require approved requirements, risk analysis, measurement capability and an authorized test procedure.

## 10. Safety and hardware-operation hold points

Before any physical test:
- identify stored-energy, spring release, rotating-part, pinch, ejection, electrical, thermal and tooling hazards applicable to the actual setup;
- approve guards, restraints, emergency stop/stop method and operator access;
- define approved operating envelope and mechanical travel limits;
- verify fixture retention and sensor attachment;
- verify calibration, instrument overload protection and cable routing;
- approve pre-run inspection, abnormal-condition stop criteria and post-run inspection;
- confirm that the test article is authorized for the specific procedure and configuration.

The WP-65 software cannot approve a hazard assessment, prove a guard effective, establish a safe operating envelope or authorize hardware operation.

## 11. Calculation and validation model

`tools/c01_power_test_bench.py` provides:
- channel completeness, calibration-status, range/resolution and Nyquist-minimum checks;
- channel-register uniqueness and power-plan coverage validation;
- synchronization record validation with explicit offset, drift and uncertainty;
- root-sum-square uncertainty calculation only when independence is explicitly justified;
- raw sample numeric and timestamp-order validation;
- run-manifest and SHA-256 syntax validation;
- matched stopped/running metadata checks;
- fail-closed release-review gate reporting.

The model does not operate instruments, calculate torque from gear geometry, infer unmeasured loads, design anti-alias filters, certify sensor loading, prove physical comparability, qualify the bench, approve safety or authorize testing. The regression suite uses synthetic records only; those records are not C-01 measurements.

## 12. Acceptance criteria

The measurement-system design package is acceptable for independent engineering review when:
1. every required measurand has a defined physical boundary, unit and method;
2. channel selection is justified by range, resolution, bandwidth, loading and uncertainty;
3. calibration and traceability records are controlled;
4. synchronization and native timestamp preservation are demonstrated;
5. anti-aliasing and sampling decisions are justified for each dynamic channel;
6. uncertainty budgets include the full measurement chain and correlation treatment;
7. raw-data integrity, hashes, metadata and derived-data lineage are verified;
8. fixture and instrument effects are characterized;
9. safety review and stop conditions are approved;
10. CW/CL candidate configurations and matched comparison controls are independently reviewed.

Passing software validation is not acceptance of the physical measurement system.

## 13. Open engineering inputs

- Actual torque/speed ranges at each measurement boundary.
- Sensor technology and permissible loading at watch-scale interfaces.
- Instrument models, asset availability and calibration status.
- Required transient bandwidth and timing uncertainty for each event.
- Fixture material, dimensions, stiffness and resonance.
- Sensor mounting, alignment and datum transfer details.
- Approved temperature/orientation/reserve-state test conditions.
- Approved measurement uncertainty targets and decision rules.
- Safety assessment and hardware-operation authorization.
- Approved procedures, sample plans and acceptance requirements.

## 14. Revision and release control

Changes to measurement boundaries, channels, sensors, instrument configuration, calibration, acquisition settings, filtering, timebase, fixture, uncertainty budget or data schema require revision control and impact assessment. Raw data are never replaced by corrected or processed data.

**Current disposition:** WP-65 establishes a measurement-system engineering framework only. No instrument is selected, no physical test bench is qualified, no test is authorized, no C-01 architecture is selected, no design is frozen, and no prototype is released for manufacture.
