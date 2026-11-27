# STEWARD C-01 — WP-17 Chronograph Gear Train and Counter Kinematics

**Document ID:** C01-WP-17  
**Revision:** 0.1  
**Status:** Kinematic calculation framework; no train or counter architecture selected  
**Branch:** `steward/c-01-movement-foundation`  
**Predecessors:** WP-10 Gear Train; WP-11 Chronograph Mechanism; WP-15 Gear-Train Topology; WP-16 Chronograph Architecture  
**Next gate:** approved chronograph source member and speed, counter indication convention, measured load inputs, and reviewed candidate train geometry

## 1. Purpose and boundary

WP-17 converts the chronograph display requirements into an executable, exact-ratio kinematic framework. It answers: given a measured or otherwise approved source speed and explicit gear data, what output speed and direction result?

It does **not** select a drive take-off, tooth count, module, center distance, counter indexing mechanism, clutch, material, tolerance, or efficiency. Correct kinematics do not establish torque capacity, energy sufficiency, packaging, durability, manufacturability, or rate performance.

The existing gear-train worksheet and WP-15 topology register remain authoritative context; this package adds a calculator and an explicit counter-convention decision framework without replacing them.

## 2. Controlled output conventions

| Function | Period per revolution | Required average speed | Status |
|---|---:|---:|---|
| Central chronograph seconds | 60 s | 1 rpm | Functional display requirement |
| 30-minute totalizer, continuous convention | 1,800 s | 1/30 rpm | Conditional on continuous one-revolution convention |
| 12-hour totalizer, continuous convention | 43,200 s | 1/720 rpm | Conditional on continuous one-revolution convention |

The central seconds hand is required to make one revolution per elapsed minute while engaged. The totalizer periods are the existing worksheet's conventional one-revolution indications; WP-17 does not convert that convention into a final mechanism decision.

### Counter convention decision

For both elapsed-minute and elapsed-hour displays, retain two candidates:

- **Continuous:** the register hand rotates continuously at the required average speed.
- **Jumping/indexed:** the register advances by a discrete angular step at an explicitly defined event cadence.

A jumping register cannot be completely specified by an average RPM alone. It requires event cadence, divisions per revolution, step angle, drive/release sequence, jumper force, overshoot control, and transient load measurement. No event cadence, step count, or step angle is selected for C-01 here.

## 3. Governing equations

For a simple gear pair:

[
\frac{n_{out}}{n_{in}} =
\begin{cases}
-\frac{z_{driver}}{z_{driven}}, & \text{external mesh}\\
+\frac{z_{driver}}{z_{driven}}, & \text{internal mesh}
\end{cases}
]

where (n) is signed rotational speed and (z) is the positive integer tooth count.

For a sequence of gear meshes on correctly defined shafts:

[
R_{total}=\prod_{k=1}^{N} R_k,
\qquad n_{out}=n_{in}R_{total}
]

Compound wheels fixed to a common arbor share the same angular speed. A compound train is represented by consecutive mesh stages, with the intermediate driven wheel and next driver rigidly coupled on the same arbor. Idlers and internal meshes must be represented as their own stages; direction is never inferred from ratio magnitude alone.

For a target display period (T) seconds per revolution:

[
n_{target}=\frac{60}{T}\quad\text{rpm}
]

Given an approved input speed (n_{in}), the required magnitude ratio is:

[
|R_{required}|=\frac{n_{target}}{|n_{in}|}
]

For a supplied actual output speed, fractional speed error is:

[
e=\frac{|n_{actual}|-n_{target}}{n_{target}}
]

A tolerance comparison is only meaningful when an approved tolerance is supplied. The calculator does not assign one.

For an indexed counter with (N) divisions per revolution:

[
\Delta\theta=\frac{360^\circ}{N}
]

For (f) indexing events per hour:

[
t_{event}=\frac{3600}{f}\quad\text{seconds}
]

These equations define the display kinematics. They do not calculate jumper dynamics or the energy needed to accelerate the register.

## 4. Source-speed dependency

The central chronograph seconds output target is 1 rpm. This does not prove that the fourth wheel, another going-train wheel, or a dedicated chronograph take-off is the final source. WP-15 retains the fourth-wheel take-off and dedicated-drive candidates.

Before any C-01 ratio schedule is approved, record:
- named source wheel/arbor and its interface drawing/revision;
- measured or supplier-confirmed source RPM and direction;
- operating-state range and measurement method;
- available torque over the operating range;
- clutch interface and engagement state;
- evidence reference and approval.

Do not back-solve an assumed source RPM from the 4 Hz balance frequency alone. Escape-wheel speed also depends on escapement geometry and tooth count.

## 5. Counter kinematic definition

The central seconds drive and totalizer drives must be separated in the train diagram. For continuous counters, derive their average speeds from the selected source and explicit stage ratios. For jumping counters, document the event source and index step separately.

| Parameter | 30-minute register | 12-hour register |
|---|---|---|
| Display range | 0–30 elapsed minutes | 0–12 elapsed hours |
| Continuous convention | 1 rev / 30 min | 1 rev / 12 h |
| Jumping convention | Cadence and step TBD | Cadence and step TBD |
| Drive take-off | TBD | TBD |
| Index wheel / star | TBD | TBD |
| Jumper / spring | TBD | TBD |
| Reset-to-zero interface | Heart cam / hammer interface TBD | Heart cam / hammer interface TBD |
| Transient torque evidence | Required | Required |
| Architecture decision | Open | Open |

Do not assume the two registers use the same indexing cadence or mechanism. Their displayed ranges, event timing, drive ratios, and reset loads may differ.

## 6. Executable model

Files:
- `tools/c01_chrono_kinematics.py`
- `tools/test_c01_chrono_kinematics.py`

Capabilities:
- exact rational speed ratios using integer tooth counts;
- external and internal mesh direction handling;
- compound-path ratio and output RPM;
- required ratio derived from an explicitly supplied source RPM and target period;
- output speed comparison against an explicitly supplied tolerance;
- indexed-counter event interval and angular-step calculation from explicit inputs;
- continuous-versus-jumping counter trade register.

The model rejects missing/invalid tooth counts, nonpositive source speeds and periods, unsupported mesh types, and noninteger counter event/division inputs. It does not infer gear geometry or create design data from test fixtures.

### Verification command

From `projects/steward-timepieces/tools`:

```bash
python -m unittest test_c01_chrono_kinematics.py
```

The unit tests use synthetic arithmetic fixtures solely to test formulas, signs, validation and exact fractions. Those fixture values are not C-01 component selections.

## 7. Acceptance criteria

| ID | Acceptance criterion | Evidence |
|---|---|---|
| WP17-KIN-01 | External mesh produces opposite rotation; internal mesh preserves direction | Unit tests and independent calculation |
| WP17-KIN-02 | Compound ratios multiply exactly without floating-point drift | Fraction-based unit tests |
| WP17-KIN-03 | Output RPM is derived only from supplied source RPM and tooth counts | Model input/output review |
| WP17-KIN-04 | Required ratio is derived from source RPM and target period | Unit test and reviewed worksheet |
| WP17-KIN-05 | Counter index angle and cadence require explicit inputs | Validation tests |
| WP17-KIN-06 | Continuous and jumping counter candidates remain distinct and unselected | Document and model review |
| WP17-KIN-07 | No C-01 tooth counts, source speed, indexing cadence, tolerance or efficiency are invented | Design-data audit |
| WP17-KIN-08 | Every candidate path has a traceable source, direction, interface and evidence record before design freeze | Reviewed train schedule |

## 8. Engineering risks and controls

| Risk | Consequence | Control / evidence required |
|---|---|---|
| Wrong source RPM assumption | Incorrect register speed | Verify actual source arbor and speed |
| Compound-arbor ambiguity | Incorrect calculated ratio | Shaft-level train diagram and common-arbor register |
| Direction error | Reversed indication | Signed ratio and dial-direction check |
| Treating jumping counter as continuous | Missing transient torque and indexing behavior | Separate event/step model and physical test |
| Ratio accepted without torque analysis | Stalling, slip or rate disturbance | WP-10 energy/torque measurements |
| Kinematic fit mistaken for physical fit | Interference or unbuildable layout | CAD, tolerance stack and prototype checks |
| Reset interaction omitted | Nonzero return or damage | WP-16 reset sequence and repeatability test |

## 9. Required next evidence and decisions

1. Approve the chronograph take-off candidate only after source-speed and torque evidence is available.
2. Resolve whether each totalizer is continuous or jumping, using the intended dial convention and readability mock-ups.
3. Define the event source and cadence for any jumping counter.
4. Populate candidate train stages from a dimensioned and traceable wheel layout.
5. Independently verify ratios, directions, arbor coupling and hand periods.
6. Evaluate torque, mesh losses, indexing transients, clutch drag and amplitude change under matched tests.
7. Complete CAD checks for center distance, tooth geometry, interference, endshake, backlash and service access.
8. Freeze the train only after kinematic, energy, packaging and service reviews are approved.

## 10. Revision control

| Revision | Date | Change | Status |
|---|---|---|---|
| 0.1 | 2026-11-26 | Initial WP-17 kinematic model, tests, equations, counter convention comparison and evidence gates | Preliminary; review required |

## 11. Current decision status

- Central chrono seconds target: **1 revolution/minute**.
- Continuous totalizer reference speeds: **defined conditionally by display convention**.
- Source wheel and source speed: **not selected / not verified**.
- Gear tooth counts and train ratios: **not selected**.
- 30-minute register continuous vs jumping: **open**.
- 12-hour register continuous vs jumping: **open**.
- Indexing cadence, step angle and jumper design: **not selected**.
- Torque, transient loads and rate impact: **not measured**.
- CAD, prototype and production design: **not complete**.

---
**Engineering integrity statement:** WP-17 is an executable ideal-kinematics framework and decision package. It is not a final chronograph train, dimensioned mechanism, torque proof, CAD model, manufacturing specification or validated movement.
