# STEWARD C-01 — WP-SQ-02 First Integrated Square Layout

**Document ID:** C01-WP-SQ-02  
**Revision:** 0.1  
**Status:** Preliminary topology layout — not dimensioned / not selected  
**Branch:** `steward/c-01-movement-foundation`  
**Prepared:** 2026-11-28  
**Related:** C01-ARCH-SQ-001; WP-SQ-01; WP-REF-01/02/03; C-01 design authority decision register

## 1. Purpose

Create the first integrated square C-01 mechanical layout that connects the required indications to their driving mechanisms and separates dial-side functions from movement-side power and regulation.

This is a real subsystem topology proposal, not a dimensioned component drawing. It identifies a coherent first arrangement to investigate, the interfaces that must exist, and the unresolved geometry that prevents a fit claim.

## 2. Study configuration

For this first layout iteration, **SQ-A is used as the working study configuration only**:

- rounded-square plate / bridge architecture;
- circular barrel, gear train, balance, escapement, rotor and wheel forms retained where mechanically appropriate;
- a concentrated circular timekeeping core;
- square-perimeter regions reserved for calendar, chronograph control, display and case interfaces.

This is not a design-authority selection of SQ-A over SQ-B or SQ-C. The other candidates remain open. SQ-A is simply the least assumption-heavy first configuration to lay out against the published circular benchmark envelope.

## 3. Reference envelope — comparator only

The SW500 a catalogue publishes a 30.00 mm nominal diameter, 30.40 mm maximum outside diameter and 7.90 mm overall height. These are reference-calibre published values, not C-01 dimensions or approved limits.

For the first overlay:
- retain a **30.00 mm reference circle** as a visual comparator only;
- show the **30.40 mm maximum reference envelope** as a separate comparator;
- do not scale or infer internal component locations from catalogue illustrations;
- do not assume a 30 mm circle fits the eventual square case or plate;
- do not use the 7.90 mm reference height as a C-01 stack target.

C-01 square case, plate, dial, crystal, caseback, and movement dimensions remain TBD.

## 4. Layout logic

### 4.1 Movement-side topology

The movement-side layout is organized around four functional regions:

1. **Power and automatic winding:** barrel and automatic winding system form the energy source. The rotor's full swept envelope must be treated as a keep-out volume above the bridges, not as a static point.
2. **Timekeeping core:** going train, escapement and balance form the continuous timekeeping path. Their actual wheel centers and mesh sequence remain to be derived from the selected train topology.
3. **Chronograph drive and control:** the chronograph receives power from a yet-to-be-selected going-train take-off. Coupling, control, brake and reset are treated as separate interfaces. No clutch or control architecture is selected.
4. **Calendar and motion works:** weekday/date drive is connected to the timekeeping/motion-works path, with correction and changeover interfaces reserved. The exact calendar arrangement remains open.

### 4.2 Dial-side topology

The first square display proposal uses square dial candidate D as the study overlay:

- central hour/minute display and central chronograph seconds;
- upper-left 30-minute elapsed counter;
- lower-right 12-hour elapsed counter;
- lower-left running seconds;
- upper-right paired weekday/date display.

The display axes are conceptual functional destinations. They are not approved coordinates, and the dial candidate D is not selected over A/B/C.

### 4.3 Axial layer stack

The following layer order is a functional stack hypothesis, not a thickness definition:

| Layer | Function | Required clearance / interface evidence |
|---|---|---|
| Crystal / bezel | Protects and retains dial/hand system | Crystal underside, bezel opening, gasket and hand clearance |
| Hands | Primary time and chronograph indications | Hand heights, coaxial stack, sweep and hand-to-hand clearance |
| Dial / display | Dial plate, apertures, calendar windows and register scales | Dial thickness, feet/attachment, aperture geometry, disc clearance |
| Dial-side mechanisms | Motion works, counter drives, calendar works, chronograph controls where applicable | Wheel/arbor support, jumper/corrector access, vertical interference |
| Mainplate / bridges | Structural datum and bearing supports | Plate thickness, bridge stiffness, locating and fastener interfaces |
| Movement-side mechanisms | Barrel, going train, escapement, balance and automatic winding | Gear meshes, rotor sweep, caseback clearance, shock and service access |
| Caseback | Enclosure and rotor protection | Internal depth, gasket, rotor clearance and extraction route |

No layer thickness, hand height, endshake, tolerance or clearance is assigned.

## 5. Functional drive paths

| Path ID | From | To | Function | Unresolved design input |
|---|---|---|---|---|
| P-01 | Rotor | Automatic winding works | Convert wrist motion into winding input | Rotor axis, winding direction, reverser/reduction topology, efficiency |
| P-02 | Winding works | Barrel | Wind and store energy | Arbor interface, torque, spring/barrel geometry |
| P-03 | Barrel | Going train | Deliver stored energy | Gear topology, ratios, torque profile |
| P-04 | Going train | Escapement / balance | Regulate release of energy | Train topology, escapement geometry, balance parameters |
| P-05 | Going train take-off | Chronograph coupling | Supply chronograph drive | Source arbor, speed, torque, take-off geometry |
| P-06 | Chronograph coupling | Chronograph drive train | Start/stop chronograph motion | Clutch type, engagement load, friction and axial stack |
| P-07 | Chronograph control | Coupling / brake / reset | Sequence start, stop and reset | Cam vs column wheel, lever geometry, pusher force and reset sequence |
| P-08 | Chronograph drive | 30-minute counter | Display elapsed minutes | Counter ratio, advancement behavior, hand load |
| P-09 | Chronograph drive | 12-hour counter | Display elapsed hours | Counter ratio, advancement behavior, hand load |
| P-10 | Going train / motion works | Running seconds | Continuous seconds display | Source arbor and ratio |
| P-11 | Motion works | Hour/minute hand stack | Display current time | Coaxial arbor/tube/support stack and hand heights |
| P-12 | Motion works | Weekday/date calendar | Index calendar indications | Calendar topology, indexing, correctors and safe-setting interval |
| P-13 | Calendar works | Weekday/date windows | Present calendar information | Disc/hand format, aperture geometry, legibility |
| P-14 | Case pushers | Chronograph control | User start/stop/reset input | Pusher positions, travel, sealing and force path |
| P-15 | Crown / stem | Winding, setting and calendar correction | User control | Stem axis, keyless works and correction interfaces |

The paths define required functions and interfaces only. They do not prescribe a tooth count, gear ratio, wheel center, clutch, cam, column wheel, or calendar mechanism.

## 6. Interface control points

The layout cannot advance to dimensioned CAD until the following control points have owners and evidence:

- **IC-01 — Case/movement seat:** internal case geometry, support pads, movement retention and extraction direction.
- **IC-02 — Stem/crown:** stem axis, height, keyless works, winding and setting modes.
- **IC-03 — Chronograph pushers:** pusher axes, seals, travel and control lever input.
- **IC-04 — Rotor/caseback:** full rotor sweep, axial clearance, impact protection and caseback depth.
- **IC-05 — Barrel/going train:** actual center distance, mesh, arbor support and power budget.
- **IC-06 — Going train/regulator:** escapement interface, balance clearance, shock protection and adjustment access.
- **IC-07 — Going train/chronograph:** source take-off, coupling interface and stopped/running loads.
- **IC-08 — Chronograph/counters:** counter ratios, advancement behavior, reset-to-zero and hand stack.
- **IC-09 — Calendar/display:** weekday/date indication type, indexing, disc geometry and aperture.
- **IC-10 — Dial/hand stack/crystal:** dial plane, hand heights, hand sweep and crystal clearance.
- **IC-11 — Plate/bridges:** support locations, stiffness, fastening, locating and service sequence.
- **IC-12 — Service access:** removal sequence for rotor, bridges, calendar, chronograph and wear components.

## 7. What is actually placed — and what is not

**Placed at topology level:**
- a central circular timekeeping-core region;
- a separate power/barrel and automatic-winding region;
- a chronograph drive/control region with explicit drive and control paths;
- a calendar/motion-works region;
- five dial-side display destinations in square candidate D;
- external crown and pusher input interfaces.

**Not placed in physical coordinates:**
- any wheel center or arbor axis;
- balance or rotor axis;
- barrel center;
- clutch, cam, column wheel, hammer or brake;
- counter or calendar wheel centers;
- plate outline, bridge edges, screw or jewel locations;
- stem and pusher coordinates;
- dial apertures or hand heights.

This distinction is intentional. The model is the first integrated mechanism topology; it is not a falsely precise CAD drawing.

## 8. Critical design decisions still open

The following remain open in the design-authority register:
- horizontal/lateral versus vertical chronograph coupling;
- cam versus column-wheel control;
- counter advancement behavior for each counter;
- chronograph take-off arbor;
- dial A/B/C and square D selection;
- central hand-stack architecture;
- weekday/date calendar mechanism.

Month display and moon phase remain outside C-01 and assigned to LUNAR.

## 9. Acceptance criteria for this work package

WP-SQ-02 is accepted as a preliminary topology layout when:
1. every required C-01 function is represented;
2. every indication has a declared functional drive path;
3. movement-side and dial-side mechanisms are distinguished;
4. case, crown, pusher, rotor and service interfaces are explicitly identified;
5. unknown geometry remains TBD rather than inferred;
6. reference-calibre dimensions are clearly marked comparator-only;
7. no architecture or scope change is implied.

The package does not pass dimensional fit, energy, kinematic, structural, reliability, or manufacturing validation.

## 10. Next engineering sequence

1. Acquire an applicable complete reference drawing package or an authorized physical specimen and traceable survey.
2. Establish a C-01 case/dial design envelope with user-approved size constraints.
3. Resolve the central hand stack and display-axis feasibility.
4. Select counter behavior and derive the chronograph kinematics.
5. Develop alternative drive take-off and clutch/control topologies.
6. Build the first dimensioned layout only after the input geometry and architecture are sufficiently defined.
7. Compare SQ-A against SQ-B and SQ-C using the same component envelopes and interface rules.

## 11. Revision history

| Revision | Date | Change |
|---|---|---|
| 0.1 | 2026-11-28 | First integrated square topology layout; no physical coordinates or architecture decisions frozen |

## 12. Release statement

This document records a preliminary engineering topology for investigation. It does not establish a dimensioned C-01 movement, validate square-case fit, select a movement architecture, authorize procurement or manufacture, or approve design freeze.
