# STEWARD C-01 — WP-20 Integrated Parametric Movement Layout

**Document ID:** C01-WP-20  
**Revision:** 0.1  
**Status:** Integrated functional layout baseline; physical geometry remains open  
**Branch:** `steward/c-01-movement-foundation`  
**Predecessors:** WP-14 through WP-19 and the existing dial, datum and packaging studies  
**Next gate:** controlled envelope and datum; selected candidate architecture; dimensioned component and interface register

## 1. Purpose

WP-20 consolidates C-01's major functional subsystems into one machine-readable movement-layout baseline. It connects the going train, regulation, automatic winding, time display, chronograph, calendar, structure and case interfaces.

The package is intentionally two-layered:
1. **Functional architecture:** identifies required components and interfaces without asserting physical adjacency or choosing a topology.
2. **Candidate geometry:** accepts explicit component envelopes, XY positions, Z intervals and gear meshes for preliminary clearance checks.

No component positions, movement diameter, case diameter, plate thickness, gear module, tooth counts, component radii, materials or tolerances are invented. The baseline is not a dimensioned CAD assembly and does not establish physical fit.

## 2. Design basis carried forward

The functional indication baseline includes:
- hours and minutes;
- continuous running seconds;
- central chronograph seconds;
- 30-minute chronograph totalizer;
- 12-hour chronograph totalizer;
- weekday;
- day of month (1–31).

The design frequency target carried from prior work is 4 Hz / 28,800 vph. The 60–70 hour reserve remains an aspiration, not a demonstrated result. Neither value is converted into geometry by WP-20.

The user's month-window preference remains a separate scope decision. No month display or month mechanism is silently added to the C-01 component baseline.

## 3. Integrated subsystem register

| Subsystem | Included functional elements | Key open geometry |
|---|---|---|
| Energy | Mainspring barrel and arbor | Barrel envelope, arbor and torque curve |
| Automatic winding | Rotor, reverser/reduction works | Rotor sweep, support, winding interfaces |
| Going train | Center, third and fourth wheels | Tooth system, arbor axes, bridge supports |
| Regulation | Escape wheel, pallet assembly, balance | Balance envelope, escapement geometry, shock clearance |
| Time display | Motion works, hour/minute stack, running seconds | Hand stack, dial clearance, seconds take-off |
| Chronograph drive | Source take-off, reduction train, clutch | Source axis, clutch orientation and mesh geometry |
| Chronograph control | Start/stop/reset, brake, reset hammers/hearts | Lever sweep, spring reservations, pusher interface |
| Chronograph indications | Central seconds, 30-minute, 12-hour counters | Counter axes, indexing architecture, hand/scale envelopes |
| Calendar | Drive, weekday and date displays | Disc diameters, jumpers, changeover and corrector paths |
| Structure | Main plate and bridges | Datum, bearing locations, stiffness, screws and assembly order |
| Case interface | Stem, supports, pushers and caseback envelope | Case geometry, stem height, pusher axes, casing clearances |

The executable baseline assigns each functional item an identifier, zone, and explicitly TBD geometry fields. This is a controlled starting register, not a claim that each function has a separate physical part or bridge.

## 4. Functional interface map

The model records candidate relationships for:
- barrel to going train;
- going train to escapement and time display;
- rotor through winding works to barrel;
- candidate going-train source to chronograph drive;
- chronograph drive through clutch to central seconds and totalizers;
- control to clutch and brake;
- reset mechanism to all chronograph indications;
- calendar drive to weekday and date indications.

These interfaces describe functional relationships only. In particular, the fourth-wheel/seconds-arbor connection to the chronograph is marked candidate, not selected. The final physical path may require intermediate wheels, coaxial elements, idlers or a dedicated drive.

The interface validator requires unique component IDs, valid endpoints and no self-connections or duplicate typed interfaces. It does not infer a power path, gear ratio or shaft geometry.

## 5. Layout coordinate convention

The inherited dial-side convention is retained:
- origin at nominal movement/dial center;
- +X toward 3 o'clock;
- +Y toward 12 o'clock;
- millimetres only when a controlled dimension establishes scale;
- all Z positions referenced to one approved axial datum.

Normalized dial coordinates x/R and y/R remain useful for concept comparison. They cannot become physical millimetres until the dial-opening radius R is controlled.

Each component geometry record ultimately needs:
- unique component ID;
- XY center in mm;
- conservative XY envelope radius or a more detailed CAD profile;
- Z minimum and maximum in mm;
- named functional layer;
- evidence status and source drawing/model revision;
- tolerance and owner/reviewer in the controlled engineering register.

## 6. Candidate display and packaging architecture

### 6.1 Dial arrangements

The model carries the existing alternatives without selecting one:
- **A:** upper 30-minute counter, lower 12-hour counter, running seconds at 9, paired weekday/date at 3.
- **B:** 30-minute counter at 3, 12-hour counter at 6, running seconds at 9, paired weekday/date at 12.
- **C:** conventional 12/6/9 registers with a compact paired calendar near 12.

All are concept positions, not physical XY coordinates. The actual dial opening, subdial diameters, window apertures, hand lengths and calendar-disc geometry are still needed.

### 6.2 Packaging families

Three broad packaging families are retained:
- **Horizontal/lateral:** chronograph components predominantly arranged in the main movement plane.
- **Vertical/coaxial:** selected components share axes or occupy additional axial layers.
- **Hybrid/layered:** a mixture intended to balance footprint, stack height and service access.

These are comparison categories, not final designs. They must be evaluated against total movement height, friction, reset behavior, bridge stiffness, adjustment access, assembly sequence and serviceability.

## 7. Executable model

Files:
- `tools/c01_integrated_layout.py`
- `tools/test_c01_integrated_layout.py`

The model:
- emits the complete functional component and interface baseline;
- preserves dial arrangements A/B/C and packaging families as unselected candidates;
- validates component IDs and interface endpoints;
- accepts optional geometry for any component;
- evaluates only the subset with complete XY, circular-envelope and Z-interval inputs;
- reports missing geometry explicitly;
- can evaluate explicitly supplied gear meshes using the WP-19 geometry helper;
- always reports overall fit as not certified.

### Verification command

From `projects/steward-timepieces/tools`:

```bash
python -m unittest test_c01_integrated_layout.py
```

The unit tests use synthetic fixtures to test register validation and geometry gating. They are not C-01 component dimensions or a proposed physical arrangement.

## 8. Calculations and acceptance criteria

For a supplied circular-envelope pair A/B with overlapping axial intervals:

[
d_{xy}=\sqrt{(x_A-x_B)^2+(y_A-y_B)^2}
]

[
c_{xy}=d_{xy}-(r_A+r_B)
]

A negative value flags overlap of the simplified envelopes; zero is tangency; positive is nominal planar clearance. This is only evaluated when the Z intervals overlap. It is not a tolerance-aware clearance proof.

For each supplied standard external spur-gear mesh, WP-19 calculates:

[
a_{nominal}=\frac{m(z_1+z_2)}{2}
]

and compares it with the center distance derived from the supplied XY coordinates and explicit tolerance.

| ID | Acceptance criterion | Evidence |
|---|---|---|
| WP20-INT-01 | All required functional component IDs appear exactly once | Unit test and register audit |
| WP20-INT-02 | All interface endpoints resolve to registered components | Unit test |
| WP20-INT-03 | No unknown or duplicate interface is accepted | Unit test |
| WP20-INT-04 | Missing geometry is reported as not evaluable/incomplete, never as fit | Unit test |
| WP20-INT-05 | Only fully specified component envelopes are passed to clearance evaluation | Unit test and code review |
| WP20-INT-06 | Display and packaging alternatives remain explicitly unselected | Unit test and decision review |
| WP20-INT-07 | No physical-fit certification is emitted | Output review |
| WP20-INT-08 | Future geometry has controlled datum, evidence and source revision | CAD and engineering review |

## 9. Required engineering inputs before a physical layout

The next physical layout cannot be responsibly dimensioned until the following are established:
1. Case internal envelope, movement target envelope and dial-opening dimensions.
2. Axial datum, dial plane, hand-stack height and caseback/rotor clearance.
3. Display arrangement selection and register/window size requirements.
4. Actual source arbor speed and measured torque margin for the chronograph.
5. Selected gear system, module, tooth counts, profile and manufacturing constraints.
6. Clutch and control architecture, including lever/hammer swept envelopes.
7. Calendar disc diameters, indexing loads and corrector arrangement.
8. Balance/escapement and automatic winding component geometry.
9. Bearing, pivot, bridge, screw, tolerance and service-access requirements.

No values are assumed in place of these inputs.

## 10. Revision control

| Revision | Date | Change | Status |
|---|---|---|---|
| 0.1 | 2026-11-26 | Initial integrated component/interface baseline and evidence-gated candidate geometry evaluator | Preliminary; review required |

## 11. Current decision status

- Functional component register: **defined**.
- Functional interface register: **defined; physical paths remain candidates**.
- Dial arrangements A/B/C: **open**.
- Horizontal/lateral, vertical/coaxial and hybrid packaging: **open**.
- Chronograph take-off and clutch: **open**.
- Gear train and arbor coordinates: **open**.
- Calendar and month-window scope: **open**.
- Case/movement envelope and axial datum: **open**.
- Dimensioned CAD and physical fit: **not established**.

---
**Engineering integrity statement:** WP-20 is an integrated functional layout baseline and geometry-input framework. It is not a dimensioned movement, CAD assembly, validated fit, prototype or manufacturing release.
