# WP-36 — Chronograph Mechanical Component Geometry and Parametric CAD

- Document ID: SEB-C01-WP-36
- Revision: A — initial controlled issue
- Status: Parametric component input contract and CAD source generator; no C-01 part geometry selected or released
- Branch: steward/c-01-movement-foundation
- Software: tools/c01_chrono_component_geometry.py
- Verification: tools/test_c01_chrono_component_geometry.py
- Dependencies: WP-20, WP-21, WP-22, WP-23, WP-24, WP-30, WP-32, WP-33, WP-34, WP-35

## 1. Purpose

WP-36 defines a controlled route for turning approved, sourced chronograph component dimensions into reviewable parametric CAD source. It establishes component identity, role, primitive geometry, placement, provenance and interface references. It does not choose the chronograph architecture or invent component dimensions.

The immediate design objects are the source/take-off interface, clutch members, central seconds arbor, counter drive members, counter indexing components, stopped-train restraint, control levers, heart cams, reset hammers, pivots and structural supports. These are required component families, not completed part designs.

## 2. Design boundary

The four WP-33 combinations remain open: vertical clutch + column wheel; vertical clutch + cam/lever; horizontal coupling + column wheel; horizontal coupling + cam/lever. The source arbor, counter indication method, common/separate reset hammer arrangement and detailed packaging remain undecided.

No tooth counts, module, pressure angle, gear profile, cam profile, pivot diameter, arbor diameter, axial thickness, center coordinates, material, heat treatment, surface finish, lubrication, force, spring rate, tolerance or acceptance limit is assigned by this work package.

## 3. Coordinate and geometry convention

- Length units: millimetres.
- XY axes and origin: movement-centred WP-14/WP-20 convention.
- Z: signed coordinate in the approved WP-21 M0 realization.
- Pose: explicit translation (x, y, z) and rotation (rx, ry, rz), in degrees.
- Primitive geometry currently supported: cylinder, annulus and extruded XY polygon.
- Each component carries its own evidence ID and source revision, in addition to package-level provenance.

A primitive is a geometric placeholder only when it does not capture the actual tooth, cam, spring, lever, pivot or contact profile. The engineer must use appropriate detailed CAD features and controlled drawings for those parts before any physical fit or performance conclusion.

## 4. Component register and proposed decomposition

| Functional family | Required component definition | Geometry status |
|---|---|---|
| Drive source | Source arbor, take-off wheel/pinion and supports | Not supplied |
| Clutch | Driving member, driven member, engagement element, return system | Not supplied |
| Chronograph seconds | Central wheel, arbor, hand seat and retention | Not supplied |
| Minute totalizer | Reduction/indexing drive, wheel, arbor, jumper and hand | Not supplied |
| Hour totalizer | Reduction/indexing drive, wheel, arbor, jumper and hand | Not supplied |
| Stopped retention | Brake/detent candidate and actuation interface | Not selected |
| Control | Column wheel or cam/lever parts and operating levers | Not selected |
| Reset | Heart cams, hammer(s), pivots, springs and travel stops | Not supplied |
| Structure | Plate/bridge interfaces, bearing and pivot supports | Not supplied |

The table is a decomposition checklist, not a bill of materials or evidence that a specific part exists.

## 5. Parametric input schema

Each component record requires:
- safe unique component ID and functional role;
- geometry type and explicit parameters;
- explicit six-degree pose (three translations and three rotations);
- evidence ID and source revision.

Supported primitive inputs:
- cylinder: radius and height;
- annulus: outer radius, inner radius and height, with inner radius less than outer radius;
- extruded polygon: at least three unique XY vertices enclosing non-zero area, plus extrusion height.

The package requires candidate ID, global evidence ID, source revision and a unique component list. Optional interface records require unique IDs, two distinct component endpoints that exist in the package, interface type, evidence ID and source revision.

The generator emits individual OpenSCAD part modules. Assembly preview calls remain commented out intentionally so that an engineer reviews placement and orientation before assembling the candidate.

## 6. Calculations and validation

The tool validates finite numeric values, positive dimensions, annulus inner/outer radius ordering, polygon uniqueness and non-zero area, safe identifiers, unique component/interface IDs, valid interface endpoints and complete provenance.

For an annulus, the nominal radial wall is derived as:

    wall_radial = outer_radius - inner_radius

For a cylinder, the supplied circular envelope radius is the radius input. For an extruded polygon, the supplied vertices are used directly. These are geometric input checks only; the model does not infer missing values.

No strength, contact stress, tooth contact ratio, undercut, fatigue, deflection, bearing pressure, wear, lubrication, tolerance stack, swept collision or manufacturing capability is calculated.

## 7. CAD handoff

Run the software tests from the tools directory:

    python -m unittest test_c01_chrono_component_geometry.py

Generate source from an engineer-supplied configuration:

    from c01_chrono_component_geometry import generate_component_scad
    source = generate_component_scad(approved_candidate_package)

Review the generated source in OpenSCAD. The generator does not invoke a CAD renderer. Detailed gears, cams, heart profiles, lever contacts, spring geometry and assembly constraints must be authored and reviewed in the selected CAD system using controlled source drawings and measured/supplier-confirmed data.

## 8. Acceptance criteria

- WP36-AC-01: every part has a unique ID, role, supported geometry and six-degree pose.
- WP36-AC-02: every part and interface has traceable evidence and source revision.
- WP36-AC-03: invalid or incomplete geometry fails validation.
- WP36-AC-04: all interface endpoints resolve to defined package components.
- WP36-AC-05: generated part modules reproduce supplied primitive geometry and provenance.
- WP36-AC-06: assembly calls remain disabled pending engineering review.
- WP36-AC-07: synthetic fixtures are isolated to tests and are never treated as C-01 dimensions.
- WP36-AC-08: no software output authorizes manufacture or design freeze.

## 9. Risks and controls

| Risk | Control |
|---|---|
| Primitive cylinder used as a substitute for a detailed gear or cam | Label primitive as envelope/placeholder; require detailed feature geometry |
| Wrong datum or pose convention | Verify against approved WP-21 datum realization and WP-14 axes |
| Missing source revision | Fail validation |
| Interface endpoint mismatch | Fail package validation |
| Fixture values copied into a candidate | Keep fixtures exclusively in unit tests |
| CAD source mistaken for released drawing | Require independent review and WP-30 verification records |

## 10. Revision control and disposition

Revision A establishes the first controlled component-geometry input contract. Geometry changes require impact review against WP-20, WP-22 through WP-24, WP-30, WP-32 through WP-35.

**Disposition:** WP-36 provides an evidence-gated parametric component CAD foundation. No physical chronograph parts, dimensions, architecture winner or manufacturing release are established.
