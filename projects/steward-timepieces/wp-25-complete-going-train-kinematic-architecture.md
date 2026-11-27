# WP-25 — Complete Going-Train Kinematic Architecture and Ratio Closure

- **Document ID:** SEB-C01-WP-25
- **Project:** STEWARD C-01
- **Revision:** A (initial controlled issue)
- **Status:** Kinematic integration method; no C-01 tooth schedule or train selected
- **Branch:** `steward/c-01-movement-foundation`
- **Software:** `tools/c01_going_train.py`
- **Verification:** `tools/test_c01_going_train.py`
- **Dependencies:** WP-10, WP-15, WP-17, WP-18, WP-20, WP-23 and WP-24

## 1. Purpose and scope

WP-25 defines an exact-rational model for evaluating a candidate going train as a connected set of arbors, gears fixed to arbors, and gear meshes. It addresses the missing link between isolated ratio calculations and a complete, traceable shaft-to-shaft kinematic path.

The package:
- represents each arbor as a rotating shaft;
- represents each wheel or pinion as a gear attached to exactly one arbor;
- represents external/internal meshes as connections between gears on different arbors;
- calculates exact compound speed ratio and direction along a unique path;
- compares explicitly supplied output targets against explicitly supplied input speed;
- refuses to choose when no path or multiple paths exist;
- provides a conditional escapement-rate relationship only when the event convention is explicitly supplied.

It does not choose a physical train, tooth counts, module, barrel speed curve, escapement geometry, chronograph take-off, or display architecture.

## 2. Coordinate and functional baseline

The functional going-train hypothesis remains:
`barrel → center → third → fourth/seconds → escape wheel → escapement`

This sequence is a topology hypothesis, not a selected physical gear schedule. The balance is the regulating oscillator and is not modeled as a downstream gear wheel.

The model's arbor, gear and mesh IDs must map to controlled WP-20 component and WP-21/WP-23 arbor/axis registers. WP-23 provides coordinate and nominal center-distance methods; WP-24 provides support/member traceability. WP-25 adds exact path closure, not another geometry solver.

## 3. Kinematic definitions

For gear (i) driving gear (j), the signed ideal speed ratio is:
[
R_{ij}=\frac{n_j}{n_i}=
\begin{cases}
-\frac{z_i}{z_j}, & \text{external mesh}\\
+\frac{z_i}{z_j}, & \text{internal mesh}
\end{cases}
]

Gears rigidly fixed to the same arbor have identical angular speed. For a connected path of (N) meshes:
[
R_{total}=\prod_{k=1}^{N}R_k,\qquad n_{out}=n_{in}R_{total}
]

For a display making one revolution every (T) seconds:
[
n_{target}=\frac{60}{T}\quad\mathrm{rpm}
]

The fractional absolute speed error is:
[
e_{abs}=\frac{\left||n_{actual}|-n_{target}\right|}{n_{target}}
]

The implementation uses exact rational arithmetic for ratios and error. Direction is retained independently of speed magnitude.

## 4. Shaft, gear and mesh representation

### 4.1 Arbor register

Each arbor has a unique ID, role, evidence and source revision. The register should be cross-referenced to WP-20 component IDs and WP-21 axis IDs in the controlled candidate data. The WP-25 calculation schema keeps its minimum inputs explicit and does not fabricate coordinates.

### 4.2 Gear register

Each gear has a unique ID, positive integer tooth count, arbor ID, functional role, evidence and source revision. A wheel and pinion rigidly coupled on one arbor are represented as separate gear records sharing the same arbor ID.

### 4.3 Mesh register

Each mesh declares driver gear, driven gear, mesh type, evidence and source revision. A mesh cannot connect two gears on the same arbor. External meshes reverse direction; internal meshes preserve direction under the adopted signed convention.

### 4.4 Path closure

The path evaluator searches arbor-level directed connections. A unique source-to-target path is required for a determinate result. It reports:
- `no_path` if the output is not connected;
- `multiple_paths` if more than one directed path exists;
- `unique_path` with exact ratio and direction otherwise.

This avoids arbitrarily selecting one branch in an ambiguous graph. The evaluator guards against cycles during path search. It does not prove that the represented topology is physically assemblable.

## 5. Display speed requirements

These are functional display requirements, not a chosen train:

| Function | Period | Target speed |
|---|---:|---:|
| Running seconds | 60 s/rev | 1 rpm |
| Central chronograph seconds | 60 s/rev | 1 rpm |
| Minute hand | 3,600 s/rev | 1/60 rpm |
| Hour hand | 43,200 s/rev | 1/720 rpm |
| 30-minute totalizer, continuous convention | 1,800 s/rev | 1/30 rpm |
| 12-hour totalizer, continuous convention | 43,200 s/rev | 1/720 rpm |

Chronograph outputs remain separate from the going-train baseline. Their drive source, clutch, and totalizer branch must be evaluated as a distinct candidate path and reconciled with WP-16/WP-17.

## 6. Escapement and 4 Hz relationship

The 4 Hz / 28,800 vph oscillator target remains a preliminary C-01 target from WP-09. It does not by itself determine escape-wheel RPM. A conditional relationship requires:
- balance cycles per second;
- the explicitly defined number of relevant balance events per cycle;
- the explicitly defined lock/release events per escape-wheel revolution.

For supplied definitions:
[
n_{escape}=60\times\frac{f_{balance}\,b}{L}
]
where (b) is balance events per cycle and (L) is lock/release events per escape-wheel revolution. The tool does not assume a convention for either count. Escape-wheel tooth count alone is not enough to determine (L).

This relationship is a kinematic bookkeeping aid only; pallet geometry, impulse, locking, drop, safety, amplitude and rate must be resolved in the escapement design and test programme.

## 7. Input and evidence requirements

| Input | Required evidence | Current C-01 status |
|---|---|---|
| Barrel arbor speed | Measured/approved barrel speed vs wind state | TBD |
| Gear tooth counts | Controlled wheel/pinion design | TBD |
| Arbor/gear coupling | Assembly and shaft definition | TBD |
| Mesh type and direction | Gear pair definition | TBD per mesh |
| Going-train path | Approved topology and component mapping | Hypothesis only |
| Display target periods | Functional display requirements | Defined as above |
| Speed tolerance | Approved rate/indication error budget | TBD |
| Escape event convention | Escapement geometry and event definition | TBD |
| Module/center distance | Controlled gear geometry | TBD |
| Chronograph take-off | Approved WP-16/WP-17 architecture | Open |

No input defaults to a fabricated design value.

## 8. Acceptance criteria

1. Arbor, gear and mesh IDs are unique and all references resolve.
2. Gear tooth counts are positive integers; gear mesh type is explicit.
3. No mesh connects gears on the same arbor.
4. Each evaluated source/target pair has exactly one directed path.
5. Compound ratios are calculated exactly and direction is retained.
6. Output speed comparisons use explicit source RPM and target period.
7. A speed tolerance is only applied when explicitly supplied and approved.
8. No-path and multiple-path conditions remain unresolved, not silently selected.
9. Escapement speed is evaluated only with an explicit event convention.
10. All candidate values have evidence and source revision before design review.

Passing these criteria establishes kinematic consistency of the declared graph only. It does not establish physical gear mesh, torque capacity, efficiency, timekeeping accuracy or manufacturability.

## 9. Verification

Run from the tools directory:
```sh
python -m unittest test_c01_going_train.py
```

The tests cover exact target speeds, compound ratio and direction, no-path and multiple-path behavior, same-arbor mesh rejection, target comparison, absent tolerance handling and conditional escapement event arithmetic. All numeric tooth counts and input speeds in tests are synthetic fixtures, not C-01 design values.

## 10. Limitations and next evidence

Not included: tooth-form design, undercut, contact ratio, profile shift, backlash, center-distance tolerance, wheel inertia, torque curve, losses, lubrication, wear, bearing loads, dynamic response, balance amplitude, rate, power reserve or CAD interference. Those remain in WP-10, WP-18, WP-19, WP-23, WP-24 and future detailed design/test packages.

The next engineering gate is a controlled candidate tooth schedule and barrel/escapement input evidence, reconciled with WP-23 XY constraints and WP-24 support/CAD handoff. No C-01 train is selected by WP-25.

## 11. Revision control

| Revision | Date | Change | Approval |
|---|---|---|---|
| A | 2026-11-26 | Initial exact-ratio going-train graph, path closure, tests and controlled document | Pending engineering review |

**Release gate:** no gear schedule, barrel input speed, escapement relationship, chronograph take-off or train architecture is frozen until its evidence, geometry, tolerance basis and engineering approvals are recorded. No merge or deployment is authorized by this work package.
