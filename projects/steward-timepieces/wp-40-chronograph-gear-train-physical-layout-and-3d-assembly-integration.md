# WP-40 — Chronograph Gear Train Physical Layout and 3D Assembly Integration

- **Document ID:** SEB-C01-WP-40
- **Revision:** A — initial controlled issue
- **Status:** Evidence-gated layout and envelope screening framework; no C-01 physical layout approved
- **Branch:** `steward/c-01-movement-foundation`
- **Software:** `tools/c01_physical_layout.py`
- **Verification:** `tools/test_c01_physical_layout.py`
- **Dependencies:** WP-20 through WP-24, WP-30, WP-32, WP-34 through WP-39

## 1. Purpose

WP-40 connects the WP-39 gear-train candidate output to the movement's spatial architecture. It defines a traceable candidate input contract for component XY placement, axial intervals, circular envelope radii, nominal gear center-distance checks, structural support references and sampled motion poses. It emits a neutral OpenSCAD envelope visualization.

This package does not invent or approve a C-01 layout. It is a screening layer between analytical candidate selection and detailed CAD.

## 2. Design basis and preserved open decisions

The WP-14/WP-20 XY convention remains movement-centred: +X toward 3 o'clock, +Y toward 12 o'clock. Z coordinates must reference the approved WP-21 M0 realization. Units are mm. All populated values require evidence ID and source revision.

The WP-33 clutch/control combinations, source arbor, continuous-versus-jumping counter behavior, common/separate reset hammer arrangement, dial layout and month-window scope remain outside this package's authority. WP-39 candidate ratios do not establish a physical gear schedule.

## 3. Component placement register

Each component envelope record requires:
- unique component ID and functional role;
- explicit XY coordinate;
- positive circular envelope radius;
- explicit [Z-min, Z-max] interval;
- evidence ID and source revision;
- optional arbor ID.

Circular envelopes are deliberately simple. For components whose axial intervals overlap, the model calculates centre distance and radial envelope clearance:

[
c_{xy}=sqrt{(x_2-x_1)^2+(y_2-y_1)^2}-(r_1+r_2)
]

A negative result flags envelope overlap. A non-negative result means only that these two supplied circular XY envelopes do not overlap at the checked axial interval. It is not proof of detailed geometry clearance.

## 4. Gear mesh placement check

For standard, unshifted external spur gears sharing module:

[
a_{nom}=rac{m(z_1+z_2)}{2}
]

The model calculates actual XY centre distance from the two declared component coordinates and compares the difference from nominal with an explicitly supplied tolerance:

[
Delta a=a_{actual}-a_{nom},qquad |Delta a|leq T_a
]

Gear mesh records require unique mesh ID, two distinct component IDs, positive module, integer tooth counts, positive tolerance, evidence and source revision. This is a nominal pitch-centre screen only. Profile shift, backlash, tooth-form compatibility, runout, elastic deflection and actual contact are not resolved.

## 5. Structural support references

Support records link a declared component to an explicit structural-member ID and support type, with evidence and source revision. This is referential integrity only. The model does not calculate bearing/jewel loads, pivot stress, endshake, side shake, bridge stiffness, screw preload or shock capability. Full support integration remains governed by WP-21/WP-24.

## 6. Motion and assembly screening

Optional trajectories provide ordered XY samples for moving components. All trajectories must have equal sample counts, representing a common documented time base. At each supplied sample, the model evaluates circular envelope clearance for moving component pairs whose Z intervals overlap.

Sparse samples can miss collisions between sample points. No continuous swept-solid collision detection is claimed. Static and sampled-motion checks do not include tolerance distributions, component deformation, gear-tooth engagement, spring/lever contact or assembly path.

## 7. CAD handoff

The generator emits OpenSCAD source containing one cylinder envelope per component, positioned using explicit XY and Z intervals, with candidate-level and component-level provenance comments. This is an envelope visualization, not detailed CAD, a native parametric feature tree, a rendered result or manufacturing geometry.

Detailed gears, clutch plates, cams, hammers, levers, springs, pivots, bearings, plate/bridge features and case/dial interfaces must be authored in a suitable CAD system from controlled drawings and reviewed source data. WP-22 remains the plate/bridge skeleton handoff; WP-36 remains the chronograph primitive component generator.

## 8. Input register — C-01 physical values remain TBD

| Input | Required source | Status |
|---|---|---|
| Component XY coordinates | Approved WP-23 coordinate solution / controlled CAD | TBD |
| Z intervals and M0 realization | WP-21 datum and axial stack | TBD |
| Envelope radii | Controlled component drawings/CAD | TBD |
| Gear tooth schedule/module | Reviewed WP-39 candidate and gear specialist | TBD |
| Center-distance tolerance | WP-37 tolerance basis / approved drawing | TBD |
| Bearing and support positions | WP-21/WP-24 and bearing design | TBD |
| Clutch/control placement | Approved WP-33 architecture decision | Open |
| Counter mechanism placement | Approved counter behavior and detailed design | Open |
| Motion trajectories | Mechanism kinematic model / measured prototype | TBD |
| Plate, bridge and case envelopes | Controlled CAD and interface drawings | TBD |

No geometry, material, bearing size, tolerance, case dimension or assembly clearance is assigned to C-01 by WP-40.

## 9. Acceptance criteria

| ID | Criterion | Evidence |
|---|---|---|
| WP40-AC-01 | Component IDs, dimensions, intervals and provenance validate | Controlled input register |
| WP40-AC-02 | Gear mesh endpoints resolve and nominal centre distance is checked | WP-23/WP-37 data |
| WP40-AC-03 | Every reported clearance identifies component pair and axial applicability | Layout report |
| WP40-AC-04 | Trajectories share a common sample count/time base | Kinematic source record |
| WP40-AC-05 | Structural supports resolve to declared component and structural member IDs | WP-21/WP-24 review |
| WP40-AC-06 | Generated OpenSCAD envelopes retain candidate/component provenance | Source review |
| WP40-AC-07 | Detailed swept-solid, tolerance and assembly checks are independently completed | CAD/analysis evidence |
| WP40-AC-08 | No software result is treated as physical fit certification or design release | Independent design review |

## 10. Verification

Run from `projects/steward-timepieces/tools`:

```sh
python -m unittest test_c01_physical_layout.py
```

Synthetic fixtures cover input validation, axial interval filtering, static envelope interference, nominal gear centre distance, sampled motion interference, common trajectory sample counts, provenance and OpenSCAD source generation. Fixture dimensions are test-only and are not C-01 design data.

## 11. Risks and limitations

- Circular envelopes may be too coarse to represent actual gear teeth, clutch plates, cams, hammers, springs or levers.
- Sparse trajectory samples may miss transient collision.
- Axial intervals depend on an approved datum and complete stack-up.
- Nominal centre distance does not establish tooth contact or backlash.
- Support references do not prove structural capacity or bearing life.
- No CAD rendering, continuous collision detection, tolerance Monte Carlo, FEA, strength, fatigue, wear, lubrication, efficiency or timekeeping impact is calculated.
- No chronograph architecture, physical gear train, plate layout or case geometry is selected.

## 12. Revision control and disposition

| Revision | Date | Change | Approval |
|---|---|---|---|
| A | 2026-11-27 | Initial evidence-gated physical placement, axial envelope, gear-centre, support-reference, motion-screening and OpenSCAD envelope framework | Pending independent engineering review |

**Disposition:** WP-40 establishes the controlled physical-layout screening method only. C-01 coordinates, gear schedule, support design, tolerances, materials and assembly remain unfrozen. No physical build, merge or deployment is authorized.
