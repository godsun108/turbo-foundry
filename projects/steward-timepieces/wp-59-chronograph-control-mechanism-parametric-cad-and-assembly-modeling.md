# WP-59 — Chronograph Control Mechanism Parametric CAD and Assembly Modeling

- **Document ID:** SEB-C01-WP-59
- **Revision:** A — initial controlled issue
- **Status:** Evidence-gated parametric assembly framework; no C-01 assembly geometry approved or released
- **Branch:** `steward/c-01-movement-foundation`
- **Software:** `tools/c01_control_cad_assembly.py`
- **Verification:** `tools/test_c01_control_cad_assembly.py`
- **Dependencies:** WP-21, WP-22, WP-36, WP-40, WP-44, WP-54, WP-55, WP-57 and WP-58

## 1. Purpose

WP-59 advances the WP-58 geometry and dimensioning framework into a controlled parametric CAD assembly handoff for the two chronograph-control candidates:

- **CW:** column-wheel control.
- **CL:** cam/lever control.

It defines component solids from explicitly supplied neutral geometry descriptors, explicit global placements, assembly hierarchy, mate/interface constraints, candidate configuration control and OpenSCAD source generation. CW and CL remain separate candidate assemblies and must share the same approved requirements, datum and interface-baseline revisions for a valid comparison.

This is an engineering data and visualization framework. It does not populate C-01 geometry, select an architecture, certify physical fit, or authorize a prototype build.

## 2. Design authority and preserved decisions

WP-33/WP-45/WP-56 architecture decisions remain open unless separately approved by the design authority. WP-58 remains the source of controlled geometry, dimension and datum inputs. WP-59 consumes sourced geometry; it does not create dimensions from a nominal watch size or infer missing placements.

The following remain unselected:
- vertical friction clutch versus horizontal/lateral coupling;
- column-wheel versus cam/lever control;
- the four clutch/control combinations;
- source arbor and take-off;
- counter drive and continuous/jumping behavior;
- stopped-train retention implementation;
- common versus separate reset hammers;
- movement layout, dial arrangement and case interface.

The WP-59 evaluator always reports architecture selected = false, design frozen = false and manufacturing release authorized = false.

## 3. Coordinate system and placement convention

- XY uses the movement-centred WP-14/WP-20 convention.
- Z references the WP-21 M0 realization.
- Length is millimetres; rotations are degrees.
- Every component carries an explicit global translation (X, Y, Z) and Euler rotation (X, Y, Z).
- Every component carries a drawing reference, geometry status, evidence ID and source revision.
- Parent-child links define assembly organization only. They do not compose transforms or imply that a child pose is local to its parent. All poses remain explicit global placements to prevent hidden transform assumptions.

A datum realization that is not approved may support only a provisional candidate visualization. It cannot be promoted to a controlled physical assembly.

## 4. Parametric component geometry

The initial neutral solid schema supports:
1. Cylinder: radius and height.
2. Annulus: outer radius, inner radius and height.
3. Extruded XY polygon: explicit unique vertices and height.

These are simple visualization primitives. They do not represent involute gear teeth, column-wheel working faces, cam/follower profiles, heart-cam geometry, spring solids, contact curvature, pivots, threads, lubrication features or manufacturing details unless the supplied geometry truly describes those features.

Each component requires:
- unique safe component ID and functional role;
- geometry type and explicit parameters;
- explicit global pose;
- parent ID or null;
- geometry status (TBD, candidate, reviewed or approved);
- drawing reference;
- evidence ID and source revision.

No default geometry, coordinates, dimensions, tolerances, materials or component counts are supplied.

## 5. Assembly hierarchy and interfaces

The component hierarchy is checked for valid parent references, self-parenting and cycles. The hierarchy is organizational only; it does not substitute for a kinematic joint definition.

Mate records support the following narrowly defined checks:

| Mate type | Calculation | Limitation |
|---|---|---|
| Coaxial | Compare declared local +Z axis directions (parallel or antiparallel) using an angular tolerance in degrees, and distance between axis lines using a separate offset tolerance in mm | Nominal axis alignment only |
| Planar | Compare global Z coordinates | Does not solve plane normals or contact |
| Fixed distance | Compare explicit global component-origin distance with target and tolerance | Does not define a full linkage |
| Angular | Compare relative global Z Euler angle with target and tolerance | Does not define a 3D joint |
| Contact reference | Validate two named feature references | No contact detection or solver |

Each mate requires unique ID, two distinct component endpoints, definition, evidence ID and source revision. Numeric mates require explicit positive tolerances in dimensionally appropriate units; coaxial mates use separate angular (degrees) and offset (mm) tolerances. A failed mate check is a screening failure; a passed check is not proof of physical fit or mechanism operation. Contact-reference mates deliberately remain unverified.

## 6. Candidate assembly package and baseline control

The assembly-set input requires both CW and CL packages. Each candidate must match the common:
- requirements revision;
- movement datum revision;
- interface-baseline revision.

Each candidate separately identifies configuration revision, evidence, source revision, owner, component register and mate register. The evaluator reports component approval status and mate screening results. It does not treat a complete register as evidence that the underlying geometry is correct.

Candidate-specific component geometry and measurements must not be pooled. A comparison requires matched common baselines and independently controlled candidate configurations.

## 7. CAD source generation

The generator emits one OpenSCAD module per supplied component and explicit assembly calls using the declared global poses. The source includes candidate, configuration, evidence, source and drawing references.

The output is intended for engineer review of component organization, orientation and neutral envelope assembly. It does not run OpenSCAD, render a model, generate a native feature tree, validate detailed solid intersections or produce manufacturing drawings. Assembly calls are generated only from explicitly supplied components; no omitted component is inferred.

## 8. Verification and acceptance criteria

The software acceptance criteria are:

1. Reject missing provenance, unsafe/duplicate IDs, unsupported geometry, non-finite values and invalid dimensions.
2. Reject unknown parents, self-parenting and hierarchy cycles.
3. Reject mate endpoints that are absent, identical or duplicated by mate ID.
4. Calculate each supported numeric mate only from explicit supplied poses and tolerances.
5. Mark contact references as reference-only and unverified.
6. Require CW and CL packages with matching common baseline revisions.
7. Generate deterministic OpenSCAD source with candidate and provenance comments.
8. Never report physical fit, swept-motion clearance, architecture selection, design freeze or manufacturing release as approved.

Synthetic unit-test fixtures are software tests only. They are not C-01 dimensions, component proposals, a scale model, measured results or design evidence.

Run the tests from the tools directory:

```bash
python -m unittest test_c01_control_cad_assembly.py
```

No test result is claimed by this document. Test execution and CAD rendering must be independently performed and recorded.

## 9. Engineering limitations and required next evidence

WP-59 does not perform:
- detailed involute tooth or cam/follower solid generation;
- continuous swept-volume or collision analysis;
- full 3D joint/constraint solving;
- contact force, friction, stress, wear or fatigue calculations;
- tolerance-aware physical fit, thermal or elastic deflection analysis;
- bearing, shock, lubrication or serviceability qualification;
- physical reset-interlock verification;
- manufacturing capability or inspection certification.

Before a physical article can be considered, the project requires approved datum realization, released candidate drawings and dimensions, complete interface definitions, detailed geometry, tolerance analysis, independent CAD review, BOM and work instructions, metrology plan, risk review and formal build/test authorization under WP-31/WP-32/WP-53/WP-57.

## 10. Revision and release record

| Revision | Change | Status |
|---|---|---|
| A | Initial evidence-gated parametric assembly model, validation, CAD source generator and synthetic regression tests | Framework only; no C-01 assembly released |

**Release statement:** WP-59 is a controlled engineering framework on the development branch. It does not freeze C-01, select CW or CL, select a clutch, certify fit, authorize manufacture, or authorize prototype assembly or testing.
