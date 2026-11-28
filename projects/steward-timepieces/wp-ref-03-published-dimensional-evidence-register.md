# C-01 — WP-REF-03 Published Dimensional Evidence Register

**Document ID:** C01-REF-003  
**Revision:** 0.1  
**Status:** Preliminary evidence register — not a C-01 design input approval  
**Project:** STEWARD C-01  
**Branch:** `steward/c-01-movement-foundation`  
**Prepared:** 2026-11-28

## 1. Purpose

Record dimensional information explicitly published for the Sellita SW500 a benchmark and separate it from interpretation, missing information, and measurements that would require an identified physical specimen.

This register is a controlled transcription of published reference data. It is not a complete movement drawing, a metrology report, or an authorization to copy proprietary component geometry. The SW500 a is a benchmark only; no assumption is made that its dimensions or architecture should be adopted by C-01.

## 2. Reference identity and source hierarchy

Primary reference: Sellita SW500 a, as identified in the Sellita 2024–2025 catalogue, printed page 58.

Primary source:
- Sellita, *Catalogue 2024–2025*, SW500 family / SW500 a, printed page 58, PDF: https://sellita.ch/images/documents/Catalogue2024_ENG.pdf

Supporting source:
- Sellita, *Technical Documentation — SW500*, edition dated 20.04.2021, available as a public reproduction at: https://www.manualslib.com/manual/3134613/Sellita-Sw500.html
- Sellita, *Documentation Technique — SW500*, code 10.000, part SW102574, revision A. The separately located stem/crown-position sheet is a specific interface document, not a complete movement drawing: https://www.sellita.ch/scripts/calibres/images/DocTec_SW500.pdf

**Applicability caution:** the catalogue explicitly identifies the SW500 a. The supporting technical documentation is labelled SW500; exact variant and revision applicability to a specific SW500 a specimen must be confirmed with Sellita before using detailed service dimensions as a design constraint.

## 3. Published dimensional observations

Evidence class: **M — manufacturer-published**. These are transcribed published values, not independently measured values.

| Register ID | Published callout | Unit | Evidence / interpretation boundary |
|---|---:|---|---|
| PUB-001 | 13¼ | ligne | Catalogue movement size designation |
| PUB-002 | 30.00 | mm | Catalogue identifies movement diameter |
| PUB-003 | 30.40 | mm | Catalogue side-view drawing labels maximum outside diameter |
| PUB-004 | 7.90 | mm | Catalogue identifies movement height |
| PUB-005 | 3 × 0.70 | mm | Repeated callout shown on side-view drawing; feature identity and datum not resolved in this register |
| PUB-006 | 3 × Ø0.18 | mm | Repeated diameter callout shown on side-view drawing; exact hand/shaft assignment not resolved here |
| PUB-007 | Ø0.25 | mm | Diameter callout shown; exact feature assignment not resolved here |
| PUB-008 | Ø1.20 | mm | Diameter callout shown; exact feature assignment not resolved here |
| PUB-009 | Ø2.00 | mm | Diameter callout shown; exact feature assignment not resolved here |
| PUB-010 | 3.00 | mm | Linear callout shown; datum and feature assignment require drawing inspection / manufacturer confirmation |
| PUB-011 | 1.40 | mm | Linear callout shown; datum and feature assignment require drawing inspection / manufacturer confirmation |
| PUB-012 | 1.95 | mm | Linear callout shown; datum and feature assignment require drawing inspection / manufacturer confirmation |
| PUB-013 | 2.39 | mm | Linear callout shown; datum and feature assignment require drawing inspection / manufacturer confirmation |

The catalogue labels the side drawing's hand-fitting reference as “Standard hand fitting height.” The numeric callouts above are preserved as printed; this register deliberately does not assign each one to a particular arbor, hand, shoulder, or datum without a fully legible dimensioned drawing and verified interpretation.

## 4. Published functional context (not dimensional geometry)

The same catalogue entry describes the SW500 a as:
- automatic, cam-operated chronograph with two push-buttons;
- central 60-second chronograph indication;
- 30-minute counter at 12 o’clock and 12-hour counter at 6 o’clock;
- small seconds at 9 o’clock;
- quick-set day and date;
- 28,800 vibrations/hour (4 Hz), 25 jewels;
- typical power reserve 62 hours.

These are benchmark specifications, not C-01 requirements proven by testing. The catalogue's 62-hour typical reserve is not evidence that C-01 can meet its own 60–70-hour aspiration.

## 5. What this evidence does and does not establish

### Established at published-data level
- The catalogue's nominal movement diameter, maximum outside diameter and overall height callouts.
- The existence of selected hand-fitting / side-profile callouts.
- The listed functional configuration and published nominal operating specifications.

### Not established
- XY coordinates of barrel, balance, escapement, gear arbors, chronograph components, calendar works, rotor axis, or counters.
- Mainplate or bridge outline, thickness map, recesses, pockets, screw locations, jewel positions, bearing seats, or gear center distances.
- Rotor sweep envelope, winding clearance, winding efficiency, or winding torque.
- Full hand-stack heights, arbor lengths, endshake, runout, or all relevant clearances.
- A complete Z-stack or case interface for the exact intended reference variant.
- Any geometry, tolerance, performance, or material specification for C-01.

No coordinates may be inferred from the catalogue illustration by scaling pixels. The published drawing is a limited side-view dimensional reference, not a complete orthographic component package.

## 6. Square C-01 packaging implications

The overall published SW500 a envelope is useful as a benchmark for comparing a circular reference movement with proposed square movement packaging. It does **not** determine the dimensions of a square C-01 plate or case.

For SQ-A, SQ-B and SQ-C, the next valid geometry inputs still require:
1. an explicitly chosen reference envelope and declared allowance policy;
2. verified datum definitions and orthographic views;
3. exact variant/revision applicability;
4. a component-level XY and Z survey, if a physical specimen is later authorized and obtained;
5. rotor, barrel, balance, chronograph and calendar keep-out envelopes;
6. crown, pusher, dial, hand-stack and case interface definitions.

No square candidate is selected by this register.

## 7. Evidence and release rules

- Manufacturer-published values must retain the source title, revision/date where available, page, unit and applicability.
- Supplier-confirmed values require written confirmation identifying the exact calibre variant and document revision.
- Measured values require specimen identity, datum, method, instrument, resolution, calibration status, uncertainty, operator and date.
- Values transcribed from a drawing with ambiguous callout association remain unassigned until resolved.
- A blank or unknown value must remain unknown; it must not be estimated from an illustration.
- This register does not authorize purchase, disassembly, destructive inspection, architecture selection, design freeze, or manufacturing release.

## 8. Revision history

| Revision | Date | Change |
|---|---|---|
| 0.1 | 2026-11-28 | Initial published-data register for SW500 a catalogue dimensions; ambiguous callouts intentionally left unassigned |

## 9. Next engineering action

Obtain or request from Sellita the current, applicable technical package for the exact SW500 a variant, including dimensioned movement/frame and hand-fitting drawings with datums and revision identifiers. Reconcile that package against the catalogue before creating any coordinate-based benchmark model. Any physical measurement campaign remains a separate, explicitly authorized activity.
