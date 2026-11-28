# STEWARD C-01 — Reference Movement Benchmark Study 01

**Document ID:** C01-REF-001  
**Revision:** 0.1  
**Status:** Preliminary benchmark study; physical dimensional survey not yet performed  
**Branch:** `steward/c-01-movement-foundation`  
**Related:** C-01 README; WP-14; C01-ARCH-SQ-001; WP-SQ-01; C-01 design authority decision register  
**Design authority:** STEWARD C-01 requirements baseline

## 1. Purpose

Establish a traceable, evidence-based reference for the next dimensioned C-01 packaging phase. The study identifies proven automatic day-date chronograph movements whose published functions and dimensions overlap the C-01 baseline, distinguishes manufacturer-published facts from geometry that still requires measurement, and defines a controlled survey protocol.

The reference calibers are engineering benchmarks only. C-01 is not authorized to copy either movement's component geometry, train topology, bridge shapes, control mechanism, or proprietary drawings. Any adopted principle must be independently justified against C-01 requirements and recorded through the design authority process.

This document does not select the final C-01 architecture, approve a square case, or establish a physical fit.

## 2. C-01 requirements relevant to the benchmark

The reference comparison is limited to the requirements that influence movement packaging:

- Automatic winding.
- Hours and minutes.
- Running seconds.
- Central chronograph seconds.
- Elapsed-minute and elapsed-hour counters.
- Weekday and date.
- Two-pusher chronograph baseline.
- Preliminary frequency target: 4 Hz / 28,800 vph.
- Aspirational power reserve: 60–70 hours, unvalidated.

Month display and moon phase remain outside C-01 and assigned to LUNAR. No month or moon-phase complication is included in this benchmark.

## 3. Reference candidates and selection

### 3.1 Primary dimensional/function benchmark — Sellita SW500 a

The SW500 a is selected as the primary published-data benchmark for this study because the manufacturer's 2024–2025 catalogue identifies an automatic cam-operated chronograph with day and date, central 60-second chronograph indication, 30-minute and 12-hour counters, small seconds, 4 Hz frequency, and a typical 62-hour power reserve. Its published movement envelope is 30.00 mm diameter by 7.90 mm height.

This makes its published function set and stated reserve particularly relevant to C-01's preliminary 60–70-hour aspiration. It is not proof that C-01 can achieve that reserve, and the manufacturer's typical reserve is not a C-01 acceptance result.

### 3.2 Secondary benchmark — ETA 7750 / Valjoux 7750

ETA's official product page lists the 7750 as a 30.00 mm diameter, 7.90 mm high, 4 Hz automatic cam chronograph with day/date, central chronograph seconds, 30-minute and 12-hour counters, small seconds, and a typical 54-hour power reserve.

The ETA 7750 is retained as a secondary reference for its official dimensional/function data and its established cam-operated chronograph arrangement. Its reserve is below C-01's aspirational target and therefore provides a useful comparison point, not a target to reproduce.

### 3.3 Published-data comparison

| Attribute | Sellita SW500 a | ETA 7750 | Evidence / interpretation |
|---|---:|---:|---|
| Movement diameter | 30.00 mm | 30.00 mm | Manufacturer-published |
| Movement height | 7.90 mm | 7.90 mm | Manufacturer-published |
| Frequency | 28,800 vph / 4 Hz | 28,800 vph / 4 Hz | Manufacturer-published |
| Winding | Automatic, ball-bearing rotor | Automatic, unidirectional | Manufacturer-published |
| Chronograph control | Cam-operated, two pushers | Cam-operated, two pushers | Manufacturer-published |
| Central chronograph seconds | Yes | Yes | Manufacturer-published |
| Elapsed-minute counter | 30 minutes | 30 minutes | Manufacturer-published |
| Elapsed-hour counter | 12 hours | 12 hours | Manufacturer-published |
| Running seconds | Small seconds at 9 | Small seconds | Manufacturer-published |
| Calendar | Day and date | Day and date | Manufacturer-published |
| Typical power reserve | 62 hours | 54 hours | Manufacturer-published; not independently measured here |
| Jewels | 25 | 25 | Manufacturer-published |

**Important:** The equal 30.00 × 7.90 mm headline envelope does not mean the calibers have interchangeable parts, identical internal coordinates, identical case interfaces, or equivalent component geometry. Each caliber and exact variant must be treated as its own controlled configuration.

## 4. Architecture observations

### 4.1 Functional architecture visible from manufacturer data

Both references demonstrate that an automatic movement can package a cam-operated two-pusher chronograph, central chronograph seconds, minute/hour elapsed counters, running seconds, and day-date calendar within a published 30.00 mm × 7.90 mm envelope.

This is a useful system-level benchmark for C-01's initial packaging study. It does not show that the same envelope is achievable with C-01's preferred square architecture, a different dial layout, different counter axes, or different clutch/control choices.

### 4.2 Chronograph control

Both manufacturers identify cam-operated chronograph control. C-01's cam-versus-column-wheel decision remains open. The reference architecture provides a concrete cam-controlled system for study, but it does not settle C-01's decision.

The exact cam profile, lever geometry, spring loads, contact surfaces, tolerances, lubrication, and adjustment procedures must be obtained from an authorized technical document or measured from a physical specimen. No such geometry is inferred in this revision.

### 4.3 Automatic winding

ETA identifies the 7750 winding system as unidirectional. Sellita identifies the SW500 a as automatic with a ball-bearing winding mechanism. The exact rotor sweep, bearing dimensions, winding train geometry, mass properties, winding efficiency, and vertical clearances are not established by the headline specifications.

For square C-01 packaging, the full swept rotor envelope and service/removal path must be surveyed. A circular movement's rotor arrangement must not be presumed to fit any of SQ-A, SQ-B, or SQ-C.

### 4.4 Calendar

Both references include day and date indications with quick correction. C-01's desired independently correctable weekday/date architecture remains open. The reference data does not establish calendar disc diameters, indexing torque, jumper loads, changeover timing, corrector geometry, or safe-setting windows for C-01.

### 4.5 Counter and dial arrangement

The reference functions show a conventional arrangement with small seconds and elapsed counters. The exact display layout differs by variant and must be verified against the specific caliber's technical drawing.

C-01's existing dial candidates A/B/C and square dial concept D remain open. No dial candidate is selected by this benchmark.

## 5. Published dimensions versus measured geometry

The 30.00 mm diameter and 7.90 mm height values are manufacturer-published overall movement dimensions. They are not a complete dimensional definition.

The following are **not** established by the headline product data and remain TBD until a dimensioned manufacturer drawing or physical survey is available:

- Main plate perimeter and corner/edge profiles.
- Exact movement datum and center axis definition.
- Barrel, wheel, pinion, balance, escapement, and chronograph component center coordinates.
- Pivot, jewel, bearing and screw locations.
- Bridge outlines, heights, thicknesses and fastening coordinates.
- Rotor diameter, swept envelope, axial position and caseback clearance.
- Stem axis and pusher axes relative to movement datum.
- Calendar disc geometry and display aperture coordinates.
- Counter arbor coordinates and hand heights.
- Central hand-stack heights and tube/arbor dimensions.
- Component envelopes, clearances, endshake and tolerance stack.
- Case seat, casing supports, dial feet, crystal and caseback interfaces.

Do not reverse-engineer missing coordinates from product photographs or schematic illustrations. Such images may support qualitative subsystem identification but are not dimensional evidence.

## 6. Dimensional survey plan

### 6.1 Preferred evidence sequence

1. Obtain the exact manufacturer's technical communication, dimensioned drawing, parts list and service documentation for the chosen caliber/variant.
2. Record document number, revision/date, variant designation, units and any restrictions on use.
3. Acquire or inspect an exact identified physical specimen only if authorized and practical.
4. Have a qualified watchmaker perform controlled disassembly and measurement where required.
5. Record all measurement methods, instruments, calibration status, resolution and uncertainty.
6. Photograph each assembly layer with a scale and specimen ID; images are supporting evidence, not substitutes for measured values.
7. Reconcile drawing values and physical measurements; investigate discrepancies rather than averaging them.
8. Promote only reviewed values into the C-01 reference geometry register.

No movement purchase, disassembly, or destructive inspection is authorized by this document.

### 6.2 Measurement register schema

Every future observation must record:

| Field | Required content |
|---|---|
| Observation ID | Unique controlled identifier |
| Caliber / variant | Exact manufacturer designation |
| Specimen ID | Serial, lot or internal sample identifier where available |
| Part / interface ID | Controlled part or interface identity |
| Parameter | Clearly defined measured quantity |
| Value / unit | Numeric value and explicit unit |
| Datum | Reference surface, axis or coordinate origin |
| Method | Instrument and measurement procedure |
| Instrument | Make/model/ID where available |
| Resolution | Instrument resolution |
| Calibration | Calibration status / certificate reference |
| Uncertainty | Measurement uncertainty and method |
| Evidence class | Manufacturer-published, supplier-confirmed, measured, calculated, provisional or TBD |
| Source | Drawing/document/photo/file and revision |
| Operator / reviewer | Names or controlled roles |
| Date | Measurement date |
| Notes | Condition, wear, variant caveats and anomalies |

### 6.3 Critical survey groups

**A. Global envelope**
- Overall movement diameter or perimeter.
- Overall height with explicitly stated datum faces.
- Rotor maximum swept envelope.
- Highest and lowest component planes.
- Casing support surfaces.

**B. XY geometry**
- Main plate outline.
- Central time/chronograph axis.
- Barrel and going-train wheel centers.
- Balance and escapement axes.
- Chronograph drive, clutch, counter and control axes.
- Calendar display axes and disc boundaries.
- Stem and pusher axes.
- Screw, locating pin and jewel center coordinates.

**C. Z geometry**
- Main plate datum.
- Bridge and rotor plane heights.
- Wheel and arbor stack heights.
- Dial plane and dial-side component heights.
- Central hand-stack heights.
- Crystal and caseback clearance interfaces.

**D. Service and assembly**
- Bridge removal directions.
- Required disassembly order.
- Access to regulation and lubrication points.
- Rotor removal and installation path.
- Calendar and chronograph adjustment access.
- Replaceable wear components and service tools.

## 7. Implications for the square C-01 candidates

The reference movements are circular. Their 30.00 mm diameter is therefore a circular envelope, not a square plate dimension or a square-case recommendation.

The next comparison must use actual measured or manufacturer-confirmed component envelopes, then place those envelopes into the three C-01 square concepts without assuming that the entire reference movement is transplanted.

| C-01 candidate | What the reference study can inform | What remains to be proven |
|---|---|---|
| SQ-A — rounded-square plate / circular mechanisms | Whether circular subsystem envelopes can be organized within a square plate concept | Plate shape, support bridges, rotor sweep, case fit, service access |
| SQ-B — square-organized movement | Which subsystems resist relocation and which interfaces constrain a square organization | Whether added transfer interfaces, complexity and loading are justified |
| SQ-C — circular core / square outer structure | Which geometry-sensitive systems may remain concentrated in a core | Core-to-outer interfaces, display/calendar routing, structural and service consequences |

The first square layout should be a measured-envelope study, not a detailed gear design. It should contain:
- A controlled square case/dial envelope, initially marked TBD.
- Reference subsystem envelopes tagged by source and evidence class.
- Separate C-01 functional blocks.
- Candidate-specific interface paths.
- Explicit clearance and service-access reservations.
- No invented gear centers, teeth, torque, dimensions or tolerances.

## 8. Benchmark conclusion

The Sellita SW500 a is the best first published-data benchmark for C-01's current function set and aspirational reserve because it combines day/date, automatic winding, cam chronograph, 4 Hz operation and a manufacturer-stated typical 62-hour reserve in a published 30.00 mm × 7.90 mm envelope.

The ETA 7750 remains a useful secondary benchmark with the same headline envelope and a manufacturer-stated typical 54-hour reserve.

Neither reference establishes C-01's final dimensions or proves that a square C-01 can meet its requirements. Full component geometry and interface data remain outstanding. The next engineering gate is to obtain exact variant technical documents and perform a controlled dimensional survey before creating the first dimensioned SQ-A/SQ-B/SQ-C layout.

## 9. Acceptance criteria

This benchmark study is acceptable for preliminary planning when:

- Primary and secondary reference variants are clearly identified.
- Manufacturer-published facts are distinguished from measured geometry.
- C-01 functions and the LUNAR scope boundary are preserved.
- No missing component dimensions are inferred from photographs.
- A repeatable dimensional survey protocol and data schema are defined.
- SQ-A/SQ-B/SQ-C remain unselected.
- No C-01 design freeze, physical fit claim, or manufacturing release is implied.

The study is **not** accepted as a completed dimensional survey. The survey gate remains open.

## 10. Source register

1. ETA SA, official 7750 product page: https://portal.eta.ch/en/7750-7750-5.html  
   Used for published 7750 dimensions, functions, cam-operated chronograph, winding direction, frequency, jewels and typical power reserve.

2. Sellita, *Catalogue 2024–2025*, SW500 family, printed catalogue pages 57–61 (PDF pages 57–61): https://www.sellita.ch/images/documents/Catalogue2024_ENG.pdf  
   Used for SW500 family description, SW500 a published dimensions, functions, cam-operated chronograph, winding, frequency, jewels, typical power reserve and technical drawing overview.

3. ETA, *Technical Communication CT 7750 ESI 414230 04* (third-party hosted copy): https://myretrowatches.co.uk/wp-content/uploads/2023/03/ETA-7750.pdf  
   Secondary technical-document reference only. Obtain the exact current authorized manufacturer document before relying on detailed component drawings or service instructions.

## 11. Revision history

| Revision | Date | Change | Status |
|---|---|---|---|
| 0.1 | 2026-11-28 | Initial ETA 7750 / Sellita SW500 benchmark, published-data comparison and dimensional survey protocol | Preliminary / review |
