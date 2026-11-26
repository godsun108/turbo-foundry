# STEWARD C-01 — WP-07 Weekday and Date Calendar Architecture

**Revision:** 0.1  
**Status:** Functional model and subsystem architecture; geometry and safe-setting window open  
**Branch:** `steward/c-01-movement-foundation`

## 1. Objective and scope

C-01 requires a seven-day weekday display and a 1–31 day-of-month display. WP-07 defines the daily indexing, independent correction functions, month-end user procedure, safe-setting design requirements and energy measurements.

Baseline scope is a conventional 31-day date mechanism with weekday. It is **not** an annual or perpetual calendar. It does not automatically know whether a month has 28, 29 or 30 days.

## 2. Functional architecture

The calendar is treated as a separately serviceable subsystem with:
- a daily drive take-off from the going train;
- a 24-hour program/indexing interface;
- a seven-position weekday display and jumper;
- a 31-position date display and jumper;
- a weekday correction interface;
- a date correction interface;
- a correction interlock whose safe condition must be derived from the final mechanism;
- accessible inspection, cleaning, lubrication and replacement interfaces.

Two construction options remain open:
1. Separate weekday and date discs with separate indexing/jumper elements, driven by a common daily program.
2. Separate weekday and date indexing assemblies with a shared daily actuator, subject to measured force, tolerance and service analysis.

A shared drive does not imply that both displays must use one combined disc or one correction train.

## 3. Daily indexing behavior

At the designated daily changeover:
- weekday advances exactly one of seven positions;
- date advances exactly one of 31 positions;
- both indications must settle fully into their next detents;
- no partial index, double step or rebound may remain;
- the calendar must not cause unacceptable amplitude or rate disturbance.

The precise changeover phase, duration and mechanism are TBD. No clock-time safe-setting restriction is published in this work package.

## 4. Month-end behavior

The baseline date disc advances 1 through 31. At the end of a shorter month the wearer manually corrects the date to the first day of the next month.

| Month length | Date corrections after month end |
|---:|---:|
| 31 days | 0 |
| 30 days | 1 forward step |
| 29 days | 2 forward steps |
| 28 days | 3 forward steps |

The table describes the user correction count for a 31-day display; it is not a calendar calculation mechanism. Weekday continues its daily progression independently. Leap years and month lengths are not mechanically encoded.

## 5. Quick-set and correction interfaces

Candidate user interface:
- crown/stem positions are to be defined in the stem and setting architecture;
- weekday and date corrections may share a crown position with separate rotational directions, or use independent correctors;
- correction direction, tactile feedback, protection against accidental actuation and access are to be evaluated;
- the selected design must not back-drive or load the daily indexing train in a damaging way.

No crown position or rotation direction is frozen. A correction-permission interlock must block correction outside a safe mechanical state. The safe state and any restricted time interval must be derived from the actual calendar geometry, tested, and then described in the user/service manual. Do not copy a setting window from another caliber.

## 6. Energy and load interfaces

The calendar is an intermittent load, not merely an average daily power draw. Record separately:
- energy per weekday index;
- energy per date index;
- energy when both index simultaneously;
- peak torque and force during the event;
- jumper release and seating load;
- correction energy and peak load;
- changeover timing and duration;
- effect on balance amplitude and rate.

If weekday and date index together, measure the combined event at the relevant output plane rather than double-counting two isolated measurements. The barrel energy model can use event energy and events/day for average reserve impact, but its first-order averaging does not predict peak torque or amplitude disturbance.

## 7. Serviceability requirements

- Calendar discs must be replaceable without destructive disassembly.
- Jumpers, springs and correction levers should be inspectable and serviceable.
- Provide unambiguous assembly datum and indexing marks.
- Document correct weekday/date phase relationship during assembly.
- Avoid inaccessible fasteners and trapped components.
- Identify lubrication points and compatible lubricants after material/contact review.
- Provide a safe calendar correction and hand-setting procedure.
- Establish replacement-part availability and service tooling.

## 8. Executable functional model

- `tools/c01_calendar_model.py` models weekday/date daily advancement, independent correction, date wrap, month-end correction count and event-energy bookkeeping.
- `tools/test_c01_calendar_model.py` tests indexing, wrap, independent correction, correction interlock, month-end steps and input validation.

Run from the tools directory:

```bash
python -m unittest test_c01_calendar_model.py
```

The model deliberately accepts a `correction_permitted` input. It does not invent an unsafe-hour window. The actual mechanical interlock must determine that permission from the final cam, lever and calendar state.

## 9. Prototype test plan

1. Cycle weekday/date through at least a full 31-day wheel sequence and repeat.
2. Verify 7-day and 31-day indexing without missed or double steps.
3. Measure display alignment, detent retention and backlash.
4. Test simultaneous changeover under full and low-reserve states.
5. Measure amplitude/rate before, during and after changeover.
6. Test correction at all mechanically permitted states.
7. Attempt correction at prohibited states and verify physical blocking without damage.
8. Test 28-, 29-, 30- and 31-day month-end user procedures.
9. Repeat after defined shock, temperature, lubrication and cycle-life testing.
10. Verify assembly phasing and service replacement procedure.

## 10. Open decisions

| Decision | Status |
|---|---|
| Seven weekday positions | Required |
| 1–31 date positions | Required |
| Daily changeover | Required; exact phase TBD |
| Independent weekday/date correction | Functional requirement; interface open |
| Shared daily drive vs separate drive elements | Open |
| Separate discs | Leading serviceability candidate, not frozen |
| Safe-setting state/window | Must be derived and validated |
| Month-length mechanism | Out of scope |
| Disc dimensions, tooth counts, jumper force | TBD |
| Calendar torque/energy | Not measured |
| Physical CAD/prototype | Not created |

**Next gate:** obtain a measured calendar teardown/reference, establish disc and jumper geometry envelopes against the three dial concepts, then design the daily drive and correction interlock around actual mechanical states.
