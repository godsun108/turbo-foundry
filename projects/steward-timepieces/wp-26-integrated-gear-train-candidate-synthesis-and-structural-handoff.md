# WP-26 — Integrated Gear-Train Candidate Synthesis and Structural Handoff

- **Document ID:** SEB-C01-WP-26
- **Project:** STEWARD C-01
- **Revision:** A (initial controlled issue)
- **Status:** Candidate synthesis and interface orchestration; no design selected
- **Branch:** `steward/c-01-movement-foundation`
- **Software:** `tools/c01_gear_train_candidate.py`
- **Verification:** `tools/test_c01_gear_train_candidate.py`
- **Dependencies:** WP-18, WP-20, WP-22, WP-23, WP-24 and WP-25

## 1. Purpose

WP-26 composes the existing integer tooth-count, arbor-coordinate, bearing-support, CAD-input and going-train kinematic tools into one evidence-gated candidate workflow. It is intended to move from independent calculations toward a coherent candidate gear schedule without inventing C-01 geometry or declaring a mathematical candidate physically buildable.

The workflow:
1. synthesizes bounded integer tooth-count candidates for each explicitly declared external mesh;
2. combines mesh candidates while enforcing consistent tooth counts for any gear ID reused across meshes;
3. validates gear-to-arbor mapping;
4. evaluates complete declared source-to-output kinematic paths using WP-25;
5. checks nominal mesh center distances only when module, coordinates and tolerance are supplied;
6. optionally validates WP-24 support/bearing registers;
7. optionally generates WP-22 OpenSCAD source from a complete, explicit CAD configuration.

## 2. Engineering boundary

WP-26 does not freeze:
- going-train wheel order or physical layout;
- barrel speed or torque curve;
- wheel/pinion tooth counts;
- gear module, profile, face width, material or finish;
- arbor coordinates, plate or bridge geometry;
- bearing/jewel dimensions or support topology;
- escapement tooth/event convention;
- chronograph take-off or calendar drive.

All candidate values must be traceable to explicit inputs, declared search bounds or cited source revisions. Missing values remain unevaluated. No hidden default design parameters are applied.

## 3. Data model

### 3.1 Arbor register

Each arbor declares unique ID, role, WP-20 component ID, WP-21 axis ID, evidence and source revision. XY coordinates are optional and are only used for geometry checks when supplied.

### 3.2 Mesh specification

Each physical mesh declares:
- mesh ID;
- driver and driven gear IDs;
- the two distinct arbor IDs;
- mesh type;
- evidence and source revision;
- target ratio and bounded synthesis constraints, either local to the mesh or supplied in the common search object;
- optional module, center-distance tolerance and explicit XY coordinates through the arbor register.

WP-26 currently synthesizes one external spur pair per mesh specification. A compound train is represented by multiple mesh specifications connected through gears sharing a declared intermediate arbor. Internal gear synthesis is not silently treated as external and is explicitly unsupported in this release.

### 3.3 Shared gear consistency

A gear ID appearing in multiple meshes must retain one tooth count and one arbor assignment throughout the candidate. Conflicting assignments are rejected. This enforces the mathematical meaning of a wheel/pinion rigidly fixed to one shaft.

## 4. Tooth-count synthesis and candidate combinations

WP-18's exact-rational bounded synthesis is called for each mesh. Search bounds must be explicit:
- minimum/maximum tooth count;
- minimum/maximum stage ratio;
- maximum fractional ratio error;
- maximum results;
- optional module.

The orchestration combines the returned single-stage mesh candidates up to an explicit maximum combination count. This is a bounded candidate exploration, not a proof of global optimality. Search ordering and result caps can exclude other valid combinations; all search constraints must be recorded with the study.

A common module is only a synthesis calculation input. It is not a material, strength, tooth-form or manufacturing approval.

## 5. Kinematic closure

For each combined candidate, WP-25 receives the declared arbor, gear and mesh graph plus explicit input arbor RPM and output targets. It calculates exact rational compound ratios and direction, reports no-path or multiple-path conditions, and compares output speeds only against explicitly supplied tolerances.

The barrel input RPM is a required measured/approved input. It is not inferred from the display speed or from the 4 Hz balance target.

Chronograph outputs require a separately declared take-off/drive path and remain an independent architecture decision. WP-26 does not automatically equate the fourth-wheel seconds axis with a selected chronograph drive.

## 6. Center-distance and coordinate constraints

When the following are all supplied, WP-23's nominal standard spur center-distance relationship is checked against actual arbor XY coordinates:
- module;
- synthesized integer tooth counts;
- XY coordinate for both arbors;
- explicit center-distance tolerance;
- evidence and source revision.

For an external mesh:
[
a_{nom}=m\frac{z_1+z_2}{2}
]

The comparison is a nominal pitch-center check only. It does not assess profile shift, backlash, tooth form, undercut, contact ratio, runout, center-distance tolerance stack, interference, plate edge distance or dynamic clearance. If any required input is missing, the mesh remains unevaluated; no coordinate is generated to force a fit.

## 7. Bearing, bridge and CAD handoff

The optional WP-24 structural-support input checks component/axis/arbor/support/member traceability and optional bearing-bore/CAD consistency. The optional WP-22 CAD configuration may generate OpenSCAD source only from complete explicit geometry and provenance.

A successful register validation is not a bearing design or structural proof. Generated source is not a rendered, dimensionally inspected or manufacturing-released CAD model. No bridge stiffness, bearing load, pivot stress, shock response or assembly access is calculated.

## 8. Acceptance criteria

1. Every arbor, gear and mesh ID is unique and every reference resolves.
2. Each mesh joins two distinct arbors and uses an explicitly supported mesh type.
3. Every synthesis search has explicit bounds and target ratio.
4. Each gear ID has one consistent tooth count and arbor assignment across all meshes.
5. Each evaluated output has a unique directed path from the declared input.
6. Exact ratio, direction and target error are reported; tolerance is applied only when supplied.
7. Center distance is evaluated only with module, coordinates and tolerance.
8. Support and CAD checks are performed only when their complete explicit inputs are supplied.
9. No candidate is labeled production-ready or physically fit based on these calculations.
10. All fixture values remain clearly identified as synthetic software tests.

## 9. Verification

Run from the tools directory:
```sh
python -m unittest test_c01_gear_train_candidate.py
```

Tests cover bounded synthesis and exact kinematic closure, explicit center-distance checks, missing coordinate handling, shared-gear consistency, required search bounds and explicit rejection of unsupported internal-gear synthesis. Test values are synthetic fixtures only and are not C-01 design data.

## 10. Limitations and next engineering gate

WP-26 does not replace detailed design of gear teeth, escapement, chronograph, calendar, winding works, bearings, structure or case. It does not calculate torque, efficiency, power reserve, inertia, dynamic response, timekeeping rate or fatigue life.

The next gate is to obtain controlled reference inputs: a barrel speed/torque characterization, selected topology, gear tooth-form constraints, module feasibility, movement envelope, plate/bridge datums, arbor support design and an approved error budget. Candidate schedules can then be screened against real geometry and mechanical performance evidence.

## 11. Revision control

| Revision | Date | Change | Approval |
|---|---|---|---|
| A | 2026-11-26 | Initial integrated candidate synthesis and WP-18/WP-23/WP-24/WP-25 orchestration | Pending engineering review |

**Release gate:** no candidate schedule, module, arbor location, bearing size, support arrangement, CAD geometry or movement architecture is frozen by WP-26. No merge or deployment is authorized.
