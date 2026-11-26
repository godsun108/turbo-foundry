# STEWARD C-01 — WP-12 Integrated Calendar

**Document ID:** C01-WP-12  
**Revision:** 0.1  
**Status:** Preliminary engineering definition and verification plan  
**Branch:** `steward/c-01-movement-foundation`  
**Interfaces:** WP-08 Automatic Winding; WP-09 Balance and Escapement; WP-10 Gear Train and Energy Transmission; WP-11 Chronograph Mechanism  
**Scope baseline:** weekday and day-of-month; month indication is an open scope decision and is not silently added to C-01

## 1. Purpose

Define the calendar subsystem for STEWARD C-01, with a mechanically advanced weekday indication and a day-of-month indication from 1 through 31. Establish the mechanism architecture, correction philosophy, integration interfaces, calculations, verification requirements, and unresolved decisions.

C-01's current repository baseline is chronograph + day + date. The repository assigns month display and moon phase to the separate LUNAR concept. The user's previously expressed interest in a month window is recorded here as an explicit scope decision requiring review; this document does not authorize a month display, month cam, additional wheel train, or change to the C-01 baseline.

## 2. Requirements baseline

| ID | Requirement | Status | Verification |
|---|---|---|---|
| CAL-001 | Display day of month, 1–31 | Baseline | Visual and cycle test |
| CAL-002 | Display weekday, seven positions | Baseline | Seven-day advance test |
| CAL-003 | Calendar advances once per calendar day | Required function | Long-duration rollover test |
| CAL-004 | Date and weekday can be corrected independently | Proposed; confirm architecture | Correction and retention test |
| CAL-005 | Calendar does not compromise timekeeping | Required | WP-09 rate/amplitude comparison |
| CAL-006 | Calendar load remains inside approved energy budget | Required | WP-10 measurement |
| CAL-007 | Correction cannot damage calendar near changeover | Required | Interlock / misuse test |
| CAL-008 | Month indication | Open scope decision | Formal C-01/LUNAR scope decision |

The weekday display uses seven discrete states. The date display uses a 31-position indication. Neither display alone identifies month length or leap-year state.

## 3. Calendar principle and month-end behavior

A conventional 31-position date mechanism does not inherently know whether a month has 28, 29, or 30 days. Without a month-length program, the wearer must correct the date after shorter months.

For a 31-day date wheel:
- 31 → 1 is a natural 31-day rollover.
- After a 30-day month, the date must be advanced from 31 to 1 by correction.
- After a 28- or 29-day February, correction is required after the final day.
- Weekday continues to advance every day and is not reset when the date is corrected.

The executable model accepts the actual month length as an input for calendar-state verification. It does not imply the physical C-01 movement contains a month cam or perpetual-calendar program.

## 4. Candidate mechanical architecture

### 4.1 Date indication

Candidate conventional architecture:
- 31-position date ring or date disc;
- date driving finger or equivalent once-per-day drive;
- date jumper and spring;
- date corrector and setting interface;
- controlled display aperture and dial-side alignment datum.

Detailed design must compare a ring versus disc arrangement against movement diameter, dial aperture, hand stack, bridge access, inertia, torque, and serviceability.

### 4.2 Weekday indication

Candidate architecture:
- seven-position weekday star or ring;
- once-per-day drive from the calendar train;
- jumper/indexing spring;
- independent corrector if confirmed as a requirement;
- dial-side alignment and legibility control.

Determine whether the weekday is advanced directly from the date/calendar train or through a dedicated indexing stage. The selected design must avoid missed or double indexing and must remain synchronized through month-end date corrections.

### 4.3 Shared calendar drive

The calendar drive may derive from a once-per-day motion in the going train. The exact drive point, reduction stages, date finger travel, and weekday indexing relationship must be established in the integrated gear-train drawing.

No gear tooth counts, date-star geometry, jumper force, spring rate, calendar torque, or drive ratio is frozen in Revision 0.1.

## 5. Correction philosophy and safety

Independently correctable date and weekday indications are a desired architecture, subject to packaging and reliability review.

The final design must define:
- correction direction and increment per crown/pusher action;
- positive indexing and feedback;
- prevention of partial engagement;
- correction behavior during normal running;
- safe correction interval relative to the calendar changeover;
- protection against simultaneous corrector engagement;
- retention against accidental correction;
- documented setting instructions.

A date quickset can damage a calendar mechanism if used while its changeover works are engaged. The safe correction window must be established from the actual calendar train's engagement phase, tolerances, and prototype tests. Do not publish a generic clock-time prohibition as a C-01 fact until the mechanism is designed and verified.

If the selected mechanism cannot safely support independent correction during all phases, define a mechanical inhibit or a clear operating restriction and validate it.

## 6. Month display scope control

The user's month-window preference is retained as an open design request. The existing C-01 README currently states that month display and moon phase belong to LUNAR, while C-01 is chronograph + day + date.

Before adding month indication, conduct a formal scope review covering:
- whether the month window is a C-01 requirement or a future LUNAR feature;
- display location and legibility;
- month indexing source and 12-position mechanism;
- correction and annual rollover behavior;
- month-length and leap-year implications;
- additional torque, power reserve, thickness, parts, and service burden;
- interaction with the chronograph and weekday/date displays.

A simple 12-position month display would require a defined monthly indexing mechanism and correction strategy. It would not, by itself, solve 28/29/30/31-day date programming. No month wheel, annual cam, perpetual calendar, or leap-year function is included in the current baseline.

## 7. Kinematic and logical model

The logical calendar state is represented by:
- date (D), valid from 1 through supplied month length (L);
- weekday index (W), valid from 0 through 6;
- month length (L), supplied as 28, 29, 30, or 31 days.

Daily advance:
- If (D < L), next date is (D+1).
- If (D = L), next date is 1 and a month rollover is recorded.
- In every case, next weekday is ((W+1) mod 7).

A 31-position date wheel has zero-based position (D-1), with positions 0 through 30. This is a software representation only; physical tooth counts and indexing geometry remain to be designed.

## 8. Energy and timekeeping integration

Calendar energy has at least two distinct conditions:
1. steady idle drag from the calendar train and indexing elements;
2. transient load during date and weekday changeover.

Measure:
- calendar idle energy over a defined interval;
- changeover transient peak and duration;
- energy for simultaneous date and weekday indexing;
- corrector actuation behavior;
- effect at full, intermediate, and low reserve;
- amplitude and rate before, during, and after changeover.

Use the same measurement boundary and controlled test conditions as WP-10. Compare calendar idle and changeover measurements over matched intervals; capture transient peaks separately. Compare amplitude and rate against WP-09 limits and test the chronograph both stopped and running where practical.

The model in `tools/c01_calendar.py` reports an incremental energy/load delta from supplied measurements. It does not estimate calendar energy from unverified geometry.

## 9. Chronograph interaction and packaging

The calendar must be integrated with WP-11, not designed in isolation. Confirm:
- no interference with chronograph clutch, column/cam control, hammer, heart cams, or counters;
- no unacceptable calendar load when the chronograph is running;
- sufficient axial height and radial envelope;
- independent bridge and service access where possible;
- corrector access through crown/pushers without conflicting with chronograph controls;
- hand stack and aperture clearances;
- no calendar component can contact or displace chronograph hands.

A simultaneous-load test is required: calendar changeover with chronograph stopped and with chronograph running, at controlled reserve states.

## 10. Materials, tolerances, lubrication, and durability

The detailed design must specify:
- date ring/disc and weekday star/ring material and finish;
- indexing finger geometry, contact, and retention;
- jumper spring material, geometry, preload, fatigue life, and replacement method;
- corrector lever, pivot, and engagement tolerances;
- date and weekday display alignment datum and allowable visual error;
- wheel/pinion geometry and backlash;
- pivots, jewels, bushings, endshake, and side-shake;
- lubricant type, location, quantity, and migration control;
- wear surfaces and inspection criteria.

Calendar parts must be durable under repeated daily indexing and occasional correction. Avoid overloading a small driving finger or relying on excessive spring force to mask poor geometry.

## 11. Verification plan and acceptance criteria

| Test | Method | Acceptance criterion |
|---|---|---|
| Date progression | Instrumented 1–31 cycle | Exactly one index per commanded day |
| Weekday progression | Seven-day cycle | Exactly one weekday step per day; correct wrap |
| Month-end | Simulate 28, 29, 30, and 31-day months | Date state matches supplied month length; manual correction documented where needed |
| Independent correction | Correct date without weekday change and vice versa | Only selected indication changes |
| Quickset safety | Phase-swept correction around changeover | No tooth clash, damage, partial index, or loss of synchronization |
| Changeover reliability | Repeated date + weekday indexing | No missed or double steps |
| Energy | WP-10 measurement protocol | Within approved incremental load budget |
| Timekeeping | WP-09 amplitude/rate tests | Within approved calendar-on/off disturbance limits |
| Simultaneous load | Calendar changeover with chrono off/on | Within approved energy and timekeeping limits |
| Low reserve | Repeat changeover near approved low-reserve boundary | Complete indexing without stall or damage |
| Shock and wear | Approved shock and endurance protocols | Alignment and operation remain within released limits |
| Service repeatability | Disassemble, inspect, service, reassemble | Released limits maintained |

Numerical tolerances and pass/fail thresholds remain TBD until dial readability, movement envelope, prototype capability, measurement uncertainty, and project requirements are approved. No test is a pass merely because a proposed threshold has not yet been defined.

## 12. Failure modes and controls

| Failure mode | Effect | Control / verification |
|---|---|---|
| Missed date index | Incorrect date | Drive-finger engagement and low-reserve test |
| Double date index | Incorrect date | Jumper force, drive travel, and cycle test |
| Weekday/date desynchronization | Incorrect calendar display | Long-duration synchronized cycle |
| Quickset during engaged changeover | Damaged teeth or levers | Phase-based inhibit or validated user restriction |
| Excessive jumper force | High load / stalled calendar | Force and energy measurement |
| Weak jumper | Poor indexing or display misalignment | Shock, vibration, and repeatability test |
| Calendar drag | Reduced reserve / amplitude | WP-09 and WP-10 comparison |
| Corrector partial engagement | Wear or incorrect state | Engagement geometry and misuse testing |
| Month-end not corrected | Date display incorrect | Clear setting instructions; month-end procedure |
| Calendar/chrono interference | Malfunction or hand collision | Packaging review and simultaneous-load test |

## 13. Assumptions and unresolved decisions

| Item | Revision 0.1 position |
|---|---|
| Weekday display | Seven-position mechanical indication |
| Date display | 1–31 mechanical indication |
| Month length | Manual correction after shorter months in baseline |
| Independent date/weekday correction | Desired; detailed architecture open |
| Month window | User preference recorded; C-01 scope decision required |
| Month cam / annual calendar | Not in baseline |
| Perpetual calendar / leap-year program | Not in baseline |
| Calendar drive point | Open pending WP-10 integration |
| Changeover time | Open pending drive and dial requirements |
| Quickset safe window | TBD from mechanism geometry and test |
| Calendar torque and energy | Not measured |
| Numerical acceptance limits | TBD pending approved requirements and prototype evidence |

## 14. Revision control and release gate

Revision 0.1 establishes the preliminary calendar basis. Any change to calendar scope, display, drive point, correction mechanism, month programming, or energy allocation must be recorded with reason, affected interfaces, analysis, verification evidence, and approval.

WP-12 may advance to preliminary design release only when:
1. date and weekday display geometry is reconciled with the dial;
2. the calendar drive point and cadence are defined against WP-10;
3. independent correction and safe correction behavior are detailed;
4. calendar/chronograph packaging and simultaneous-load interfaces are resolved;
5. energy and timekeeping effects meet approved criteria;
6. month-display scope is explicitly resolved;
7. drawings, BOM, assembly, setting, service, and inspection documents are revision-controlled.

**Current disposition:** preliminary calendar engineering definition and logical calculation model only. No physical calendar architecture, measured torque, verified safe correction interval, month mechanism, prototype pass, or production release is claimed.
