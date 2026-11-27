# STEWARD C-01 — WP-21 Master Datum, Plate and Bridge Architecture

**Document ID:** C01-WP-21  
**Revision:** 0.1  
**Status:** Preliminary structural control architecture; no physical geometry frozen  
**Branch:** `steward/c-01-movement-foundation`  
**Predecessors:** WP-14 preliminary movement architecture; WP-19 chronograph spatial layout; WP-20 integrated parametric movement layout; existing datum, plate-zone and packaging studies  
**Next gate:** controlled case/movement envelope, datum realization, bearing-axis evidence and dimensioned structural CAD skeleton

## 1. Purpose

WP-21 establishes the structural reference framework needed to turn WP-20's functional movement layout into a controlled, buildable spatial definition. It defines the master datum register, axial reference planes, structural zones, bearing/arbor-axis register, bridge-support register, stack-check protocol and assembly/serviceability gates.

This is a control architecture and parametric register, not a dimensioned plate design, CAD assembly, manufacturing drawing or physical-fit certification.

## 2. Design basis and preserved decisions

The functional component and interface baseline remains WP-20. Its 25 component roles and 23 functional interfaces are not redefined here. WP-21 introduces structural control references that may later be linked to those components.

The following remain open and are not selected by WP-21:
- dial display arrangement A, B or C;
- horizontal/lateral, vertical/coaxial or hybrid chronograph packaging;
- vertical friction clutch or horizontal/lateral coupling;
- column-wheel or cam/lever control;
- continuous or jumping totalizers;
- month-window scope (not part of the current C-01 baseline);
- movement/case envelope and all component geometry.

No dimensions, coordinates, plate thicknesses, bridge count, bearing size, arbor position, fastener location, material or clearance is assigned.

## 3. Master datum system

The register establishes identifiers, not numerical locations. M0 is the controlled master axial datum identifier; its physical realization, sign convention and measured location remain TBD until the case/movement interface and datum strategy are approved.

| Datum ID | Controlled reference | Intended use | Numerical value |
|---|---|---|---|
| M0 | Master axial datum | Primary axial reference for all movement stack dimensions | TBD |
| DIAL | Dial reference plane | Dial, hand and dial-side calendar stack | TBD |
| PLATE_TOP | Main-plate upper face | Going-train and dial-side structural reference | TBD |
| PLATE_BOTTOM | Main-plate lower face | Rotor/caseback-side structural reference | TBD |
| BRIDGE_UNDERSIDE | Bridge underside plane | Wheel, arbor and bridge clearance | TBD |
| BRIDGE_TOP | Bridge upper face | Movement height and case clearance | TBD |
| ROTOR_PLANE | Automatic rotor operating plane | Rotor sweep and bridge/caseback clearance | TBD |
| CASEBACK_INNER | Caseback inner surface | Case interface and rotor clearance | TBD |

All axial offsets shall be signed distances from M0 in millimetres after the datum convention is approved. A datum value may only be populated with a source drawing, controlled CAD revision, supplier drawing or measured inspection record. Every populated value requires evidence and source revision. A blank or TBD value is not zero.

## 4. Structural zone architecture

The following zones are functional partitions, not fixed plate or bridge outlines:

| Zone | Structural responsibility | Required future definition |
|---|---|---|
| Main plate | Primary structural body and bearing datum | Perimeter, thickness, bearing seats, mounting and datum features |
| Going train | Barrel-to-escapement wheel/arbor support | Axis locations, endshake, wheel clearances and bridge support |
| Regulation | Balance, hairspring, escapement and shock system | Dynamic envelope, shock travel, regulator access and service clearance |
| Chronograph | Drive, clutch, controls, brake, counters and reset | Selected topology, pivots, bridge support and adjustment access |
| Calendar/dial side | Weekday/date works and indication stack | Dial clearance, jumper access, correction mechanism and safe setting window |
| Automatic winding | Rotor, reverser and winding train | Rotor sweep, bearing/support, winding works and caseback clearance |
| Dial display | Hands, central arbors and registers | Hand heights, coaxial clearances and dial/window interfaces |
| Case interface | Stem, pushers, casing supports and caseback | Case envelope, stem/pusher alignment and casing tolerances |

Zone boundaries must be explicitly defined in CAD. A zone label alone does not establish physical separation.

## 5. Main plate and bridge strategy

The main plate is the primary structural datum carrier. Its bearing seats, locating features and case attachment interfaces must be dimensioned from the approved master datum scheme. Plate material, thickness, local reinforcement and manufacturing process remain open pending loads, stiffness, thermal, corrosion, wear and manufacturability studies.

Bridges and cocks shall be partitioned by functional support and service sequence, not by an assumed bridge count. The bridge register records:
- unique bridge identifier and functional zone;
- the component/arbor set supported;
- evidence and source revision;
- later-defined locating features, fasteners, thickness, stiffness and removal direction;
- whether removal exposes a serviceable subsystem without disturbing unrelated calibrated assemblies.

No bridge is considered designed merely because its support assignment is listed. The eventual structure must be checked for stiffness, deflection, bearing alignment, screw access, tool access, assembly order and service repeatability.

## 6. Bearing and arbor-axis register

Each bearing/arbor entry must carry a unique register ID, linked WP-20 component ID, controlled axis ID, support type, evidence and source revision. Optional XY coordinates and axial intervals may be populated only from controlled geometry.

The register deliberately does not infer:
- jewel or bearing diameter;
- pivot diameter, length or shoulder geometry;
- radial or axial clearance;
- endshake or sideshake;
- bearing material or press fit;
- load capacity, friction or lubrication.

A bearing axis is accepted for layout freeze only when its source geometry, datum references, tolerance, support arrangement and inspection method are approved.

## 7. Axial stack and clearance method

For two supplied axial intervals in the same declared zone:

[
I_A=[z_{A,min},z_{A,max}],quad
I_B=[z_{B,min},z_{B,max}]
]

A positive interval overlap is:

[
Delta z=min(z_{A,max},z_{B,max})-max(z_{A,min},z_{B,min})
]

An overlap is reported only when (Delta z>0). Touching faces produce zero overlap, not proof of acceptable running clearance. Required clearance must be separately specified and tolerance-adjusted.

The evaluator only compares explicitly supplied intervals within the same declared zone. Different zones can still intersect physically. It does not calculate a tolerance stack, deflection, thermal growth, swept motion, gear-tooth interference, shock travel or assembly clearance. A clean result is not a fit certification.

## 8. Assembly and service-access strategy

The detailed assembly sequence remains a controlled design output. At minimum, future reviews must demonstrate:
1. main plate can be fixtured and inspected from stable datum features;
2. going-train wheels and pivots can be installed without forced bending or damage;
3. balance/escapement can be installed, adjusted and removed with controlled access;
4. chronograph clutch, brake, control and reset components can be adjusted and serviced;
5. calendar and dial-side parts can be installed and corrected without damaging hands or discs;
6. rotor and winding components can be installed and removed without compromising the train;
7. bridges can be removed in a documented order without uncontrolled release of springs or jumpers;
8. screws, pushers, stem and casing interfaces are accessible with specified tools;
9. service operations preserve calibration or define mandatory re-checks.

A service-access claim requires a CAD tool-path/access study or physical assembly demonstration, not a textual assumption.

## 9. Engineering calculations and assumptions

The executable helper `tools/c01_structure_layout.py` provides:
- baseline datum and structural-zone registers with values intentionally unassigned;
- uniqueness and reference validation for datums, bearing axes and bridges;
- optional checks for supplied XY coordinates and positive axial intervals;
- component-reference checks against WP-20 component IDs when provided;
- axial interval overlap detection with explicit evidence/provenance.

It performs no structural stress, plate deflection, bearing-load, gear-train, dynamic rotor, tolerance-stack or CAD calculation. No numerical design result is claimed.

## 10. Acceptance criteria

| ID | Acceptance criterion | Evidence required |
|---|---|---|
| WP21-AC-01 | One approved master datum and sign convention are controlled | Approved datum drawing/CAD and revision |
| WP21-AC-02 | All required axial reference planes are defined or explicitly dispositioned | Datum register and interface review |
| WP21-AC-03 | Every bearing/arbor axis resolves to a WP-20 component and controlled source | Axis register, drawing/CAD and source revision |
| WP21-AC-04 | Main plate and bridge support assignments are complete | Structural register and review |
| WP21-AC-05 | Rotor, balance, chrono and calendar envelopes are dimensioned | Supplier/measurement/CAD evidence |
| WP21-AC-06 | Critical clearances include tolerances and dynamic allowances | Tolerance stack and swept-envelope analysis |
| WP21-AC-07 | Assembly and service access are demonstrated | CAD access study or physical build record |
| WP21-AC-08 | Structural stiffness and bearing alignment are acceptable | Analysis and inspection plan |
| WP21-AC-09 | All open architecture choices are formally resolved before freeze | Signed design review and decision record |

WP21-AC-01 through AC-09 are not passed by this preliminary package. They define the evidence required for later acceptance.

## 11. Verification plan

Run from the tools directory:

```bash
python -m unittest test_c01_structure_layout.py
```

The tests cover baseline datum control, no-invented-geometry behavior, unique datum enforcement, master-datum reference validation, bearing/bridge component references, positive axial interval overlap, touching intervals and provenance requirements. Test fixtures are synthetic software fixtures, not C-01 design values.

## 12. Risks and controls

| Risk | Control |
|---|---|
| Datum ambiguity propagates into every component | Freeze M0 and sign convention before dimensioning |
| Plate/bridge geometry is optimized before load paths are known | Complete load, stiffness and serviceability studies |
| Bearing axes drift between drawings and CAD | Single controlled axis register and revision traceability |
| Chronograph stack collides with calendar or hand stack | Integrated tolerance-aware 3D and swept-envelope review |
| Rotor or balance dynamic envelope is underestimated | Include operating, shock and service envelopes |
| Service requires unnecessary disassembly | Validate access and removal paths before architecture freeze |
| Nominal clearances conceal tolerance or deflection failure | Include manufacturing, assembly, thermal and operating allowances |

## 13. Revision control

| Revision | Change | Status |
|---|---|---|
| 0.1 | Initial master datum, structural zone, bearing-axis, bridge and stack-control framework | Preliminary; no geometry frozen |

Changes to datum definitions, zone responsibilities, bearing-axis assignments, bridge support or stack limits require a revision entry and traceable design-review disposition.

## 14. WP-21 exit gate

WP-21 exits preliminary status only when the master datum is approved, the movement/case envelope is controlled, component axes and structural supports are traceable, the plate/bridge split is dimensioned, tolerance-aware clearance and deflection checks are complete, and assembly/service access has been demonstrated. Until then, the model remains a structural architecture register—not a finished movement design.
