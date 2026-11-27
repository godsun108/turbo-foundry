# STEWARD C-01 — WP-14 Preliminary Movement Architecture and Layout

**Document ID:** C01-WP-14  
**Revision:** 0.1  
**Status:** Preliminary spatial architecture; no dimensions or architecture frozen  
**Branch:** `steward/c-01-movement-foundation`  
**Predecessors:** WP-08 through WP-13; Dial-Side Display Arrangement Study 01; Mechanical Layout and Packaging Study 01; Mechanical Datum and Plate-Zone Skeleton 01; Preliminary Mechanical Architecture 01  
**Next gate:** traceable reference geometry, dimensioned CAD skeleton, and subsystem placement review

## 1. Purpose

WP-14 consolidates the existing C-01 display, mechanical packaging, datum, kinematic and subsystem studies into one spatial-architecture work package. It establishes how the movement will be laid out, what geometry must be controlled, how candidate dial arrangements remain linked to the underlying movement, and which evidence is required before dimensions can be promoted.

This package deliberately does not replace the existing dial-side study or mechanical layout generator. It defines their next engineering gate and adds a measurement-driven envelope/stack calculation helper. It is not a finished CAD assembly, production drawing, supplier specification, or physical-fit certification.

## 2. Existing design baseline and preservation

The branch already contains:
- `dial-side-display-arrangement-study-01.md`: dial concepts A, B and C, display hierarchy, coordinate convention and normalized coordinates;
- `mechanical-layout-and-packaging-study-01.md`: functional zones, packaging constraints, assembly/service path and reference-movement strategy;
- `mechanical-datum-and-plate-zone-skeleton-01.md`: XY/Z datum convention, layer separation and evidence labels;
- `preliminary-mechanical-architecture-01.md`: integrated architecture direction and unresolved subsystem choices;
- `parametric-dial-layout-generator-01.md` and `tools/c01_dial_layout.py`: normalized dial layout generator;
- `tools/c01_mechanical_layout.py`: shared movement reservations and three candidate SVG/JSON outputs.

WP-14 preserves these files and their A/B/C alternatives. The new helper does not silently alter their provisional coordinates or choose a display arrangement.

## 3. Controlled functional and display baseline

C-01 remains:
- automatic mechanical winding;
- hours and minutes;
- weekday and day-of-month;
- central chronograph seconds;
- 30-minute and 12-hour chronograph registers;
- continuous running seconds.

The central chronograph seconds hand and ordinary running seconds remain separate indications. The 4 Hz / 28,800 vph frequency remains a preliminary target. The 60–70-hour reserve remains aspirational. No movement diameter, height, shaft coordinate, component envelope, gear center distance, hand height or tolerance is approved by WP-14.

The month-window preference remains an open C-01/LUNAR scope decision. WP-14 does not add a month display or moon-phase mechanism to the C-01 baseline.

## 4. Spatial architecture and datum

### 4.1 Common coordinate system

Use the existing controlled convention:
- XY origin: nominal central hour/minute/chronograph axis;
- +X: 3 o'clock; +Y: 12 o'clock;
- Z=0: approved dial plane;
- positive Z: movement side;
- positive angular direction: counter-clockwise viewed from dial side.

The origin is a functional datum convention, not proof that all central hands share one arbor or that their coaxial stack is feasible. Arbor/tube geometry, bearing support and hand heights must be defined in the axial stack study.

### 4.2 Required physical layers

Maintain separate but linked geometry for:
1. Dial/display layer: dial, apertures, calendar displays, registers, hands and hand sweep.
2. Dial-side mechanism layer: calendar discs, indexing works, motion works and any dial-side chronograph components.
3. Main movement layer: barrel, going train, escapement, balance, chronograph drive/control/counters and bridges.
4. Automatic winding layer: rotor, bearing/support and winding/reversing works.
5. Case interface layer: movement supports, stem, pushers, caseback, crystal and clearances.

A component may occupy more than one functional subsystem but must have one controlled part identity, datum reference and assembly revision.

## 5. Layout strategy

### 5.1 Preserve three dial candidates

| Candidate | Register arrangement | Calendar arrangement | Status |
|---|---|---|---|
| A | 30-minute at 12, 12-hour at 6, running seconds at 9 | Paired weekday/date at 3 | Open |
| B | 30-minute at 3, 12-hour at 6, running seconds at 9 | Paired weekday/date at 12 | Open |
| C | Registers at 12, 6 and 9 | Compact paired calendar near 12 | Open; upper-zone interaction flagged |

All three are visual/packaging candidates. Their normalized rectangles are not dimensions. Do not rank or freeze them until comparable actual-size dial mock-ups and mechanical-axis feasibility checks are complete.

### 5.2 Movement-side placement principles

- Treat barrel, balance, going train, chronograph and calendar as reserved functional zones until actual part geometry and torque paths are known.
- Keep balance/escapement access available for regulation and service.
- Make the chronograph clutch/control works inspectable and serviceable; evaluate whether rotor removal is required for access.
- Keep the calendar assembly independently serviceable where feasible, without assuming a modular plate until assembly studies justify it.
- Ensure rotor sweep, bearing support and caseback clearance are analyzed in the rotor plane, not inferred from the dial-side drawing.
- Define the stem and pusher axes from a controlled case interface, not from visual dial symmetry alone.

These are layout requirements, not final physical placements.

## 6. Plate and bridge architecture

The first CAD skeleton shall distinguish:
- Main plate and fixed datum features.
- Barrel bridge/support.
- Going-train bridge/support.
- Balance/escapement cock or bridge.
- Chronograph bridge and removable control/coupling access.
- Calendar retaining plate/bridge.
- Automatic winding bridge and rotor support.

This list is a candidate partition only. Components may be combined or separated after stiffness, jewel support, assembly order, lubrication, access and service trials. No bridge outline, thickness, screw location, jewel seat or plate material is assigned.

For each proposed bridge, record supported pivots/components, screw and locating features, assembly/removal direction, tool access, adjustment access, and which subsystems must be removed first.

## 7. Geometry control and evidence classes

Every critical spatial parameter must include:
- parameter/part/interface ID;
- value and unit;
- coordinate or datum reference;
- evidence class: measured, calculated, supplier-confirmed, provisional or TBD;
- source document/file and revision;
- method, instrument and uncertainty where measured;
- owner/reviewer and change history.

A measured shaft axis must identify the sample and measurement method. A supplier-confirmed dimension must identify the exact caliber/part variant and drawing revision. A calculated coordinate must identify the equation and source inputs. A provisional reservation must never be presented as a physical fit result.

## 8. Executable envelope and axial checks

New helper: `tools/c01_architecture_envelope.py`.

It provides:
- conversion from normalized dial coordinates to millimetres only when an explicit opening radius is supplied;
- conservative rectangular-zone corner check against a circular opening;
- Z-interval intersection flags for components sharing a declared layer;
- critical arbor-axis register validation and source/evidence checks.

The calculations do not prove fit. The 2D corner check does not check neighboring components, hands, case geometry, tolerance, deformation or other layers. The Z-interval helper checks axial overlap only; it does not establish XY collision or a valid assembly. A no-overlap result is not a clearance certification.

The unit tests use synthetic values solely to test arithmetic and input validation. No test fixture represents a C-01 dimension.

Run from the tools directory:

```bash
python -m unittest test_c01_architecture_envelope.py
```

## 9. Required CAD model structure

The first controlled CAD assembly should contain:
- master XY and Z datums;
- case, dial, crystal and caseback reference surfaces;
- stem and pusher axes;
- central display axis and candidate subdial/calendar axes;
- measured reference movement envelope, if obtained;
- provisional barrel, balance, train, chronograph, calendar and rotor zones;
- separate dial-side, main movement and rotor layers;
- component envelope solids with part IDs and evidence tags;
- critical clearances and tolerance variables.

Begin with a skeleton and envelope bodies. Do not create detailed teeth, springs, escapement surfaces or production geometry until source dimensions, selected ratios and subsystem architecture are available.

## 10. Verification and review matrix

| ID | Review / test | Required evidence | Acceptance |
|---|---|---|---|
| LAY-001 | Datum integrity | Approved XY/Z datum drawing and source references | All axes traceable |
| LAY-002 | Dial candidate legibility | Comparable 1:1 printed mock-ups and review record | Criteria approved before review |
| LAY-003 | Shaft-axis closure | Measured/supplier-confirmed axes with uncertainty | Critical axes resolved |
| LAY-004 | Envelope conversion | Approved dial opening and controlled coordinate inputs | No unapproved scale conversion |
| LAY-005 | Planar packaging | CAD interference/clearance analysis across all relevant layers | Approved clearance limits |
| LAY-006 | Axial stack | Datum-consistent component heights and tolerance stack | Approved limits |
| LAY-007 | Rotor/caseback | Rotor sweep, deflection, shock and caseback geometry | Clearance verified |
| LAY-008 | Bridge/service access | Assembly sequence and service-tool access review | Independent watchmaker review |
| LAY-009 | Case interface | Stem, pusher, support and sealing interface drawing | Case interface approved |
| LAY-010 | Configuration traceability | Part/drawing revision and source register | No untracked critical geometry |

Numerical acceptance criteria remain TBD until the case, component geometry, manufacturing process and service requirements are defined.

## 11. Critical risks and mitigations

| Risk | Effect | Mitigation |
|---|---|---|
| Normalized placeholders mistaken for dimensions | Invalid CAD or supplier assumptions | Evidence labels, source IDs and explicit unit conversion gate |
| Dial selected before movement-axis closure | Display/gear-train incompatibility | Keep A/B/C in parallel until both reviews pass |
| Z-stack closed without common datum | False clearance result | Datum-controlled axial register and tolerance analysis |
| Rotor overlaps service-critical components | Poor service access or interference | Rotor removal/service sequence review |
| Bridge partition driven by appearance | Weak support or difficult assembly | Pivot support, stiffness and service review |
| Case/pusher axes inferred from dial symmetry | Stem/control misalignment | Case interface drawing and measured case data |
| Month indication silently enters C-01 | Added complexity and energy/space demand | Formal scope decision before requirement change |

## 12. Architecture freeze gate

No detailed architecture freeze until:
- requirements and month-window scope decision are controlled;
- one dial candidate is selected after visual and mechanical review;
- movement envelope and case interface are supported by traceable data;
- critical shaft axes and gear-train centers are dimensioned;
- barrel, balance, escapement, chronograph and calendar component envelopes are reconciled;
- XY and Z clearances/tolerance stacks are reviewed;
- rotor sweep, bearing support and service access are closed;
- bridge/plate partition and assembly sequence are independently reviewed;
- energy and torque interfaces are reconciled with WP-13;
- critical parts, materials, lubrication and supplier constraints are reviewed.

A missing item remains an open gate. This document does not authorize production drawings or prototype claims.

## 13. Revision history

| Revision | Date | Change |
|---|---|---|
| 0.1 | 2026-11-26 | Initial spatial architecture consolidation and evidence-gated envelope/stack calculation helper |

## 14. Engineering status

WP-14 establishes a controlled route from normalized concept zones toward dimensioned CAD. It does not select A, B or C; assign a C-01 diameter or height; freeze bridge geometry; validate fit; or claim a manufactured prototype.
