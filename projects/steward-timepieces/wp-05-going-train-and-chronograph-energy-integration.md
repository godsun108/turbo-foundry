# STEWARD C-01 — WP-05 Going-Train Topology and Chronograph Energy Integration

**Revision:** 0.1  
**Status:** Functional architecture and exact-ratio calculator; no physical train selected  
**Branch:** `steward/c-01-movement-foundation`

## 1. Objective

Define the power-path questions and exact display-speed requirements for the integrated automatic chronograph. Keep the going train, escapement, time display, running seconds, chronograph, and calendar as explicit subsystems. Compare two plausible chronograph power takeoff strategies without prematurely selecting either.

## 2. Functional power path

The movement's energy path begins at the mainspring barrel. The going train transmits power to the escapement/balance and provides motion-work and seconds outputs. The chronograph is a selectively engaged load, with its own drive, coupling, brake, control, counters and reset system.

The functional diagram is not a shaft-level train drawing. It intentionally leaves actual wheel identities, arbor speeds, tooth counts, torque and gear geometry unresolved.

## 3. Exact indication speeds

| Output | Period per revolution | Required speed |
|---|---:|---:|
| Running seconds | 60 seconds | 1 rpm |
| Central chronograph seconds | 60 seconds | 1 rpm |
| Minute hand | 60 minutes | 1/60 rpm |
| Hour hand | 12 hours | 1/720 rpm |
| 30-minute totalizer | 30 minutes | 1/30 rpm |
| 12-hour totalizer | 12 hours | 1/720 rpm |

Relative ideal speed reductions:
- Running seconds to minute hand: 60:1.
- Minute hand to hour hand: 12:1.
- Chronograph seconds to 30-minute totalizer: 30:1.
- Chronograph seconds to 12-hour totalizer: 720:1.

These are exact indication requirements, not tooth-count prescriptions. The totalizer may include intermediate wheels, compound arbors, cams, jumpers and reset components.

## 4. Chronograph power takeoff alternatives

### P1 — Fourth-wheel / seconds-axis takeoff

A candidate arrangement takes chronograph drive from the nominal 1 rpm seconds axis and selectively couples the chronograph train.

**Potential benefit:** A direct speed source may simplify the kinematic relationship to central chronograph seconds.

**Risks and tests:** Engaging the chronograph adds load at the seconds wheel/arbor. Measure available torque margin, amplitude change, start transient, rate change and reserve with chronograph stopped/running. Confirm the actual fourth-wheel architecture and seconds-hand arrangement before assigning this takeoff.

### P2 — Dedicated chronograph drive train

A candidate arrangement takes power at a defined going-train point and routes it through a dedicated chronograph drive train before the clutch and counters.

**Potential benefit:** Allows deliberate placement of the drive, coupling and service interfaces; may permit a more considered load path.

**Risks and tests:** Additional gear meshes, pivots, friction, parts, bridge area and adjustment can reduce efficiency and complicate packaging. Measure total losses and test amplitude/rate with the chronograph engaged.

**Decision:** Both remain open. Do not select one based on prestige or appearance. The decision requires a measured energy and packaging comparison.

## 5. Chronograph subsystems to detail

1. Drive source and intermediate train.
2. Coupling: horizontal or vertical candidate.
3. Brake: stop the central chronograph seconds and counter train when disengaged.
4. Control: cam or column-wheel candidate; separate decision from clutch type.
5. Counter drive: 30-minute and 12-hour outputs.
6. Reset: heart cams, hammers, hammer return and zero alignment.
7. Actuation: pusher force, lever travel, safety interlocks and start/stop/reset sequencing.

A running chronograph must not be assumed to be energy-neutral. The incremental load must be measured at a clearly defined reference plane.

## 6. Calculator and verification

- `tools/c01_train_topology.py` defines exact display speeds using rational arithmetic, computes compound ratios for explicitly supplied gear pairs, tracks rotation direction, and can estimate ideal torque transformation when explicit efficiencies are supplied.
- `tools/test_c01_train_topology.py` checks exact ratios, direction, torque transformation, invalid inputs and the two open power-path alternatives.

Run from the tools directory:

```bash
python c01_train_topology.py --requirements
python -m unittest test_c01_train_topology.py
```

The test fixtures use arbitrary example gear pairs only to test the mathematics. They are not proposed C-01 tooth counts.

## 7. Inputs required before selecting a train

- Approved barrel usable torque curve and speed/turn data.
- Measured torque available at candidate going-train takeoff points.
- Exact escapement architecture, wheel tooth count and balance frequency.
- Motion works and running-seconds shaft arrangement.
- Candidate chronograph clutch geometry and engagement load.
- Counter train, jumper, reset hammer and heart-cam loads.
- Gear geometry constraints, center distances, pivot/jewel dimensions and axial stack.
- Efficiency and friction data with instrument uncertainty.

## 8. Required prototype measurements

Record at minimum:
- Balance amplitude, rate and beat error: chronograph stopped, running, start, stop and reset.
- Chronograph hand jump at engagement and repeatability across multiple start phases.
- Barrel torque and reserve with chronograph off/on.
- Pusher force/travel and reset-to-zero error.
- Counter advancement accuracy and reset alignment.
- Calendar changeover behavior with chronograph stopped and running.
- Temperature, lubrication state, orientation, winding state and measurement uncertainty.

## 9. Current decision register

| Decision | Status |
|---|---|
| Required display speeds | Defined |
| Exact ideal ratio relationships | Calculated |
| Fourth-wheel takeoff vs dedicated drive | Open |
| Horizontal vs vertical clutch | Open |
| Cam vs column-wheel control | Open |
| Going-train topology | Not selected |
| Escape-wheel tooth count | Not selected |
| Gear tooth counts / module | Not selected |
| Torque margin / efficiency | Not measured |
| Amplitude and rate disturbance | Not measured |
| Physical CAD / prototype | Not created |

## 10. Engineering integrity

No tooth counts, gear dimensions, torque values, efficiency values, barrel specifications or performance claims are frozen in WP-05. Exact arithmetic is not evidence of physical feasibility. A ratio solution must still pass geometry, strength, lubrication, friction, assembly, service and prototype testing.

**Next gate:** establish a documented reference movement teardown and identify the candidate takeoff interfaces. Then use measured torque and amplitude data to compare P1 and P2 before detailed shaft placement or gear selection.
