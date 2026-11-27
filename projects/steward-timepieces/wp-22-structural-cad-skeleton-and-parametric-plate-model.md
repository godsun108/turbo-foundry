# STEWARD C-01 — WP-22 Structural CAD Skeleton and Parametric Plate Model

**Document ID:** C01-WP-22  
**Revision:** 0.1  
**Status:** Parametric CAD generator and input contract; no C-01 geometry supplied or frozen  
**Branch:** `steward/c-01-movement-foundation`  
**Predecessors:** WP-14, WP-19, WP-20 and WP-21  
**Next gate:** controlled source geometry, generated candidate model, independent CAD review and tolerance-aware verification

## 1. Purpose

WP-22 establishes a neutral, reproducible CAD handoff for the C-01 main plate, bearing bores, bridge envelopes and subsystem keepout envelopes. It adds a Python generator that produces reviewable OpenSCAD source from an explicit geometry input record.

This is a CAD skeleton generator, not a dimensioned C-01 design, manufacturing drawing, validated solid model or proof of physical fit. No C-01 dimensions or placements are provided by this package.

## 2. Design boundary and preserved decisions

WP-20 remains the functional component/interface baseline. WP-21 remains the structural datum and support-register baseline. WP-22 defines the input contract and CAD source-generation process without selecting:
- dial arrangement A, B or C;
- horizontal/lateral, vertical/coaxial or hybrid chronograph packaging;
- clutch or control architecture;
- plate/bridge partition count;
- calendar month-window scope;
- movement or case dimensions.

The geometry input is a candidate, not a released design. All physical values must originate in controlled drawings, supplier data, measured inspection or approved CAD revisions.

## 3. CAD coordinate contract

- XY origin and axes follow the WP-14/WP-20 movement-centered convention: +X toward 3 o'clock and +Y toward 12 o'clock.
- All geometry uses millimetres.
- Z values are signed coordinates from the approved WP-21 M0 realization.
- The plate upper face is supplied as `plate.top_z_mm`; thickness extends in the negative Z direction.
- Polygon vertices are explicit XY coordinates; no automatic diameter or outline is inferred.
- Every geometry object requires traceable evidence and source revision. The overall candidate also carries global provenance.

If M0 is not yet approved, the input may only be treated as a provisional candidate coordinate frame. It cannot be promoted to a controlled production datum.

## 4. Input schema

The generator accepts a Python dictionary with these required groups:

| Group | Required fields | Meaning |
|---|---|---|
| Candidate | `candidate_id`, `provenance.evidence`, `provenance.source_revision` | Candidate identity and global source |
| Plate | `outline_xy_mm`, `thickness_mm`, `top_z_mm` | Explicit plate polygon and axial extent |
| Bearing bores | `id`, `component_id`, `axis_id`, `xy_mm`, `diameter_mm`, evidence, revision | Explicit bore geometry and functional traceability |
| Bridges | `id`, `outline_xy_mm`, `z_min_mm`, `z_max_mm`, `supported_components`, evidence, revision | Explicit bridge envelope and support assignment |
| Keepouts | `id`, `xy_mm`, `radius_mm`, `z_min_mm`, `z_max_mm`, evidence, revision | Cylindrical envelope for balance, rotor, chrono or calendar candidates |

Bridge and keepout collections may be empty when no sourced candidate geometry exists. The plate itself and global provenance are mandatory for source generation. A bearing bore must link to a WP-20 component ID and a controlled axis ID.

## 5. Calculations and validation

The generator performs only input validation and geometric source construction:

- Polygon validation: at least three unique vertices and non-zero signed area.
- Plate axial extent: (z_{bottom}=z_{top}-t_{plate}), with positive supplied thickness.
- Bearing bore radius: (r=d/2), from supplied bore diameter.
- Bridge extrusion height: (h=z_{max}-z_{min}), requiring (h>0).
- Keepout extrusion height: (h=z_{max}-z_{min}), requiring (h>0).

The generated OpenSCAD source contains a plate blank, bearing-bore subtraction, separate bridge solids and separate cylindrical keepout envelope modules. Assembly calls remain commented out so the engineer deliberately chooses which layers to display and inspect.

The tool does not compute or certify polygon containment, bore edge distance, bridge-to-plate fit, bridge stiffness, bearing fit, gear mesh, component clearance, swept motion, tolerance stack, deflection, shock travel, assembly access or manufacturability. These require separate engineering checks.

## 6. Synthetic software fixture

The unit tests use a small rectangular plate and synthetic bore, bridge and envelope values solely to test validation and code generation. These values are explicitly test fixtures and are not C-01 design inputs, suggested dimensions or a scale model.

No production candidate geometry is included in this commit.

## 7. Execution and CAD review

Run the unit tests from the tools directory:

```bash
python -m unittest test_c01_cad_skeleton.py
```

To generate a candidate OpenSCAD source file from an engineer-supplied Python configuration:

```python
from c01_cad_skeleton import generate_openscad

source = generate_openscad(candidate_config)
with open("c01_candidate_skeleton.scad", "w", encoding="utf-8") as handle:
    handle.write(source)
```

Open the resulting `.scad` file in OpenSCAD for visual review. The generator does not invoke OpenSCAD or claim a rendered/validated solid. Export to mesh or manufacturing formats only after independent CAD review and appropriate downstream checks.

## 8. Acceptance criteria

| ID | Acceptance criterion | Evidence |
|---|---|---|
| WP22-AC-01 | All geometry is explicitly supplied in mm and uses the approved coordinate frame | Controlled input and datum approval |
| WP22-AC-02 | Every geometry item has evidence and source revision | Input provenance audit |
| WP22-AC-03 | Plate polygon and axial extent validate | Generator validation and CAD inspection |
| WP22-AC-04 | Bearing bores resolve to approved component and axis registers | WP-20/WP-21 cross-reference review |
| WP22-AC-05 | Bridge envelopes and support assignments are approved | Structural design review |
| WP22-AC-06 | Rotor, balance, chronograph and calendar keepouts are sourced | Supplier/measurement/CAD evidence |
| WP22-AC-07 | Interference, tolerance, stiffness and service access are independently evaluated | CAD/analysis/assembly verification |
| WP22-AC-08 | Generated model is independently reviewed before design release | Signed CAD review and revision record |

No acceptance criterion is passed for a production design by this preliminary package.

## 9. Verification plan

The test suite checks required geometry and provenance, polygon validation, unique bore IDs, positive bridge extents, keepout provenance and generated OpenSCAD source content. The tests establish software behavior only. They do not validate any C-01 geometry.

## 10. Risks and controls

| Risk | Control |
|---|---|
| Synthetic test dimensions mistaken for design values | Keep fixtures inside tests and label them explicitly |
| Uncontrolled datum shifts all axial positions | Require approved M0 and source revision before design freeze |
| Bore geometry is disconnected from functional architecture | Require WP-20 component and WP-21 axis references |
| Bridge envelope appears valid but lacks stiffness | Require structural analysis and physical verification |
| Keepout cylinders oversimplify dynamic envelopes | Replace with sourced swept envelopes during detailed CAD |
| Generated source mistaken for a released solid | Keep assembly calls commented and require independent CAD review |

## 11. Revision control

| Revision | Change | Status |
|---|---|---|
| 0.1 | Initial input contract, validation model, OpenSCAD source generator and software tests | Preliminary; no C-01 geometry frozen |

## 12. WP-22 exit gate

WP-22 exits preliminary status when approved source geometry is populated, datum and component references are controlled, the generated CAD is independently reviewed, and tolerance-aware interference, structural, dynamic and service-access verification has been completed. Until then, the deliverable is a reproducible CAD skeleton generator—not a finished movement or manufacturing model.
