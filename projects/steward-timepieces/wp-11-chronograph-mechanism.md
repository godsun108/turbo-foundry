# STEWARD C-01 — WP-11 Chronograph Mechanism

**Document ID:** C01-WP-11  
**Revision:** 0.1  
**Status:** Preliminary engineering definition, architecture trade study, and verification plan  
**Branch:** `steward/c-01-movement-foundation`  
**Predecessors:** WP-08 Automatic Winding; WP-09 Balance and Escapement; WP-10 Gear Train and Energy Transmission  
**Next gate:** select a clutch/control architecture using packaging, energy, timing, wear, and service evidence

## 1. Purpose and design intent

Define the chronograph subsystem for STEWARD C-01: a mechanical elapsed-time function with central chronograph seconds and elapsed-minute/hour indications, controlled start, stop, and reset. The chronograph must operate without unacceptable disturbance to the base time display, escapement, reserve, or calendar.

The chronograph is a core feature, not an add-on. The central chrono seconds hand is the primary elapsed-time readout; counter layout and cadence must be coordinated with the dial-side display study and movement envelope.

This package is a controlled engineering basis. It does not claim a completed physical chronograph, selected clutch, frozen gear train, measured load, or validated performance.

## 2. System requirements and interfaces

| Requirement | Current basis | Verification |
|---|---|---|
| Start / stop | User-commanded, repeatable | Instrumented state-transition and cycling test |
| Reset | Return all elapsed-time hands to defined zero | Optical angular measurement |
| Central chrono seconds | Continuous elapsed seconds indication | Calibrated timebase and hand-rate test |
| Elapsed minutes | Accumulate elapsed minutes | Counter indexing/cadence test |
| Elapsed hours | Accumulate elapsed hours | Counter indexing/cadence test |
| Base timekeeping | No unacceptable chrono-on/off disturbance | Matched WP-09 timing tests |
| Energy | Quantify steady and transient demand | WP-10 matched energy measurements |
| Service | Accessible, inspectable, replaceable wear interfaces | Service trial and post-service test |

Interfaces requiring controlled drawings include the going-train drive point, chronograph wheel train, clutch axis and engagement plane, control lever/column-wheel plane, reset hammer and heart-cam stack, counter carry mechanisms, hand heights, bridges, jewels, case/dial clearances, and lubrication zones.

Do not assume a center-seconds drive point, counter location, hand stack, or movement diameter until the dial, gear train, and bridge layouts are reconciled.

## 3. Functional architecture

The functional chain is:

**Going train drive → coupling/clutch → chronograph seconds train → minute counter indexing → hour counter indexing**

The control path is separate:

**Pusher input → operating control (column wheel or alternative) → clutch and brake/stop elements → reset interlock and hammer**

Reset path:

**Reset command while stopped → hammer release → heart cams → hands return to zero → hammer withdrawal**

The final design must define the exact kinematic and control relationship among the clutch, brake, operating levers, jumper springs, heart cams, and counters. A state model is not a substitute for a mechanical interlock or tolerance analysis.

## 4. Clutch architecture trade study

No clutch architecture is selected in Revision 0.1.

### 4.1 Vertical clutch

Potential benefits:
- Direct axial engagement may reduce gear-to-gear tooth impact at start.
- Can support a compact, continuously meshed chronograph train depending on layout.
- Potential for low hand jump when the coupling faces are properly controlled.

Risks and evidence required:
- Axial stack height and endshake sensitivity.
- Friction material, surface finish, contact pressure, and wear behavior.
- Drag when nominally disengaged.
- Engagement repeatability, slip, contamination, and lubricant migration.
- Service access and adjustment complexity.

### 4.2 Horizontal / lateral clutch

Potential benefits:
- Conventional, visually inspectable gear engagement.
- Discrete coupling path can simplify understanding and service diagnosis.
- Candidate arrangement may integrate naturally with a lateral chronograph wheel.

Risks and evidence required:
- Tooth entry impact, backlash, and hand jump at engagement.
- Engagement depth and center-distance tolerance sensitivity.
- Tooth wear, tip interference, and partial engagement.
- Control-lever force, spring behavior, and space consumed by lateral travel.

### 4.3 Decision matrix

Score candidates only after the same requirements, geometry envelope, and test methods are defined.

| Criterion | Evidence needed | Decision status |
|---|---|---|
| Start hand jump | High-speed optical hand-angle capture | TBD |
| Running drag | Matched chrono-off/on energy and rate tests | TBD |
| Engagement reliability | Repeated start cycles across reserve states | TBD |
| Axial/radial packaging | CAD envelope and tolerance stack | TBD |
| Wear | Endurance cycling and microscopic inspection | TBD |
| Serviceability | Timed disassembly, inspection, reassembly | TBD |
| Shock response | Approved shock protocol and post-test function | TBD |
| Manufacturability | Supplier capability, process and yield evidence | TBD |

Selection gate: no weighted score or winner is declared until the movement envelope, measurable acceptance limits, supplier capability, and prototype evidence are available.

## 5. Operating control: column wheel or alternative

A column wheel is a candidate control architecture, not a frozen decision. Compare it with a cam/lever or other mechanically interlocked control arrangement.

Assess:
- deterministic sequencing of start, stop, and reset;
- lever travel, pusher force, tactile feedback, and return;
- risk of simultaneous or contradictory control states;
- reset blocking while the chronograph is running;
- wear at column/lever or cam/lever contact points;
- spring fatigue, bounce, and incomplete indexing;
- tolerance sensitivity, assembly phasing, and service adjustment.

If a column wheel is selected, document column count/profile, indexing method, jumper geometry, control-lever contact geometry, and assembly datum. If another control is selected, document equivalent state definitions and positive interlocks. No column count, profile, spring force, or pusher force is assigned here.

## 6. Start, stop, and reset logic

The logical sequence begins in the stopped state:

| Current state | Command | Required resulting state | Mechanical intent |
|---|---|---|---|
| Stopped | Start | Running | Engage coupling; release any stop element |
| Running | Stop | Stopped, elapsed value retained | Disengage drive; apply defined stopping/braking behavior |
| Stopped | Reset | Stopped at zero | Release hammer; align all hearts to zero |
| Running | Reset | Prohibited | Positive mechanical interlock prevents reset |

Repeated start while running and stop while stopped must be mechanically prevented or have a defined, non-damaging behavior. Reset must not be possible while the chronograph train is driven unless a specifically engineered flyback function is separately approved. Flyback is not part of the current C-01 baseline.

The executable model `tools/c01_chronograph.py` checks logical command sequences and calculates ideal gear-stage display ratios. It is a requirements aid, not proof that the mechanism physically enforces these rules.

## 7. Display train and counter kinematics

The central seconds, minute counter, and hour counter must be derived from a single consistent timebase and the selected drive point.

For a simple external gear pair:

`output rev/input rev = driver teeth/driven teeth`

For a compound train, multiply the stage ratios. Counter indexing mechanisms may use intermittent motion and must be analyzed separately from continuous gear ratios.

Define for every hand:
- required revolutions per elapsed-time unit;
- drive point and source cadence;
- gear stages and tooth counts after architecture selection;
- direction of rotation;
- hand inertia and torque demand;
- backlash and lost-motion budget;
- reset heart-cam datum and zero-angle tolerance;
- counter carry/indexing phase.

No tooth counts, counter layout, hand inertia, gear module, or display ratio is frozen in this package. Ratios must be reconciled with WP-10 and the actual dial arrangement.

## 8. Reset-to-zero and hand alignment

Each elapsed-time hand requires a defined zero datum and a repeatable return mechanism. Heart cams are the current reset concept for the hands, subject to packaging and detailed design.

Verify:
1. heart-cam profile and concentricity;
2. hammer face geometry, contact pressure, and simultaneous contact;
3. hammer spring force and return behavior;
4. hand-to-arbor fit and slip resistance;
5. counter jumper/index position and backlash;
6. zero alignment after repeated resets;
7. reset repeatability after shock, wear, and service.

Measure angular zero error optically at a defined resolution. Acceptance tolerance remains TBD pending dial readability, hand length, scale graduation, manufacturing capability, and approved requirement. Do not invent a degree tolerance.

A multi-hand reset must avoid one hand reaching zero early and blocking or displacing another. Establish contact sequencing and compliance from CAD, force analysis, and prototype testing.

## 9. Energy and timekeeping interaction

Chronograph energy demand must be split into:
- steady-state running load;
- start engagement transient;
- stop/disengagement transient;
- reset/hammer transient;
- minute/hour counter indexing and carry events;
- control pusher actuation energy, where relevant to the movement.

Use WP-10 measurement boundaries and matched intervals. Compare stopped and running energy at the same reserve state, temperature, orientation, lubrication condition, and measurement setup. Capture transient events at sufficient sampling rate; an average over a long interval can hide a damaging peak.

Compare WP-09 amplitude and rate with chronograph stopped and running. Record the change at full, intermediate, and low reserve states and in all required positions. Separate clutch drag, train friction, counter indexing, and escapement behavior before attributing a timing shift to a single component.

No generic chronograph power penalty, efficiency, amplitude drop, or rate shift is assigned in this document.

## 10. Mechanical design, tolerances, and materials

The detailed design package must define:
- clutch contact geometry, engagement depth, axial/radial runout, and clearances;
- wheel and pinion tooth form, counts, module/equivalent size, backlash, and center distance;
- pivot, jewel, bushing, endshake, and side-shake requirements;
- lever/column or cam interface geometry and contact stresses;
- springs, preload, travel, fatigue, and retention;
- heart-cam profile, concentricity, hardness, finish, and mounting;
- hammer geometry, alignment, and contact finish;
- hand/arbor fit, friction, inertia, and shock retention;
- lubricant identity, quantity, placement, migration, and aging;
- inspection datums, tolerances, and replaceable wear parts.

Use horological-scale design methods and supplier-confirmed process capability. Any stress, wear, or friction calculation must state its assumptions and be correlated with prototype measurements.

## 11. Verification plan and acceptance criteria

| Test | Method / evidence | Acceptance basis |
|---|---|---|
| State sequencing | Command cycling and inspection of interlocks | No invalid mechanical state or damaging operation |
| Start engagement | Optical hand capture and high-speed observation | Hand jump within approved limit; no missed engagement |
| Stop retention | Timing observation over defined interval | Elapsed indication remains stable within approved limit |
| Reset alignment | Optical measurement of all hands after repeated resets | Zero error within approved dial/readability requirement |
| Counter indexing | Long-duration cadence and carry observation | Correct elapsed-time indication; no missed/double index |
| Running load | Matched WP-10 energy measurement | Within approved incremental energy budget |
| Timing interaction | Matched WP-09 rate/amplitude tests | Within approved chrono-on/off disturbance limits |
| Low reserve | Repeat operating sequence at low usable wind | Reliable operation within approved reserve envelope |
| Endurance | Repeated start/stop/reset cycles | No unacceptable wear, drift, or failure |
| Shock | Approved shock test before/after | Function and alignment meet approved recovery criteria |
| Service repeatability | Inspect, service, reassemble, retest | Released limits maintained |

All numerical limits are TBD until the dial readability requirement, prototype capability, test method, and project requirements are approved. A test cannot be marked pass against an unapproved threshold.

## 12. Test data and traceability

Each test record must identify:
- movement serial number and revision;
- chronograph configuration and component revisions;
- clutch and control architecture under test;
- procedure revision and operator;
- instrument IDs, calibration status, resolution, and uncertainty;
- state of wind, temperature, orientation, and lubrication condition;
- command sequence and cycle count;
- raw timing, hand-angle, energy, and inspection data;
- anomalies, repairs, and post-test condition.

Preserve raw data. Derived results must be reproducible from the source record and tool revision.

## 13. Failure modes and controls

| Failure mode | Potential effect | Detection / control |
|---|---|---|
| Clutch fails to engage | Chronograph does not start | Engagement observation and repeated cycle test |
| Clutch drag while stopped | Base train energy loss / hand creep | Stopped-state drag and hand stability test |
| Engagement hand jump | Elapsed-time error | High-speed optical capture; geometry and backlash review |
| Partial gear engagement | Tooth damage / intermittent drive | Engagement-depth and tolerance inspection |
| Reset while running | Damage or loss of elapsed time | Positive mechanical reset interlock |
| Incomplete reset | Hands fail to return to zero | Hammer/heart contact and zero-angle inspection |
| Unequal multi-hand reset | Hand interference / displaced indication | Contact sequence and simultaneous reset testing |
| Counter carry failure | Incorrect elapsed minutes/hours | Long-duration indexing test |
| Excessive counter load | Amplitude/rate loss | WP-09 and WP-10 matched load tests |
| Spring fatigue / lever wear | Inconsistent actuation | Endurance and post-cycle inspection |
| Lubricant migration | Clutch slip/drag or contamination | Aging, temperature, and service tests |

## 14. Interface control and change impact

| Interface | Owner package | Change impact |
|---|---|---|
| Drive cadence and torque | WP-10 | Recalculate ratios, load, and energy margin |
| Escapement/timekeeping | WP-09 | Repeat chrono-on/off rate and amplitude tests |
| Barrel/winding | WP-08 | Reassess reserve and winding adequacy |
| Dial and hand stack | Dial-side layout study | Recheck hand heights, readability, clearances, reset datum |
| Calendar | Integrated calendar package | Check shared drive, simultaneous loads, and interference |
| Case and bridges | Movement architecture | Recheck envelope, stiffness, shock, service access |

## 15. Revision and decision register

| Decision | Status at Rev 0.1 |
|---|---|
| Central chrono seconds | Requirement retained |
| Elapsed minute/hour indications | Requirement retained; exact display layout open |
| Vertical vs horizontal clutch | Open trade study |
| Column wheel vs alternative control | Open trade study |
| Flyback | Not in baseline; requires separate approval |
| Counter drive and tooth counts | Open; derive from selected drive point |
| Reset heart cams | Candidate concept; geometry unselected |
| Reset-zero tolerance | TBD from dial/readability requirement |
| Pusher force/travel | TBD from ergonomics and mechanism testing |
| Chronograph incremental energy | Not measured |
| Chronograph-on/off rate delta | Not measured |
| Endurance life target | TBD; approve before qualification |

## 16. Release gate

WP-11 may advance to preliminary design release only when:
1. dial display arrangement and hand stack are controlled;
2. drive point and cadence are reconciled with WP-10;
3. clutch and control trade studies are supported by packaging and prototype evidence;
4. state interlocks and reset architecture are detailed;
5. tooth geometry, tolerances, materials, and lubrication are reviewed;
6. energy and timing interaction tests meet approved criteria;
7. endurance, shock, and service repeatability are demonstrated;
8. drawings, bill of materials, assembly instructions, and inspection procedures are revision-controlled.

**Current disposition:** preliminary engineering definition, logical state model, and verification plan only. No physical architecture selection, measured performance, prototype pass, or production release is claimed.
