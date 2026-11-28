# STEWARD C-01 — Design-Authority Decision Register 01

**Document ID:** C01-DADR-001  
**Revision:** 0.1  
**Status:** Open decision register — no architecture decisions approved by this document  
**Branch:** `steward/c-01-movement-foundation`  
**Authority:** STEWARD C-01 design authority  
**Inputs reviewed:** Project README; WP-14 preliminary movement architecture and layout; Preliminary Mechanical Architecture 01; Dial-Side Display Arrangement Study 01; Mechanical Layout and Packaging Study 01; Mechanical Datum and Plate-Zone Skeleton 01  
**Purpose:** Convert the existing unresolved architecture questions into controlled decisions with explicit alternatives, evidence requirements, decision criteria and release consequences.

---

## 1. Decision-control rules

1. This register records choices that require design-authority approval. Listing an option does not select it.
2. No tooth counts, gear ratios, center distances, dimensions, tolerances, materials, spring specifications, torque values or performance values may be invented to make an option appear complete.
3. Distinguish documented baseline facts, proposed candidates, calculated results, measured evidence and unresolved assumptions.
4. A decision may be approved only when its required evidence is attached or referenced, trade criteria are agreed, consequences are understood and the approving authority is recorded.
5. A decision that changes the functional baseline must trigger requirements, interface, CAD, energy, verification and downstream-document impact review.
6. No decision in this register authorizes design freeze, manufacturing release, procurement, physical testing or prototype construction.
7. Where evidence is insufficient, the correct disposition is **OPEN** or **HOLD**, not a forced selection.

## 2. Verified baseline and boundary

The project README defines C-01 as an automatic mechanical chronograph with hours/minutes, weekday, day-of-month, central chronograph seconds, elapsed-minute and elapsed-hour counters, and running seconds. Hand winding and hacking seconds are desired functions whose compatibility remains to be checked.

The dial-side study describes three subdials: 30-minute counter, 12-hour counter and running seconds. The central chronograph seconds hand is a separate central indication.

The project README explicitly places month display and moon phase in the separate LUNAR concept. Accordingly, this register treats **month display as outside the current C-01 baseline**. Reintroducing it requires a formal scope change; it is not silently added to C-01.

The following remain proposed targets rather than validated performance:
- 4 Hz / 28,800 vph frequency;
- 60–70-hour power reserve aspiration;
- −4/+6 seconds per day rate objective.

The movement envelope remains open. The ETA 7750 dimensions in the packaging study are reference data only, not C-01 dimensions.

## 3. Decision summary

| ID | Decision | Current state | Required disposition |
|---|---|---|---|
| D-001 | Chronograph coupling | Horizontal/lateral and vertical candidates retained | Compare and approve one, or document a justified hybrid |
| D-002 | Chronograph control | Cam and column wheel retained; cam is only a preliminary study baseline | Compare and approve one |
| D-003 | Counter advancement | Continuous geared and indexed/jumping approaches remain to be reconciled per indication | Define behavior for each counter |
| D-004 | Chronograph drive take-off | Functional path identified; physical take-off and wheel topology unresolved | Approve source arbor and interface |
| D-005 | Dial arrangement | A, B and C remain open visual/packaging candidates | Select only after comparable mock-up and axis review |
| D-006 | Central hand-stack architecture | Coaxial representation is provisional; arbor/tube/support stack unresolved | Approve functional arbor stack and axial interfaces |
| D-007 | Calendar architecture | Weekday/date required; indexing, correction and setting-safety geometry unresolved | Approve mechanism and user-correction strategy |
| D-008 | Month display scope | Outside C-01 baseline; assigned to LUNAR | Closed at current baseline; scope change requires approval |

---

## 4. Decision records

### D-001 — Chronograph coupling

**Question:** How should the chronograph drive be coupled to and decoupled from the running train?

**Candidates**
- Horizontal/lateral coupling.
- Vertical clutch.
- Other arrangement only if a documented engineering case justifies it.

**Current evidence**
- Existing architecture studies retain horizontal and vertical approaches.
- A vertical clutch is a candidate, not an approved selection.
- No C-01 comparative physical test result is recorded in the reviewed baseline.

**Trade criteria to agree before scoring**
- Start-hand jump and engagement repeatability.
- Added load and timekeeping/amplitude disturbance with chronograph running.
- Energy consumption and reserve impact.
- Friction, wear, lubrication sensitivity and long-term stability.
- Packaging and axial stack consequences.
- Adjustment, assembly and service access.
- Manufacturing complexity, inspection burden and cost.

**Required evidence**
- Equivalent functional schematics for both candidates.
- Defined measurement methods and acceptance limits.
- Load-path and energy-budget comparison using traceable inputs.
- Packaging/interface comparison against the selected movement envelope.
- Prototype or reference-mechanism evidence before final approval.

**Status:** OPEN. No winner selected.

### D-002 — Chronograph control

**Question:** Should start/stop/reset sequencing use a cam-and-lever system or a column wheel?

**Candidates**
- Cam and lever control.
- Column-wheel control.

**Current evidence**
- Preliminary Mechanical Architecture 01 says cam is the first baseline candidate for manufacturing/service evaluation, while column wheel remains open.
- This is a study direction only, not an approved design decision.
- No comparative C-01 pusher-force, wear, tolerance, service or manufacturing evidence is established in the reviewed baseline.

**Trade criteria**
- Reliable sequencing and prevention of invalid state transitions.
- Pusher force, travel and tactile consistency.
- Reset timing and hammer coordination.
- Wear surfaces, contact stress and lubrication.
- Adjustment sensitivity and tolerance accumulation.
- Assembly complexity, inspection and serviceability.
- Manufacturing process capability and cost.

**Required evidence**
- Complete start/stop/reset state and interlock diagrams for each candidate.
- Contact/interface list and failure-mode review.
- Pusher force/travel measurement plan.
- Comparative prototype or reference-mechanism test data.
- Service procedure and adjustment assessment.

**Status:** OPEN. Cam remains a preliminary comparison baseline only.

### D-003 — Counter advancement behavior

**Question:** What is the intended advancement behavior for each chronograph counter?

**Candidates to evaluate**
- Continuously moving geared counter.
- Indexed or jumping counter.
- A mixed architecture where different counters use different behaviors.

**Required clarification**
- Define the visual behavior of the 30-minute register.
- Define the visual behavior of the 12-hour register.
- Confirm whether either counter must jump at discrete intervals.
- Define hand alignment and reset-to-zero requirements.

**Trade criteria**
- Readability at intermediate elapsed times.
- Load and energy demand.
- Gear-train complexity and backlash.
- Reset repeatability and hand stability.
- Packaging, service and durability.

**Required evidence**
- Time/angle kinematic specification for each hand.
- State-transition and reset sequence.
- Torque/load path for each candidate.
- Dial mock-up demonstrating legibility.

**Status:** OPEN. Do not assume both counters share the same behavior.

### D-004 — Chronograph drive take-off

**Question:** From which going-train arbor or derived wheel should the chronograph drive receive motion, and through what interface?

**Current evidence**
- The architecture documents identify a going-train chronograph take-off as a functional requirement.
- The physical take-off arbor, gear pair, ratio, location and load interface are not frozen.

**Trade criteria**
- Available speed and required downstream ratios.
- Torque margin in stopped and running chronograph states.
- Disturbance to timekeeping.
- Packaging and gear-mesh feasibility.
- Assembly and service access.
- Compatibility with selected clutch and counter architecture.

**Required evidence**
- Approved going-train topology and kinematic model.
- Measured or otherwise defensible torque/energy inputs.
- Candidate interface drawings and gear-mesh checks.
- Integrated power analysis for chronograph stopped and running.

**Status:** OPEN. No source arbor or gear topology selected.

### D-005 — Dial-side arrangement

**Question:** Which of the three display concepts should become the preferred packaging baseline?

**Candidates**
- **A:** 30-minute at 12, 12-hour at 6, running seconds at 9, paired weekday/date at 3.
- **B:** 30-minute at 3, 12-hour at 6, running seconds at 9, paired weekday/date at 12.
- **C:** conventional 12/6/9 register positions with compact paired weekday/date apertures near 12.

**Current evidence**
- The dial study preserves A/B/C and assigns no scores.
- Coordinates are normalized visual concepts, not millimetre dimensions.
- No case diameter, dial opening, aperture dimensions, hand lengths or shaft-axis locations are approved.

**Trade criteria**
- Everyday hour/minute and weekday/date legibility.
- Chronograph counter legibility and hierarchy.
- Crown, stem and pusher clearance.
- Calendar disc and indexing packaging.
- Hand-stack and hand-sweep clearance.
- Movement-axis feasibility and drive complexity.
- Visual balance and distinct STEWARD identity.
- Assembly and service access.

**Required evidence**
- Comparable 1:1 physical or accurately scaled dial mock-ups.
- Agreed legibility review conditions and acceptance criteria.
- Verified candidate shaft-axis feasibility.
- Calendar-disc, hand-stack and case-interface packaging review.
- Evidence-based comparison using the same criteria for all candidates.

**Status:** OPEN. No preferred layout selected.

### D-006 — Central hand-stack architecture

**Question:** What is the actual arbor, tube, bearing and axial-stack arrangement for the hour, minute and central chronograph seconds hands?

**Current evidence**
- Dial studies place the central indications at a common nominal XY datum.
- The documentation explicitly warns that this does not prove shared coaxiality or physical stack feasibility.
- Arbor diameters, tube geometry, bearing support, hand heights and clearances remain unresolved.

**Required evidence**
- Functional arbor diagram and torque paths.
- Axial stack drawing referenced to the approved dial plane.
- Bearing/support and endshake strategy.
- Hand-to-hand, hand-to-dial and hand-to-crystal clearance analysis with tolerances.
- Assembly, setting and service sequence.

**Status:** OPEN. The common center is a datum convention, not a completed mechanical design.

### D-007 — Weekday/date calendar architecture

**Question:** How will weekday and 1–31 date be driven, corrected and protected during setting?

**Current evidence**
- Weekday and day-of-month indications are required.
- Existing packaging study notes that a simple 1–31 date mechanism requires manual correction after shorter months unless a month-length mechanism is deliberately added.
- The exact safe-setting interval must be derived from final geometry and tested; it must not be guessed.

**Trade criteria**
- Reliable midnight changeover.
- Correct weekday/date progression.
- Behavior through 28-, 29-, 30- and 31-day months.
- User correction and setting ergonomics.
- Protection against correction under damaging calendar load.
- Serviceability, wear and dial-side packaging.

**Required evidence**
- Calendar state and indexing diagram.
- Corrector and crown/stem interface definition.
- Month-end behavior and user-operation specification.
- Safe-setting interval derived from mechanism geometry.
- Repeated-cycle prototype test and service procedure.

**Status:** OPEN. Functional requirements are set; mechanical implementation is not.

### D-008 — Month display scope

**Question:** Is a month display part of C-01?

**Current controlled baseline:** No. The project README assigns month display and moon phase to LUNAR, while C-01 remains chronograph + weekday + date.

**Disposition:** CLOSED for the current baseline. Any change requires explicit design-authority scope approval and impact assessment across dial, calendar mechanism, power, packaging, verification and documentation.

---

## 5. Decision scoring method — not yet populated

Do not assign numeric scores or weights until the design authority approves the criteria and their relative importance.

For each open decision:
1. Confirm the required function and operating conditions.
2. Agree criteria and any mandatory pass/fail constraints.
3. Identify evidence quality and uncertainty for each candidate.
4. Record advantages, disadvantages, risks and downstream interfaces.
5. Score only where evidence supports comparison.
6. Record dissent, residual risks and conditions of approval.
7. Obtain design-authority disposition.

A candidate with missing critical evidence cannot win solely because it is familiar, visually attractive or simpler to describe.

## 6. Required next engineering sequence

1. Confirm the functional/display behavior for the three chronograph counters and central seconds.
2. Complete the A/B/C dial comparison with a consistent mock-up and interface review.
3. Resolve the chronograph drive take-off and counter kinematics.
4. Compare coupling and control candidates using agreed criteria.
5. Define the central arbor stack and calendar interfaces.
6. Update the integrated architecture and interface register only after decisions are approved.
7. Establish a dimensioned CAD skeleton from traceable case/dial constraints and approved interfaces.
8. Release detailed component design only when the required source inputs exist.

## 7. Change history

| Revision | Date | Change |
|---|---|---|
| 0.1 | 2026-11-27 | Initial controlled decision register; records current baseline and unresolved decisions without selecting architecture. |

## 8. Release statement

This document is a decision-control artifact. It does not certify a completed movement design, select a chronograph architecture, establish dimensions, authorize manufacture or claim prototype readiness. All open decisions remain open until explicitly approved and supported by traceable evidence.
