# STEWARD C-01 — WP-63 Chronograph Power Train and Counter Mechanism Detailed Design

- **Document ID:** SEB-C01-WP-63
- **Revision:** A — initial controlled issue
- **Status:** Parametric engineering definition; no C-01 train, source arbor or counter architecture selected
- **Branch:** `steward/c-01-movement-foundation`
- **Calculation model:** `tools/c01_chrono_power_train.py`
- **Synthetic regression tests:** `tools/test_c01_chrono_power_train.py`
- **Dependencies:** WP-17, WP-18, WP-25, WP-26, WP-27 through WP-30, WP-34, WP-37 through WP-41, WP-61 and WP-62

## 1. Purpose

WP-63 advances the chronograph from functional component definition into an integrated, evidence-gated power-train and counter-mechanism engineering definition. It establishes:

1. the going-train take-off interface and drive path to the central chronograph seconds indication;
2. the separate elapsed-minute and elapsed-hour counter branches;
3. continuous versus jumping counter calculation boundaries;
4. stopped-state retention, start/stop/resume/reset behavior and the running-reset interlock;
5. torque, power and energy measurement interfaces; and
6. calculation, verification and design-release gates.

This package is a calculation and design-definition framework. It is not a selected C-01 physical design, a completed gear schedule, a validated energy budget or a manufacturing release.

## 2. Controlled functional targets and unresolved decisions

| Function | Functional convention | Status |
|---|---|---|
| Central chronograph seconds | 1 revolution per 60 seconds = 1 rpm | Required target |
| Elapsed-minute totalizer | 1 revolution per 1,800 seconds = 1/30 rpm, if a 30-minute continuous register is chosen | Conditional convention |
| Elapsed-hour totalizer | 1 revolution per 43,200 seconds = 1/720 rpm, if a 12-hour continuous register is chosen | Conditional convention |
| Source arbor | Approved going-train take-off and measured/approved speed | Open |
| Minute counter | Continuous or jumping/indexed | Open |
| Hour counter | Continuous or jumping/indexed | Open |
| Counter branch source | Central seconds arbor, intermediate arbor or other approved take-off | Open |
| Stopped retention | Brake, detent or equivalent | Open |
| Clutch and control | WP-16/WP-33/WP-45 candidate decisions | Open |
| Reset hammers | Common or separate | Open |

The stated minute/hour periods describe conventional continuous indication only. They do not prescribe a dial layout, hand revolution count, jump interval, number of register divisions or counter mechanism.

## 3. Power-path architecture

The functional path boundary is:

**Going-train source arbor → approved take-off → coupling/clutch → central chronograph seconds arbor → minute and hour counter branches.**

The source arbor remains unresolved. The fourth-wheel/seconds-arbor take-off and a dedicated-drive alternative remain candidates from the prior work. The source speed must be measured or approved for the defined movement configuration and operating condition. Balance frequency alone must not be treated as a source-arbor RPM.

### 3.1 Central seconds drive

The central seconds target is 1 rpm. For a supplied source speed (n_s), the required ideal speed-ratio magnitude is:

\[
|R|=\frac{1\ \mathrm{rpm}}{n_s}
\]

For an explicitly declared ordered spur-gear path:

- external mesh: signed stage ratio (R_i=-z_{driver}/z_{driven});
- internal mesh: signed stage ratio (R_i=+z_{driver}/z_{driven});
- compound path: (R=\prod_i R_i);
- output speed: (n_o=n_sR).

The WP-63 model retains exact rational arithmetic for ideal speed ratios and reports direction separately. Every stage requires explicit positive integer tooth counts, mesh type, evidence ID and source revision. No tooth counts or source RPM are supplied as C-01 defaults.

The central seconds branch must be checked against an approved fractional speed tolerance when one exists. A zero tolerance in a synthetic software fixture is not a C-01 acceptance limit.

### 3.2 Candidate drive topologies

The following are topology families to investigate, not selected alternatives:

- **Direct central-seconds take-off:** source drives a clutch/coupling and central seconds path, with counter branches downstream.
- **Intermediate chronograph drive arbor:** source drives a dedicated arbor; central seconds and totalizer branches are taken from that arbor.
- **Counter branches from central seconds:** each totalizer derives its motion from the central chronograph seconds arbor.
- **Counter branches from an intermediate arbor:** one or both totalizers are driven from a distinct intermediate member to improve packaging or ratio closure.

Each candidate must identify physical arbors, gears fixed to each arbor, mesh relationships, direction, support references, bearing interfaces, axial layer, and source evidence. The same physical gear cannot be assigned incompatible tooth counts or incompatible rigid-arbor speeds in one configuration. WP-25/WP-26 remain the governing kinematic and candidate-synthesis references; WP-23/WP-24/WP-40 govern coordinate/support handoff.

## 4. Counter branch engineering

Minute and hour branches are evaluated independently. Each branch needs its own source member, output period or indexing convention, transmission path, arbor, support, hand interface, reset datum, stopped-state behavior and evidence.

### 4.1 Continuous counter

For a continuous register with one revolution per period (T):

\[
n_{target}=\frac{60}{T}\ \mathrm{rpm}
\]

The ideal branch ratio is the target speed divided by the explicitly supplied branch-source speed. Continuous rotation allows average-speed kinematics to define the nominal indication rate, but it does not establish friction, torque margin, backlash, hand inertia, reset drag or rate disturbance.

### 4.2 Jumping/indexed counter

A jumping register is not fully defined by its average RPM. It additionally requires:

- events per hour and event interval;
- divisions per revolution and angular step;
- event phase relative to the central seconds/elapsed-time datum;
- storage and release of indexing energy;
- jumper spring behavior and holding torque;
- anti-bounce/overshoot behavior;
- indexing completion under worst-case measured load;
- transient torque at the driving interface;
- reset interaction and zero-position repeatability.

For explicit events per hour (N_e) and divisions per revolution (N_d):

\[
t_e=\frac{3600}{N_e}\ \mathrm{s},\qquad
\Delta\theta=\frac{360^\circ}{N_d}
\]

These are event-cadence descriptors only. WP-63 does not infer indexing torque, spring energy, acceleration, impulse, contact stress or dynamic power. Those require measured or validated dynamic inputs and a physical mechanism model. A jumping counter's instantaneous load must not be replaced by its average-speed ratio.

### 4.3 Counter selection evidence

Continuous and jumping candidates must be compared using the same requirements and test boundary. Required evidence includes indication readability, phase accuracy, steady running load, indexing transient load, amplitude/rate effect, reset repeatability, overshoot/bounce, wear, serviceability, packaging and manufacturability. No winner or counter mode is selected by WP-63.

## 5. Clutch, stopped retention and reset interfaces

The selected clutch must transmit the required chronograph train load when engaged and minimize unintended drag when disengaged. Candidate clutch alternatives and control-system selection remain under WP-16/WP-33/WP-45. WP-63 does not select a vertical friction clutch or horizontal/lateral coupling.

Stopped-state retention must preserve elapsed indication after stop while preventing unintended hand movement. The retention implementation remains brake/detent/equivalent open. Its holding torque, release timing, wear and interaction with the clutch and reset mechanism require explicit geometry and physical test evidence.

The required functional sequence remains:

1. stopped at zero → start → running;
2. running → stop → stopped with elapsed time retained;
3. stopped with elapsed time retained → resume → running;
4. stopped with elapsed time retained → reset → stopped at zero;
5. reset command while running must be physically blocked and must leave the chronograph running.

The software state validator checks declared command/result sequences only. A test ID is a traceability reference, not proof of a successful physical interlock. Direct physical verification remains mandatory under WP-30/WP-46/WP-52/WP-53.

## 6. Torque, power and energy interfaces

WP-63 deliberately separates ideal kinematics from energy evidence.

### 6.1 Shaft power

For an explicitly measured or approved shaft torque (\tau) and rotational speed (n):

\[
P=\tau\omega=\tau\frac{2\pi n}{60}
\]

where torque is in N·m, speed is in rpm and power is in watts. The calculation helper records evidence ID and source revision. It does not estimate torque from tooth counts, infer efficiency, or treat an unmeasured value as a C-01 result.

### 6.2 Load aggregation

Measured load records may be summed only when they share:
- the same explicitly declared measurement boundary;
- the same measurement interval;
- the same source/configuration revision;
- unique load IDs; and
- evidence references for every load.

Duplicate IDs are rejected to prevent double counting. Loads measured at different interfaces or over unmatched intervals must not be combined into a single power budget. WP-27 through WP-29 remain authoritative for barrel energy, matched-boundary load comparisons and reserve-state evidence.

### 6.3 Required measurement points

The future instrumented prototype should define traceable measurement interfaces for:
- source/take-off speed and available torque;
- clutch input/output speed and torque or validated load proxy;
- central chronograph seconds drive load;
- minute and hour branch steady load;
- jumping-counter transient torque/energy, if applicable;
- stopped-retention holding and release behavior;
- reset work and post-reset residual drag;
- movement amplitude/rate with chronograph off, running, indexing and reset conditions.

Instrument, sensor, calibration, sample rate, uncertainty, boundary and test-condition selections remain controlled inputs. No measurement values or instrument models are populated here.

## 7. Calculation model and input contract

The WP-63 module provides:

- exact rational signed gear-path ratio and output speed;
- continuous output speed and comparison to an explicitly supplied target period/tolerance;
- explicit jumping-counter event interval and angular step;
- measured/approved torque-speed shaft-power calculation;
- matched-boundary load aggregation with duplicate-load rejection;
- logical chronograph operating-sequence validation; and
- an integrated input contract for source, central-seconds path and counter branches.

The integrated input identifies the source arbor and RPM explicitly. Each continuous branch supplies ordered gear stages and its target period. Each jumping branch supplies its period convention, events per hour and divisions per revolution. All gear stages require evidence and source revision.

The model's result flags remain false for source-arbor selection, counter-mode selection and physical-train selection. It does not call WP-39 optimization automatically, fabricate optimization bounds, or treat a numerically closed ratio as a physically acceptable gear train.

## 8. Verification plan and acceptance criteria

| Verification item | Method | Acceptance basis |
|---|---|---|
| Source identity and speed | Trace source arbor to controlled drawing and measure speed under defined condition | Approved source configuration and uncertainty |
| Central seconds ratio | Exact rational calculation plus measured output speed | 1 rpm functional target and approved tolerance |
| Direction and phase | Direction observation and phase/datum inspection | Approved dial and hand convention |
| Counter branch ratio | Exact rational calculation and measured output | Approved continuous indication convention |
| Jumping cadence/step | Event timing and angular measurement | Approved event phase, interval and step |
| Jumping transient | Instrumented torque/energy and motion capture | Approved dynamic load and completion limits |
| Clutch engagement/disengagement | Start/stop load and drag test | Approved disturbance and drag limits |
| Stopped retention | Hold, stop, resume and drift test | Approved retention and repeatability limits |
| Reset | Zero error, reset work, contact sequence and repeated cycles | Approved zero and repeatability limits |
| Running-reset interlock | Direct physical attempt under controlled test | Reset positively blocked; train remains running |
| Energy/load budget | Matched-boundary measured data | WP-27 through WP-30 approved limits |
| Durability/service | Endurance, wear and service procedure | Approved life and serviceability requirements |

No numerical acceptance limits are created by this package. The software regression fixtures are synthetic examples only and are not C-01 design data. Test definitions, instrument calibration, uncertainty and design-authority approval remain prerequisites.

## 9. Synthetic regression coverage

The test module includes synthetic cases for:
- central seconds exact ratio closure;
- compound path ratio and direction;
- internal mesh direction;
- missing provenance and invalid mesh rejection;
- a conditional continuous minute-register ratio;
- explicit jumping cadence and step;
- shaft-power calculation from explicit torque and speed;
- matched-boundary load aggregation and duplicate rejection;
- stopped/running/retained/reset state transitions;
- running-reset interlock reference and state preservation; and
- integrated central-seconds plus continuous/jumping branch analysis.

These fixtures are code-validation data only. This document does not claim that the test suite has been executed.

Run from the tools directory:

```bash
python -m unittest test_c01_chrono_power_train.py
```

## 10. Open decisions and required next evidence

The following remain open:
1. approved going-train source arbor and take-off;
2. measured/approved source speed and available torque under defined conditions;
3. direct versus intermediate chronograph drive topology;
4. central seconds drive tooth schedule and physical geometry;
5. minute and hour counter branch source members;
6. continuous versus jumping convention for each counter independently;
7. counter event cadence, phase, divisions and transient-load design if jumping;
8. stopped-retention mechanism;
9. clutch and control architecture;
10. reset hammer arrangement and heart-cam geometry;
11. bearing/support geometry, axial stack and case/dial interfaces;
12. materials, lubrication, manufacturing processes and tolerances;
13. approved performance limits and verification procedures.

Next engineering work should obtain controlled source-arbor speed/load evidence and make an explicit counter-indication decision before populating candidate gear schedules. Any candidate schedule must then be passed through WP-18/WP-26/WP-37/WP-38/WP-39 and WP-40 geometry, contact, support and tolerance reviews.

## 11. Release boundary

WP-63 does not establish physical gear contact, tooth strength, efficiency, friction, wear life, bearing life, dynamic indexing behavior, energy reserve, amplitude/rate performance, shock resistance, serviceability, manufacturability or safety. It does not select a source arbor, gear topology, tooth schedule, counter mode, clutch, control system or retention mechanism.

**Release statement:** WP-63 is a development-branch engineering calculation and definition package. C-01 remains unfrozen and not released for prototype manufacture. No physical build, test campaign, manufacturing release, merge or deployment is authorized by this work package.
