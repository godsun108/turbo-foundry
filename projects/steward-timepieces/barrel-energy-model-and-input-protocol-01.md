# STEWARD C-01 — Barrel Energy Model and Input Protocol 01

**Revision:** 0.1  
**Status:** Executable first-order estimator; not a validated reserve prediction  
**Branch:** `steward/c-01-movement-foundation`

## Purpose

Turn the existing energy equations into an input-driven calculation tool. It calculates usable barrel energy from a torque-versus-unwind-angle dataset and estimates reserve for two operating states: chronograph stopped and chronograph running.

The model intentionally has no default torque, efficiency, base-load or chronograph-load values. The user must supply measured, supplier-confirmed or explicitly justified inputs.

## Calculation

Usable barrel energy is integrated with the trapezoidal rule:

`E_{barrel} = \sum_i \frac{T_i+T_{i+1}}{2}(\theta_{i+1}-\theta_i)`

Energy at the modeled train output reference plane:

`E_{out}=E_{barrel}\eta_{train}`

Calendar event energy is averaged over a day:

`P_{calendar,avg}=E_{event}N_{events/day}/86400`

The first-order reserve estimates are:

`t_{off}=E_{out}/(P_{base}+P_{calendar,avg})`

`t_{on}=E_{out}/(P_{base}+P_{calendar,avg}+P_{chrono})`

All loads are specified at the same useful train output reference plane. Train efficiency is an aggregate barrel-to-output input. These simplifying assumptions must be revisited as the train architecture becomes known.

## Inputs

JSON input fields:
- `torque_samples`: ordered list of `angle_rad` and `torque_nm` measurements covering only the approved usable unwind interval.
- `train_efficiency`: aggregate measured or justified efficiency, strictly greater than zero and no more than one.
- `base_load_w`: continuous timekeeping/display load at the output reference plane.
- `chrono_incremental_load_w`: incremental load while the chronograph is engaged.
- `calendar_event_energy_j`: energy per calendar change event at the output reference plane.
- `calendar_events_per_day`: average number of such events per day. Both calendar inputs must be zero together or positive together.

No example numeric input is included because invented values could be mistaken for C-01 measurements.

## Measurement protocol required before populating inputs

1. Define the barrel usable unwind limits from safe winding and minimum acceptable delivered torque.
2. Measure torque at multiple angular positions across that interval using a calibrated torque instrument and a repeatable fixture.
3. Record instrument calibration, sample spacing, temperature, spring condition, lubrication, direction and uncertainty.
4. Determine aggregate train efficiency from a validated test or a traceable component-level model; do not assign generic watch-train efficiency.
5. Measure base and incremental chronograph loads at a clearly defined shaft/reference plane.
6. Measure calendar event energy and peak torque separately. The present model averages event energy and cannot assess the short-duration changeover disturbance.
7. Repeat measurements at full, mid and low wind and under relevant temperature/service conditions.

## Output and interpretation

The tool reports integrated barrel energy, energy at the output plane, calendar average load, and estimated reserve with the chronograph stopped and running.

These are constant-average-load estimates. They do not predict balance amplitude, rate shift, escapement stability, calendar peak-load behavior, chronograph engagement transients, automatic winding efficiency or real-world stoppage margin. A reserve target is not met merely because this estimate exceeds 60 hours; the design must retain acceptable torque and timekeeping over the full reserve.

## Run

From the tools directory:

```bash
python c01_barrel_energy_model.py measured_inputs.json
python -m unittest test_c01_barrel_energy_model.py
```

## Engineering decision

No barrel size, spring material, spring geometry, number of turns, torque curve, train efficiency, gear ratio or reserve claim is selected by this model. These remain open until measured/source-backed data and prototype tests are available.
