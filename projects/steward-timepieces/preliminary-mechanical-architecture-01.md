# STEWARD C-01 — Preliminary Mechanical Architecture 01

**Revision:** 0.1  
**Status:** Preliminary architecture definition — for engineering review  
**Branch:** `steward/c-01-movement-foundation`  
**Design authority:** STEWARD C-01 requirements baseline  
**Release state:** Not a production specification; no architecture or dimensions frozen

## 1. Purpose

Translate the approved functional requirements, dial-side study, kinematic worksheet, packaging study, benchmark work and architecture trade study into a coherent preliminary mechanical system architecture.

This document defines subsystem responsibilities, interfaces, candidate arrangements, engineering constraints and the next evidence required. It deliberately does not invent tooth counts, spring dimensions, torque values, gear modules, center distances, clearances or manufacturing tolerances.

## 2. Design basis and status

### 2.1 Required indications and functions

- Automatic mechanical winding.
- Hours and minutes.
- Weekday indication.
- Day-of-month indication, 1–31.
- Central chronograph seconds.
- 30-minute chronograph register.
- 12-hour chronograph register.
- Continuous running seconds.

Manual winding and hacking seconds remain desired functions and must be checked against the selected architecture.

### 2.2 Preliminary targets

| Parameter | Current basis | Status |
|---|---:|---|
| Oscillator frequency | 4 Hz / 28,800 vph | Preliminary target |
| Power reserve | 60–70 h | Aspirational; energy budget not closed |
| Rate objective | −4/+6 s/day | Proposed; test protocol incomplete |
| Movement envelope | Open | No C-01 dimensions frozen |
| Chronograph control | Cam and column wheel | Both retained for evaluation; cam is first baseline candidate |
| Chronograph coupling | Horizontal and vertical | Both retained for evaluation |
| Calendar | Weekday + 1–31 date | Required; month-end manual correction expected unless a month-length mechanism is added |

### 2.3 Reference envelope, not a C-01 target

The ETA 7750 and Sellita SW500 day-date family provide useful functional and packaging benchmarks at approximately 30.00 mm diameter and 7.90 mm height in their published specifications. These values are reference points only. C-01's envelope must be derived from the chosen dial, hand stack, calendar, chronograph, rotor, case and service-access requirements.

Record the exact caliber variant and manufacturer document revision whenever benchmark dimensions or performance are reused.

## 3. Top-level mechanical architecture

C-01 is to be studied first as an integrated automatic chronograph with an independently serviceable calendar subsystem. This is the leading study direction, not an approved design freeze. A modular alternative remains available if measured development risk, cost or schedule makes it materially preferable.

### 3.1 Functional power and control paths

**Energy path**

Automatic rotor → winding/reversing works → mainspring barrel → going train → escapement and balance.

Manual winding, if retained, feeds the winding works through the crown/stem interface.

**Time indication path**

Going-train take-off → motion works → hour and minute hands.

Going-train take-off → running-seconds display.

**Chronograph path**

Going-train chronograph take-off → chronograph drive → selected coupling → central chronograph seconds and elapsed-time counter trains.

Start/stop/reset pushers → control mechanism → coupling, brake and reset hammers.

**Calendar path**

Going-train/calendar take-off → calendar program and indexing mechanism → weekday and date displays.

Crown/stem or dedicated correctors → calendar correction interfaces, subject to safe-setting and packaging studies.

These are functional relationships, not a physical placement drawing or final wheel topology.

## 4. Subsystem architecture

### 4.1 Barrel and energy storage

**Baseline to investigate:** one mainspring barrel driving the base going train.

A single barrel is the lowest-complexity starting point. Twin barrels, series/parallel barrel arrangements or other energy-storage strategies should be considered only if a measured or defensible energy budget shows that a single barrel cannot meet the reserve and torque-stability objectives within the packaging envelope.

Required design inputs:
- Barrel outside diameter, height and arbor geometry.
- Mainspring material, thickness, width, length and attachment method.
- Usable winding angle and safe operating range.
- Delivered torque as a function of unwind angle.
- Bridle/slipping behavior for automatic winding.
- Barrel arbor and wheel interface.
- Torque reserve needed for low-amplitude and low-reserve operation.

Required analysis:
- Integrate the measured or supplier-supported torque curve over usable angular travel.
- Estimate total train demand with chronograph stopped and running.
- Include calendar changeover and chronograph actuation transients.
- Evaluate amplitude and rate stability from full wind to the defined stopping threshold.
- Quantify uncertainty and identify inputs requiring physical measurement.

No barrel dimensions, spring dimensions, torque curve or reserve guarantee is assigned in this revision.

### 4.2 Going train

The going train must supply the escapement, motion works, running seconds and the chronograph drive take-off without unacceptable rate or amplitude disturbance.

The required indication speeds are controlled by the kinematic worksheet:
- Running seconds: 1 revolution per minute.
- Minute hand: 1 revolution per hour.
- Hour hand: 1 revolution per 12 hours.

The final train topology must be derived from the selected escapement, escape-wheel geometry, barrel speed, available center distances and packaging. A correct display ratio alone does not prove adequate torque or efficiency.

Required decisions:
- Center-wheel / third-wheel / fourth-wheel / escape-wheel topology.
- Chronograph drive take-off location and loading.
- Calendar take-off location and indexing interval.
- Motion-works arrangement and hand-setting friction.
- Wheel and pinion tooth geometry, modules, materials and lubrication.
- Pivot, jewel, endshake and backlash requirements.

No tooth counts or center distances are selected in this revision.

### 4.3 Balance and escapement

**Frequency study baseline:** 4 Hz (28,800 vph), retained as a preliminary target because it is consistent with the principal day-date chronograph benchmarks.

The oscillator and escapement must be designed as a matched system. Frequency alone does not establish accuracy, robustness or energy consumption.

Required definition:
- Escapement type and geometry.
- Escape-wheel tooth count and impulse relationship.
- Balance diameter, inertia and poising method.
- Hairspring material, geometry, attachment and terminal curve.
- Balance staff, pivots and shock-protection system.
- Regulator or free-sprung approach.
- Beat error adjustment and service procedure.
- Lubrication points and inspection criteria.

Required validation:
- Amplitude and rate across positions and power states.
- Chronograph stopped versus running.
- Full, intermediate and low reserve.
- Temperature sensitivity and magnetism response.
- Shock testing against a selected, documented test standard.
- Repeatability after service and regulation.

No balance dimensions, hairspring geometry, escapement tooth count or accuracy claim is approved here.

### 4.4 Chronograph drive, clutch and controls

The chronograph is treated as four distinct functional elements:

1. **Drive:** derives motion from the going train and supplies the chronograph train.
2. **Control:** sequences start, stop and reset from the pushers.
3. **Coupling and brake:** engages/disengages the chronograph and holds the hands stationary when stopped.
4. **Counters and reset:** drives the elapsed-time indications and returns hands to zero.

Candidate decisions remain separate:

| Decision | Candidates | Preliminary treatment |
|---|---|---|
| Control | Cam; column wheel | Cam is the first baseline candidate for manufacturing/service evaluation; column wheel remains open |
| Coupling | Horizontal/lateral; vertical | Compare measured start jump, drag, amplitude disturbance, wear and service requirements |
| Counter drive | Continuous geared train and/or indexed stages | Determine from exact counter behavior and mechanism geometry |
| Reset | Heart cams, hammers and return springs | Define after arbor positions and counter loads are known |

A vertical clutch is not synonymous with column-wheel control. Either control architecture may be evaluated independently of coupling choice.

Required load cases:
- Chronograph stopped.
- Chronograph running continuously.
- Start and stop at high, medium and low mainspring torque.
- Reset from multiple elapsed-time positions.
- Repeated start-stop-reset cycling.
- Chronograph operation during automatic winding.
- Calendar changeover while chronograph is stopped and running.

Measure rate, amplitude, power consumption, start-hand displacement, pusher force/travel, reset alignment and wear. No numerical acceptance threshold is invented before prototype data and test methods exist.

### 4.5 Weekday and date calendar

Required displays:
- Weekday: seven positions.
- Date: 1–31.

A conventional 1–31 date display requires manual correction after months shorter than 31 days. It must not be described as annual or perpetual unless a month-length mechanism is deliberately designed and validated.

Candidate construction:
- Separate weekday and date discs with their own indexing/jumper elements.
- A shared calendar program/drive with separate output indexing.
- Independent correction interfaces, subject to packaging and misuse analysis.

The final design must specify:
- Calendar take-off and 24-hour indexing relationship.
- Weekday and date indexing geometry.
- Changeover timing and whether switching is instantaneous or gradual.
- Simultaneous day/date changeover load.
- Jumper force, spring loads and retention.
- Quick-set mechanism and correction direction.
- Crown positions or dedicated corrector geometry.
- Protection against correction while the calendar train is loaded.
- Safe-setting window derived from the actual mechanism.
- Behavior when hands are positioned around midnight.
- Month-end user procedure and leap-year limitations.

The safe-setting window must not be copied from another caliber or published until C-01's calendar is designed and tested. User instructions must describe the actual mechanism.

### 4.6 Automatic winding, stem and setting interfaces

The automatic winding system must be assessed for winding efficiency, rotor clearance, noise, bearing durability and service access.

Define:
- Rotor mass, inertia, sweep and bearing.
- Reversing/winding architecture.
- Winding ratio and direction behavior.
- Bridle/slipping interface.
- Crown/stem positions and setting sequence.
- Hacking interface, if retained.
- Manual winding compatibility, if retained.
- Access for cleaning, lubrication and replacement.

The rotor must not obstruct routine adjustment or removal of critical chronograph and escapement components without a justified service sequence.

## 5. Dial arrangements remain in parallel

No dial identity is selected in this architecture revision.

- **A — Traditional:** three-register arrangement; weekday and date at 3.
- **B — Balanced:** registers at 3, 6 and 9; weekday and date at 12.
- **C — Distinctive compact calendar:** traditional counter positions; paired calendar display near 12.

Each candidate must be evaluated against the same movement functions and comparable dial dimensions. The layout study's coordinate variables remain TBD until a case/dial envelope and verified shaft-axis references are available.

A dial mock-up can verify visual hierarchy and legibility; it cannot establish that the movement fits or that the calendar and chronograph can physically occupy the proposed positions.

## 6. Provisional physical envelope and datum strategy

**Envelope status: OPEN.** Do not assign a nominal diameter or height based only on a benchmark caliber.

Establish a common coordinate system before CAD:
- XY origin: central hour/minute/chronograph axis.
- Z datum: defined dial plane.
- Primary axes: central arbor, subdial arbors, balance staff, barrel arbor, stem and pusher axes.
- Case interface: movement support plane, casing clamps/feet, anti-rotation features and caseback clearance.

Parametric CAD should begin with a skeleton model containing:
- Case and dial envelope parameters.
- Dial opening and crystal/caseback limits.
- Hand-stack Z planes and clearances.
- Candidate register axes for A, B and C.
- Weekday/date aperture and disc zones.
- Barrel, rotor, balance and escapement reserved zones.
- Stem and pusher interface axes.
- Bridge/service-access zones.

Use three parameter states:
- **Measured:** verified from a documented physical sample or drawing.
- **Supplier-confirmed:** stated in a current manufacturer document.
- **Provisional:** design assumption requiring review.

Every parameter must record its source, revision, uncertainty and owner. A placeholder is not a dimension.

## 7. Architecture interface register

| Interface | Inputs / outputs | Evidence required before freeze |
|---|---|---|
| Barrel → going train | Torque, speed, arbor and wheel geometry | Torque curve, usable travel, power budget |
| Going train → escapement | Speed, impulse energy, arbor geometry | Escapement design and amplitude analysis |
| Going train → motion works | Required time-display speeds | Verified ratios and hand-setting analysis |
| Going train → chronograph | Drive speed and available torque | Take-off study and measured chronograph load |
| Chronograph → registers | Counter speed, direction and reset | Kinematic closure and reset-repeatability tests |
| Going train → calendar | Daily indexing drive | Calendar ratio, changeover load and timing |
| Calendar → dial | Disc positions and apertures | Dial layout, disc geometry and hand clearances |
| Rotor → winding works | Motion, torque and winding direction | Winding-efficiency and durability tests |
| Stem/pushers → controls | User input and actuator travel | Force/travel measurements and misuse tests |
| Movement → case | Supports, stem, pushers and clearances | Case interface drawing and tolerance stack-up |

## 8. Failure and service considerations to carry into FMEA

Initial failure modes for formal analysis:
- Mainspring fatigue, breakage or slipping failure.
- Low torque causing amplitude collapse or inconsistent calendar/chronograph operation.
- Gear tooth wear, damage, excessive backlash or pivot friction.
- Escapement contamination, shock damage or hairspring interference.
- Chronograph clutch slip, drag, engagement jump or failure to disengage.
- Reset hammer/heart-cam misalignment or incomplete return to zero.
- Calendar jumper failure, incomplete indexing or date/day misalignment.
- User correction during an unsafe calendar state.
- Rotor bearing wear, winding failure or rotor/caseback interference.
- Corrosion, lubricant migration, magnetism and shock-related damage.

For each, the FMEA must record severity, occurrence, detectability, mitigation, test evidence and service remedy. Ratings are not assigned in this document without an agreed scoring method.

## 9. Next engineering sequence

1. Verify and revision-control the exact ETA 7750 and Sellita SW500 a technical drawings and service documentation.
2. Obtain or measure a lawfully sourced reference movement; document its identity before teardown.
3. Complete a component/function map for the barrel, going train, escapement, chronograph, calendar and automatic winding system.
4. Build a traceable input register separating measured, supplier-confirmed and provisional data.
5. Close the first barrel/energy budget using sourced or measured torque and load inputs.
6. Compare cam and column-wheel control; compare horizontal and vertical coupling using the same test matrix.
7. Define the calendar drive, indexing, correction and safe-setting logic.
8. Build the common parametric skeleton for dial arrangements A, B and C.
9. Review service access, assembly sequence and preliminary FMEA with an independent watchmaker.
10. Only after these reviews, select a preferred architecture and begin detailed component CAD.

## 10. Release gates

This document supports preliminary architecture discussion only.

Do not release detailed production drawings or supplier manufacturing data until:
- Requirements and architecture decisions are reviewed and traceable.
- Envelope and critical interfaces are dimensioned.
- Gear ratios close mathematically and tooth geometry is checked.
- Energy budget closes with documented torque/load assumptions.
- Chronograph and calendar mechanisms pass subsystem tests.
- Tolerance stack-ups, materials, lubrication and assembly sequence are specified.
- FMEA mitigations and service procedures are reviewed.
- Independent watchmaking review is complete.

## 11. Current decision register

| Decision | Status |
|---|---|
| Develop all three dial arrangements | Continue in parallel |
| Integrated vs modular | Integrated is leading study; not frozen |
| Cam vs column-wheel control | Cam first baseline candidate; column wheel retained |
| Horizontal vs vertical clutch | Open; evidence required |
| Single vs multiple barrels | Single barrel baseline; energy budget decides |
| Frequency | 4 Hz preliminary target |
| Movement diameter/height | Open |
| Gear tooth counts and center distances | Open |
| Balance/hairspring/escapement geometry | Open |
| Calendar correction architecture | Open |
| Month-length mechanism | Out of scope unless explicitly added |
| Production drawings / prototype | Not released / not built |

---

**Engineering integrity note:** This is a preliminary mechanical architecture definition. It is not a dimensioned movement drawing, parametric CAD model, supplier specification, manufactured prototype or validated performance claim.
