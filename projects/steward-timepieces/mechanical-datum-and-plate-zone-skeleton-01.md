# STEWARD C-01 — Mechanical Datum and Plate-Zone Skeleton 01

**Revision:** 0.1  
**Status:** Conceptual engineering skeleton; not CAD or a production drawing  
**Branch:** `steward/c-01-movement-foundation`

## Purpose

Establish a shared coordinate and evidence framework that links the three dial concepts to one underlying movement architecture. This is the next packaging layer after the dial-layout generator.

## Datum convention

- Origin O=(0,0): nominal dial/movement center.
- +X: 3 o'clock; +Y: 12 o'clock.
- Z=0: dial plane; positive Z points toward the movement side.
- Positive angles are counter-clockwise when viewed from the dial side.
- XY values are normalized to a provisional dial-opening radius R=1. They are not millimetres.

The central time/chronograph axis is provisionally represented at O. Actual coaxiality, arbor diameters, tube geometry, bearing support and Z-stack are unresolved. Barrel, balance, calendar-drive and other shaft axes remain TBD until derived from a measured reference, a selected architecture or verified CAD.

## Shared movement-side reservations

All three dial concepts share the same conceptual core reservations:

| Zone | Function | Evidence status |
|---|---|---|
| Barrel reservation | Mainspring barrel and service access | Provisional |
| Going-train corridor | Train path; wheel centers not selected | Provisional |
| Balance reservation | Balance, escapement and shock-setting access | Provisional |
| Chronograph reservation | Drive, coupling, control and counters | Provisional |
| Rotor sweep | Rotor plane reservation | Provisional |
| Calendar mechanism | Weekday/date discs and indexing | Provisional |

The script stores these as normalized rectangles. Their positions and extents are illustrative placeholders, not inferred component dimensions.

## Three linked dial candidates

- **A:** three-register arrangement with paired weekday/date at 3.
- **B:** registers at 3, 6 and 9 with paired weekday/date at 12.
- **C:** traditional counter axes with compact paired calendar near 12.

Each candidate uses the same core movement-side reservations. Candidate C carries an explicit upper calendar/register review note. The current overlap warnings are 2D same-layer rectangle intersections only; they are not a substitute for physical clearance analysis.

## Plate and bridge separation — current architectural proposal

The model separates conceptual layers, not finished plates:

1. **Dial side:** calendar display, calendar indexing interface, motion works and any dial-side chronograph elements.
2. **Movement side:** barrel, going train, balance/escapement, chronograph drive/control/counters and winding works.
3. **Rotor plane:** rotor sweep reservation, winding interface and caseback clearance.

A later bridge map should identify removable bridge groups, screw access, jewel supports, assembly sequence and service dependencies. No bridge outlines, thicknesses, screw coordinates or plate thickness are assigned in this revision.

## Evidence labels

Every future dimensional parameter must be tagged as one of:

- `measured`: directly measured from a documented physical sample or prototype.
- `calculated`: derived from an explicit equation and cited inputs.
- `supplier_confirmed`: supported by a named supplier drawing/specification and revision.
- `provisional`: a design placeholder awaiting evidence.
- `TBD`: not yet assigned.

Do not silently promote a provisional value to a measured or calculated value. Record source, date, method, uncertainty and revision when evidence becomes available.

## Executable artifacts

- `tools/c01_mechanical_layout.py`: builds a JSON model and three schematic SVG sheets.
- `tools/test_c01_mechanical_layout.py`: unit tests for candidate consistency, evidence labels, layer-aware overlap logic and unresolved axes.

Run from the tools directory:

```bash
python c01_mechanical_layout.py --output-dir ../../build/c01-mechanical-layout
python -m unittest test_c01_mechanical_layout.py
```

## Limits and next gate

This is a 2D conceptual reservation model. It does not establish gear ratios, tooth counts, gear mesh, torque, spring geometry, jewel locations, material selection, plate stiffness, component thickness, hand-stack height, axial endshake, tolerances, manufacturability or physical fit. A detected rectangle overlap is a review flag; absence of overlap does not prove clearance.

Next engineering gate:
1. Select or acquire a documented reference movement for teardown study.
2. Record actual case/dial opening and hand-stack constraints.
3. Measure candidate shaft axes and component envelopes with traceable methods.
4. Convert normalized coordinates to millimetres only after the reference envelope is approved.
5. Build a dimensioned 2D/3D CAD assembly with explicit XY and Z clearances.
6. Compare bridge/plate partitioning against assembly and service sequence.
7. Revisit energy budget and chronograph loading before freezing barrel and train placement.

**Release statement:** No movement dimensions, plate geometry, bridge geometry or manufacturing instructions are frozen. No production or prototype-fit claim is made.
