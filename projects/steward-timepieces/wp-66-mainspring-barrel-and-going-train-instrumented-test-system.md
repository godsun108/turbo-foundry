# STEWARD C-01 — WP-66 Mainspring, Barrel and Going-Train Instrumented Test System

- **Document ID:** SEB-C01-WP-66
- **Revision:** A — initial controlled issue
- **Status:** Instrumented test-system engineering definition; no instruments selected and no physical test authorized
- **Branch:** `steward/c-01-movement-foundation`
- **Validation model:** `tools/c01_source_train_test_system.py`
- **Synthetic regression tests:** `tools/test_c01_source_train_test_system.py`
- **Dependencies:** WP-25, WP-27, WP-28, WP-29, WP-30, WP-49, WP-64 and WP-65

## 1. Purpose and engineering question

WP-66 defines the instrumented test system needed to characterize the actual energy source and transmission path of STEWARD C-01:

**Mainspring → barrel output → going-train input → going-train output → escapement/balance.**

The purpose is to obtain traceable measured evidence for:
- barrel torque versus angular state;
- usable spring energy over explicitly approved operating endpoints;
- barrel and going-train shaft speed;
- torque and power at named transmission interfaces;
- reserve-state-dependent supply and timekeeping behavior;
- chronograph-off and chronograph-on source/load comparisons; and
- measurement uncertainty and test repeatability.

The engineering question is whether measured source capability and delivered power remain adequate across the approved operating window while the balance/escapement maintains approved timekeeping performance, including the chronograph's incremental demand.

WP-66 is a test-system definition, not a finding that C-01 has sufficient power. It does not validate a 60–70 hour reserve, select a mainspring, establish a torque curve, infer missing measurements or authorize a prototype test.

## 2. Interface and measurement-boundary definition

Every torque, speed, energy and power value must be tied to a named physical boundary. The measurement register shall identify:
1. the shaft/arbor or barrel interface;
2. the physical measurement plane and rotation axis;
3. the positive rotation direction and torque sign convention;
4. whether the sensor measures transmitted torque, reaction torque or an indirect proxy;
5. the fixture and support configuration;
6. the sensor loading and parasitic-loss assessment; and
7. the associated movement, fixture, procedure and test-condition revisions.

Fixture datums remain distinct from movement master datum M0. Any fixture-to-movement transform must be controlled and independently checked. The measurement boundary must not move between paired source/demand measurements without a documented correction and review.

## 3. Test-system architecture

### 3.1 Barrel torque-angle characterization
The barrel test station shall support controlled measurement of torque as a function of barrel/spring angular state. The method must distinguish the spring's loading and unloading behavior where relevant, document the angular datum and direction, and identify the approved usable operating endpoints.

The preferred evidence is a calibrated torque measurement synchronized with angular position. A fixture that restrains or drives the barrel must have characterized friction, compliance, backlash and parasitic torque. If the measurement method adds load or changes the spring boundary condition, that influence must be measured and assessed.

WP-27's measured torque-angle integration is retained:

\[
E=\int_{\theta_1}^{\theta_2}\tau(\theta)\,d\theta
\]

For discrete measured samples, trapezoidal integration is used:

\[
E\approx\sum_i\frac{\tau_i+\tau_{i+1}}{2}(\theta_{i+1}-\theta_i)
\]

Torque is in N·m, angle in radians and energy in joules. The integration is valid only over the measured interval. No extrapolation beyond measured samples or unapproved operating endpoints is permitted.

### 3.2 Barrel output torque and speed
A separate running measurement shall characterize torque and angular speed at the declared barrel output interface under the intended movement load. If torque is measured with an inline transducer or reaction fixture, the test must quantify the added inertia, friction, alignment and support effects. A sensor that changes the operating point cannot be assumed transparent.

For synchronized torque τ and angular speed ω:

\[
P(t)=\tau(t)\,\omega(t)
\]

For speed (n) in rpm:

\[
\omega=\frac{2\pi n}{60}
\]

Torque and speed must refer to the same shaft, measurement plane, direction, timebase and operating state. A single average torque or speed is insufficient where dynamic behavior is material.

### 3.3 Going-train transmission station
The going-train test architecture shall identify the input and output arbors and the relevant gear-train revision. Measure input/output speed synchronously; torque measurement at both ends is preferred where feasible and non-intrusive. Where direct torque measurement is not possible, any indirect method must be explicitly documented, validated and kept distinct from a direct measurement.

Measured transmission efficiency may be calculated only when input and output power are measured at declared boundaries under matched steady conditions:

\[
\eta=\frac{P_{out}}{P_{in}}
\]

The report must state uncertainty, direction, reserve state, load configuration and whether losses in supports, sensors or fixtures are included. A calculated ratio is not automatically the intrinsic gear-train efficiency.

### 3.4 Escapement and balance observation
The same operating state must be observed using an approved timing measurement method for:
- balance amplitude;
- rate;
- beat error;
- orientation;
- reserve state;
- temperature;
- chronograph state; and
- stabilization/conditioning history.

Amplitude must be measured, not inferred from torque or power. Rate and amplitude comparisons require matched instrument settings and test conditions. The appropriate lift-angle setting and timing protocol require approval by the escapement engineering authority.

## 4. Instrument channel dictionary

The campaign channel register shall include, as applicable:

| Channel | Measurand | Unit | Purpose |
|---|---|---|---|
| Barrel torque | Torque | N·m | Spring torque-angle curve and running output |
| Barrel angle/state | Angular position or declared state | rad or controlled state code | Spring operating point |
| Barrel speed | Rotational speed | rpm or rad/s | Barrel output behavior |
| Going-train input torque | Torque | N·m | Power entering declared train boundary |
| Going-train input speed | Rotational speed | rpm or rad/s | Input shaft power |
| Going-train output torque | Torque | N·m | Delivered output power where measurable |
| Going-train output speed | Rotational speed | rpm or rad/s | Kinematic and transmission observation |
| Balance amplitude | Oscillation amplitude | deg | Oscillator response |
| Rate | Timekeeping rate | s/day | Timekeeping performance |
| Beat error | Beat asymmetry | ms or approved unit | Regulation/escapement observation |
| Temperature | Local temperature | °C | Test-condition and drift context |
| Event marker | Timestamp/event code | s / controlled code | Winding, state change and transient alignment |

Every channel shall include unique ID, measurand, unit, physical boundary, location/axis, sensor and instrument IDs, range, resolution, bandwidth, sample method, timebase, anti-alias disposition, calibration record/status, loading assessment, uncertainty-budget reference, evidence ID and source revision.

The required channel list is a campaign-planning baseline. Individual approved procedures may use a justified subset; no sensor is assumed to be installed.

## 5. Sampling, synchronization and data integrity

### 5.1 Steady and transient methods
Separate quasi-static torque-angle characterization from dynamic running measurements. The required bandwidth and sample rate must follow the fastest event and frequency content relevant to each test. The Nyquist condition (f_s\ge2f_B) is a lower mathematical bound, not a practical design margin or proof of adequate event capture. Anti-alias filter response, sensor response, phase delay, timing uncertainty and dropped-sample behavior must be justified.

### 5.2 Timebase
Use a shared traceable clock where practical. If independent instruments are used, characterize offset and drift against a common reference, retain native timestamps, and store correction coefficients as separate evidence. Command timestamps and physically observed events must be recorded as distinct channels.

### 5.3 Immutable raw records
Preserve native instrument exports unchanged with a cryptographic digest, instrument configuration, calibration references, operator, UTC timestamps, movement/fixture/procedure revisions, reserve-state ID, boundary ID, test-condition ID and deviations. Filtering, synchronization correction, resampling, integration and plotting create derived records linked to their source; they never replace raw data.

Dropped, clipped, saturated, missing or invalid samples must be flagged and dispositioned. Interpolation must not be represented as measured evidence.

## 6. Reserve-state campaign

The reserve-state campaign shall use explicitly measured and documented operating states. Each state record includes:
- state ID and measured state descriptor;
- barrel torque and angular position/state;
- barrel and train speeds where applicable;
- amplitude, rate and beat error;
- chronograph stopped/running state;
- temperature and orientation;
- elapsed conditioning and test history;
- evidence ID and source revision.

State fractions, if used, must be defined by an approved physical measurement method and must not be mistaken for elapsed reserve hours. A series of measured points does not establish a continuous reserve curve. No remaining-hours estimate may be inferred without a separately validated model and approved evidence.

## 7. Matched power and timekeeping comparisons

At each approved reserve state, acquire matched observations for:
1. baseline movement with chronograph stopped;
2. same movement configuration with chronograph running;
3. event-driven counter/clutch/reset tests only under separate approved procedures.

The matched pair must share movement revision, fixture revision, procedure revision, test condition, reserve state, measurement boundary, interval definition and verified timebase. Distinct run IDs and evidence IDs are required. Review assembly condition, lubrication, temperature, orientation, conditioning, operator actions and sensor loading before attributing a difference to chronograph load.

For measured energy values at the same boundary and interval:

\[
\Delta E=E_{source}-E_{demand}
\]

This difference is only meaningful if the energy terms are defined over the same boundary, interval, state and accounting convention. It is not by itself proof of dynamic torque margin, oscillator stability, long-term reserve or reliable operation. WP-64's power and load analysis remains the controlled reduction method.

## 8. Metrology and uncertainty

The uncertainty budget must include relevant contributions from:
- torque calibration, linearity, hysteresis and resolution;
- angular position and speed calibration;
- alignment and axis/runout effects;
- fixture friction, compliance and sensor loading;
- timebase synchronization and channel phase;
- temperature and environmental drift;
- sampling, filtering and numerical integration;
- repeatability and reproducibility;
- balance timing measurement and instrument settings.

For justified independent standard uncertainty contributions:

\[
u_c=\sqrt{\sum_i(c_i u_i)^2},\qquad U=k u_c
\]

Correlated contributions require covariance treatment. A calibration certificate for one sensor is not the uncertainty of the complete measurement chain. The uncertainty budget and decision rule must be approved before acceptance decisions are made.

## 9. Safety and equipment qualification

Before physical testing, engineering must approve:
- stored-energy and spring-release hazards;
- barrel restraint and controlled release method;
- rotating shaft, fixture and ejection hazards;
- guarding, access and emergency stop/stop conditions;
- instrument overload protection and sensor attachment;
- fixture stiffness, resonance, alignment and mounting repeatability;
- pre-test inspection, abnormal-condition criteria and post-test inspection.

No mainspring winding, unwinding, release or powered movement test is authorized by this document. The actual operating envelope and safety controls must be established for the specific apparatus and test article.

## 10. Software validation model

`tools/c01_source_train_test_system.py` provides:
- channel-register completeness, uniqueness, calibration-status and sampling-floor checks;
- campaign metadata and approval validation;
- trapezoidal integration of supplied measured barrel torque-angle samples;
- reserve-state sequence validation without interpolating reserve hours;
- synchronized going-train input/output speed record validation;
- matched source/demand energy metadata checks;
- fail-closed review-gate reporting.

The model does not operate instruments, estimate unmeasured torque, infer gear ratios from incomplete data, calculate physical efficiency without matched measured power, predict reserve duration, certify the bench or authorize a test. Synthetic regression fixtures are not C-01 design data or test results.

## 11. Acceptance criteria

The WP-66 measurement-system package may proceed to independent engineering review when:
1. barrel and train measurement boundaries are explicit and traceable;
2. sensor loading and fixture parasitics are characterized;
3. channel ranges, resolution, bandwidth and sampling are justified;
4. instrument calibration and traceability are current;
5. native timestamp synchronization is verified;
6. raw-data preservation and derived-data lineage are demonstrated;
7. torque-angle and dynamic power uncertainty budgets are approved;
8. reserve-state definitions and test conditions are controlled;
9. matched stopped/running measurement procedure is approved;
10. safety review and independent technical review are complete.

Software validation alone cannot qualify the physical system or authorize testing.

## 12. Open engineering inputs

- Actual barrel torque-angle and operating-endpoint data.
- Barrel and going-train shaft speeds and torque ranges.
- Approved physical measurement boundaries and sign conventions.
- Sensor technologies and permissible loading at watch-scale interfaces.
- Fixture design, material, stiffness, resonance and parasitic-loss evidence.
- Instrument models, calibration status, bandwidth and sample methods.
- Approved reserve-state definitions, temperature and orientation conditions.
- Approved uncertainty targets and acceptance decision rules.
- Safety assessment, operating envelope and test authorization.
- Approved procedures and test sample plans.

## 13. Revision and release control

Any change to measurement boundary, fixture, sensor, instrument, calibration, channel, acquisition settings, timebase, uncertainty budget, reserve-state definition, procedure or data schema requires revision control and impact assessment. Raw evidence is immutable.

**Current disposition:** WP-66 defines an instrumented measurement and validation framework only. No C-01 mainspring or barrel performance is claimed, no reserve duration is established, no instruments are selected, no test bench is qualified, no hardware test is authorized, no architecture is selected, and no design is frozen or released for manufacture.
