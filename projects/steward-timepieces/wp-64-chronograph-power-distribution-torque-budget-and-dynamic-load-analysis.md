# STEWARD C-01 — WP-64 Chronograph Power Distribution, Torque Budget and Dynamic Load Analysis

- **Document ID:** SEB-C01-WP-64
- **Revision:** A — initial controlled issue
- **Status:** Measurement-driven engineering definition; no C-01 torque budget or power sufficiency finding
- **Branch:** `steward/c-01-movement-foundation`
- **Calculation model:** `tools/c01_power_distribution.py`
- **Synthetic regression tests:** `tools/test_c01_power_distribution.py`
- **Dependencies:** WP-13, WP-17, WP-27, WP-28, WP-29, WP-30, WP-34, WP-49, WP-50, WP-52, WP-63

## 1. Purpose

WP-64 connects the chronograph power train defined in WP-63 to the movement's mainspring/barrel, going train, escapement and oscillator. It establishes a controlled method to measure and compare:

- steady shaft torque, speed and power at declared interfaces;
- chronograph stopped versus running incremental demand;
- counter branch steady and event-driven loads;
- clutch engagement/disengagement and stopped-retention transitions;
- reset work and short-duration event energy;
- supply-versus-demand margin at a common interface;
- measured amplitude/rate changes with chronograph operating state; and
- reserve-state dependence without extrapolating unmeasured performance.

WP-64 is a measurement and analysis framework. It is not a dynamic watch simulation, a validated C-01 torque budget, proof of power sufficiency or a reserve-duration prediction.

## 2. Energy and power architecture

The energy chain remains:

**Automatic winding works → mainspring/barrel → going train → escapement → balance/oscillator.**

The chronograph is an additional load path:

**Going-train take-off → approved coupling/clutch → central seconds train → minute/hour counter branches**, with separate loads from control, stopped retention and reset mechanisms.

The energy source must supply the baseline timekeeping load and the additional chronograph demand without violating approved amplitude, rate, beat-error, reserve or durability requirements. Those requirements and limits must be approved and measured; WP-64 does not assign them.

### 2.1 Distinguish the quantities

| Quantity | Meaning | Unit |
|---|---|---|
| Torque | Rotational effort at a declared shaft/interface | N·m |
| Angular speed | Rotational rate at that same interface | rad/s or rpm |
| Power | Instantaneous rate of mechanical energy transfer | W |
| Energy | Power integrated over a defined time interval | J |
| Incremental power | Matched running-minus-stopped load at the same boundary | W |
| Incremental energy | Time integral of incremental power over a defined interval | J |
| Reserve-state fraction | Test-state descriptor, not remaining hours | dimensionless |

A torque value without its shaft, direction, speed, operating state and measurement boundary is not a complete power datum. Likewise, a power value without interval and evidence is not a complete energy budget.

## 3. Shaft torque and power calculations

For a measured or approved torque \(\tau\) in N·m and rotational speed \(n\) in rpm:

\[
\omega=\frac{2\pi n}{60}
\]

\[
P=\tau\omega=\tau\frac{2\pi n}{60}
\]

The WP-64 helper calculates this value only from explicit inputs. It does not infer torque from tooth ratios, estimate gear efficiency, or assign a load to an unmeasured component.

Where input and output torque/speed are measured at matched boundaries, a transmission efficiency may be calculated only when the measurement planes, operating state, direction, interval and uncertainty are controlled. No efficiency is defaulted or assumed by WP-64.

## 4. Chronograph stopped/running incremental load

The primary comparative method is a matched stopped/running measurement at the same physical boundary and reserve state.

For synchronized samples at times \(t_i\):

\[
\Delta P_i=P_{running,i}-P_{stopped,i}
\]

The incremental energy over the observed interval is estimated by trapezoidal integration:

\[
\Delta E=\sum_i\frac{\Delta P_i+\Delta P_{i+1}}{2}
(t_{i+1}-t_i)
\]

The mean incremental power is:

\[
\overline{\Delta P}=\frac{\Delta E}{t_{end}-t_{start}}
\]

Requirements:
- movement revision, boundary, interval, test condition and reserve-state ID must match;
- stopped and running data must use the same timestamp grid;
- each record retains its own evidence ID;
- instrument response, synchronization, calibration and uncertainty must be documented;
- comparison must use the same hand/counter configuration and defined operating condition.

The reducer reports measured differences only. It does not convert incremental power into remaining reserve hours or claim that the chronograph's demand is constant across the full spring unwind.

## 5. Load ledger and double-counting control

Every load record requires a unique load ID, measured/approved power, movement revision, measurement boundary, interval ID, test condition, reserve-state ID and evidence ID.

Loads may be aggregated only when all records share the same declared:
- movement revision;
- measurement boundary;
- measurement interval;
- test condition; and
- reserve-state ID.

Duplicate load IDs are rejected. Loads observed at different interfaces or over unmatched intervals must not be added together. A component measured upstream and again downstream may represent the same transmitted energy; the ledger must define whether each entry is a component demand or a boundary flow to avoid double counting.

The ledger is not a complete power budget until all relevant loads and losses are measured or otherwise approved and the accounting boundary is reviewed.

## 6. Dynamic event analysis

Steady-state average power does not describe short-duration events. The following event families require separate characterization:

| Event | Required observations |
|---|---|
| Clutch engagement | Input/output speed, torque or load proxy, engagement transient, central-seconds disturbance |
| Clutch disengagement | Residual drag, release timing, hand disturbance |
| Counter jump/index | Event phase, peak torque, pulse duration, angular completion, overshoot/bounce |
| Stop/retention | Retention engagement, hand drift, release load |
| Resume | Release transient, hand continuity and timekeeping disturbance |
| Reset | Reset force/work, hammer/heart-cam contact, residual drag, return behavior |
| Calendar advance | Coincident calendar load if chronograph/calendar overlap is permitted |

WP-64 can integrate sampled power within an event window only when both event boundaries coincide with actual measured samples. It does not interpolate missing event boundaries, reconstruct unobserved impulses or claim that a sampled peak equals the true physical peak.

### 6.1 Sampling and sensor qualification

Before a transient result can be accepted, the test plan must specify:
- sensor measurand and range;
- bandwidth and dynamic response;
- sampling rate and anti-aliasing method;
- synchronization to event trigger and movement timebase;
- calibration and traceability;
- uncertainty including sensor, fixture, alignment and processing contributions;
- raw-data retention and evidence hash; and
- repeatability and event-to-event variability.

If the instrument bandwidth or sample rate is insufficient to capture the event, the result is indeterminate, not a pass.

## 7. Supply/demand and torque budget

At a declared interface and matched operating state:

\[
M_P=P_{supply}-P_{demand}
\]

A nonnegative measured power margin is a necessary screening result at that interface, not proof of transient capacity, acceptable tooth contact, adequate torque at every reserve state or stable oscillator performance.

Torque and power comparisons must use the same shaft/interface and speed. A supply/demand comparison at different shafts cannot be made by comparing raw torque values without the intervening ratio and measured losses. Ideal gear ratios from WP-63 do not supply those losses.

The torque budget shall eventually be populated by measured or validated values for:
1. going-train take-off availability;
2. clutch and coupling losses;
3. central chronograph seconds load;
4. minute counter steady load;
5. hour counter steady load;
6. jumping-counter transient load, if selected;
7. stopped-retention and control load;
8. reset event load; and
9. additional bearing, mesh and lubrication losses.

No row is assigned a numeric value in this revision.

## 8. Escapement and timekeeping interaction

A chronograph can have a numerically acceptable power margin at one interface and still disturb the oscillator through friction, torque ripple, transient load or train interaction. Therefore, every comparative chronograph test must record movement amplitude, rate and beat error under defined conditions.

For matched off/on records:

\[
\Delta rate=rate_{on}-rate_{off}
\]

\[
\Delta amplitude=amplitude_{on}-amplitude_{off}
\]

WP-64 calculates the measured differences against caller-supplied limits only. It does not define or approve those limits. Any supplied amplitude floor or rate-delta limit remains provisional until formally approved by the design authority.

The existing preliminary 4 Hz frequency target and preliminary rate aspiration are not substituted for a measured chronograph-on acceptance criterion. WP-28 remains the reference for barrel-to-balance matching and WP-29 for the integrated measured operating envelope.

## 9. Reserve-state and operating-envelope campaign

The same stopped/running comparison must be repeated at defined reserve states. Each state must be identified by an actual test condition and measured barrel state; a normalized fraction is a label, not remaining-hours data.

The campaign should cover:
- chronograph stopped baseline;
- central seconds running;
- each counter branch active under its declared mode;
- clutch start/stop transitions;
- stop and retained elapsed time;
- resume;
- reset;
- calendar overlap where allowed by requirements; and
- any approved combined operating condition.

At each state, record barrel torque/speed, relevant branch loads, amplitude, rate and beat error. The exact state grid and acceptance limits require design-authority approval. WP-29 must not interpolate between measured states or extrapolate to an unmeasured reserve duration.

The 60–70 hour power-reserve aspiration remains unvalidated and is not demonstrated by WP-64.

## 10. Model functions and input contract

`tools/c01_power_distribution.py` provides:
- shaft power from explicit torque and RPM;
- trapezoidal integration of measured power samples;
- paired chronograph stopped/running incremental power and energy;
- same-interface supply/demand power margin;
- unique-ID and common-condition load-ledger aggregation;
- event-window energy integration with measured boundaries only;
- matched amplitude/rate delta evaluation against supplied limits; and
- an integrated evidence reducer that explicitly refuses to certify physical power sufficiency, reserve duration or timekeeping acceptance.

All sample values are caller-supplied measurements or explicitly approved inputs. Evidence identifiers and configuration metadata remain attached to results. No synthetic values are embedded as default C-01 data.

## 11. Verification and acceptance plan

| Verification item | Method | Acceptance basis |
|---|---|---|
| Shaft power | Calibrated torque and speed measurement | Approved uncertainty and boundary |
| Chronograph incremental load | Matched stopped/running paired campaign | Approved incremental-load limits |
| Load ledger | Independent boundary and duplicate review | Complete, non-overlapping accounting |
| Counter transient | High-bandwidth torque/power and motion capture | Approved peak, duration and completion limits |
| Clutch transient | Synchronized input/output observation | Approved disturbance and drag limits |
| Reset event | Force/travel/power measurement and repeated cycles | Approved reset work and zero-repeatability limits |
| Supply/demand | Matched interface/state measurements | Approved torque/power margin |
| Timekeeping | Amplitude/rate/beat-error comparison | Approved chronograph-on limits |
| Reserve-state robustness | Repeat campaign across approved measured states | All approved states meet requirements |
| Instrumentation | Calibration, bandwidth, synchronization, uncertainty | Approved metrology plan |

No numeric thresholds, instruments, sample rates, cycle counts or results are fabricated.

## 12. Synthetic regression coverage

The synthetic regression suite covers:
- shaft power arithmetic;
- trapezoidal power integration;
- invalid sample-time rejection;
- paired stopped/running incremental load;
- mismatch rejection;
- explicit supply/demand margin;
- load-ledger duplicate and interval guards;
- event-window integration and measured-boundary enforcement; and
- timekeeping delta calculation against caller-supplied limits.

Synthetic fixtures are code-validation examples, not physical measurements or C-01 design data. This document does not claim the test suite has been executed.

Run from the tools directory:

```bash
python -m unittest test_c01_power_distribution.py
```

## 13. Open engineering inputs

The following evidence is still required:
1. approved movement revision and chronograph configuration;
2. source-arbor and barrel torque/speed measurements;
3. defined power measurement planes and boundary diagrams;
4. matched stopped/running data with reserve-state coverage;
5. selected counter modes and measured branch loads;
6. dynamic event measurements for clutch, indexing and reset;
7. instrument bandwidth, calibration and uncertainty records;
8. approved amplitude, rate, beat-error, load and reserve limits;
9. accounting review for all load and loss entries; and
10. independent engineering review of the integrated torque and energy budget.

## 14. Release boundary

WP-64 does not prove physical power sufficiency, dynamic torque capacity, gear strength, efficiency, wear life, shock resistance, oscillator stability, a 60–70 hour reserve, or production readiness. It does not select the chronograph architecture or authorize physical testing/build.

**Release statement:** WP-64 is a development-branch measurement and analysis framework. C-01 remains unfrozen and is not released for prototype manufacture. No physical build, test campaign, manufacturing release, merge or deployment is authorized by this work package.
