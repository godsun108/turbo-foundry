# STEWARD C-01 — WP-10 Gear Train and Energy Transmission

**Document ID:** C01-WP-10  
**Revision:** 0.1  
**Status:** Preliminary engineering definition, calculation framework, and verification plan  
**Branch:** `steward/c-01-movement-foundation`  
**Predecessors:** WP-08 Automatic Winding; WP-09 Balance and Escapement  
**Next gate:** gear-train architecture trade study, measured barrel/escapement data, and integrated prototype energy audit

## 1. Purpose

Define the going train and movement-wide energy accounting needed to connect the mainspring barrel to the escapement while accommodating the chronograph and calendar. Establish calculation methods, measurement planes, acceptance logic, failure controls, and service requirements.

WP-10 is an engineering framework, not a frozen gear train. No tooth counts, modules, wheel diameters, pivots, gear materials, efficiencies, barrel torque curves, or measured reserve values are selected or claimed.

## 2. C-01 controlled baseline

C-01 remains an automatic mechanical chronograph with hours/minutes, day-of-week, day-of-month, central chronograph seconds, elapsed-minute and elapsed-hour counters, and running seconds. The proposed oscillator target is 4 Hz (28,800 vph). The 60–70-hour power reserve is aspirational and must be demonstrated by a complete movement.

The design must be serviceable and maintainable over the intended long service life. The chronograph and calendar are not optional test accessories: their energy demand and interactions must be included in the complete movement assessment.

## 3. Functional energy architecture

**Mainspring → barrel → center wheel / intermediate train → fourth wheel / seconds output → escape wheel → pallet fork → balance oscillator.**

The chronograph and calendar are driven through their own interfaces from the going train. Their incremental loads must be measured independently and in combination where simultaneous operation is possible. Automatic winding replenishes the barrel but does not change the requirement to account for the energy consumed by all movement functions.

Create and maintain an energy-flow diagram with:
- input boundary: usable energy released by the mainspring/barrel;
- going-train boundary: energy delivered to the escapement and losses in pivots/meshes;
- escapement boundary: energy supplied to the balance and losses in locking, impulse, and friction;
- complication boundaries: chronograph and calendar incremental demand;
- output boundary: usable energy remaining for stable timekeeping over the required operating interval.

Avoid double counting. Every measured or estimated loss/load must be assigned to one boundary and one interval.

## 4. Gear-train kinematics

For a simple external gear pair:
- driven wheel speed / driver pinion speed = driver tooth count / driven tooth count;
- ideal torque multiplication = driven tooth count / driver tooth count, before losses;
- each external mesh reverses rotational direction.

For a compound train, multiply the stage speed ratios. Actual train design must account for pinion/wheel compound relationships, center distances, module, tooth form, addendum/dedendum, backlash, runout, pivot friction, and assembly tolerances.

The executable tool `tools/c01_gear_train.py` provides ideal pair and compound ratio calculations. These are kinematic calculations only; they do not establish a viable watch train, mesh strength, manufacturability, or real efficiency.

### 4.1 Required design inputs

- Target output frequency and hand/counter display cadence.
- Escapement wheel tooth count and required impulse frequency, once WP-09 architecture is selected.
- Barrel arbor and barrel rotation behavior over the usable wind range.
- Candidate center distance and movement envelope.
- Wheel/pinion material, module, tooth form, face width, finish, and tolerance data.
- Required hand torque and complication interface loads.
- Pivot/jewel geometry, lubrication, and service access.

The train must be solved as a coupled kinematic system. Do not pick tooth counts independently and assume the rest of the train will close.

## 5. Torque-angle and stored-energy model

For a measured mainspring/barrel torque curve, incremental work is:

`dE = τ(θ) dθ`

Total released/stored energy over the measured angular interval is:

`E = ∫ τ(θ) dθ`

WP-10's executable model uses trapezoidal numerical integration of measured torque-angle samples. The sample path must be monotonic in angle and must represent a consistent loading or unloading direction. The result is only as accurate as sensor calibration, angular resolution, friction isolation, and sample coverage.

Record:
- spring/barrel identity and condition;
- loading or unloading direction;
- angle reference and zero definition;
- torque transducer calibration and uncertainty;
- temperature and lubricant condition;
- bridle slip state and whether barrel-wall friction is included;
- sample spacing and repeatability.

Do not extrapolate beyond measured data without an explicitly reviewed model.

## 6. Energy budget and power reserve

For a common defined operating interval:

`E_available ≥ E_going-train-loss + E_escapement + E_chronograph + E_calendar + E_other`

All terms must use consistent system boundaries and the same interval. The executable energy-budget evaluator reports total demand, energy margin, average required/available power, and whether the calculated margin is non-negative. It does not declare the movement feasible unless its inputs are valid and representative.

The idealized reserve estimate is:

`t_reserve = E_usable / P_average`

This estimate is not a reserve prediction unless usable barrel energy and average total load are measured or credibly established over the complete operating envelope. Mainspring torque is not constant; escapement behavior and losses vary with state of wind, orientation, temperature, and wear. Validate reserve by running a complete movement from a documented full-wind condition to the defined stopping criterion.

### 6.1 Mandatory load cases

1. Base timekeeping only.
2. Timekeeping plus automatic winding input.
3. Chronograph stopped.
4. Chronograph running continuously.
5. Chronograph start/stop/reset events.
6. Calendar normal operation and changeover.
7. Combined chronograph and calendar interaction where overlap can occur.
8. Full, intermediate, and low states of wind.
9. Defined positional and temperature conditions.
10. New, run-in, and post-service conditions.

For each case capture torque, rate, amplitude, beat error, reserve state, and the applicable complication state.

## 7. Chronograph energy integration

The chronograph architecture remains open; vertical clutch and column wheel are candidates, not approved selections. Measure the actual incremental load rather than assigning a generic penalty.

Use matched intervals and states of wind to compare:
- chronograph stopped;
- chronograph running;
- start and stop actuation;
- reset operation;
- counter indexing and carry events;
- clutch engagement/disengagement;
- repeated operation and wear-in.

Separate steady running load from transient actuation peaks. Inspect hand jump, coupling slip, gear interference, amplitude disturbance, and rate shift. Test the central seconds, minute counter, and hour counter together as an integrated train.

The model compares chronograph stopped/running energy demand only when measurement intervals match. Transient events require separately captured high-resolution data.

## 8. Calendar energy integration

Day and date mechanism energy must be assessed across the full changeover cycle. Measure normal drive load, jumper/spring work, friction, indexing impacts, correction operations, and any carry interaction.

Required tests:
- ordinary day/date changeover;
- month-end date transition and date rollover;
- day indication cycle;
- independent correction in every approved crown position;
- correction near the prohibited changeover window;
- simultaneous chronograph operation;
- low-reserve operation;
- repeated cycles after wear and service.

The calendar must not stall the going train, cause unacceptable amplitude/rate disturbance, or permit user correction to damage the mechanism. Exact correction windows and operating instructions must be derived from the final calendar architecture and validated.

## 9. Gear geometry, materials, and strength

For each proposed wheel/pinion pair, document:
- tooth counts, module or equivalent tooth-size definition, pressure angle/tooth form;
- pitch diameters, center distance, addendum, dedendum, root geometry;
- face width, backlash, runout, concentricity, and profile tolerances;
- material, hardness, heat treatment, surface finish, and wear pairing;
- calculated contact and bending stresses using a justified method;
- lubrication type, application quantity, migration risk, and aging;
- inspection and replacement criteria.

Use a recognized gear-design method appropriate to miniature horological gearing, validated by supplier capability and prototype testing. Conventional industrial gear formulas may not transfer directly to tiny watch gears without scale, material, tooth-form, and lubrication validation. Record the calculation method and its limits.

## 10. Friction, lubrication, and efficiency

Measure losses by boundary rather than applying one assumed efficiency to the entire train. Separate:
- gear-mesh losses;
- pivot and jewel friction;
- barrel/arbor friction;
- escapement losses;
- chronograph coupling and counter-train losses;
- calendar jumper/indexing losses.

Lubricant selection, quantity, surface preparation, and application method must be defined from validated horological practice, supplier data, and testing. Evaluate migration, aging, temperature sensitivity, contamination, and compatibility with adjacent materials.

Efficiency is calculated as measured output energy divided by measured input energy across the same boundary and interval. No nominal efficiency is assigned in this work package.

## 11. Verification and acceptance matrix

| Verification | Evidence | Acceptance basis |
|---|---|---|
| Kinematic closure | Measured/verified ratios, hand cadence, escapement rate | All display and escapement outputs meet approved cadence |
| Gear mesh geometry | CAD/drawing inspection and prototype metrology | Approved tolerance and clearance stack |
| Torque-angle curve | Calibrated measured data | Complete valid curve over usable barrel range |
| Energy transfer | Input/output energy at defined boundaries | Approved minimum efficiency established before test |
| Energy budget | Complete measured load inventory | Positive margin with approved reserve and operating margin |
| Chronograph load | Matched chrono-off/on measurements | Approved incremental load and timekeeping disturbance limits |
| Calendar load | Changeover/correction measurements | No stall, damage, or unacceptable timekeeping disturbance |
| Reserve | Full-wind run-down test | Approved reserve target and stopping criterion |
| Durability | Cycle, wear, shock, and service tests | No unacceptable degradation; approved life criteria |
| Service repeatability | Pre/post service measurements | Within released performance limits |

Do not assign pass/fail to an unapproved numeric threshold. All acceptance limits must be approved, traceable to requirements, and tied to a stated test method and revision.

## 12. Instrumentation and data integrity

Required instrumentation may include calibrated torque transducers, angular encoders, timing equipment, amplitude measurement, optical inspection/metrology, temperature control, and a repeatable drive/load fixture. Instrument selection and range must follow the expected measured values once the prototype envelope is known.

Each data record must include:
- unique test ID and date;
- movement serial/revision and component configuration;
- instrument identity, calibration status, range, and uncertainty;
- operator and procedure revision;
- temperature, orientation, state of wind, and elapsed interval;
- chronograph/calendar state;
- raw samples, units, data processing method, and anomalies.

Preserve raw data. Derived values must be reproducible from recorded inputs and code revision.

## 13. Failure modes and controls

| Failure mode | Consequence | Detection / mitigation |
|---|---|---|
| Insufficient barrel energy | Reserve shortfall / stoppage | Torque-angle measurement and complete load budget |
| Excessive train friction | Low amplitude / reserve | Boundary efficiency tests, pivot and mesh inspection |
| Incorrect ratio or train closure | Incorrect hand cadence / escapement drive | Independent kinematic calculation and prototype verification |
| Tooth wear or breakage | Loss of drive / debris | Stress review, material controls, endurance inspection |
| Excessive backlash | Hand jitter, impact, poor engagement | Tolerance stack and dynamic test |
| Chronograph load excessive | Amplitude/rate loss | Matched stopped/running and transient load tests |
| Calendar indexing overload | Stoppage or timing disturbance | Changeover torque and low-reserve tests |
| Lubricant migration/aging | Increased friction or contamination | Aging, temperature, and service-cycle testing |
| Barrel bridle drag/instability | Reduced usable energy | WP-08 bridle characterization integrated with barrel test |
| Incorrect assembly/phasing | Interference or timing failure | Datum, phasing marks, assembly and service procedure |

## 14. Interfaces to other work packages

- **WP-08:** winding input, barrel arbor, bridle slip, winding efficiency, and automatic winding load.
- **WP-09:** escapement frequency, impulse demand, amplitude/rate envelope, and timekeeping acceptance.
- **Calendar package:** day/date drive, indexing, correction, and changeover loads.
- **Chronograph package:** clutch/control architecture, counter train, transient and steady running loads.
- **Case/dial package:** hand heights, center distances, display cadence, movement envelope, and service clearances.

Maintain a controlled interface register. A change to any interface must trigger review of affected ratios, energy budget, tolerance stack, and verification evidence.

## 15. Revision and decision register

| Decision | Status |
|---|---|
| Barrel torque-angle curve | Required; not yet supplied |
| Usable barrel energy | TBD from measured curve and approved usable range |
| Going-train wheel/pinion counts | Open |
| Gear module/tooth form | Open |
| Gear materials and finishes | Open |
| Pivot/jewel architecture | Open |
| Train efficiency | Not measured |
| Chronograph incremental load | Not measured |
| Calendar incremental load | Not measured |
| 60–70 h reserve feasibility | Not established |
| Numeric efficiency/load margins | Await approved limits and prototype evidence |

## 16. Release gate

WP-10 may progress to preliminary design release only when:
1. barrel torque-angle data and usable energy are measured;
2. WP-09 escapement demand and operating envelope are established;
3. all going-train ratios close kinematically against the display and escapement requirements;
4. gear geometry, material, tolerance, and stress calculations are reviewed;
5. chronograph and calendar loads are measured or bounded by documented evidence;
6. energy budget shows adequate margin across defined states of wind and operating modes;
7. prototype reserve and timing tests meet approved criteria;
8. assembly, lubrication, inspection, and service procedures are reviewed.

**Current disposition:** preliminary engineering definition and executable calculation framework only. No production gear train, measured efficiency, validated energy margin, or achieved power reserve is claimed.
