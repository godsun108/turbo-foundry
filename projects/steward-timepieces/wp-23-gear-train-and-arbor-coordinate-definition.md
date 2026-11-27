# WP-23 — Gear Train and Arbor Coordinate Definition

- **Document ID:** SEB-C01-WP-23
- **Project:** STEWARD C-01
- **Revision:** A (initial controlled issue)
- **Status:** Preliminary engineering method; no physical coordinate set approved
- **Branch:** `steward/c-01-movement-foundation`
- **Software:** `tools/c01_arbor_coordinates.py`
- **Verification:** `tools/test_c01_arbor_coordinates.py`

## 1. Purpose and scope

WP-23 establishes the coordinate-definition method linking the functional gear-train topology (WP-15), kinematics and integer-tooth synthesis (WP-17/WP-18), spatial geometry checks (WP-19), integrated component register (WP-20), structural bearing/support register (WP-21), and neutral CAD skeleton (WP-22).

It defines how barrel, center, third, fourth, escape-wheel and balance axes, plus candidate chronograph take-off axes, are to be represented and constrained. It does **not** choose a C-01 layout or populate physical coordinates.

## 2. Controlled coordinate convention

Use the existing WP-20 convention:
- XY origin: movement/dial center.
- +X: toward 3 o'clock.
- +Y: toward 12 o'clock.
- Distances: mm, only when sourced from controlled geometry.
- Z: referenced to the approved WP-21 master datum M0; physical realization and offsets remain TBD.

A coordinate is not design data unless it has evidence and a source revision. Missing values remain null/TBD, never zero.

## 3. Arbor register and functional mapping

The software register is keyed by unique arbor ID and includes role, WP-20 component ID, WP-21 axis ID, optional XY coordinate, optional axial interval, supporting structure references, evidence and source revision.

Expected functional roles to populate when evidence exists:
1. Barrel arbor / barrel wheel axis — component `barrel`.
2. Center wheel arbor — `center_wheel`.
3. Third wheel arbor — `third_wheel`.
4. Fourth wheel / running-seconds axis — `fourth_wheel`.
5. Escape wheel axis — associated with the escape wheel within `escapement`; its distinct axis ID must be allocated in WP-21.
6. Balance axis — `balance`.
7. Chronograph source/take-off and counter axes — candidate components `chrono_drive`, `chrono_seconds`, `chrono_30m`, `chrono_12h`; source and exact arrangement remain open.

These are functional mapping requirements, not a declaration that all parts are coaxial or share a single arbor.

## 4. Gear center-distance calculations

For standard, unshifted spur gears with common module (m):

External mesh:
[
a = \frac{m(z_1+z_2)}{2}
]

Internal mesh (ring tooth count (z_r), pinion tooth count (z_p)):
[
a = \frac{m|z_r-z_p|}{2}
]

where (a) is nominal center distance in mm when module is mm and tooth counts are integers.

Actual center distance is computed from the supplied arbor coordinates:
[
a_{xy}=\sqrt{(x_2-x_1)^2+(y_2-y_1)^2}
]
[
\Delta a=a_{xy}-a
]

Acceptance against center-distance tolerance is evaluated only when an approved tolerance is supplied:
[
|\Delta a|\leq T_a
]

This nominal relationship excludes profile shift, backlash, tooth corrections, center-distance modification, tooth-form geometry and manufacturing effects. A passing result is not proof of correct tooth contact or mesh quality.

## 5. Coordinate constraint solving

Two supported methods are implemented:

### 5.1 Polar constraint

Given an explicitly anchored axis ((x_0,y_0)), radius (r), and angle (	heta) measured counter-clockwise from +X:
[
x=x_0+r\cos\theta,\qquad y=y_0+r\sin\theta
]

All three inputs must be controlled. The function does not choose an angle.

### 5.2 Two-circle intersection

An unknown axis constrained to distances (r_a) and (r_b) from two known axes may have zero, one or two valid XY intersections. The solver returns both branches when two exist. It never silently selects one. A coincident-locus case is reported as underdetermined.

Further constraints (case envelope, plate boundary, additional meshes, bridge support, dial layout, dynamic clearances and service access) must be applied before any candidate is selected.

## 6. Support and structural relationships

Each arbor references one or more WP-21 bearing-axis IDs and support records. Each support identifies:
- the arbor it supports;
- the structural member/interface ID (plate, bridge, cock or other controlled structure);
- support type;
- evidence and source revision.

The register validates referential integrity only. It does not calculate bearing pressure, pivot stress, endshake, side shake, bridge stiffness, jewel fit, shock capacity or assembly sequence.

## 7. Chronograph and going-train interfaces

The conventional functional going-train path remains barrel → center → third → fourth → escape/escapement, subject to WP-15 topology and future detailed wheel/pinion definition. The exact wheel/pinion members, compound arbors, coaxial arrangements and drive ratios remain TBD.

Candidate chronograph take-off remains open. WP-20 currently labels the fourth-wheel/seconds interface as a candidate energy interface, not a selected source. WP-23 can evaluate a candidate take-off only after source arbor, gear data, coordinates and evidence are supplied.

The central chronograph seconds, 30-minute and 12-hour axes must be related to WP-17 target kinematics and WP-18 integer tooth-count candidates. No counter indexing architecture or clutch layout is selected here.

## 8. CAD handoff to WP-22

`cad_bore_register()` maps an arbor with a supplied XY coordinate to a WP-22 bearing-bore record only when an explicit bore definition supplies diameter, evidence and source revision. It does not infer a bore diameter from arbor diameter, bearing type or component name.

The returned records can populate WP-22 `bearing_bores` after review. Plate outline, thickness, Z placement, bridge geometry, bore clearances and keepout envelopes remain separate required inputs. No complete CAD configuration is generated from this register alone.

## 9. Inputs and assumptions

| Input | Requirement | Current C-01 status |
|---|---|---|
| Module and integer tooth counts | Controlled gear definition | TBD |
| Gear mesh type | External/internal explicitly stated | TBD per pair |
| Arbor XY coordinates | Surveyed, calculated from approved constraints, or controlled CAD | TBD |
| Center-distance tolerance | Approved engineering tolerance | TBD |
| M0 and axial intervals | WP-21 controlled datum and evidence | TBD |
| Bearing/support IDs | WP-21 register references | To be allocated |
| Chronograph take-off | Approved architecture decision | Open |
| Bore diameter and provenance | Explicit bearing/jewel design input | TBD |

No module, tooth count, coordinate, center distance, tolerance, bore size, plate dimension, bridge position or case envelope is assumed.

## 10. Acceptance criteria

A candidate register is acceptable for engineering review when:
1. Arbor IDs, axis IDs and component references are unique and resolve.
2. Every populated coordinate is finite, in mm, and supported by evidence and source revision.
3. Every support resolves to a declared arbor and structural member reference.
4. Every gear mesh connects two distinct declared arbors and has explicit module, integer tooth counts, mesh type, tolerance, evidence and source revision.
5. Evaluated XY center-distance deviation is within its supplied approved tolerance, or the deviation is explicitly dispositioned.
6. Coordinate solvers preserve all mathematical branches and disclose underdetermined/no-solution cases.
7. CAD bore handoff contains only explicit, traceable bore diameters.
8. No missing input is silently treated as zero or as a successful fit.

Passing these criteria establishes register integrity and nominal geometric consistency only. It does not certify the movement.

## 11. Verification plan

Run from the tools directory:
```sh
python -m unittest test_c01_arbor_coordinates.py
```

Tests cover external/internal nominal center distance, invalid inputs, polar solving, two-circle intersections, tangent/no-intersection cases, mesh tolerance, register references, and traceable CAD bore export. All numeric fixtures are synthetic software-test data and are **not** C-01 design values.

## 12. Risks and limitations

- Nominal pitch-circle spacing can differ from a manufacturable/functional mesh after profile shift, backlash, tooth correction and tolerance allocation.
- Multiple coordinate solutions may satisfy gear-center constraints but conflict with plate boundary, display, case, bridge, rotor or service requirements.
- Functional component IDs do not necessarily correspond one-to-one with physical arbors.
- Axial support and dynamic clearances are not resolved by XY center-distance checks.
- No CAD rendering, finite-element analysis, detailed gear geometry, tolerance stack, shock test, prototype measurement or manufacturing validation is performed.

## 13. Revision control and approvals

| Revision | Date | Change | Approval |
|---|---|---|---|
| A | 2026-11-26 | Initial method, calculation model, tests and CAD handoff definition | Pending engineering review |

**Release gate:** no arbor coordinates, tooth counts, modules, bearing sizes, bridge locations or architecture are frozen until their evidence, source revision, tolerance basis and engineering approval are recorded. No merge or deployment is authorized by this work package.
