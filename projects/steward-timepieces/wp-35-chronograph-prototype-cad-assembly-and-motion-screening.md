# WP-35 — Chronograph Prototype CAD Assembly and Mechanism Motion Screening

- Document ID: SEB-C01-WP-35
- Revision: A — initial controlled issue
- Status: Evidence-gated CAD envelope and motion-screening framework; no C-01 physical geometry released
- Branch: steward/c-01-movement-foundation
- Software: tools/c01_chrono_cad_simulation.py
- Verification: tools/test_c01_chrono_cad_simulation.py
- Dependencies: WP-19, WP-20, WP-22, WP-23, WP-24, WP-30, WP-32, WP-33, WP-34

## 1. Purpose and boundary

WP-35 establishes a repeatable route from controlled component geometry to a chronograph candidate assembly and sampled motion-clearance review. It formalizes the data needed to visualize fixed and moving component envelopes and to check a start/stop/resume/reset functional sequence.

No production dimensions, coordinates, tooth counts, cam profiles, pivot locations, material properties, forces, speeds, tolerances or acceptance limits are supplied. No candidate architecture is selected. The model is a screening aid and is not a substitute for a parametric solid CAD assembly, contact simulation, tolerance analysis or physical prototype.

## 2. Assembly datum and component register

All geometry shall follow the WP-14/WP-20 XY convention and the approved WP-21 M0 axial datum realization. Units are millimetres. Every body requires:
- unique component ID and functional kind (fixed, rotating, translating or envelope-only);
- explicit circular envelope radius and Z interval;
- sampled XY position and angular pose values on a common time base;
- evidence ID and source revision;
- parent assembly candidate ID and global provenance.

Circular envelopes are conservative simplifications only where their radius actually bounds the component. Gear teeth, eccentric cams, hammer faces, levers, springs, hands, pivots and non-circular parts require suitable swept-solid CAD before their interference can be assessed. Angular pose is retained in the input record but circular-envelope checks do not use it to infer geometry.

## 3. Motion and state sequence

The initial kinematic scenario shall cover:
1. stopped at zero;
2. start actuation and clutch engagement;
3. running chronograph;
4. stop actuation and retained elapsed indication;
5. resumed running from retained indication;
6. reset actuation while stopped;
7. reset completion at zero;
8. attempted reset while running, confirming positive mechanical blocking.

WP-35's sequence validator checks the core state order (zero, running, stopped-retained, resumed running, zero) and requires a physical interlock test reference. It cannot prove that the hardware interlock works. The separate attempted-reset-while-running test remains mandatory in the WP-30 physical verification record.

For motion clearance, every body trajectory must be sampled on a common time base. Asynchronous source trajectories must be resampled by the engineer and the resampling method recorded. The current screening model compares corresponding sample indices only; it does not interpolate between them.

## 4. Sampled clearance method

For circular planar envelopes A and B whose axial intervals overlap:

    c(k) = sqrt((xA(k)-xB(k))^2 + (yA(k)-yB(k))^2) - rA - rB

A negative value indicates overlap at that sampled instant. A zero value indicates tangency. Pairs with non-overlapping Z intervals are not reported as planar collisions by this model.

The minimum sampled clearance and sample index are reported for each pair. A clear result means only that no overlap was detected at the supplied samples under the simplified circular-envelope model. It does not prove continuous-path clearance, non-interference of actual solids, clearance under tolerance, elastic deflection, shock, wear or lubrication-film adequacy.

## 5. CAD visualization handoff

The OpenSCAD source generator creates a simple cylindrical envelope visualization from the first supplied pose of each body, with explicit provenance comments. It is a lightweight visualization aid, not a native feature-tree assembly or manufacturing solid. The engineer must create detailed component solids and assembly constraints in the selected CAD environment, then export reviewed neutral geometry for independent interference and tolerance analysis.

The generator intentionally does not create a watch plate, gear teeth, heart cams, hammer surfaces, springs, pivots or bearings from assumed dimensions.

## 6. Required detailed CAD assembly content

A prototype-level assembly must eventually include:
- main plate and bridge solids tied to WP-21/WP-22;
- source arbor and chronograph take-off interface;
- selected clutch/coupling components;
- central chronograph seconds arbor and hand envelope;
- minute and hour totalizer branches and their indexing mechanisms;
- stop brake or equivalent elapsed-value retention element;
- control wheel/cam, operating levers and pusher interface;
- reset heart cams, hammer(s), pivots, springs and travel stops;
- bearing/pivot supports, endshake and side-shake allowances;
- case, dial, hand-stack and service-access envelopes.

Each component must carry a drawing/revision and material/supplier source when known. Unknowns remain explicitly open.

## 7. Acceptance criteria

- WP35-AC-01: all bodies have unique IDs, explicit geometry, axial intervals and evidence provenance.
- WP35-AC-02: all motion trajectories share a documented common time base.
- WP35-AC-03: sampled pairwise clearance is calculated only for axially overlapping bodies.
- WP35-AC-04: sampled interference is flagged and traceable to component IDs and sample index.
- WP35-AC-05: generated visualization includes candidate and source provenance.
- WP35-AC-06: logical sequence covers start, stop, resume and reset, with a physical interlock test reference.
- WP35-AC-07: output explicitly states that continuous swept-solid clearance and physical verification are not proven.
- WP35-AC-08: synthetic fixture geometry is never presented as C-01 design geometry.

## 8. Verification

Run from the tools directory:

    python -m unittest test_c01_chrono_cad_simulation.py

Tests use synthetic fixture geometry only. They establish software behavior and do not constitute C-01 CAD validation or prototype verification.

## 9. Risks and controls

| Risk | Control |
|---|---|
| Envelope model misses tooth/cam/lever interference | Require detailed swept-solid CAD |
| Sparse samples miss transient collision | Increase samples and use continuous collision detection in CAD |
| Incorrect axial datum creates false clearance | Require WP-21 datum realization and stack review |
| Fixture mistaken for actual design | Keep synthetic geometry exclusively in unit tests |
| Motion input hides phase mismatch | Require common time base and documented synchronization |
| Logical interlock mistaken for physical safety | Require hardware test evidence under WP-30 |

## 10. Revision control and disposition

Revision A is the initial controlled issue. Changes to component geometry, motion trajectories, datum, clutch/control architecture, reset mechanism or counter behavior require impact review against WP-20, WP-22, WP-30, WP-33 and WP-34.

**Disposition:** WP-35 provides an evidence-gated assembly visualization and sampled motion-screening foundation. No physical C-01 dimensions, architecture winner or prototype release is established.
