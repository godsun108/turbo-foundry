# WP-SQ-06 — Conditional Going-Train Ratio Closure

- **Document ID:** SEB-C01-WP-SQ-06
- **Revision:** 0.1
- **Status:** Preliminary analytical closure; functional assumptions remain unapproved
- **Branch:** `steward/c-01-movement-foundation`
- **Dependencies:** WP-SQ-03, WP-SQ-04, WP-SQ-05, WP-18, WP-23, WP-25, WP-26, WP-38 and WP-39
- **Controlled calculation register:** `data/c01-square-going-train-ratio-constraints.csv`

## 1. Purpose and boundary

This study extracts the exact speed relationship implied by the current *conditional* display-arbor hypotheses. It is the first numerical closure of a portion of the square C-01 going train, not a tooth-count candidate and not a selected movement design.

The calculation reuses the existing exact-rational WP-25 kinematic model and the WP-18/WP-26 synthesis chain when approved inputs exist. It does not create a second gear solver.

No barrel-speed measurement, approved escapement interface, gear-system definition, arbor coordinates, center distances or tolerance inputs are currently available. Accordingly, this study does not assign tooth counts, module, gear dimensions, or an actual barrel-to-escapement ratio.

## 2. Conditional display boundary conditions

WP-SQ-03 and WP-SQ-05 identify two provisional roles:

- Center arbor: candidate direct minute-motion interface, one revolution per hour.
- Fourth arbor: candidate direct running-seconds source, one revolution per minute.

For a period-based speed target:

\[
n = \frac{60}{T}
\]

where (n) is revolutions per minute and (T) is seconds per revolution.

| Candidate arbor role | Period | Conditional target speed |
|---|---:|---:|
| Center / minute motion | 3,600 s/rev | 1/60 rpm |
| Fourth / running seconds | 60 s/rev | 1 rpm |

These are exact mathematical conversions of the stated display functions. They are not measured speeds, approved internal ratios, or proof that the proposed arbor roles are mechanically appropriate.

## 3. First closed relationship: center to fourth arbor

The conditional speed-magnitude ratio is:

\[
\left|\frac{n_{fourth}}{n_{center}}\right|
= \frac{1}{1/60}
= 60
\]

Therefore, if the working topology is retained and the center-to-third and third-to-fourth meshes are both external spur meshes, the compound gear relationship must satisfy:

\[
\frac{Z_{center\ wheel}}{Z_{third\ pinion}}
\times
\frac{Z_{third\ wheel}}{Z_{fourth\ pinion}}
= 60
\]

Here (Z) denotes the tooth count of the identified gear. The third wheel and third pinion are separate gears fixed to the same third arbor; their tooth counts are not assumed equal.

Two external meshes reverse direction twice. Under this specific topology, the fourth arbor rotates in the same direction as the center arbor. If mesh type or topology changes, direction must be recalculated rather than carried forward.

**What this establishes:** the two intermediate mesh ratios, multiplied together, must provide a 60:1 speed increase in magnitude if the two provisional direct-drive display roles are approved.

**What it does not establish:** any particular tooth-count combination, module, center distance, gear diameter, efficiency, torque, strength, backlash, manufacturability, or physical fit. Many mathematical factorizations may satisfy the equation; only a bounded and evidence-based engineering screen can distinguish viable candidates.

## 4. Unclosed relationships

### 4.1 Barrel to center

If the barrel arbor speed is (n_b), the required magnitude ratio under the direct minute-motion hypothesis is:

\[
\left|\frac{n_{center}}{n_b}\right|
= \frac{1}{60\,n_b}
\]

The barrel speed is a measured, load-dependent input and is not available as an approved C-01 value. The first mesh tooth ratio therefore remains open. A balance frequency target cannot be used as a substitute for barrel RPM.

### 4.2 Fourth to escape wheel

If the fourth wheel drives an escape-wheel pinion, a simple external mesh would have the conditional magnitude relationship:

\[
\left|\frac{n_{escape}}{n_{fourth}}\right|
= \frac{Z_{fourth\ wheel}}{Z_{escape\ pinion}}
\]

Neither tooth count nor the final escapement event convention is approved. The 4 Hz oscillator target alone does not determine escape-wheel RPM without the escapement architecture and event/impulse definition.

## 5. Numerical result and evidence classification

| Result | Value | Classification | Disposition |
|---|---:|---|---|
| Center target speed | 1/60 rpm | Derived from provisional functional hypothesis | Conditional |
| Fourth target speed | 1 rpm | Derived from provisional functional hypothesis | Conditional |
| Fourth/center speed magnitude | 60:1 | Derived conditional ratio | Partial closure only |
| Barrel/center ratio | Not calculable | Missing measured barrel speed | Open |
| Fourth/escape ratio | Not calculable | Missing escapement and gear definition | Open |
| Physical tooth schedule | Not generated | Missing approved inputs | Prohibited at this gate |

No synthetic tooth schedule is presented as C-01 data. No physical candidate is ranked or recommended.

## 6. Required next inputs and calculations

1. **Functional approval:** confirm that center and fourth arbors are direct-drive minute and running-seconds interfaces, respectively, and confirm the center→third→fourth path.
2. **Source characterization:** obtain traceable barrel speed under defined load and wind states, paired with WP-27/WP-66 torque-angle and source-test evidence.
3. **Escapement definition:** approve escapement type, escape-wheel tooth count, event convention, and the interface to WP-28.
4. **Gear-system basis:** approve module, pressure angle, tooth-form coefficients, profile-shift policy and manufacturing assumptions for every mesh.
5. **Geometry closure:** approve arbor coordinates and center-distance/tolerance inputs through WP-23 and related packaging work.
6. **Candidate synthesis:** use WP-18 for bounded integer tooth-pair enumeration, WP-26 for shared-gear consistency and candidate orchestration, WP-25 for exact signed speed closure, and WP-38/WP-39 for involute and gear-pair screening.
7. **Independent engineering checks:** assess undercut, interference, contact ratio, strength, fatigue, inertia, bearing loads, lubrication, losses, power and service access before any design recommendation.

Search bounds and result caps must be explicit. A truncated search must be reported as incomplete; the lowest mathematical ratio error is not automatically the best physical design.

## 7. Acceptance criteria

- The 1/60 rpm and 1 rpm boundary conditions are reproduced exactly from their stated periods.
- The conditional 60:1 center-to-fourth relationship is reproduced exactly.
- The compound ratio equation preserves separate wheel and pinion identities on the third arbor.
- Direction is stated only for the declared two-external-mesh topology.
- Barrel-to-center and fourth-to-escape ratios remain explicitly open.
- No tooth counts, dimensions, material, torque, efficiency, reserve, or performance values are invented.
- All assumptions remain hypotheses until approved by design authority.
- C-01 scope remains chronograph + weekday + date; month and moon phase remain assigned to LUNAR.

## 8. Conclusion

We have closed one meaningful mathematical relationship: **under the current direct-display hypotheses, the fourth arbor must run 60 times faster than the center arbor.** The two intermediate meshes must collectively produce that ratio. This is a real constraint for later synthesis, but it is not yet a gear train.

The next legitimate step toward a numerical tooth schedule is not guessing tooth counts. It is obtaining the barrel and escapement inputs, then running a bounded WP-18/WP-26 search and checking every candidate through WP-25, WP-38 and WP-39.

## 9. Revision control

| Revision | Change | Disposition |
|---|---|---|
| 0.1 | Establishes exact conditional display speeds and center-to-fourth compound ratio closure | Preliminary; functional assumptions and all physical design inputs remain open |

**Disposition:** No gear schedule selected. No design freeze, physical test, manufacture, merge or deployment is authorized.
