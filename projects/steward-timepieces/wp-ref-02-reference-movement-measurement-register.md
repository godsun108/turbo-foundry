# STEWARD C-01 — Reference Movement Measurement Register

**Document ID:** C01-WP-REF-02  
**Revision:** 0.1  
**Status:** Measurement infrastructure defined; no physical measurements entered  
**Branch:** \`steward/c-01-movement-foundation\`  
**Predecessor:** C01-REF-001 Reference Movement Benchmark Study 01

## 1. Purpose

Create a controlled data structure for collecting, validating and reviewing dimensional evidence from the Sellita SW500 a reference movement and, where useful, the ETA 7750 secondary reference.

This work package creates a blank measurement register and a structural validator. It does not perform a physical survey, certify instrument calibration, establish uncertainty, prove physical fit, or approve any C-01 design geometry.

## 2. Reference evidence discovered

The following source material is available for planning:

1. Sellita, *Catalogue 2024–2025*, SW500 family, printed catalogue page 58 / PDF page 60. It publishes the SW500 a overall dimensions and function set and includes a side-view technical drawing with selected dimensional callouts.  
   https://www.sellita.ch/images/documents/Catalogue2024_ENG.pdf
2. Sellita, *Documentation Technique — SW500*, drawing/document code 10.000, part number SW102574, revision A; title block identifies dimensions in mm and tolerances in µm. This document covers setting-stem length and crown position, not a complete movement geometry definition.  
   https://www.sellita.ch/scripts/calibres/images/DocTec_SW500.pdf
3. Sellita, *Documentation Technique — SW500 MP/MPC*, drawing SW107557, dated 11.08.2020, for the movement frame/case interface. This is a specific frame/case-interface document and must not be treated as the complete SW500 a component drawing set.  
   https://watchangels-live-171a32ea5b4446588cdf25-2d56b1d.divio-media.com/filer_public/da/f6/daf6f42e-ee6c-48ab-9f3c-6019f2c77b60/doctec_sw500_mpc.pdf
4. ETA, official 7750 product page. Published headline specifications only; request the exact applicable technical communication and variant-specific drawings from an authorized source before using detailed geometry.  
   https://portal.eta.ch/en/7750-7750-5.html

**Evidence limitation:** The Sellita catalogue drawing contains selected overall/hand-fitting and case-related callouts. It is not a complete plate, bridge, gear-center, rotor-sweep, calendar, chronograph or hand-stack drawing. The SW500 setting-stem technical document and SW500 MP/MPC frame document apply to their stated document scopes and configurations only. Do not combine them into a fictitious complete drawing package.

## 3. Controlled data artifact

Executable tool:

- \`tools/c01_reference_measurement_register.py\`

Regression test:

- \`tools/test_c01_reference_measurement_register.py\`

The tool supports:

- Creating a blank CSV register with a fixed, controlled column schema.
- Validating required identification, evidence and source fields.
- Requiring a source revision for manufacturer-published and supplier-confirmed entries.
- Requiring specimen, datum, method, instrument, resolution, calibration status, uncertainty, operator and date for measured entries.
- Rejecting duplicate observation IDs.
- Checking numeric value syntax where a value is supplied.
- Ignoring the intentionally blank template row.

The validator checks record structure only. It cannot determine whether a source is authentic/current, whether an instrument is calibrated, whether a measurement is correct, or whether stated uncertainty is technically justified.

## 4. Register field definitions

| Field | Meaning |
|---|---|
| observation_id | Unique controlled record identifier |
| caliber / variant | Exact reference caliber and variant |
| specimen_id | Identified physical specimen, if measured |
| part_interface_id | Controlled component or interface identity |
| parameter | Unambiguous property being recorded |
| value / unit | Numeric value and explicit engineering unit |
| datum | Reference plane, surface, axis or coordinate system |
| method | Measurement or derivation method |
| instrument | Instrument identity |
| instrument_resolution | Instrument resolution |
| calibration_status | Calibration state / certificate reference |
| uncertainty | Expanded or otherwise defined uncertainty and method |
| evidence_class | manufacturer_published, supplier_confirmed, measured, calculated, provisional or tbd |
| source_document / source_revision | Exact source identity and revision |
| operator / reviewer | Responsible roles |
| measurement_date | Date of measurement |
| notes | Configuration, condition, limitations and anomalies |

## 5. Evidence-class rules

- **manufacturer_published:** transcribed from an identified manufacturer document and revision. It is not a physical measurement.
- **supplier_confirmed:** supplied in a controlled supplier response or drawing.
- **measured:** obtained from an identified physical specimen using a documented method and instrument.
- **calculated:** derived from identified inputs and an equation.
- **provisional:** planning placeholder; not eligible for physical fit acceptance.
- **tbd:** unknown; no numeric geometry should be inferred.

A published value must not be relabeled as measured. A photograph or schematic without dimensional control is not a dimensional source.

## 6. Initial survey sequence

1. Obtain the current, exact SW500 a technical documentation package directly from Sellita or an authorized technical distributor.
2. Confirm the exact variant, document revision, applicability and permitted use.
3. Review the official catalogue's dimensional drawing and identify which callouts are explicitly dimensioned.
4. Request full movement assembly drawings, parts list, service documentation and case-interface drawings where available.
5. Do not disassemble or purchase a specimen as part of this work package; that requires a separate explicit decision and qualified watchmaker support.
6. When a specimen is authorized, create its specimen ID before measurement.
7. Establish datums and metrology method before collecting coordinate data.
8. Record instrument resolution, calibration evidence and uncertainty.
9. Have a second reviewer verify transcribed and measured critical values.
10. Only promote reviewed records to the square packaging model.

## 7. Required measurement groups

### Global envelope
- Movement diameter / perimeter and total height with stated datum faces.
- Main plate outline and casing interfaces.
- Maximum rotor swept envelope and rotor plane.
- Stem and pusher axis positions.

### XY reference geometry
- Central axis.
- Barrel and going-train arbor centers.
- Balance/escapement axis.
- Chronograph drive, coupling, control and counter axes.
- Calendar disc/display axes.
- Screw, locating pin and jewel centers.

### Z-stack geometry
- Plate datum and bridge planes.
- Rotor plane and maximum height.
- Wheel/arbor stack heights.
- Calendar and counter layers.
- Dial plane, hand stack and crystal/caseback interfaces.

### Service geometry
- Bridge removal directions.
- Rotor removal path.
- Adjustment and lubrication access.
- Chronograph and calendar service sequence.

Do not populate a coordinate unless its datum and source are known.

## 8. Acceptance criteria

The register infrastructure is accepted for use when:

- The CSV schema is stable and documented.
- Blank rows are ignored without generating false evidence.
- Duplicate IDs and malformed numeric values are rejected.
- Manufacturer-published and supplier-confirmed records require source revision.
- Measured records require specimen and metrology traceability.
- No synthetic values are presented as C-01 or reference-movement measurements.

The measurement campaign itself remains **not started** until an exact documentation package or authorized specimen is available.

## 9. Run instructions

From the tools directory:

\`\`\`bash
python c01_reference_measurement_register.py --create-template ../build/reference-movement-measurements.csv
python c01_reference_measurement_register.py --validate ../build/reference-movement-measurements.csv
python -m unittest test_c01_reference_measurement_register.py
\`\`\`

The blank CSV contains only column headers and one empty row. It does not contain invented reference measurements.

The six regression tests are synthetic structural tests. They must be executed in the project environment before being reported as passing.

## 10. Design authority and release boundary

This package does not:
- select SQ-A, SQ-B or SQ-C;
- select the C-01 clutch or control architecture;
- select a dial arrangement;
- define C-01 dimensions, gear centers, tooth counts, torque, clearances or tolerances;
- authorize purchase, disassembly or destructive inspection;
- approve a prototype, design freeze or manufacturing release.

C-01 remains chronograph + weekday + date. Month display and moon phase remain assigned to LUNAR.

## 11. Revision history

| Revision | Date | Change | Status |
|---|---|---|---|
| 0.1 | 2026-11-28 | Initial reference measurement schema, validator and survey controls | Preliminary / review |
