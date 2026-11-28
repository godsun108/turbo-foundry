# STEWARD C-01 — WP-SQ-03 Central Mechanical Core and Train Topology

**Document ID:** C01-WP-SQ-03  
**Revision:** 0.1  
**Status:** Preliminary topology proposal — no physical coordinates or dimensions approved  
**Branch:** `steward/c-01-movement-foundation`  
**Prepared:** 2026-11-28  
**Related:** WP-14; WP-25 through WP-29 engineering work; WP-SQ-01/02; WP-REF-01/02/03; C-01 design authority decision register

## 1. Purpose

Advance the square C-01 concept from subsystem blocks to a coherent central mechanical topology. This package defines:
- a candidate energy path from automatic winding and barrel through the going train and regulator;
- the interfaces needed for a chronograph take-off without prematurely choosing its source arbor;
- a spatial zoning strategy for a rounded-square plate;
- rotor, balance, bearing, bridge and service constraints;
- the evidence required before any coordinate or dimension is released.

This is an engineering topology, not a dimensioned gear-train design, CAD assembly, or claim of physical fit.

## 2. Baseline and study configuration

C-01 functional baseline remains automatic winding, hours/minutes, weekday, date 1–31, central chronograph seconds, elapsed-minute and elapsed-hour counters, and running seconds.

SQ-A is the working topology configuration for this study only: rounded-square plate/bridge envelope with mechanically appropriate circular elements. SQ-B and SQ-C remain open alternatives. Dial candidate D remains a square display concept only; A/B/C are not superseded.

The preliminary 4 Hz frequency, 60–70-hour reserve aspiration and −4/+6 s/day rate goal remain unvalidated. Month and moon phase remain outside C-01 and assigned to LUNAR.

## 3. Proposed central going-train topology T-A

### 3.1 Functional chain

The first train topology to investigate is a conventional center-seconds-style mechanical going-train chain:

**Mainspring barrel → center wheel / center arbor → third wheel → fourth wheel / seconds arbor → escape wheel → pallet fork → balance.**

This chain is a candidate functional topology, not a selected wheel count or a validated C-01 gear train. The actual wheel arrangement, direction, ratios, tooth counts, center distances, arbor positions and escapement type must be derived and checked.

The center arbor is a useful candidate interface for the ordinary time display's minute motion, while the fourth-wheel arbor is a candidate source for continuous running seconds. These are functional role hypotheses only. The exact motion-works and hand-stack arrangement must be reconciled with the central chronograph seconds hand and the dial-side counter layout.

### 3.2 Required kinematic definitions

Before gear synthesis, define and approve:
- desired output speed for each arbor;
- direction of rotation viewed from dial side;
- number and type of external/internal meshes;
- required hand/display ratio;
- escapement frequency and beat relationship;
- permissible train loading and amplitude disturbance;
- chronograph take-off source and stopped/running load cases.

For each gear pair, the eventual calculation record must include tooth counts, module or diametral pitch, pressure angle, addendum/dedendum system, center distance, backlash, material, face width, profile modification if any, lubrication and manufacturing tolerance. None is assigned in this package.

## 4. Spatial zoning strategy — not coordinates

Use the controlled datum convention from WP-14: nominal display center O=(0,0), +X toward 3 o'clock, +Y toward 12 o'clock, Z=0 at the approved dial plane and positive Z toward the movement side. The convention does not imply that the balance, barrel or any other arbor has a known coordinate.

The rounded-square plate is divided into functional zones rather than dimensioned placements:

| Zone ID | Functional reservation | Placement rule | Evidence needed before coordinates |
|---|---|---|---|
| Z-PWR | Barrel and winding input | Keep energy source and winding interface accessible; preserve barrel bridge support | Barrel envelope, spring data, torque-angle curve, winding train geometry |
| Z-TRN | Going-train corridor | Preserve a continuous mesh path with bearing support at every arbor | Selected train topology, gear geometry, center distances and torque budget |
| Z-REG | Balance / escapement | Protect regulator from rotor, case impact and service interference | Balance/escapement package, shock system, adjustment access, dynamic clearance |
| Z-AUTO | Rotor and automatic works | Treat rotor as a swept volume across its full operating angle and axial plane | Rotor mass properties, bearing, winding works, sweep, caseback and bridge clearances |
| Z-CHR | Chronograph drive/coupling/control | Keep take-off, coupling, brake and reset loads traceable and serviceable | Selected take-off, clutch/control architecture, counter kinematics and loads |
| Z-CAL | Weekday/date | Reserve dial-side volume and correction/changeover access | Calendar topology, disc geometry, jumper loads and safe-setting study |
| Z-HS | Central hand stack | Reserve central axis without assuming coaxial arbor feasibility | Arbor/tube design, bearing support, friction, hand heights and axial clearances |

No zone is a physical rectangle, component center, or approved keep-out boundary. SQ-A plate outline and bridge shapes remain TBD.

## 5. Barrel and automatic-winding module

The energy-source module consists of the barrel, barrel arbor, winding input and supporting bridge/plate structure. Its location must be selected jointly with the going-train mesh path, crown/stem access, rotor sweep and service route.

Automatic winding module elements to resolve:
- rotor and rotor bearing/support;
- unidirectional or bidirectional winding strategy;
- reversing/reduction train architecture, if required;
- winding-to-barrel interface;
- overwind/slipping behavior;
- winding efficiency and wear;
- rotor clearance to bridges, balance, caseback and case;
- service access and rotor removal sequence.

No winding architecture is selected. A full-angle rotor sweep must be modeled as a swept envelope, not a single rotor pose. Dynamic deflection and shock clearance must be considered in a later tolerance/structural study.

## 6. Chronograph interface — intentionally unresolved

The chronograph needs a drive input from the going train, but the source arbor is not selected. Preserve at least these study candidates:
- take-off from the center-wheel/center-arbor path;
- take-off from the fourth-wheel/seconds-arbor path;
- take-off from another derived wheel or intermediate stage, if supported by kinematic and energy analysis.

Compare each on required speed conversion, torque margin, disturbance to timekeeping, clutch packaging, counter ratios, hand jump, energy reserve and service access.

The clutch remains horizontal/lateral versus vertical open. Control remains cam versus column wheel open. The 30-minute and 12-hour counter advancement behaviors remain open independently. The central chronograph seconds and ordinary running seconds must remain distinct indications.

## 7. Bridge, bearing and support concept

Candidate bridge groups for investigation:
1. barrel / winding support;
2. going-train support;
3. escapement and balance support;
4. chronograph drive/control support;
5. calendar retaining/support structure;
6. automatic winding rotor support.

This is not a final part breakdown. Bridge consolidation or separation must be justified by pivot support, stiffness, locating repeatability, screw access, assembly order, lubrication access, shock path and serviceability.

Every rotating arbor requires a defined support strategy. The eventual bearing register must identify pivot dimensions, jewel or bushing type, endshake, radial clearance, lubrication, load, shock protection, inspection and replacement method. No jewel count, jewel location or bearing dimensions are assigned.

## 8. Axial stack and interference control

The following interfaces require a linked 3D stack model:
- dial and calendar disc layers;
- motion works and central arbor/tube stack;
- counter wheels and counter hands;
- chronograph clutch and control components;
- mainplate and bridges;
- barrel and going-train wheel planes;
- balance/escapement and shock-setting envelope;
- rotor plane, rotor bearing and caseback;
- crystal underside, hand sweep and dial plane.

For every interface, later design release must state nominal clearance, tolerance stack, worst-case clearance, dynamic allowance, assembly direction and inspection method. This package assigns none of those values.

## 9. Core topology interface register

| Interface | Inputs required | Verification |
|---|---|---|
| Barrel → center wheel | Barrel torque/speed, wheel geometry, arbor support | Kinematic and torque calculation; mesh inspection |
| Center → third wheel | Speed ratio, tooth geometry, center distance | Gear synthesis and tolerance analysis |
| Third → fourth wheel | Speed ratio, tooth geometry, center distance | Gear synthesis and tolerance analysis |
| Fourth → escape wheel | Escapement speed and energy demand | Dynamic/energy model and prototype test |
| Escape wheel → pallet/balance | Escapement geometry, impulse and locking | Escapement analysis and rate/amplitude test |
| Going train → chronograph | Candidate take-off, load and coupling | Stopped/running power comparison |
| Rotor → winding works | Rotor dynamics and winding direction | Winding efficiency and shock test |
| Winding works → barrel | Winding torque and overwind behavior | Torque/energy test |
| Motion works → calendar | Changeover and correction load | Calendar cycle and safe-setting tests |
| Central works → hands | Arbor stack and hand loads | Axial stack and hand-clearance inspection |

## 10. Engineering calculations required next

No numeric result is claimed. The next calculation package must establish, with traceable inputs:

1. **Train speed synthesis:** solve arbor speeds from approved output requirements and gear tooth counts.
2. **Direction synthesis:** track direction through each mesh.
3. **Torque flow:** calculate available torque at each arbor with explicitly stated mesh/bearing loss assumptions.
4. **Power reserve:** integrate measured or supplier-confirmed mainspring torque-angle and movement demand; do not infer reserve from the reference caliber.
5. **Regulator energy:** calculate and later measure escapement energy demand and amplitude sensitivity.
6. **Chronograph load:** compare stopped and running chronograph states with the selected take-off and clutch.
7. **Automatic winding:** evaluate rotor inertia, winding input and energy transfer using measured or defensible mass properties.
8. **Tolerance stack:** establish minimum clearances through the full axial and radial stack.

## 11. Acceptance criteria for WP-SQ-03

This work package is accepted as a preliminary central topology when:
- every required C-01 function has an identified path or explicitly open interface;
- a candidate going-train chain is documented without invented tooth counts or coordinates;
- barrel, train, regulator, automatic winding and chronograph are linked in one energy/mechanical system;
- all spatial zones and critical interfaces are identified;
- the rotor is treated as a swept volume;
- bridge and bearing support needs are explicit;
- the central hand stack, calendar and chronograph source remain unresolved where evidence is missing;
- all dimensional and performance unknowns remain TBD.

It does not establish dimensional fit, gear-train performance, reserve, rate, amplitude, winding efficiency, reliability, manufacturability, design freeze or prototype readiness.

## 12. Next gate

WP-SQ-04 should develop a parametric going-train kinematic synthesis model. It should accept declared output speeds and candidate tooth counts, calculate arbor speed and direction, and reject invalid/underspecified gear meshes. All numerical examples must be explicitly synthetic fixtures until approved C-01 inputs exist.

## 13. Revision history

| Revision | Date | Change |
|---|---|---|
| 0.1 | 2026-11-28 | Initial central mechanical core and going-train topology proposal |

## 14. Release statement

This document records a candidate engineering topology for investigation. It is not a final architecture decision, dimensioned layout, supplier drawing, production specification or authorization to manufacture.
