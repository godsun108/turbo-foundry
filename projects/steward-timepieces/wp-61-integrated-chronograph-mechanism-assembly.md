# WP-61 — Integrated Chronograph Mechanism Assembly

- **Document ID:** SEB-C01-WP-61
- **Revision:** A — initial controlled issue
- **Status:** Integrated assembly definition framework; no C-01 geometry approved or released
- **Branch:** `steward/c-01-movement-foundation`
- **Software:** `tools/c01_integrated_chrono_assembly.py`
- **Verification:** `tools/test_c01_integrated_chrono_assembly.py`
- **Dependencies:** WP-20, WP-21, WP-22, WP-30, WP-31, WP-32, WP-33, WP-36, WP-40 through WP-59

## 1. Purpose

WP-61 integrates the chronograph functional architecture and interface requirements from WP-41 with the evidence-gated neutral component geometry, placements, mates and CAD source generation established by WP-59. It creates a complete functional assembly register for two separate candidates:
- **CW:** column-wheel control.
- **CL:** cam/lever control.

The work package defines the required functional roles, interfaces, structural support roles, candidate configuration and common baseline controls, and generates separate neutral OpenSCAD assembly sources from supplied WP-59 geometry. It does not invent missing components, dimensions, positions, tooth forms, profiles or mechanism behavior.

## 2. Assembly boundary and architecture status

The chronograph assembly boundary begins at the declared drive-source interface and includes:
- drive coupling and selected clutch candidate;
- central chronograph seconds arbor/indication;
- minute and hour totalizer branches;
- stopped-train retention;
- candidate-specific control mechanism;
- pusher input and operating-state command path;
- reset hammer and heart-cam functions;
- running-reset interlock;
- main plate, bridge support and bearing support interfaces.

This is a functional decomposition and controlled assembly register, not a released bill of materials. A functional role may share a physical component only when the WP-59 component record explicitly lists the role in `functional_roles`; no such sharing is inferred.

CW and CL remain distinct configurations. Both must reference the same requirements, datum and interface-baseline revisions to be compared. The candidate-specific control role is explicit:
- CW requires `column_wheel_control`.
- CL requires `cam_lever_control`.

The work package does not select either candidate, does not choose vertical versus horizontal/lateral clutch, and does not resolve the source arbor, counter topology, stopped-retention implementation, or common/separate reset-hammer question.

## 3. Functional component-role register

| Required role | Functional responsibility | Geometry status |
|---|---|---|
| `drive_source` | Declared chronograph drive take-off | Source and geometry TBD |
| `drive_coupling` | Transmit source motion to clutch input | Coupling type TBD |
| `clutch` | Engage/disengage chronograph train | Vertical/horizontal candidate open |
| `central_seconds` | Central chronograph seconds arbor and hand interface | Axis and gear train TBD |
| `minute_counter` | Elapsed-minute indication and drive | Continuous/jumping open |
| `hour_counter` | Elapsed-hour indication and drive | Continuous/jumping open |
| `stopped_retention` | Retain indication when stopped | Brake/detent/equivalent open |
| `column_wheel_control` / `cam_lever_control` | Candidate-specific sequencing and indexing | Candidate geometry TBD |
| `reset_hammer` | Transfer reset command to heart-cam interfaces | Common/separate arrangement open |
| `heart_cam` | Establish zero-return geometry for indications | Profiles and mounting TBD |
| `pusher` | External command input and sealing interface | Travel/force/seal TBD |
| `running_reset_interlock` | Positively block reset while running | Physical proof required |
| `main_plate` | Primary structural datum and support | WP-21 geometry TBD |
| `bridge_support` | Support structural and arbor-bearing members | Bridge architecture TBD |
| `bearing_support` | Locate/support rotating arbors | Bearing design and loads TBD |

Roles are engineering requirements, not an assertion that a component exists or that a particular component count is needed. The register is complete only when every role is mapped to a sourced WP-59 component record.

## 4. Functional interface-control register

The model requires unique, traceable interface records for these types:

| Interface type | Functional boundary |
|---|---|
| `drive_coupling` | Drive source to coupling/clutch input |
| `seconds_output` | Clutch/drive train to central seconds |
| `minute_counter_drive` | Chronograph train to minute totalizer |
| `hour_counter_drive` | Chronograph train to hour totalizer |
| `stopped_retention_control` | Control to stopped-train restraint |
| `clutch_control` | Control to clutch command |
| `reset_hammer_actuation` | Control to reset hammer |
| `seconds_reset` | Reset mechanism to seconds heart/zero interface |
| `minute_counter_reset` | Reset mechanism to minute indication |
| `hour_counter_reset` | Reset mechanism to hour indication |
| `running_reset_interlock` | Running-state control blocks reset actuation |
| `pusher_input` | Pusher to control input |
| `control_indexing` | CW indexer or CL follower/lever to state mechanism |
| `structural_support` | Structural member to supported mechanism |
| `bearing_support` | Bearing/support member to rotating arbor |

Each interface includes distinct component endpoints, definition, evidence ID and source revision. These are functional connections, not fully dimensioned mechanical joints. Detailed interface-control records still require approved mating geometry, datums, degrees of freedom, motion direction, contact conditions, force/load boundaries, axial stack, tolerances, lubrication, inspection and verification.

## 5. Integration with WP-59 CAD assembly

WP-61 calls the WP-59 component, hierarchy, mate and neutral OpenSCAD source routines. All component geometry and global placements remain explicit WP-59 inputs. Parent links remain organizational only; they do not compose local transforms.

Two independent source outputs are generated:
- CW integrated chronograph assembly envelope.
- CL integrated chronograph assembly envelope.

The source includes candidate/configuration/evidence/source comments. It is not rendered by this software. Cylinder, annulus and polygon primitives are neutral envelopes, not detailed involute gears, working column-wheel faces, cam/follower profiles, heart cams, springs, pivots or manufactured parts.

## 6. Operating states and physical interlock

The functional state sequence remains governed by WP-41 and WP-60:
- stopped at zero → running;
- running → stopped with elapsed time retained;
- stopped with retained elapsed time → running;
- stopped with retained elapsed time → reset to zero;
- reset while running must be positively blocked and leave the mechanism running.

WP-61's assembly register does not simulate these transitions. A component/interface role for the running-reset interlock is not proof that the interlock exists or functions. Physical evidence remains required under WP-30, WP-46 and controlled prototype test procedures. Software validation cannot authorize or substitute for physical testing.

## 7. Open engineering decisions

The following remain explicitly open:
1. Vertical friction clutch versus horizontal/lateral coupling.
2. Column-wheel versus cam/lever control.
3. Source arbor and going-train take-off.
4. Minute-counter continuous versus jumping.
5. Hour-counter continuous versus jumping.
6. Stopped-train brake, detent or equivalent retention.
7. Common versus separate reset hammers.
8. Heart-cam geometry, mounting and zero datums.
9. Bearing type, pivot geometry, support span and loads.
10. Main-plate/bridge arrangement, axial stack and case/dial interfaces.
11. Gear tooth counts, modules, profiles, center distances and backlash.
12. Materials, heat treatment, surface finish and lubrication.
13. Approved dimensional tolerances and performance acceptance limits.

No values or design winners are populated by WP-61.

## 8. Software validation and acceptance

The validator checks:
- both CW and CL packages exist and match common baseline revisions;
- WP-59 geometry, global placements, parent hierarchy and mate records validate;
- all required common and candidate-specific functional roles are mapped;
- all required interface types have unique IDs and valid distinct endpoints;
- open decisions remain recorded;
- separate CAD sources can be generated from the supplied geometry.

Synthetic tests cover candidate completeness, missing roles/interfaces, baseline mismatch, unresolved decisions and separate CAD source generation. Synthetic geometry is test data only and is not C-01 design information.

Run from the tools directory:

```bash
python -m unittest test_c01_integrated_chrono_assembly.py
```

No test execution or rendered CAD result is claimed by this document.

## 9. Release boundary

WP-61 does not certify physical fit, swept motion clearance, gear mesh, tooth contact, torque, energy, rate performance, durability, serviceability, shock resistance, manufacturability or safety. It does not authorize a prototype build, physical test, design freeze, manufacturing release, merge or deployment.

**Release statement:** WP-61 is a development-branch integrated assembly framework. CW and CL remain unselected. All geometry, interfaces and placements require controlled source evidence and design-authority approval before they can support physical prototype release.
