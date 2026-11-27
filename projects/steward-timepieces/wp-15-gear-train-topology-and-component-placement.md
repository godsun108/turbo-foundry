# STEWARD C-01 — Gear-Train Topology and Component Placement

**Document:** WP-15  
**Revision:** 0.1  
**Status:** Preliminary topology and placement-control study; no physical topology or geometry frozen  
**Branch:** `steward/c-01-movement-foundation`  
**Dependencies:** WP-10 gear train and energy transmission; WP-11 chronograph; WP-12 calendar; WP-13 system integration; WP-14 movement architecture/layout; Gear-Train Kinematic Worksheet 01; Mechanical Datum and Plate-Zone Skeleton 01.

## 1. Purpose and release boundary

WP-15 converts the existing speed requirements and conceptual movement reservations into a controlled topology decision framework and a traceable component-placement register. It deliberately does **not** choose gear tooth counts, gear centers, module, shaft coordinates, plate dimensions, bridge geometry, rotor dimensions or clutch construction.

The existing `tools/c01_train_topology.py` remains the source for exact rational speed-ratio calculations from explicitly supplied gear stages. WP-15 does not duplicate that calculator. The new `tools/c01_component_placement.py` validates a placement register without inventing locations.

## 2. Functional power and indication architecture

### 2.1 Going-train baseline — conceptual only

```text
Mainspring barrel
      |
      v
Center wheel -> Third wheel -> Fourth wheel / seconds take-off
                                      |
                                      v
                              Escape wheel
                                      |
                                      v
                              Pallet / balance
```

This is a conventional conceptual sequence used as a starting hypothesis, not a selected C-01 wheel topology. Actual wheel order, arbor arrangement, escape-wheel drive, reduction stages and motion-works take-off must be confirmed from a measured reference movement or engineered tooth/center-distance solution. The balance is the regulator, not a downstream gear output.

### 2.2 Chronograph drive candidates

**P1 — Fourth-wheel / seconds-axis take-off**

```text
Going train -> seconds-axis take-off -> clutch -> central chrono seconds
                                                |-> 30-minute totalizer
                                                |-> 12-hour totalizer
```

Potential advantage: direct access to a seconds-rate source. Primary risk: engagement and running chronograph loads act at or through the seconds-axis drive; verify rate/amplitude disturbance and torque margin.

**P2 — Dedicated take-off and chronograph drive train**

```text
Going train -> selected take-off -> dedicated chrono drive -> clutch
                                                        -> central chrono seconds
                                                        -> totalizer branches
```

Potential advantage: permits deliberate drive ratio, coupling and service packaging. Primary risk: added meshes, pivots, friction, adjustment and axial/planar packaging.

Neither candidate is selected. A final design may use a hybrid arrangement, but that requires a documented reason and updated interface/energy accounting.

### 2.3 Calendar drive interface

```text
Timekeeping / motion works
          |
          v
Daily calendar drive -> indexing / jumper system
                     -> weekday display
                     -> date display
```

The drive take-off, advance timing, indexing geometry, jumper force, correction interface and safe quickset window remain open. WP-12's logical calendar behavior does not define the physical drive train.

### 2.4 Automatic winding and axial separation

The rotor is assigned to a separate **rotor-plane reservation** in WP-14. Do not assume it occupies the same planar layer as the going train. Rotor support, winding reduction/reversing works, winding direction, bearing system, rotor sweep and caseback clearance require separate XY/Z packaging and service review.

## 3. Required speed interfaces

The existing kinematic worksheet defines these display requirements; they are not physical train ratios:

| Indication | Required rotation period | Required speed |
|---|---:|---:|
| Running seconds | 60 s/rev | 1 rpm |
| Central chronograph seconds | 60 s/rev when engaged | 1 rpm |
| Minute hand | 3,600 s/rev | 1/60 rpm |
| Hour hand | 43,200 s/rev | 1/720 rpm |
| 30-minute totalizer | 1,800 s/rev | 1/30 rpm |
| 12-hour totalizer | 43,200 s/rev | 1/720 rpm |

The ratio calculator's signed direction convention must be retained. Compound-arbor assumptions, idlers, internal meshes and counter indexing must be represented explicitly. Speed compliance alone does not establish torque sufficiency, efficiency, tooth strength, low friction or reserve.

## 4. Component placement register

The starter register in `tools/c01_component_placement.py` includes reservations for barrel, center/third/fourth wheels, escape wheel, balance, chronograph drive and clutch, totalizers, calendar drive, weekday/date display, rotor and central hand stack.

Each eventual placement entry shall include:

| Field | Requirement |
|---|---|
| component_id / system | Unique stable identifier and functional subsystem |
| layer | `dial_side`, `main_movement`, `rotor_plane`, `case_interface` or `cross_layer` |
| x_mm / y_mm | Paired coordinates in WP-14 datum; blank until supported |
| z_min_mm / z_max_mm | Axial interval; blank until supported |
| envelope_mm | Positive X/Y/Z envelope, from measured or supplier evidence |
| status | measured, calculated, supplier_confirmed, provisional or TBD |
| source | Drawing/part/revision, measurement record, calculation inputs, or explicit not-assigned note |
| owner | Responsible engineering function |

No component coordinate or envelope is assigned in this revision. The register validator checks evidence labels, uniqueness, coordinate pairing, finite values, Z interval order and envelope completeness. A valid register is not proof of collision-free physical fit.

## 5. Topology and placement decision method

1. Confirm the functional output periods and central-axis/display requirements.
2. Obtain a documented reference movement or independently justify a fresh architecture.
3. Identify candidate arbors and possible take-off points from measured geometry.
4. Create a directed component/mesh graph. Mark compound wheels on common arbors explicitly; do not imply rigid coupling from visual proximity.
5. Use exact rational stage ratios from supplied tooth counts; independently verify output speed and rotation direction.
6. Evaluate center distances and tooth geometry using an identified module/tooth form, pinion geometry, backlash and manufacturing process.
7. Allocate components to XY zones and Z layers using measured or supplier-confirmed envelopes.
8. Check gear mesh, pivot/jewel support, axial endshake, hand stack, bridge access, assembly sequence, lubrication access and serviceability.
9. Compare chronograph stopped/running load, engagement transient, rate/amplitude and reserve using WP-10/WP-11/WP-13 measurement boundaries.
10. Record rejected alternatives and evidence; do not silently promote provisional data.

## 6. Preliminary subsystem placement intent

| Subsystem | Placement reservation | Interface / principal concern | Status |
|---|---|---|---|
| Barrel and going train | Main movement | Power path, arbor support, wheel mesh | Provisional |
| Balance and escapement | Main movement, dedicated service zone | Oscillator clearance, shock setting, regulation access | Provisional |
| Chronograph drive/clutch | Main movement and/or cross-layer interface | Torque take-off, engagement, reset, control access | Open |
| Totalizers | Main movement with dial-side indication shafts | Register ratio, jumper and reset loads | Provisional |
| Calendar | Dial-side mechanism with movement-side drive interface as required | Daily indexing, correction, display-disc packaging | Provisional |
| Motion works / hand stack | Central dial-side axis reservation | Coaxiality, hand clearance, calendar interface | Provisional |
| Automatic winding | Rotor plane | Rotor sweep, reversing works, caseback clearance | Provisional |
| Plate/bridges | Layer-dependent support structure | Assembly, screw access, serviceability, stiffness | TBD |

## 7. Engineering calculations and assumptions

No numerical gear geometry or physical placement calculation is released because required measured inputs are absent.

Permitted calculations once inputs exist:
- Exact compound speed ratio: product of signed stage ratios.
- Gear-center distance: only after compatible module/tooth geometry and center-distance convention are specified.
- XY clearance: only from dimensioned component envelopes in a common datum.
- Z clearance: only from documented axial intervals, tolerances, endshake and deflection allowances.
- Torque/power: only from defined measurement boundaries and explicit efficiency/load data.

Do not treat the 4 Hz / 28,800 vph target as sufficient to infer escape-wheel speed or tooth count. Do not use nominal watch-industry dimensions as C-01 dimensions without a cited design basis.

## 8. Verification and acceptance criteria

| ID | Verification | Acceptance criterion |
|---|---|---|
| V-15-01 | Requirements trace | Every indication and subsystem has a documented source and interface |
| V-15-02 | Topology graph review | No unexplained cycles, missing path segments or ambiguous compound arbors |
| V-15-03 | Kinematic calculation | Independently reproduced exact output speed and direction for every selected path |
| V-15-04 | Gear geometry | Tooth form, module, center distance, interference and backlash reviewed in dimensioned CAD |
| V-15-05 | XY placement | All selected components have evidence-backed coordinates/envelopes in common datum |
| V-15-06 | Z stack | Axial clearances include component heights, endshake, tolerances and operating deflection |
| V-15-07 | Energy integration | Chronograph stopped/running and calendar loads measured on matched boundaries |
| V-15-08 | Service review | Assembly/removal sequence, bridge access, lubrication and adjustment access documented |
| V-15-09 | Prototype verification | Physical mesh, friction, amplitude/rate, engagement and reset tests meet approved limits |

Acceptance is **not achieved** by this concept study. Each item remains open until supporting artifacts and test records are attached.

## 9. Risk register

| Risk | Consequence | Mitigation / evidence required |
|---|---|---|
| Seconds-axis chronograph take-off overloaded | Rate/amplitude loss or stoppage | Measure torque margin and chrono on/off behavior |
| Additional dedicated train meshes | Reduced energy reserve, friction and complexity | Compare measured losses and service burden |
| Register or calendar indexing load underestimated | Missed indexing or poor timekeeping | Measure jumper, indexing and reset loads |
| XY reservations mistaken for physical locations | False fit confidence | Require traceable coordinates and dimensioned CAD |
| Rotor plane conflicts with bridges/caseback | Interference or restricted service | Full Z-stack and sweep envelope |
| Hand-stack and calendar discs compete for axial space | Collision or excessive movement height | Dimensioned axial stack and tolerance analysis |
| Unverified gear ratios or compound arbors | Incorrect indications | Explicit graph, exact ratios and independent review |

## 10. Architecture freeze gate

The going-train topology, chronograph take-off/clutch, calendar drive, rotor arrangement and component locations remain **not frozen**. Freeze requires:
- Approved case/dial/movement envelope and datum.
- Documented reference measurements or justified original design inputs.
- Selected topology with complete gear-stage schedule.
- Verified kinematic ratios and directions.
- Dimensioned XY/Z CAD with tolerance and clearance analysis.
- Measured energy/torque evidence, including chronograph states.
- Assembly and service review.
- Closed high-severity risks and signed design review.

## 11. Revision history

| Revision | Change | Status |
|---|---|---|
| 0.1 | Initial controlled topology alternatives, placement schema, verification plan and freeze gate | Preliminary; no design frozen |

**Engineering release statement:** WP-15 is a controlled architecture study. It does not constitute a detailed gear-train design, dimensioned drawing, CAD assembly, manufacturing instruction or validated prototype.
