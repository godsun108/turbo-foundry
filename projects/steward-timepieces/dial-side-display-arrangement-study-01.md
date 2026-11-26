# STEWARD C-01 — Dial-Side Display Arrangement Study 01

**Revision:** 0.1  
**Status:** Concept study; no display layout frozen  
**Branch:** `steward/c-01-movement-foundation`

## 1. Purpose and design boundary

This study converts the C-01 indications into candidate dial-side arrangements and establishes a coordinate convention for subsequent parametric CAD.

C-01 must display:
- Hours and minutes
- Weekday
- Day of month (1–31)
- Central chronograph seconds
- 30-minute chronograph register
- 12-hour chronograph register
- Continuous running seconds

The three subdials therefore have distinct functions. The central chronograph seconds hand is not a subdial.

**No case diameter, dial opening, hand length, subdial diameter, window size, shaft coordinate or tolerance is approved by this study.** All positions below are normalized layout concepts, not manufacturing dimensions.

## 2. Display hierarchy

The dial must make the everyday time and calendar readable first, while keeping chronograph elapsed time immediately legible.

Proposed hierarchy for evaluation:
1. Hours and minutes: primary, highest visual priority.
2. Central chronograph seconds: high contrast and clearly distinguishable from ordinary seconds.
3. Weekday and date: legible at normal wrist distance.
4. 30-minute and 12-hour registers: legible, with clear scale and hand differentiation.
5. Running seconds: continuously visible but visually subordinate to the chronograph.

The chronograph seconds hand should have a distinct finish or color from the hour/minute hands and running-seconds hand. This is a design recommendation, not a selected color specification.

## 3. Coordinate convention for CAD

Use a dial-side orthographic view, looking from the crystal toward the movement.

- Origin O = nominal movement/dial center.
- +X = 3 o'clock direction.
- +Y = 12 o'clock direction.
- −X = 9 o'clock direction.
- −Y = 6 o'clock direction.
- Positive angular direction = counter-clockwise when viewed from the dial side.
- Coordinates are expressed in millimetres only after the case/dial envelope is selected.
- Until then, use normalized coordinates: x/R and y/R, where R is the chosen dial-opening radius.

For a point at radius r and angle θ measured counter-clockwise from +X:
- x = r cos(θ)
- y = r sin(θ)

For a register or window, record its centre, outer diameter/width, visible aperture, hand stack height, scale radius, and clearance envelope separately. Do not treat the centre coordinate as the complete packaging definition.

## 4. Candidate arrangement A — conventional chronograph / calendar at 3

**Concept:** Familiar three-register chronograph arrangement with the weekday and date grouped at 3 o'clock.

| Element | Nominal dial direction | Normalized centre | Notes |
|---|---:|---|---|
| 30-minute counter | 12 o'clock | (0, +r₁) | Upper register |
| 12-hour counter | 6 o'clock | (0, −r₂) | Lower register |
| Running seconds | 9 o'clock | (−r₃, 0) | Left register |
| Weekday + date | 3 o'clock | (+r₄, 0) | Twin window or adjacent apertures |
| Central chrono seconds | Centre | (0, 0) | Shared central axis |
| Hour/minute hands | Centre | (0, 0) | Main time display |

### Advantages to test
- Familiar chronograph reading pattern.
- Day/date grouped in a predictable location.
- Counter hierarchy can be communicated with conventional dial graphics.
- Potentially compatible with established three-register movement layouts.

### Risks to test
- Day/date apertures at 3 o'clock compete with the right-side dial edge and crown-side visual mass.
- Upper and lower registers must clear the central hand stack and hour markers.
- The 9 o'clock running-seconds register may create visual imbalance if the calendar windows are large.
- The actual movement architecture may not support these axes without additional transfer gearing.

## 5. Candidate arrangement B — calendar at 12 / balanced three-register face

**Concept:** Place weekday and date in a paired window at 12 o'clock, with three registers at 3, 6 and 9 o'clock.

| Element | Nominal dial direction | Normalized centre | Notes |
|---|---:|---|---|
| 30-minute counter | 3 o'clock | (+r₁, 0) | Right register |
| 12-hour counter | 6 o'clock | (0, −r₂) | Lower register |
| Running seconds | 9 o'clock | (−r₃, 0) | Left register |
| Weekday + date | 12 o'clock | (0, +r₄) | Paired window |
| Central chrono seconds | Centre | (0, 0) | Shared central axis |
| Hour/minute hands | Centre | (0, 0) | Main time display |

### Advantages to test
- Symmetrical three-register visual rhythm.
- Calendar is visible near the top of the dial.
- Day and date can be treated as one clear information group.
- Strong identity opportunity for STEWARD without adding an unnecessary complication.

### Risks to test
- Top calendar window may compete with the 12 o'clock marker and upper case curvature.
- Right-side 30-minute register may be crowded by crown/pusher geometry.
- Window discs and calendar drive must fit without compromising the hand stack or dial thickness.
- The arrangement may require a different movement-side counter-drive layout.

## 6. Candidate arrangement C — compact calendar / asymmetric register study

**Concept:** Retain the conventional 12 / 6 / 9 register positions but use two compact calendar apertures near 12 o'clock, slightly separated from the upper register.

This option is intentionally left as a packaging study rather than a fixed coordinate proposal. It may be viable if the dial opening and upper register permit sufficient separation.

### Advantages to test
- Keeps the familiar chronograph counter positions.
- Moves calendar information away from the crown-side edge.
- May create a distinctive dial identity.

### Risks to test
- Upper register and twin calendar windows may overlap in the available vertical space.
- Small apertures may reduce weekday/date legibility.
- A visually attractive dial could conceal an impractical disc/bridge arrangement.

## 7. Comparative decision matrix

Scores are not assigned because there is not yet a dimensioned dial, case, movement architecture or legibility test. Use the following criteria in a physical mock-up and CAD review.

| Criterion | A: calendar at 3 | B: calendar at 12 | C: compact calendar at 12 |
|---|---|---|---|
| Everyday day/date legibility | Test | Test | Test |
| Counter legibility | Test | Test | Test |
| Visual balance | Test | Test | Test |
| Crown/pusher clearance | Test | Test | Test |
| Calendar-disc packaging | Test | Test | Test |
| Hand-stack clearance | Test | Test | Test |
| Movement-drive complexity | Test | Test | Test |
| Service access | Test | Test | Test |
| Dial identity | Test | Test | Test |

**Decision rule:** Do not select a layout from appearance alone. A candidate must pass the dial legibility mock-up, movement-axis feasibility, calendar packaging, hand-clearance and service-access reviews.

## 8. Parametric coordinate register

Create a CAD parameter table with the following fields. Values remain `TBD` until the case/dial envelope and movement architecture are selected.

| Parameter | Meaning | Initial state |
|---|---|---|
| D_case | Case outside diameter | TBD |
| D_dial | Dial outside diameter | TBD |
| D_opening | Visible dial opening | TBD |
| R_opening | D_opening / 2 | Derived after D_opening |
| X_HM, Y_HM | Hour/minute axis | (0, 0) datum |
| X_CCS, Y_CCS | Central chrono-seconds axis | (0, 0) datum, subject to coaxial stack |
| X_30M, Y_30M | 30-minute register axis | TBD by candidate |
| X_12H, Y_12H | 12-hour register axis | TBD by candidate |
| X_RS, Y_RS | Running-seconds axis | TBD by candidate |
| X_DAY, Y_DAY | Weekday aperture centre | TBD by candidate |
| X_DATE, Y_DATE | Date aperture centre | TBD by candidate |
| D_subdial | Subdial outside diameter | TBD |
| D_scale | Register scale diameter | TBD |
| W_DAY, H_DAY | Weekday visible aperture | TBD |
| W_DATE, H_DATE | Date visible aperture | TBD |
| Z_dial | Dial plane / thickness datum | TBD |
| Z_hour, Z_min, Z_chrono | Hand stack planes | TBD |
| C_hand | Minimum hand-to-hand clearance | Engineering-derived |
| C_dial | Minimum hand-to-dial clearance | Engineering-derived |
| C_crystal | Minimum hand-to-crystal clearance | Engineering-derived |

The central time and central chronograph seconds functions may share a coaxial hand stack, but the actual arbor/tube arrangement and vertical clearances must be resolved in the movement design.

## 9. Required physical mock-ups

Before freezing the dial:
1. Produce a 1:1 printed dial mock-up for each candidate using the same outer diameter and hand lengths.
2. Include actual-size weekday/date character samples, not placeholder rectangles alone.
3. Use paper or transparent overlays to test counter scales and hand sweep.
4. Review readability at normal wrist distance and under low indoor light.
5. Check that the central chrono seconds hand is unmistakable from the running-seconds indication.
6. Confirm that the case crown and pusher positions do not visually or physically collide with the registers.
7. Ask at least one independent watchmaker or experienced dial designer to review the layout.

A printed mock-up verifies visual hierarchy only. It does not verify movement fit, torque, clearances, calendar operation or manufacturing feasibility.

## 10. Next engineering actions

1. Select a provisional case-size range for envelope studies, without treating it as final.
2. Obtain or measure the exact reference movement variant and record its revision.
3. Establish the true shaft-axis coordinates from a verified technical drawing or measured sample.
4. Build a 2D parametric dial layout for A, B and C.
5. Compare calendar disc geometry and counter drive locations against the dial apertures.
6. Freeze the display layout only after mechanical and legibility reviews agree.

## 11. Current decision status

- Display functions: **defined by requirements**.
- Coordinate datum: **defined conceptually**.
- Candidate arrangements: **A, B and C documented**.
- Numerical shaft coordinates: **not established**.
- Dial/case dimensions: **not established**.
- Preferred arrangement: **not selected**.
- CAD model: **not created**.
- Prototype: **not built**.

---
**Engineering integrity note:** This is a display-layout and coordinate-control study. It is not a dimensioned dial drawing, movement drawing, CAD model, manufacturing specification or validated prototype.
