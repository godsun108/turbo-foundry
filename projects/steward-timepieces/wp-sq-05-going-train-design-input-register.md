# WP-SQ-05 — Square C-01 Going-Train Design Input Register

- **Document ID:** SEB-C01-WP-SQ-05
- **Revision:** 0.1
- **Status:** Controlled input definition; synthesis held pending approved inputs
- **Branch:** `steward/c-01-movement-foundation`
- **Dependencies:** WP-SQ-03, WP-SQ-04, WP-18, WP-23, WP-25, WP-26, WP-27, WP-28, WP-38, WP-39, WP-66 and WP-67
- **Data register:** `data/c01-square-going-train-input-register.csv`

## 1. Purpose

WP-SQ-05 establishes the minimum authoritative inputs needed before generating a credible square C-01 going-train tooth schedule. It is deliberately an input-control package, not another synthesis engine. WP-18/WP-25/WP-26/WP-38/WP-39 remain the calculation and candidate-screening tools; WP-27/WP-28/WP-66/WP-67 remain the measured source and power evidence authorities.

The current repository contains substantial calculation infrastructure but no approved C-01 barrel-speed curve, actual spring torque-angle data, escapement wheel/event convention, gear-system selection, physical arbor coordinates or center-distance tolerance. Therefore a numerical tooth schedule would currently be fabricated. WP-SQ-05 prevents that.

## 2. Controlled functional path and candidate display boundaries

The working topology from WP-SQ-03 remains:

`barrel → center → third → fourth/seconds → escape wheel → escapement`

The center and fourth arbor roles are provisional functional hypotheses:
- center arbor: candidate minute-motion interface;
- fourth arbor: candidate continuous running-seconds source.

If those direct-drive roles are retained, their ideal display boundary conditions are:
- minute-motion arbor: one revolution per hour, (n=1/60) rpm;
- running-seconds arbor: one revolution per minute, (n=1) rpm.

These are display kinematics, not measured or selected internal train ratios. They do not establish that the barrel drives the center arbor through one particular mesh, nor that a specific gear pair or physical layout is feasible. The escape-wheel target cannot be assigned until the wheel tooth count and escapement event convention are explicitly controlled. The preliminary 4 Hz oscillator target alone does not uniquely determine escape-wheel rpm.

## 3. Evidence hierarchy

Every register entry must be classified:
- **M — Manufacturer-published:** explicit manufacturer data with exact document, revision, page/drawing and applicable caliber variant.
- **S — Supplier-confirmed:** written supplier data tied to exact part/variant and revision.
- **P — Physically measured:** actual specimen, method, datum, instrument, calibration status, uncertainty, operator and date.
- **D — Derived:** calculation with identified inputs, model version and calculation record.
- **A — Approved requirement/decision:** signed or otherwise controlled C-01 requirement or design-authority decision.
- **H — Hypothesis:** open design proposal, not an accepted input.
- **T — Synthetic test fixture:** software regression data only; never C-01 design evidence.

A reference caliber's published outside diameter and overall height are not internal gear geometry. The Sellita SW500 a / ETA 7750 benchmark dimensions cannot be used to infer C-01 arbor centers, tooth counts, module, barrel speed, bridge layout or gear ratios. Applicability of generic SW500 documentation to the exact SW500 a variant must be confirmed before relying on it for a detailed interface.

## 4. Input register and current disposition

| Input group | Required input | Authority / source | Current status | Gate |
|---|---|---|---|---|
| Functional topology | Approved arbor/mesh order and compound-wheel identities | WP-SQ-03 and design authority | H — candidate only | G1 |
| Display speeds | Center and fourth arbor target speeds, conditional on direct-drive roles | Functional display requirement | H — provisional | G1 |
| Barrel source | Barrel angular speed versus wind state and load | WP-66 measured data | Missing | G2 |
| Spring source | Torque-angle curve and approved operating endpoints | WP-27 measured data | Missing | G2 |
| Escapement | Escape-wheel tooth count and event/impulse convention | Escapement design authority and WP-28 | Missing | G3 |
| Gear system | Module, pressure angle, rack coefficients, profile-shift policy | Approved gear design basis / supplier | Missing | G3 |
| Arbor geometry | XY coordinates, axis IDs, datum transforms | WP-23 / approved square layout | Missing | G4 |
| Mesh geometry | Center distances, tolerances, backlash requirements | WP-23, WP-37 and tolerance analysis | Missing | G4 |
| Loads | Torque at each gear mesh, inertia and operating states | WP-27/WP-28/WP-64/WP-66 | Missing | G5 |
| Gear integrity | Undercut, interference, contact ratio, tooth strength and fatigue | WP-38/WP-39 plus specialist review | Not evaluated | G5 |
| Packaging | Plate/bridge thickness, bearing supports, rotor sweep, clearances | WP-21/WP-22/WP-24 and physical layout | Missing | G6 |
| Evidence | Calibration, uncertainty, revision and chain of custody | WP-30/WP-49/WP-66/WP-67 | Missing for physical C-01 measurements | G7 |

## 5. Gate sequence

**G1 — Functional definition.** Approve the arbor roles, mesh order, compound wheel identities, direct-drive display assumptions and escapement interface convention. SQ-A remains a study configuration, not a selected plate design.

**G2 — Source characterization.** Obtain traceable barrel speed under representative load and measured spring torque-angle data across a proposed operating window. WP-27 and WP-66 require physical measurement and approved endpoints; no nominal curve or reserve estimate may substitute.

**G3 — Gear-system definition.** Approve the gear family and generating system: module, pressure angle, addendum/dedendum coefficients, profile-shift policy, material/process basis and escapement wheel convention. These inputs must be compatible across each mating pair.

**G4 — Geometry closure.** Establish controlled arbor coordinates, physical center distances, plate/bridge datum references, bearing support and tolerances. WP-23/WP-24 remain authorities; a schematic or normalized zone is not a coordinate source.

**G5 — Candidate synthesis and engineering screening.** Use WP-18 to enumerate tooth pairs, WP-26 to enforce shared-gear consistency and connect the train, WP-25 to close signed speed ratios, and WP-38/WP-39 to screen involute geometry and bounded candidate rankings. Then assess torque, strength, fatigue, inertia, efficiency and escapement power. A high kinematic score is not a physical design pass.

**G6 — Packaging and service review.** Integrate the selected candidate geometry into the square plate/bridge architecture, verify rotor and calendar/chronograph clearances, bearing supports, assembly sequence and service access. No layout is released based on gear ratio alone.

**G7 — Independent review and release.** Review source data, derivations, model revisions, uncertainty, candidate truncation and all acceptance limits. Only then can a candidate be recommended for controlled design-authority selection.

## 6. Candidate synthesis rules

1. No tooth count or module may be assigned from a photograph, marketing drawing or outside envelope.
2. No barrel RPM may be guessed from the 4 Hz balance target.
3. The center and fourth arbor speed targets may only be used as provisional display boundary conditions until their direct-drive roles are approved.
4. Escape-wheel speed must remain unresolved until its tooth count and event convention are defined.
5. All gear pairs must share a compatible declared gear system; all shared gear IDs must retain one tooth count and arbor assignment across the train.
6. Search bounds and candidate caps must be explicit. Truncated searches must be reported as incomplete, not globally optimal.
7. Geometry, strength, dynamic load and packaging gates remain separate from kinematic ratio closure.
8. Synthetic fixtures may exercise code but must never enter the C-01 evidence register.

## 7. Acceptance criteria

- The register contains every required input group and an identified authority.
- Missing physical data remain explicitly missing; no placeholder numeric values are accepted as C-01 data.
- Each populated entry has evidence class, source reference/revision, unit, datum or boundary, uncertainty where measured, and approval state.
- A candidate schedule is not generated until G1–G4 inputs are approved.
- No candidate is recommended until G5–G7 evidence is complete.
- The 60–70 hour reserve remains an aspiration, not a demonstrated outcome.
- The C-01 scope remains chronograph + weekday + date; month and moon phase remain assigned to LUNAR.

## 8. Immediate engineering conclusion

We can state the display-side speed boundary conditions conditionally, but cannot yet close the barrel-to-escape kinematic chain or select real tooth counts. The most valuable next physical evidence is a measured barrel/source speed and torque profile plus a controlled escapement interface definition. The reference movement documents supply useful external benchmarks, not the missing internal gear schedule.

## 9. Revision control

| Revision | Change | Disposition |
|---|---|---|
| 0.1 | Establishes controlled input groups, evidence hierarchy, gate sequence and conditional display-speed boundaries for square C-01 going train | Preliminary; design-authority review required |

**Disposition:** WP-SQ-05 is an input authority register. It selects no tooth schedule, gear system, barrel, escapement or plate geometry. No physical test, design freeze, manufacture, merge or deployment is authorized.
