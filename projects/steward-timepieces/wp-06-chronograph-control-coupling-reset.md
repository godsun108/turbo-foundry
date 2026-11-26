# STEWARD C-01 — WP-06 Chronograph Control, Coupling and Reset Architecture

**Revision:** 0.1  
**Status:** Functional state specification and architecture trade study; no mechanism selected  
**Branch:** `steward/c-01-movement-foundation`

## 1. Purpose

Define what the chronograph mechanism must do at start, stop and reset, then compare control and coupling options independently. The control system sequences levers; the clutch connects or disconnects drive; the brake arrests the elapsed-time train; the reset system returns hands/counters to zero. These are related but distinct functions.

C-01's benchmark family demonstrates a two-pusher integrated automatic chronograph. A two-pusher arrangement is the baseline study, not a frozen user-interface decision.

## 2. Functional state model

Three required operating states:

| State | Clutch | Brake | Counters |
|---|---|---|---|
| Stopped at zero | Disengaged | Applied | At zero |
| Running | Engaged | Released | Advancing |
| Stopped with elapsed time | Disengaged | Applied | Held at elapsed reading |

Two-pusher functional sequence:
1. First upper-pusher actuation: start; clutch engages and brake releases.
2. Second upper-pusher actuation: stop; clutch disengages and brake applies.
3. Lower-pusher actuation while stopped: reset hammers act on heart cams and return chronograph hands to zero.
4. Upper-pusher actuation after stop: resume timing from the retained elapsed position.

Reset while running is prohibited in this baseline functional specification. The mechanical interlock must prevent destructive or ambiguous simultaneous engagement of drive and reset. Whether the interlock is implemented by cam profile, lever geometry, blocking piece or another mechanism is open.

The executable state model is a logical requirements aid. It does not model inertia, backlash, elastic deflection, pusher bounce, friction, component timing, cam geometry or real hand alignment.

## 3. Control architecture: cam vs column wheel

| Criterion | Cam / shuttle / switching plate | Column wheel |
|---|---|---|
| State sequencing | Profiled surfaces and switching levers establish operating states | Column positions index the control levers |
| Manufacturing | Potentially simpler geometry and repeatable production | More precision features and finishing |
| Adjustment | Can be designed for standardized lever clearances | Lever-to-column engagement and indexing need precise fit |
| Pusher feel | Determined by cam ramps, spring forces and lever ratios | Can provide a distinct indexed action; actual feel still depends on complete pusher train |
| Service | Potentially straightforward if parts and access are well designed | Serviceable when tolerances and replacement parts are controlled |
| C-01 position | Baseline candidate | Keep as comparator |

No universal claim that one is always more durable or better is justified. Compare teardown, part count, adjustment sensitivity, wear, force/travel and service time.

## 4. Coupling architecture: horizontal vs vertical

| Criterion | Horizontal / lateral clutch | Vertical friction clutch |
|---|---|---|
| Engagement | A drive wheel moves into mesh with chronograph wheel | Friction elements engage axially |
| Start behavior | Tooth phase can create hand jump or delayed engagement | Can reduce gear-tooth engagement jump; frictional slip and adjustment still matter |
| Power draw | Added gear mesh and chronograph train load | Clutch drag and continuously rotating elements can impose load |
| Packaging | Requires lateral wheel/lever space | Requires axial stack, friction surfaces and controlled endshake |
| Service | Familiar gear engagement and tooth inspection | Friction surfaces, preload, endshake and contamination control |
| C-01 position | Baseline candidate | Comparator; justify only with measured benefit |

A vertical clutch is not synonymous with column-wheel control. All four combinations remain eligible for study:
- cam + horizontal;
- cam + vertical;
- column wheel + horizontal;
- column wheel + vertical.

## 5. Brake and reset subsystem

The brake must stop the chronograph seconds and dependent elapsed-time counters without disturbing the base time display. Brake contact, spring force, friction, wear and repeatability require physical evaluation.

Reset subsystem responsibilities:
- heart cams fixed to the chronograph hand arbors;
- reset hammers with controlled contact geometry;
- hammer return and clearance;
- zero-stop alignment and repeatability;
- no interference with running drive;
- simultaneous reset of central seconds and both registers.

The actual heart-cam profiles, hammer geometry, spring rates, contact materials, tolerances and reset forces are not designed in this work package.

## 6. Pusher and interlock requirements

Measure:
- force vs travel curve for start, stop and reset;
- peak force and actuation hysteresis;
- pusher travel and return;
- state transition reliability over repeated cycles;
- accidental double-actuation and bounce sensitivity;
- reset-blocking behavior while running;
- wear after a defined cycle test.

Do not specify numerical force or travel targets until benchmark movements are instrumented and a prototype mechanism exists.

## 7. Executable state model

- `tools/c01_chronograph_control.py` defines the abstract three-state, two-pusher logic and its required clutch/brake outputs.
- `tools/test_c01_chronograph_control.py` verifies start, stop, reset, resume, reset interlock and output-state behavior.

Run from the tools directory:

```bash
python -m unittest test_c01_chronograph_control.py
```

This verifies logical transitions only. It does not validate a mechanical cam, column wheel, clutch, brake or reset assembly.

## 8. Four-combination evaluation matrix

| Control | Coupling | Main evidence required |
|---|---|---|
| Cam | Horizontal | Start jump, tooth wear, lever force, amplitude and service time |
| Cam | Vertical | Drag, clutch preload, amplitude, reset repeatability, service time |
| Column wheel | Horizontal | Indexing reliability, pusher feel, start jump, wear and adjustment |
| Column wheel | Vertical | Combined tolerance sensitivity, drag, pusher feel, serviceability |

Each candidate must be assessed against a common test protocol and comparable condition. Do not score a mechanism from appearance or marketing descriptions.

## 9. Prototype validation sequence

1. Verify state transitions across repeated start-stop-reset cycles.
2. Measure pusher force and travel at each actuation.
3. Measure central seconds engagement jump across varied starting tooth phases for horizontal coupling.
4. Measure vertical clutch slip/drag and start repeatability if that candidate is built.
5. Measure brake stopping time and hand creep.
6. Measure reset-to-zero error for all chronograph hands.
7. Measure base movement amplitude, rate and reserve with chrono stopped and running.
8. Inspect contact wear, lubrication migration and contamination.
9. Repeat after shock, temperature and cycle testing defined by the final validation plan.

## 10. Decision status

- Two-pusher functional interface: preliminary baseline.
- State sequence: defined at functional level.
- Reset while running: prohibited by baseline interlock requirement.
- Cam vs column wheel: open.
- Horizontal vs vertical clutch: open.
- Brake geometry and force: TBD.
- Heart cams and reset hammers: TBD.
- Pusher dimensions/force/travel: TBD.
- Physical mechanism and CAD: not created.
- Prototype validation: not performed.

**Next gate:** instrument a lawful reference chronograph teardown and develop a parameterized lever/cam layout only after component interfaces, force paths and available axial/lateral space are measured.
