# WP-41 — Chronograph Mechanism Integration and Detailed Assembly Definition

- **Document ID:** SEB-C01-WP-41
- **Revision:** A — initial controlled issue
- **Status:** Integrated functional/interface definition; no physical mechanism selected or released
- **Branch:** `steward/c-01-movement-foundation`
- **Software:** `tools/c01_chrono_integration.py`
- **Verification:** `tools/test_c01_chrono_integration.py`
- **Dependencies:** WP-11, WP-16, WP-17, WP-20, WP-25, WP-30, WP-32 through WP-40

## 1. Purpose

WP-41 defines one integrated functional architecture and interface register for the STEWARD C-01 chronograph. It connects the source drive, clutch/coupling, central chronograph seconds, minute and hour totalizers, stopped-train retention, control, reset hammer and heart cams. It also establishes the operating-state sequence, reset interlock requirement, unresolved decision register and prototype evidence gates.

This is an integration definition, not a final mechanical design. All component geometry, gear schedule, force, torque, materials, tolerances and performance limits remain subject to evidence and approval.

## 2. Functional architecture

The integrated functional path is:

**Going-train source → take-off interface → clutch/coupling → central chronograph seconds arbor → minute and hour totalizer branches.**

Parallel functional systems:
- **Control:** receives start/stop/reset commands and sequences the clutch, stopped-train restraint and reset hammer.
- **Stopped-train retention:** retains elapsed indication when drive is disengaged.
- **Reset:** hammer/heart-cam interfaces return the central seconds and both totalizer indications to their approved zero datums.
- **Interlock:** mechanically prevents reset actuation while the chronograph is running.

The role model is intentionally technology-neutral. It does not imply that a single part must implement each role, or that a specific clutch/control/brake arrangement has been chosen.

## 3. Functional component register

| Role | Required function | Design status |
|---|---|---|
| Drive source | Provide a traceable going-train power take-off | Source arbor TBD |
| Clutch/coupling | Engage/disengage chrono drive | Vertical vs horizontal open |
| Central seconds | Drive central chrono seconds indication | 1 rev/min target |
| Minute counter | Indicate elapsed minutes | Continuous vs jumping open |
| Hour counter | Indicate elapsed hours | Continuous vs jumping open |
| Stopped retention | Hold elapsed indication when stopped | Brake/detent/equivalent open |
| Control | Sequence operating states | Column wheel vs cam/lever open |
| Reset hammer | Apply reset contact to hearts | Common/separate arrangement open |
| Heart cams | Establish zero-return geometry | Profiles and datums TBD |

A component may implement multiple roles only when the controlled component register explicitly identifies that arrangement and its interfaces. Functional roles are not a bill of materials.

## 4. Interface-control register

The software requires these interface types to be represented with unique IDs, component endpoints, a definition, evidence ID and source revision:

| Interface | Functional boundary |
|---|---|
| drive_coupling | Source arbor to clutch input |
| seconds_output | Clutch output to central seconds arbor |
| minute_counter_drive | Chronograph train to minute totalizer |
| hour_counter_drive | Chronograph train to hour totalizer |
| stopped_retention_control | Control to stopped-train restraint |
| clutch_control | Control to clutch/coupling |
| reset_hammer_actuation | Control to reset hammer |
| seconds_reset | Reset mechanism to central seconds heart |
| minute_counter_reset | Reset mechanism to minute heart/index |
| hour_counter_reset | Reset mechanism to hour heart/index |
| running_reset_interlock | Running-state mechanism blocks reset actuation |

These are functional interfaces. Each detailed interface-control document must add, as applicable: mating geometry, axis/datum, degrees of freedom, direction of motion, travel, contact condition, axial stack, tolerance, load/force boundary, spring/return behavior, lubrication, inspection and verification method. No numerical value is assigned here.

## 5. Operating-state definition

| Current state | Command | Resulting state | Required mechanical outcome |
|---|---|---|---|
| stopped_zero | start | running | Engage drive; release retention; keep hammer clear |
| running | stop | stopped_retained | Disengage drive; retain elapsed indication |
| stopped_retained | start | running | Resume without losing elapsed value |
| stopped_retained | reset | stopped_zero | Apply reset; return all indications; withdraw hammer |
| running | reset | running | Block reset positively; no partial reset |

The executable validator checks this logical sequence. A reset command while running is accepted only when a physical interlock evidence reference is provided, and the state must remain running. A software evidence string is not physical proof; the referenced record must document inspection and testing of the actual mechanism.

## 6. Reset system integration

The reset assembly must account for all indicated chronograph axes and their zero datums. The detailed design must resolve:
- heart-cam profile, mounting and angular zero datum;
- hammer contact face, contact order and simultaneous or sequenced return;
- hammer pivot/translation, travel limits, spring return and withdrawal;
- hand and counter arbor retention against slip;
- minute/hour counter jumper or index release and reset phase;
- reset while stopped, blocked reset while running and interrupted pusher release;
- axial and radial clearances through the full reset stroke;
- force/travel measurement, zero-error measurement and repeat-cycle inspection.

Common versus separate hammers remains open. No spring rate, force, cam profile, angular tolerance or reset acceptance limit is invented.

## 7. Counter drive integration

The central chronograph seconds target remains one revolution per minute. The continuous counter conventions remain conditional: minute totalizer 1/30 rpm and hour totalizer 1/720 rpm. These are display-speed conventions only. If either counter is jumping, a separate event-driven design must define cadence, step angle, indexing member, jumper, release timing, impulse energy, anti-bounce behavior and reset phase.

No counter architecture or gear ratio is selected by WP-41.

## 8. Architecture decisions retained open

| Decision ID | Topic | Current status |
|---|---|---|
| D-01 | Vertical friction clutch vs horizontal/lateral coupling | Open |
| D-02 | Column wheel vs cam/lever control | Open |
| D-03 | Continuous vs jumping minute totalizer | Open |
| D-04 | Continuous vs jumping hour totalizer | Open |
| D-05 | Stopped-train brake, detent or equivalent | Open |
| D-06 | Common vs separate reset hammers | Open |
| D-07 | Source arbor and drive take-off | Open |
| D-08 | Counter branch topology and compound arbors | Open |
| D-09 | Detailed assembly geometry and axial stack | Open |

Any selection requires a controlled decision record, comparable evidence, design-authority approval and impact review against WP-30 and WP-32.

## 9. Executable integration model

Files:
- `tools/c01_chrono_integration.py`
- `tools/test_c01_chrono_integration.py`

The model validates:
- functional role completeness;
- unique component/interface IDs;
- valid interface endpoints and provenance;
- required functional interface coverage;
- unresolved decision register;
- start/stop/resume/reset state sequence;
- running-reset block with evidence reference;
- explicit non-authorization of design freeze and prototype release.

It does not calculate gear ratios, forces, torque, contact stress, energy, friction, timing, wear, reliability or physical fit. It does not create a detailed CAD assembly.

Run from the tools directory:

```sh
python -m unittest test_c01_chrono_integration.py
```

Synthetic fixtures are software test data only, not C-01 dimensions, interfaces or measurements.

## 10. Acceptance criteria

| ID | Criterion | Required evidence |
|---|---|---|
| WP41-AC-01 | All nine functional roles represented | Approved functional architecture |
| WP41-AC-02 | All eleven functional interface types documented | Interface-control register |
| WP41-AC-03 | Each interface has endpoints, definition and provenance | ICD/drawing references |
| WP41-AC-04 | Start, stop, resume and reset sequence is logically complete | State sequence review |
| WP41-AC-05 | Reset while running is physically prevented | Actual interlock inspection and test |
| WP41-AC-06 | All three indicated chronograph axes have reset interfaces and zero datums | Detailed mechanism drawings |
| WP41-AC-07 | Counter behavior and indexing architecture resolved | Approved counter design |
| WP41-AC-08 | Gear train and supports reconcile with WP-25 through WP-40 | Kinematic, CAD and support review |
| WP41-AC-09 | Energy, disturbance, rate, repeatability and wear verified | Approved WP-30 test procedures |
| WP41-AC-10 | Independent design review and configuration baseline complete | Signed WP-32 gate record |

## 11. Prototype assembly sequence — planning basis only

1. Establish approved datum and plate/bridge reference configuration.
2. Install and inspect source arbor and take-off supports.
3. Install selected clutch/coupling and verify disengaged clearance.
4. Install central seconds arbor and drive path.
5. Install minute and hour branches using approved counter architecture.
6. Install stopped-train restraint and verify retained indication.
7. Install control components and check state phasing.
8. Install heart cams, reset hammer(s), return springs and interlock.
9. Verify hand/counter zero datums, full reset stroke and running hammer clearance.
10. Conduct dimensional, kinematic, force/travel, energy and repeat-cycle checks under approved procedures.

This is not an assembly work instruction; detailed steps, torque values, lubrication and inspection limits must be issued in controlled manufacturing documentation.

## 12. Revision control and disposition

| Revision | Date | Change | Approval |
|---|---|---|---|
| A | 2026-11-27 | Initial integrated chronograph role architecture, interface register, state sequence, reset/interlock definition and synthetic validator | Pending independent engineering review |

**Disposition:** WP-41 integrates the chronograph at functional and interface level. No clutch, control, counter, stopped-retention or reset architecture is selected. C-01 remains unfrozen and is not released for physical manufacture. No merge or deployment is authorized.
