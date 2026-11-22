# C-01 Architecture Study — Open

**Revision:** 0.1  
**Status:** Investigation plan; no architecture selected

## Design question

What is the most reliable, serviceable, manufacturable architecture for an automatic chronograph with day-of-week and day-of-month indications?

## Candidate chronograph architectures

### A. Integrated chronograph

Chronograph components are designed into the base caliber.

**Potential advantages**
- Purpose-designed component placement and thickness.
- Fewer module interfaces.
- Opportunity to optimize power flow and service access as one system.

**Potential disadvantages**
- Greater development complexity.
- More expensive initial engineering and tooling.
- A fault in the chronograph may require deeper movement disassembly.

### B. Modular chronograph

A chronograph module is mounted on a base movement.

**Potential advantages**
- May reduce initial development risk.
- Base movement can be independently serviced or sourced.
- Useful as a staged development route.

**Potential disadvantages**
- Added thickness and interfaces.
- Calendar and chronograph packaging may conflict.
- Additional tolerances and coupling interfaces.
- Not automatically easier or cheaper to service.

## Switching and coupling candidates

| Element | Candidate | Questions to resolve |
|---|---|---|
| Control | Column wheel | Cost, machining, adjustment, repairability |
| Control | Cam/lever | Simplicity, pusher feel, wear and adjustment |
| Coupling | Vertical clutch | Hand jump, friction, drag, service |
| Coupling | Horizontal clutch | Engagement behavior, tooth wear, hand jump |

Column wheel + vertical clutch remains an attractive hypothesis, not a predetermined answer. The trade study must compare the whole movement rather than optimize one chronograph feature in isolation.

## Calendar architecture

Required displays are day of week and date (1–31). Investigate:
- Day and date discs versus hands.
- Independent correction and setting safety.
- Midnight changeover torque and energy.
- Calendar behavior during chronograph operation.
- Protection against incorrect setting during the changeover window.
- Part count, spring loads, and service access.

Month-end correction is expected for a simple 1–31 calendar. No annual/perpetual calendar is in scope.

## Reference movements for benchmarking

Initial candidates to research:
- Seiko/TMI NE88 family.
- Sellita SW510 family.
- ETA/Valjoux 7750 family.

For each, record exact caliber variant and manufacturer documentation. Do not assume day/date functions, dimensions, parts availability, or interchangeability from the family name. Verify the specific variant and source every specification.

## First research deliverables

1. Exact manufacturer technical sheets and service documentation where available.
2. Dimensions, thickness, diameter, hand heights, dial-side layout, and calendar positions.
3. Frequency, reserve, winding architecture, jewel count, and stated tolerances.
4. Chronograph switching and coupling design.
5. Known service procedures and parts availability.
6. Documented reliability/test evidence, distinguishing manufacturer claims from independent tests.
7. Feasibility of adding day and date without compromising thickness, torque, or service access.

## Open questions

- Target movement diameter and maximum thickness?
- Three-register or two-register chronograph layout?
- Calendar display: two windows, or another arrangement?
- Target retail tier and realistic movement development budget?
- Integrated caliber from the beginning, or staged prototype using a proven base?
- What service-support model can Steward financially sustain?

## Decision rule

Do not select a movement because it is famous, visually impressive, or has one desirable feature. Select the architecture that best satisfies the complete requirement set with the lowest credible lifecycle risk.
