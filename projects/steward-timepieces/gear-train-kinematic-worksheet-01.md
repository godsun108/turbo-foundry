# STEWARD C-01 — Gear-Train Kinematic Worksheet 01

**Revision:** 0.1  
**Status:** First-principles speed/ratio framework; no tooth counts selected  
**Branch:** `steward/c-01-movement-foundation`

## 1. Purpose

Establish the rotational speeds and ratio relationships required by C-01's displays before selecting wheel tooth counts, modules, center distances, materials or gear geometry.

This worksheet is kinematic only. It does not prove that the train can deliver sufficient torque, fit the envelope, meet efficiency targets or be manufactured.

## 2. Reference operating assumptions

The current requirements use a provisional 4 Hz balance frequency (28,800 vibrations per hour). At 4 Hz, the balance completes four full oscillations per second. In common watch terminology, the escapement delivers eight alternating beats per second.

These frequency assumptions do not uniquely determine escape-wheel speed. Escape-wheel tooth count, escapement geometry and pallet interaction must also be known.

| Parameter | Current value | Status |
|---|---:|---|
| Balance frequency | 4 Hz | Preliminary target |
| Alternating beats | 8 beats/s | Derived from 4 Hz |
| Vibrations per hour | 28,800 vph | Derived convention |
| Nominal running-seconds rotation | 1 rev/min | Display requirement |
| Minute-hand rotation | 1 rev/hour | Display requirement |
| Hour-hand rotation | 1 rev/12 hours | Display requirement |

## 3. Required output speeds

Use revolutions per minute (rpm) for a common comparison basis.

| Output | Period per revolution | Required speed |
|---|---:|---:|
| Running seconds | 60 s | 1 rpm |
| Central chronograph seconds, running | 60 s | 1 rpm |
| Minute hand | 3,600 s | 1/60 rpm |
| Hour hand | 43,200 s | 1/720 rpm |
| 30-minute totalizer hand | 1,800 s | 1/30 rpm |
| 12-hour totalizer hand | 43,200 s | 1/720 rpm |

The chronograph totalizer values assume a conventional one-revolution register hand over the stated elapsed-time range. The actual counter indexing and gearing must be confirmed against the selected mechanism.

## 4. Ratio definitions

For a simple external gear pair:

- Driver angular speed: n₁
- Driven angular speed: n₂
- Driver tooth count: z₁
- Driven tooth count: z₂

Ignoring slip and elastic effects:

`n₂ / n₁ = -z₁ / z₂`

The negative sign indicates opposite rotation direction. For ratio magnitude:

`i = n₁ / n₂ = z₂ / z₁`

For a compound train, multiply the stage ratios, while accounting for which wheels are rigidly mounted on common arbors. Internal gearing and intermediate idlers alter direction relationships and must be represented explicitly in the eventual train diagram.

Do not choose tooth counts merely to make a convenient ratio. Tooth counts must also satisfy undercut, module, center-distance, wheel diameter, pinion leaf, backlash, strength, manufacturing and available-space constraints.

## 5. Display ratio relationships

These are required speed relationships, not a proposed physical train.

### Going-train display relationships

- Running seconds to minute hand: 60:1 speed reduction.
- Minute hand to hour hand: 12:1 speed reduction.
- Running seconds to hour hand: 720:1 speed reduction.

### Chronograph relationships

When engaged:
- Central chronograph seconds: 1 rev/min.
- 30-minute register: 1 rev/30 min, or 1/30 rpm.
- 12-hour register: 1 rev/12 h, or 1/720 rpm.

Therefore, relative to the central chronograph seconds shaft:
- Central seconds to 30-minute register: 30:1 speed reduction.
- Central seconds to 12-hour register: 720:1 speed reduction.

The actual chronograph may use intermediate wheels, cams, jumper indexing or other arrangements. These ratios define the indication behavior, not the architecture.

## 6. Kinematic calculation register

Complete this table only after the reference movement or proposed C-01 train topology is defined.

| Stage ID | Driver component | Driven component | Driver teeth | Driven teeth | Ratio magnitude | Direction | Evidence |
|---|---|---|---:|---:|---:|---|---|
| GT-01 | TBD | TBD | TBD | TBD | TBD | TBD | Not defined |
| GT-02 | TBD | TBD | TBD | TBD | TBD | TBD | Not defined |
| GT-03 | TBD | TBD | TBD | TBD | TBD | TBD | Not defined |
| GT-04 | TBD | TBD | TBD | TBD | TBD | TBD | Not defined |
| CT-01 | Chronograph drive | Central chrono seconds | TBD | TBD | TBD | TBD | Not defined |
| CT-02 | Chronograph seconds train | 30-minute register | TBD | TBD | TBD | TBD | Not defined |
| CT-03 | Chronograph seconds train | 12-hour register | TBD | TBD | TBD | TBD | Not defined |

## 7. Data required before tooth-count selection

### Going train
- Barrel arbor speed over the useful torque range
- Barrel turns available between fully wound and stop
- Desired reserve and measured torque curve
- Center-wheel, third-wheel, fourth-wheel and escape-wheel topology
- Escapement type and escape-wheel tooth count
- Balance frequency and impulse geometry
- Wheel/pinion module or equivalent tooth geometry
- Pivot diameters, jewel locations and center-distance limits

### Motion works
- Verified minute and hour hand ratios
- Cannon-pinion and minute-wheel arrangement
- Hand-setting and friction requirements
- Calendar take-off location and required drive speed

### Chronograph
- Selected clutch and control architecture
- Source wheel speed and torque
- Counter arbor speeds and required direction
- Jumper/indexing loads
- Reset hammer and heart-cam geometry
- Engagement transient and amplitude disturbance limits

## 8. Energy and torque are separate constraints

A correct speed ratio does not establish adequate torque.

For each stage, the later power model must include:
- Input torque and speed
- Output torque and speed
- Mesh efficiency
- Pivot and jewel friction
- Lubricant and temperature effects
- Transient loads during calendar changeover and chronograph actuation

For an ideal lossless gear stage, power is conserved. In a real stage, output power is lower by the relevant losses. Do not assign a generic efficiency to C-01 without evidence from component data, measurement or a defensible validated model.

The existing `tools/c01_energy_budget.py` utility handles energy/efficiency calculations when measured or justified inputs are supplied. This worksheet does not duplicate that tool.

## 9. Required validation

Before a train ratio is accepted:
1. Independently recompute every stage ratio.
2. Confirm final output speeds against required hand periods.
3. Check rotation directions for each displayed hand.
4. Verify compound-arbor assumptions.
5. Check tooth geometry and center distances in CAD.
6. Evaluate minimum tooth counts and pinion geometry for undercut/interference.
7. Verify backlash and endshake requirements.
8. Measure friction and power loss on a physical train.
9. Verify rate and amplitude with chronograph stopped and running.

## 10. Current decision status

- Required display speeds: **defined**.
- Ideal ratio relationships: **calculated from display periods**.
- Physical going-train topology: **not selected**.
- Chronograph drive topology: **not selected**.
- Gear tooth counts: **not selected**.
- Gear module / tooth form: **not selected**.
- Center distances: **not established**.
- Torque and efficiency: **not validated**.
- CAD: **not created**.
- Prototype: **not built**.

---
**Engineering integrity note:** This is a kinematic requirements worksheet. It is not a detailed gear-train design, tooth-count schedule, dimensioned drawing, CAD model or validated movement.
