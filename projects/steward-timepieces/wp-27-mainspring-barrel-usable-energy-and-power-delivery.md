# WP-27 — Mainspring Barrel, Usable Energy and Power Delivery

- **Document ID:** SEB-C01-WP-27
- **Project:** STEWARD C-01
- **Revision:** A (initial controlled issue)
- **Status:** Measurement-driven engineering definition; no spring or barrel geometry selected
- **Branch:** `steward/c-01-movement-foundation`
- **Software:** `tools/c01_barrel_power.py`
- **Verification:** `tools/test_c01_barrel_power.py`
- **Dependencies:** WP-08, WP-09, WP-10, WP-13, WP-25 and WP-26

## 1. Purpose and scope

WP-27 defines the barrel-side energy source and the measurement framework required to establish whether the mainspring can deliver adequate torque and usable energy over the intended operating window.

It provides:
- torque-versus-angle curve integration;
- usable energy integration between explicitly approved operating endpoints;
- sampled torque-range characterization;
- ideal shaft power at a declared barrel interface;
- measured automatic-winding capture efficiency;
- matched chronograph stopped/running incremental-energy comparison;
- same-boundary energy accounting and idealized reserve extrapolation.

This package does not select a mainspring, barrel dimensions, spring material, bridle, arbor geometry, winding ratio, torque limits or power reserve. No numerical spring or barrel design values are inferred.

## 2. Functional energy chain

The intended functional path remains:

[
\text{Rotor} \rightarrow \text{winding works} \rightarrow
\text{mainspring/barrel} \rightarrow \text{going train} \rightarrow
\text{escapement and oscillator}
]

Chronograph and calendar mechanisms impose additional loads. The chronograph's incremental demand must be measured by paired stopped/running tests at the same measurement boundary and over the same interval. The calendar load must be measured over an interval long enough to capture its intermittent advance event, not inferred from an arbitrary short sample.

## 3. Torque-angle energy model

For measured spring torque (T(\theta)), the mechanical work over an angular interval is:

[
E=\int_{\theta_1}^{\theta_2}T(\theta)\,d\theta
]

WP-27 numerically integrates measured samples with the trapezoidal rule:

[
E\approx\sum_{i=1}^{N-1}
\frac{T_i+T_{i+1}}{2}(\theta_{i+1}-\theta_i)
]

Units are N·m, radians and joules. Angles must be strictly increasing and samples must describe one consistent loading or unloading branch. Loading and unloading curves should be measured separately if hysteresis is material; they must not be concatenated into one artificial curve.

The usable energy is the integral only between the approved operating start and end angles. The tool interpolates within the measured data range and refuses to extrapolate beyond it. The endpoints must ultimately be established by spring stress limits, barrel/bridle behavior, escapement torque requirements and validated running limits.

The sampled torque range is a descriptive statistic, not a continuous guaranteed minimum/maximum. A denser measured curve and uncertainty assessment are required for design acceptance.

## 4. Barrel output power

At a defined shaft interface, ideal instantaneous mechanical power is:

[
P=T\omega
]

where torque is N·m and angular speed is rad/s. This is an interface identity only. It does not account for transmission losses, changing torque, escapement impulses, friction or dynamic effects. A meaningful power map requires synchronized torque and speed measurements at the same shaft plane and operating state.

## 5. Winding capture and bridle

Automatic-winding capture efficiency is evaluated from measured rotor-side input energy and the measured increase in barrel stored energy over the same trial:

[
\eta_{wind}=\frac{\Delta E_{barrel}}{E_{rotor,input}}
]

Rotor revolutions and elapsed time are retained to compare test conditions. This is not a wrist-motion model and does not imply a wearer will supply a particular energy input.

Bridle slip onset must be measured against a separately approved maximum barrel torque. WP-27 does not derive that safe limit. The spring, barrel wall, bridle friction, lubrication and temperature all require physical validation.

## 6. Energy accounting and chronograph demand

For a defined interval and measurement boundary:

[
E_{margin}=E_{usable}-\sum_i E_{load,i}
]

[
P_{avg}=\frac{\sum_i E_{load,i}}{\Delta t}
\qquad
t_{ideal}=\frac{E_{usable}}{P_{avg}}
]

The ideal reserve extrapolation assumes the measured average load is representative over the full operating window. It is not a reserve test and must not be treated as a validated performance figure.

Every load record must share one boundary identifier and interval identifier. Component identifiers must be unique to prevent accidental double counting. A subsystem measurement that already includes another listed subsystem must not be added again. The test plan must distinguish baseline going-train/escapement demand from incremental chronograph and calendar loads.

For chronograph comparison, stopped and running cases must have matched duration, boundary and interval definition:

[
\Delta E_{chrono}=E_{running}-E_{stopped}
]

The incremental result may be negative within measurement uncertainty; the software preserves the measured sign rather than forcing a presumed positive penalty.

## 7. Required measurement programme

| Measurement | Method / instrument concept | Required evidence | Status |
|---|---|---|---|
| Spring torque-angle, winding branch | Calibrated torque transducer and angular encoder | Calibration, temperature, spring identity, repeatability | TBD |
| Spring torque-angle, unwinding branch | Same, controlled unwind | Hysteresis and repeatability | TBD |
| Operating endpoints | Approved spring/barrel/escapement limits | Signed engineering limit rationale | TBD |
| Barrel speed | Encoder at defined barrel/arbor plane | Synchronized speed trace | TBD |
| Barrel output torque | Calibrated torque measurement at declared plane | Calibration and uncertainty | TBD |
| Winding input energy | Instrumented rotor/winding rig | Defined input plane and interval | TBD |
| Stored-energy gain | Torque-angle state before/after winding | Same spring state definition | TBD |
| Bridle slip onset | Controlled torque ramp | Approved safe torque limit | TBD |
| Chronograph stopped/running | Paired complete movement trials | Matched boundary, interval and operating state | TBD |
| Calendar advance | Event-resolved measurement over complete advance cycle | Event energy and baseline separation | TBD |
| Reserve | Full wind, controlled run-down, defined stop criterion | Continuous trace and repeat trials | TBD |

## 8. Acceptance criteria

1. Torque-angle samples are calibrated, traceable, monotonic in angle and tied to one identified spring and test condition.
2. Usable-energy endpoints are explicitly approved and lie within the measured curve.
3. Energy integration uses documented units and a stated numerical method.
4. Barrel torque and speed are measured at a declared common interface before claiming output power.
5. Winding efficiency uses matched rotor input and barrel energy-gain intervals.
6. Bridle slip onset is below an independently approved safe maximum; the limit is not generated by this model.
7. Chronograph stopped/running measurements use matched boundary and duration.
8. Energy-budget loads are non-overlapping, unique and measured over the same interval and boundary.
9. Reserve estimates are labeled extrapolations until confirmed by full run-down testing.
10. The 60–70-hour aspiration is not accepted without complete movement reserve tests in specified operating states, including chronograph duty-cycle cases.

## 9. Interfaces to other work packages

- **WP-08:** rotor and winding architecture; bridle slip test method.
- **WP-09:** minimum torque/amplitude/rate operating envelope to be established experimentally.
- **WP-10:** going-train transmission and energy-transfer measurements.
- **WP-13:** common-boundary system energy accounting and double-counting controls.
- **WP-25/WP-26:** kinematic path and candidate gear geometry; no energy adequacy implied by ratio closure.

The barrel must supply the required torque across the full approved unwind window, not merely a sufficient total joule value. A large integrated energy value does not compensate for inadequate torque at the escapement input or an unacceptable torque profile.

## 10. Risks and unresolved decisions

| Risk / decision | Required resolution |
|---|---|
| Spring material, geometry and stress | Supplier data, stress analysis and fatigue testing |
| Barrel diameter, height and arbor | Envelope and detailed design evidence |
| Bridle type and slip behavior | Torque-limit derivation and repeatable slip testing |
| Torque decline over unwind | Measured curve and escapement operating envelope |
| Winding direction and reverser | WP-08 instrumented architecture comparison |
| Manual winding integration | Back-drive, clutch and serviceability verification |
| Chronograph energy penalty | Paired operating-state measurements |
| Calendar intermittent load | Event-resolved energy measurement |
| Reserve target | Complete movement run-down verification |

## 11. Verification

Run from the tools directory:

```sh
python -m unittest test_c01_barrel_power.py
```

The tests use synthetic curves and energy values only. They verify trapezoidal integration, in-range interpolation, refusal to extrapolate, shaft power, winding capture, matched chronograph comparison, same-boundary energy accounting and input validation. They do not represent measured C-01 hardware.

## 12. Revision control

| Revision | Date | Change | Approval |
|---|---|---|---|
| A | 2026-11-26 | Initial barrel torque-angle, usable-energy, winding capture and load-accounting model | Pending engineering review |

**Release gate:** no spring, barrel, bridle, torque limit, winding ratio, usable operating window or reserve claim is frozen by WP-27. No merge or deployment is authorized.
