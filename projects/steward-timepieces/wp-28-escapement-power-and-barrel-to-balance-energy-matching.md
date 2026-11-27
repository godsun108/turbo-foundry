# WP-28 — Escapement Power and Barrel-to-Balance Energy Matching

- **Document ID:** SEB-C01-WP-28
- **Project:** STEWARD C-01
- **Revision:** A (initial controlled issue)
- **Status:** Measurement-driven interface definition; no escapement or balance geometry selected
- **Branch:** `steward/c-01-movement-foundation`
- **Software:** `tools/c01_escapement_power.py`
- **Verification:** `tools/test_c01_escapement_power.py`
- **Dependencies:** WP-09, WP-10, WP-13, WP-25 and WP-27

## 1. Purpose

WP-28 defines the evidence required to match barrel/going-train power delivery to the escapement and regulating system over the usable reserve window. It complements WP-09's oscillator and timing checks and WP-27's barrel energy model without duplicating either.

The core engineering question is not simply whether the barrel contains enough total energy. It must deliver sufficient torque at the required operating speed at the escapement interface, across the full approved unwind range, while the balance maintains approved amplitude and rate.

## 2. Controlled design basis

- Nominal frequency target: **4 Hz / 28,800 vph**.
- Ideal full oscillation period at 4 Hz: **0.25 s**.
- Ideal half-period: **0.125 s**.
- The frequency target is not a selected balance inertia, hairspring stiffness, escapement tooth count or impulse convention.
- The preliminary rate objective of −4/+6 s/day remains unvalidated and is not automatically an acceptance limit for every test configuration.
- No numerical amplitude, beat-error, escapement torque, impulse energy or minimum power limit is selected in WP-28.
- The 60–70-hour reserve remains aspirational.

## 3. Interface power and torque envelope

At a declared shaft plane, ideal mechanical power is:

[
P=T\omega
]

WP-28 compares measured supplied and required torque and speed at the same declared interface and operating state. For each measured state:

[
\Delta T=T_{supplied}-T_{required}
]

[
\Delta P=T_{supplied}\omega_{supplied}
-T_{required}\omega_{required}
]

A state is only comparable when supplied and required speeds agree within an explicitly approved fractional tolerance. The model records speed mismatch, torque margin and ideal power margin independently. It does not treat a positive power margin as proof of adequate impulse shape, low friction, correct escapement lock, or stable amplitude.

The operating envelope must include multiple reserve states from full wind through the approved end-of-run condition. State identifiers, reserve-state fractions, measured torque and speed must be traceable to the same movement revision and test configuration.

## 4. Energy per measured balance/escapement event

For a measured energy total over an explicitly counted set of events:

[
E_{event,measured}=\frac{E_{measured}}{N_{measured\ events}}
]

The event count must come from the instrumented event definition and measurement protocol. WP-28 does not infer the number of pallet impulses, escape-wheel lock/release events or balance half-oscillations from frequency alone. The event boundary must state whether the measured energy is at the barrel, train, escape-wheel, pallet or balance interface.

This reduction is useful for comparing trials, but a single average does not characterize impulse waveform, peak torque, losses or amplitude response.

## 5. Balance amplitude and rate correlation

Amplitude and rate are measured outputs, not values calculated from a shaft power margin. WP-28 deliberately does not infer amplitude from torque, energy or power.

For each reserve state, the test record should include:
- reserve-state descriptor and elapsed run time from a documented full-wind condition;
- amplitude, rate, beat error and positional condition;
- barrel/going-train/escapement interface torque and speed where instrumentation permits;
- chronograph state and calendar event state;
- temperature, lubrication, orientation and measurement instrument details.

The existing WP-09 evaluator checks measured timing trials against explicit approved limits. The WP-28 reserve-state evaluator independently checks amplitude and rate across supplied measured reserve states. Neither tool invents acceptance limits or remaining-hours values.

## 6. Chronograph-on versus chronograph-off interaction

Paired trials must use the same movement revision, winding state, temperature, orientation, measurement boundary and interval definition. Record amplitude, rate and measured power in both states. Report the signed differences:

[
\Delta A=A_{chrono\ on}-A_{chrono\ off}
]

[
\Delta r=r_{chrono\ on}-r_{chrono\ off}
]

[
\Delta P=P_{chrono\ on}-P_{chrono\ off}
]

A chronograph can affect both energy demand and timekeeping. A measured power increase alone does not establish whether the amplitude or rate change is acceptable. The acceptance limits must be approved separately for the intended chronograph duty cycle.

## 7. Required measurement programme

| Measurement | Required method / evidence | Status |
|---|---|---|
| Barrel/going-train output torque | Calibrated transducer at named interface | TBD |
| Interface angular speed | Synchronized encoder at same plane | TBD |
| Escapement-side required torque/speed | Instrumented load or validated component test at same interface | TBD |
| Reserve-state envelope | Repeat measurements at documented wind states | TBD |
| Balance amplitude | Calibrated timing instrument, defined method | TBD |
| Rate and beat error | Timing instrument, defined positions and duration | TBD |
| Chronograph on/off | Paired matched trials | TBD |
| Energy per event | Integrated energy and directly counted events at named boundary | TBD |
| Calendar event interaction | Event-resolved trial with calendar baseline | TBD |
| End-of-run criterion | Approved minimum amplitude/rate/functional condition | TBD |

## 8. Acceptance criteria

1. Every torque/speed comparison identifies one physical measurement plane and traceable test configuration.
2. Supply and demand speeds match within a separately approved tolerance before their torque/power comparison is accepted.
3. Supplied torque and ideal power margins are non-negative at every required operating state, unless an approved transient/impulse model justifies a different criterion.
4. The complete required reserve-state range is measured; no extrapolation beyond measured states is presented as demonstrated capability.
5. Amplitude, rate and beat-error limits are explicitly approved for the movement revision and test method.
6. The 4 Hz target is verified by measured timing data, not inferred solely from nominal oscillator calculations.
7. Chronograph-on/off tests use matched boundary, interval and conditions; signed changes in amplitude, rate and power are retained.
8. Event-energy calculations use a directly documented event count and measurement boundary.
9. No shaft power or energy margin is represented as a substitute for a complete timing, amplitude, escapement and reserve test.
10. The final reserve claim requires a complete movement run-down test with defined end-of-run criteria and repeatability evidence.

## 9. Risks and unresolved engineering decisions

| Risk / decision | Evidence required |
|---|---|
| Minimum torque at escapement | Instrumented escapement and movement testing |
| Torque ripple and impulse waveform | Time-resolved torque measurement |
| Escapement architecture and event convention | WP-09 architecture study and prototype |
| Balance inertia and hairspring stiffness | Supplier or measured component data |
| Amplitude limits | Approved escapement/balance design basis and testing |
| Chronograph load penalty | Matched complete-movement trials |
| Positional and temperature sensitivity | Multi-position and temperature test matrix |
| End-of-run definition | Approved amplitude/rate/function threshold |
| Reserve performance | Full run-down tests, including chronograph duty cases |

## 10. Software verification

Run from the tools directory:

```sh
python -m unittest test_c01_escapement_power.py
```

Tests use synthetic fixtures only. They verify interface torque/power margins, speed mismatch detection, measured event-energy reduction, matched chronograph comparison, reserve-state amplitude/rate checks and invalid-input rejection. They do not represent measured C-01 hardware.

## 11. Revision control

| Revision | Date | Change | Approval |
|---|---|---|---|
| A | 2026-11-26 | Initial escapement power matching and reserve-state verification framework | Pending engineering review |

**Release gate:** no escapement torque, balance amplitude, impulse energy, gear ratio, minimum power, component geometry or reserve result is frozen by WP-28. No merge or deployment is authorized.
