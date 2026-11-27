# WP-39 — Gear Pair Optimization and Chronograph Train Selection

- **Document ID:** SEB-C01-WP-39
- **Revision:** A — initial controlled issue
- **Status:** Integrated analytical candidate ranking; no C-01 train selected
- **Branch:** `steward/c-01-movement-foundation`
- **Software:** `tools/c01_gear_train_optimization.py`
- **Verification:** `tools/test_c01_gear_train_optimization.py`
- **Dependencies:** WP-18, WP-23, WP-25, WP-26, WP-30, WP-32, WP-37 and WP-38

## 1. Purpose

WP-39 integrates bounded integer tooth-pair enumeration with involute gear geometry and external mesh screening into a shared-gear-consistent ordered train candidate workflow. It ranks candidates against explicitly supplied ratio and geometric screening constraints. It does not select a final C-01 gear train.

## 2. Scope

Supported: ordered multi-mesh external spur gear trains. A gear ID reused across consecutive meshes must retain one tooth count and one arbor assignment. Every gear requires explicit module, pressure angle, addendum/dedendum coefficients, profile shift and provenance. Each mesh requires explicit tooth search bounds, stage-ratio bounds and error limit. Overall ratio target and overall error bound are mandatory.

Optional center-distance evaluation requires explicit center distance and tolerance. Optional contact-ratio threshold is only evaluated when supplied. Missing coordinates/tolerance are reported as not evaluable, never treated as pass.

## 3. Candidate synthesis and exact ratio

WP-18 pair enumeration supplies integer tooth-count possibilities within caller-defined bounds. WP-39 combines ordered mesh possibilities while enforcing repeated-gear consistency. The overall speed ratio magnitude is the exact rational product:

[
R=prod_{i=1}^{n}rac{z_{driver,i}}{z_{driven,i}}
]

External mesh direction reverses at each stage; this package reports ratio magnitude and retains mesh order. A full physical kinematic graph, compound wheel identity and direction closure must still be reconciled with WP-25/WP-26 before design review.

Search is bounded by supplied tooth ranges and candidate limit. It is not a global optimizer; truncation is reported.

## 4. Involute and mesh screening

For each candidate gear, WP-38 calculates pitch/base/addendum/root radii and a limited analytical tip-thickness screen from explicit gear-system inputs. Each mesh receives a transverse contact-ratio calculation and zero-shift undercut risk screens.

The undercut screen is not a rack-generation simulation. Contact ratio is not a strength or durability result. No candidate is accepted solely because a numerical contact ratio exceeds a caller-provided threshold.

## 5. Center-distance screening

For standard external spur gears with common module:

[
a_{nom}=rac{m(z_1+z_2)}{2}
]

If an explicit actual center distance and tolerance are supplied, the model compares the absolute deviation with that tolerance. It does not infer coordinates, tolerance or a preferred module. It does not prove center distance, backlash, profile shift correction, runout, tooth interference or assembly clearance.

## 6. Ranking policy

Candidates are sorted deterministically by:
1. smallest absolute fractional error from the explicitly supplied overall target ratio;
2. highest minimum transverse contact ratio among evaluated meshes;
3. deterministic tooth-count assignment ordering.

This is a transparent screening rank, not a weighted engineering optimum. It does not account for torque capacity, fatigue, friction, efficiency, noise, wear, manufacturing yield, serviceability, inertia, chronograph disturbance, power reserve or case/plate packaging. A candidate may rank highly and still fail other engineering requirements.

No architecture winner is declared. WP-33 clutch/control alternatives, WP-17 counter behavior, source arbor and stopped-train restraint remain unresolved.

## 7. Input register — C-01 values remain TBD

| Input | Required authority | Status |
|---|---|---|
| Train topology and mesh order | Approved WP-15/WP-25 architecture | TBD |
| Gear tooth counts | WP-39 candidate + independent review | TBD |
| Module and tooth system | Gear specialist / approved standard | TBD |
| Reference pressure angle | Approved gear basis | TBD |
| Addendum/dedendum coefficients | Selected rack/cutter system | TBD |
| Profile shift | Gear-pair optimization and rack-generation analysis | TBD |
| Center distances and tolerances | WP-23 coordinates / WP-37 tolerance stack | TBD |
| Minimum contact ratio | Approved design requirement | TBD |
| Undercut and interference acceptance | Gear specialist analysis | TBD |
| Torque, strength and fatigue | Measured load basis and gear calculations | TBD |
| Materials, hardness, finish, lubrication | Qualified supplier/process basis | TBD |
| Chronograph energy and timekeeping impact | WP-28/WP-29 matched measurement | TBD |

No tooth count, module, pressure angle, center distance, tolerance or acceptance threshold is assigned to C-01 in this work package.

## 8. Acceptance criteria

| ID | Criterion | Evidence |
|---|---|---|
| WP39-AC-01 | All IDs, gear-arbor assignments and provenance resolve | Controlled candidate input |
| WP39-AC-02 | Each mesh has explicit bounded search constraints | Search record |
| WP39-AC-03 | Shared gear IDs have consistent tooth counts across meshes | Candidate validation |
| WP39-AC-04 | Overall ratio is exact-rational and within declared bound | Independent ratio check |
| WP39-AC-05 | Every gear passes WP-38 input/geometry validation | Gear calculation record |
| WP39-AC-06 | Contact ratio and undercut screening limitations are recorded | Gear specialist review |
| WP39-AC-07 | Center distance is evaluated only with explicit center distance and tolerance | WP-23/WP-37 evidence |
| WP39-AC-08 | Search truncation and unevaluated constraints are visible | Candidate report |
| WP39-AC-09 | Strength, fatigue, wear, lubrication and dynamic behavior are independently addressed | Specialist engineering reports |
| WP39-AC-10 | Candidate selection receives independent approval and WP-30 verification plan | Signed design review |

Software output cannot authorize a design freeze or manufacture.

## 9. Verification

Run from `projects/steward-timepieces/tools`:

```sh
python -m unittest test_c01_gear_train_optimization.py
```

Synthetic fixtures cover ranked candidate return, exact target ratio, repeated gear tooth consistency, missing geometry handling, incompatible modules, incompatible pressure angles, provenance rejection and candidate result limits. Fixtures are not C-01 design data.

## 10. Risks and limitations

- Only external involute spur gears are supported.
- Candidate combination count may grow rapidly; result caps bound search and can truncate feasible candidates.
- The ranking is not a global optimum or multi-objective engineering decision.
- No full swept motion, CAD interference, arbor/bearing loads or structural support calculation is integrated here.
- No bending/contact stress, fatigue, wear, lubrication, efficiency, acoustic, thermal or shock analysis.
- No power-reserve, rate, amplitude or chronograph-running performance is inferred.
- No final chronograph train architecture, source arbor, clutch or counter mechanism is selected.

## 11. Revision control and disposition

| Revision | Date | Change | Approval |
|---|---|---|---|
| A | 2026-11-27 | Initial integrated bounded train candidate optimizer, involute/contact screening, synthetic tests and controlled engineering plan | Pending independent engineering review |

**Disposition:** WP-39 produces ranked analytical candidates only. C-01 tooth schedule, gear system, geometry, materials, tolerances and architecture remain unfrozen. No physical build, merge or deployment is authorized.
