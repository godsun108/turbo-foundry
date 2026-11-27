# WP-34 — Chronograph Drive Train and Reset Mechanism Design

- Document ID: SEB-C01-WP-34
- Revision: A — initial controlled issue
- Status: Parametric engineering framework; no C-01 drive train or reset geometry released
- Branch: steward/c-01-movement-foundation
- Software: tools/c01_chrono_drive_reset.py
- Verification: tools/test_c01_chrono_drive_reset.py
- Dependencies: WP-11, WP-16, WP-17, WP-19, WP-20, WP-23, WP-25, WP-26, WP-27, WP-28, WP-29, WP-30, WP-33

## 1. Purpose

WP-34 defines the calculation and drawing interfaces needed to move from chronograph architecture candidates to a controlled prototype mechanism. It covers the source drive path, central seconds branch, minute/hour totalizer branches, stopped-train retention, reset hammer and heart-cam interfaces, and measured reset energy.

This is not a selected physical design. No source arbor, gear tooth schedule, module, center coordinate, heart-cam profile, hammer force, spring rate, material, tolerance, lubrication or acceptance limit is assigned.

## 2. Power-path architecture

The controlled functional path is:

Going-train source arbor → approved take-off interface → selected clutch/coupling → central chronograph seconds arbor → totalizer branches.

The source arbor remains an open decision. WP-15/WP-17 retain the fourth-wheel/seconds-arbor take-off and dedicated-drive alternatives. The 1 rpm central chronograph seconds display is a functional output target, not evidence that the source arbor itself runs at 1 rpm.

Every proposed path shall identify:
- source and destination arbor IDs mapped to WP-20/WP-21 registers;
- driver/driven gear IDs and positive integer tooth counts;
- external/internal mesh type and rotation direction;
- rigid compound-wheel relationships;
- evidence ID and source drawing revision for every stage;
- measured/approved source speed and operating condition;
- required output period and approved fractional tolerance.

For a mesh, the ideal signed speed ratio is -z_driver/z_driven for external engagement and +z_driver/z_driven for internal engagement. Compound stage ratios multiply. Exact rational arithmetic avoids rounding during candidate closure. The result is kinematic only; it does not establish tooth strength, contact ratio, backlash, friction, torque capacity, efficiency or physical fit.

## 3. Output branches and counter behavior

The central seconds branch targets one revolution per 60 seconds. WP-17's continuous-indication conventions are retained conditionally: the 30-minute register makes one revolution per 1,800 seconds and the 12-hour register one revolution per 43,200 seconds.

Those conventions are not frozen counter architectures. For each totalizer, the design authority must choose continuous or jumping indication through controlled requirements and evidence. A jumping counter needs an event source, event cadence, star/index geometry, step angle, jumper, drive/release sequence, anti-bounce behavior, phase, transient torque and reset behavior. Average RPM cannot replace this event definition.

Each branch drawing shall show the take-off arbor, all compound members, gear meshes, support points, counter mechanism, hand arbor and reset heart-cam interface. Gear paths must be separately closed and reconciled against WP-17 and WP-25. A branch may not silently borrow an assumed source speed.

## 4. Stopped-train retention and operating states

The chronograph must have a defined stopped state that retains the elapsed value after drive disengagement. A brake, detent or equivalent restraint is a design choice requiring candidate-specific geometry and evidence; WP-34 does not choose one.

Required physical sequence:
1. Start: couple the source, release the stopped-train restraint, keep the reset hammer positively clear.
2. Run: maintain drive and counter operation without unintended contact between hammer and hearts.
3. Stop: disengage the source and retain the elapsed indication without drift beyond an approved limit.
4. Resume: re-engage without losing the retained indication or causing unacceptable hand disturbance.
5. Reset while stopped: release the restraint as required, apply the hammer to all specified hearts, return indications to their zero datums, then withdraw the hammer and restore the stopped condition.
6. Reset while running: mechanically blocked; no partial hammer contact or loss of elapsed indication.

The detailed mechanism must define lever sequence, control state retention, spring return, clearances, partial-actuation behavior and pusher release. WP-33's logical state model is a requirements check only; physical interlock proof requires inspection and test of the actual mechanism.

## 5. Reset mechanism interfaces

WP-16/WP-33 retain heart cams and hammer(s) as the preliminary reset concept. The physical design must specify:
- each hand arbor and its heart-cam mounting interface;
- heart-cam profile, concentricity, angular zero datum and attachment;
- hammer face geometry, contact order and compliance strategy;
- hammer pivot/translation axis, travel stops and withdrawal clearance;
- spring return and force path, with measured force/travel evidence;
- hand-to-arbor retention and resistance to slip;
- counter jumper/index phase and reset relationship;
- axial stack and swept clearance throughout the reset stroke;
- inspection, lubrication and service access.

A common hammer versus separate hammer elements remains open. Contact sequencing must prevent one heart from reaching zero in a way that blocks, displaces or overloads another. CAD swept-volume and tolerance analysis are required before prototype fabrication.

## 6. Reset work calculation

For measured resisting torque T as a function of reset angle theta, the quasi-static work is:

    W = integral(T(theta) d(theta))

The software integrates explicitly supplied torque-angle samples using the trapezoidal rule. Inputs must be measured, nonnegative resisting torque samples at strictly increasing angles, with evidence IDs. No extrapolation is performed.

Where a separately measured available energy is compared with reset work, both must share a declared measurement boundary and traceable evidence. A nonnegative arithmetic margin is only a screening result. It excludes dynamic peaks, spring hysteresis not captured by the measurement, impact, friction changes, inertia, tolerance variation and reliability. It is not a reset-force calculation or a physical pass.

Hammer force, spring force, contact stress and reset duration require instrumented force/travel and dynamic prototype measurements. They are not inferred from work alone.

## 7. Executable calculation model

Files:
- tools/c01_chrono_drive_reset.py
- tools/test_c01_chrono_drive_reset.py

Functions:
- exact signed compound drive-path ratio from supplied integer tooth counts;
- output RPM and direction from supplied source RPM;
- branch comparison against a supplied target period and tolerance;
- trapezoidal reset work from measured torque-angle samples;
- energy-margin screening with explicit common boundary and evidence IDs;
- completeness validation for reset mechanism definition records.

The model does not create a gear train, infer an arbor speed, size a heart cam, calculate a hammer force, or certify a physical mechanism.

## 8. Required drawings and engineering records

| Record | Minimum content | Release condition |
|---|---|---|
| Drive source interface | Source arbor, speed evidence, torque boundary, revision | Approved source evidence |
| Central seconds train | Gear/arbor IDs, ratio, direction, supports, clutch interface | Kinematic and geometry review |
| 30-minute branch | Continuous/jumping definition, path or index mechanism | Requirement and load evidence |
| 12-hour branch | Continuous/jumping definition, path or index mechanism | Requirement and load evidence |
| Stopped-train restraint | Contact geometry, state, travel, retention test | Physical stop/hold test |
| Reset assembly | Hearts, hammer(s), pivots, spring, datums, swept envelope | CAD/tolerance and reset test |
| Control/interlock | Lever states, reset block, partial actuation behavior | Physical interlock test |
| Lubrication/service | Contact map, lubricant qualification, access sequence | WP-31/WP-30 review |

## 9. Acceptance criteria

- WP34-AC-01: every mesh has explicit positive integer tooth counts, mesh type and evidence ID.
- WP34-AC-02: signed compound ratio and direction are calculated exactly.
- WP34-AC-03: every output branch uses an approved source speed and explicit target period/tolerance.
- WP34-AC-04: totalizer convention is explicitly continuous or jumping before detailed design release.
- WP34-AC-05: reset work uses measured torque-angle samples with monotonic angles and traceable evidence.
- WP34-AC-06: energy comparison declares a common measurement boundary and does not claim dynamic sufficiency.
- WP34-AC-07: reset definition record identifies hearts, hammer, datum, contact sequence, spring return, hand retention, clearance and tolerance reviews.
- WP34-AC-08: reset-while-running is positively blocked by a physical mechanism and verified on the prototype.
- WP34-AC-09: no C-01 dimensions, tooth counts, material, force, tolerance or performance result is invented.

## 10. Verification

Run from the tools directory:

    python -m unittest test_c01_chrono_drive_reset.py

Tests use synthetic arithmetic fixtures only. They are not C-01 measurements, gear selections, reset-force data or physical prototype tests.

## 11. Revision control and current disposition

Revision A is the initial controlled issue. Any change to source take-off, gear path, counter convention, reset arrangement, datum, interface or measurement boundary requires impact review against WP-17, WP-19, WP-20, WP-25, WP-26, WP-30 and WP-33.

**Disposition:** WP-34 establishes the calculation framework and controlled design inputs for the chronograph drive and reset mechanism. Source path, gear schedule, counter behavior, stopped-train restraint, hammer configuration, heart-cam geometry and all physical dimensions remain open. No design is released for manufacture.
