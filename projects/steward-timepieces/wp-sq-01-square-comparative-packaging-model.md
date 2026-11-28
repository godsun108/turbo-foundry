# STEWARD C-01 — Square Comparative Packaging Model

**Document ID:** C01-WP-SQ-01  
**Revision:** 0.1  
**Status:** Conceptual engineering model; architecture comparison open  
**Branch:** steward/c-01-movement-foundation  
**Related:** C01-ARCH-SQ-001; WP-14; mechanical datum and plate-zone skeleton; C-01 integrated power/reserve campaign

## 1. Purpose and boundary

This work package turns the square architecture study into a controlled, comparable subsystem-allocation model for SQ-A, SQ-B and SQ-C.

It is a first packaging model, not a dimensioned layout or a CAD fit study. It records where each subsystem is conceptually allocated, which interfaces must be resolved, and what evidence is needed before component placement can become physical geometry.

The three candidates use the same C-01 functional baseline. The model deliberately contains no invented dimensions, component coordinates, tooth counts, gear ratios, torque, mass, efficiency or performance estimates.

## 2. Functional baseline preserved

- Automatic mechanical winding.
- Hours and minutes.
- Weekday.
- Day-of-month 1–31.
- Central chronograph seconds.
- Elapsed-minute counter.
- Elapsed-hour counter.
- Running seconds.

The preliminary 4 Hz / 28,800 vph target, aspirational 60–70-hour reserve and proposed −4/+6 s/day rate objective remain unchanged and unvalidated.

Month display and moon phase remain assigned to LUNAR. This model does not add them to C-01.

## 3. Model architecture

The executable model records:
- Three candidate architectures and their design principles.
- Allocation statements for nine required mechanical subsystems.
- Candidate-specific dominant constraints.
- Twelve key subsystem interfaces and the engineering question at each interface.
- Explicit TBD status for coordinates, dimensions and performance claims.
- A machine-readable JSON comparison and a qualitative SVG block diagram.

The SVG boxes are semantic blocks only. They are not to scale, are not component envelopes and must not be used to infer clearance or fit.

## 4. Candidate allocation comparison

### SQ-A — Rounded-square plate / circular mechanical elements

The plate and bridge envelope follows a rounded-square outline while barrel, gear train, balance, escapement, rotor and chronograph wheels retain mechanically appropriate circular forms.

Primary engineering questions:
- Can the complete circular component envelopes and service-access zones fit within a rounded-square plate?
- Does the rotor sweep clear the case, bridges and balance?
- Can the chronograph and calendar be integrated without forcing inefficient transfer gearing?
- Can bridges be partitioned for stiffness and service access?

### SQ-B — Square-organized movement

Subsystem zones are deliberately organized around a square plan. This is the most ambitious candidate and must demonstrate that square organization provides functional value rather than visual symmetry alone.

Primary engineering questions:
- Does the arrangement introduce extra transfer stages or interfaces?
- Can rotor sweep, winding efficiency and regulator protection coexist?
- Are the going-train relationships and chronograph drive path efficient?
- Can each subsystem be assembled and serviced without excessive disassembly?

### SQ-C — Circular mechanical core / square outer architecture

Geometry-sensitive timekeeping elements are concentrated in a core, with square outer structure supporting display, calendar and chronograph interfaces.

Primary engineering questions:
- How many interfaces are required between the core and outer structure?
- Do added interfaces increase alignment, friction, wear or service burden?
- Can counter and calendar drives reach their display axes efficiently?
- Does the outer structure provide genuine support and service functionality?

No candidate is ranked or selected in this revision.

## 5. Common subsystem inventory

| Subsystem | Required packaging evidence |
|---|---|
| Barrel | Barrel envelope, arbor supports, torque path, winding and service access |
| Going train | Wheel centers, mesh geometry, arbor support, train efficiency and take-off paths |
| Balance / escapement | Staff axis, shock protection, regulator access, impulse path and clearance |
| Automatic winding | Rotor axis, swept envelope, mass properties, winding works, caseback clearance and efficiency |
| Chronograph drive / coupling | Take-off arbor, clutch geometry, engagement, drag and stopped/running loads |
| Chronograph control / reset | Pusher axis, lever path, brake, hammer geometry, reset alignment and actuation force |
| Elapsed counters | Counter axes, ratios, carry/indexing, hand loads and support |
| Weekday/date calendar | Disc geometry, indexing, jumper loads, correction interfaces and changeover |
| Motion works / hand stack | Coaxial arbor arrangement, hand heights, friction, endshake and service access |

Every physical envelope remains TBD pending traceable reference measurements or a dimensioned design supported by calculations.

## 6. Interface register

The model explicitly identifies these interfaces for later engineering closure:

1. Rotor to winding works — winding torque path, direction strategy, bearing and sweep.
2. Winding works to barrel — winding input and overwind/slipping behavior.
3. Barrel to going train — torque delivery, arbor support and reserve.
4. Going train to balance/escapement — impulse demand, amplitude and rate stability.
5. Going train to chronograph drive — take-off arbor and stopped/running loading.
6. Chronograph drive to coupling — engagement, drag, hand jump and wear.
7. Control to coupling/brake/reset — start-stop-reset sequence and pusher force.
8. Chronograph drive to elapsed counters — ratios, indexing and torque.
9. Going train to calendar — calendar drive and changeover load.
10. Calendar to weekday/date displays — disc support, jumper, correction and safe setting.
11. Motion works to central hand stack — coaxial arbors, friction, height and clearances.
12. Movement to case/crown/pushers — casing supports, stem axis, pusher sealing and extraction.

The register is a requirements checklist, not proof that any interface is designed.

## 7. Evidence needed before geometry

The next dimensional phase requires a documented reference movement or approved design envelope, plus traceable measurements for:
- Movement and case internal envelope.
- Dial opening and aperture positions.
- Shaft/arbor axes and bearing locations.
- Component outer envelopes and axial heights.
- Rotor swept envelope and caseback clearance.
- Stem and pusher axes.
- Hand stack and dial/crystal clearances.
- Calendar disc and counter geometry.
- Bridge supports, screw access and service sequence.

Each value must carry an evidence status: measured, calculated, supplier-confirmed, provisional or TBD. Record source, method, date, uncertainty and revision. Normalized concept placeholders must not be silently converted to millimetres.

## 8. Decision criteria

The candidates must be compared using the same criteria:
- Going-train efficiency and load path.
- Chronograph integration and energy demand.
- Calendar integration and safe correction.
- Rotor sweep and winding efficiency.
- Balance protection and rate stability.
- Structural stiffness and shock resistance.
- Hand-stack feasibility.
- Case and dial integration.
- Assembly, adjustment and serviceability.
- Manufacturability and parts count.
- Long-term repairability.

Aesthetic identity is considered separately from functional performance. No numerical score is assigned until evidence exists.

## 9. Acceptance criteria for this model

The conceptual model is acceptable when:
- SQ-A, SQ-B and SQ-C are represented.
- All nine required subsystems are accounted for in every candidate.
- All listed subsystem interfaces remain explicitly visible.
- No unverified dimensions, coordinates or performance claims are emitted.
- C-01 functions and the LUNAR scope boundary remain unchanged.
- The JSON model and SVG are clearly labeled conceptual and not to scale.

This acceptance validates the comparison artifact only. It does not validate any movement architecture or physical fit.

## 10. Executable artifacts

- `tools/c01_square_packaging_model.py` — builds the qualitative architecture comparison JSON and SVG.
- `tools/test_c01_square_packaging_model.py` — synthetic regression tests for candidate coverage, unresolved geometry, scope and decision state.

Run from the tools directory:

```bash
python c01_square_packaging_model.py --output-dir ../../build/c01-square-packaging
python -m unittest test_c01_square_packaging_model.py
```

Tests are authored but must be executed in the project environment before being reported as passing.

## 11. Current conclusion and next gate

This model makes the three architectures comparable without pretending that component geometry is known. It does not establish that any candidate fits, performs better or is easier to manufacture.

**Next gate:** select a documented reference movement for dimensional teardown study or establish an approved case/dial envelope, then build candidate-specific dimensioned XY/Z packaging models. Until that evidence exists, all component coordinates, dimensions and fit conclusions remain TBD.

## 12. Revision history

| Revision | Date | Change | Status |
|---|---|---|---|
| 0.1 | 2026-11-27 | Initial SQ-A/SQ-B/SQ-C subsystem-allocation model and interface register | Concept / review |
