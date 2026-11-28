# STEWARD C-01 — Square Architecture Study 01

**Document ID:** C01-ARCH-SQ-001  
**Revision:** 0.1  
**Status:** Concept study — open for engineering review  
**Branch:** steward/c-01-movement-foundation  
**Design authority:** STEWARD C-01 requirements baseline  
**Release state:** No case geometry, movement architecture, dial arrangement, dimensions or materials approved

## 1. Purpose

Investigate whether STEWARD C-01 should be developed in a square or rounded-square watch format, and identify the mechanical consequences before selecting a design direction.

This study is a parallel concept track. It does not replace the existing round-case studies, change the C-01 functional requirements, or authorize a design freeze.

The central proposition is that a square watch should be designed as an integrated case, dial, movement, hand-stack and service-access system. It should not be treated as a conventional round movement placed inside a square shell without checking the resulting packaging and interfaces.

## 2. Requirements preserved

The square concept retains the C-01 baseline:

- Automatic mechanical winding.
- Hours and minutes.
- Weekday indication.
- Day-of-month indication, 1–31.
- Central chronograph seconds.
- Elapsed-minute counter.
- Elapsed-hour counter.
- Continuous running seconds.
- Hand winding and hacking seconds remain desired pending architecture compatibility.

Existing proposed targets remain proposed, not validated: 4 Hz / 28,800 vph; aspirational 60–70 hour power reserve; and proposed −4/+6 seconds per day rate objective.

**Scope boundary:** C-01 remains chronograph + weekday + date. Month display and moon phase remain assigned to LUNAR. This study does not add a month indication.

## 3. Design principle: square exterior, mechanically honest interior

A square case does not require square gears, a square balance, or a square rotor. Gear wheels, barrel, balance and rotor may remain circular where their mechanical functions favor circular geometry.

The movement's main plate and bridges can be rounded-square, square-like, or organized around a circular mechanical core. The correct choice must follow component packaging, energy transmission, rotor sweep, structural support, assembly sequence and serviceability.

The square outline must not force inefficient gear geometry or inaccessible service points merely to make the movement look square through the caseback.

## 4. Architecture candidates

### SQ-A — Rounded-square plate with conventional circular mechanical elements

**Concept:** A rounded-square movement plate and bridge envelope follows the case form. Circular barrel, gear train, balance, escapement, rotor and chronograph wheels are placed within that envelope according to their mechanical needs.

**Potential advantages**
- Strong visual relationship between case and movement.
- Allows circular mechanisms to retain familiar geometry.
- Offers opportunities for bridges and visible finishing to reinforce the square architecture.
- May provide useful corner regions for calendar, control or counter components, subject to actual clearances.

**Questions and risks**
- A square plate does not automatically create more usable area; corner volume may be inaccessible or mechanically inefficient.
- Rotor sweep and balance position may constrain the usable footprint.
- Bridge shapes must provide stiffness and service access rather than merely echo the case outline.
- The square dial and subdial layout may demand wheel positions that conflict with efficient train topology.

**Study status:** Candidate for detailed feasibility investigation; not selected.

### SQ-B — Fully square-organized movement architecture

**Concept:** The major subsystems are deliberately arranged around a square plan, with barrel, going train, regulation, chronograph and calendar distributed to create a coherent square mechanical composition. Circular components remain circular where required.

**Potential advantages**
- Strongest expression of a purpose-designed square movement.
- May create a distinctive exhibition-caseback architecture.
- Could align subsystem zones with the four sides or quadrants of the dial.

**Questions and risks**
- May increase train complexity, transfer gearing or component count.
- Rotor sweep, winding efficiency, balance protection and service access may become harder to reconcile.
- A visually symmetrical arrangement may be mechanically suboptimal.
- Requires evidence that added complexity provides functional or service benefits.

**Study status:** High-ambition candidate; no feasibility claim or selection.

### SQ-C — Circular mechanical core inside a square outer architecture

**Concept:** A compact circular or near-circular mechanical core carries the most geometry-sensitive elements. A square outer plate, dial-side structure or display architecture accommodates calendar and indication interfaces around it.

**Potential advantages**
- Preserves a concentrated region for established circular mechanical relationships.
- May reduce risk to the going train and regulating system.
- Offers a path to a square visual identity without requiring every subsystem to follow the case perimeter.

**Questions and risks**
- The transition between circular core and square outer structure may add intermediate interfaces.
- Calendar and chronograph indications still need direct, efficient drive paths.
- The outer structure must not become a decorative shell that complicates servicing.
- Casing, rotor and bridge interfaces need a complete tolerance and assembly study.

**Study status:** Candidate for comparison; not selected.

## 5. Square dial concept D — Four-quadrant chronograph

**Concept only:** A square dial with four visually organized display regions, a central time display and a central chronograph seconds hand.

| Display | Conceptual location | Function |
|---|---|---|
| 30-minute chronograph | Upper-left quadrant | Elapsed minutes |
| Weekday + date | Upper-right quadrant | Calendar |
| Running seconds | Lower-left quadrant | Continuous seconds |
| 12-hour chronograph | Lower-right quadrant | Elapsed hours |
| Hours and minutes | Central axis | Primary time |
| Chronograph seconds | Central axis | Elapsed seconds |

This is a new square-specific candidate, provisionally called D. It does not replace dial candidates A, B or C in the existing dial study.

### Visual intent

- Rounded-square outer dial geometry, with corner radii to be determined by case and dial construction.
- Four display zones organized around a clear central time axis.
- Calendar kept as a paired weekday/date information group.
- Chronograph hands and running-seconds hand visually distinguished from the primary time hands.
- Strong legibility before decorative symmetry.

### Mechanical feasibility questions

- Can the four sub-display axes be driven without excessive transfer gearing or loading?
- Do the counter wheels and calendar discs fit beneath their apertures with acceptable clearances?
- Can the central hour, minute and chronograph seconds hand stack be supported and serviced?
- Are the dial apertures sufficiently separated from the square dial's corner radii, chapter ring and case walls?
- Can the weekday/date display be corrected safely and independently as desired?
- Does the four-quadrant arrangement create unacceptable overlap with the stem, pushers or case supports?

All positions are illustrative. No normalized coordinates, dimensions, register diameters, window sizes, hand lengths, hand heights or tolerances are approved by this study.

## 6. Mechanical packaging work required

The following elements must be represented in one coordinated packaging model before an architecture can be recommended:

1. **Case and crystal:** internal case envelope, bezel, crystal seat, caseback, gasket interfaces and available vertical space.
2. **Dial:** square opening, corner radii, dial feet or attachment system, apertures, chapter ring and hand clearance.
3. **Barrel and going train:** actual wheel centers, arbor supports, mesh relationships, service access and power path.
4. **Regulator:** balance and escapement location, shock protection, adjustment access and clearance.
5. **Automatic winding:** rotor axis, full rotor sweep, winding works, winding direction strategy, caseback clearance and winding efficiency.
6. **Chronograph:** drive take-off, coupling, control, brake, reset hammers, counter trains and pusher interfaces.
7. **Calendar:** weekday/date discs or indicators, indexing, jumpers, correctors, midnight changeover and safe-setting behavior.
8. **Hand stack:** coaxial arbor arrangement, hand heights, clearances, friction and assembly access.
9. **Structure:** plate and bridge stiffness, fasteners, locating features, casing supports and shock-load paths.
10. **Service:** disassembly sequence, access to wear parts, lubrication points, adjustment points and replacement strategy.

No tooth counts, gear ratios, center distances, dimensions, clearances, torque values, material grades or tolerances are assigned here.

## 7. Case and interface investigation

The case concept should be studied as a rounded-square form before sharp-corner geometry is considered. This is a design direction for evaluation, not a selected case specification.

The case study must define, from evidence:
- External case envelope and corner radii.
- Internal movement seat and casing supports.
- Crown/stem axis and setting access.
- Chronograph pusher locations, travel and sealing interfaces.
- Crystal and caseback geometry.
- Rotor clearance and wrist-impact protection.
- Water-resistance target and validation method.
- Strap or bracelet attachment and load paths.
- Service opening and movement extraction method.

Titanium and sapphire may be evaluated as candidate case/crystal materials, but neither is selected by this study. Material choice requires structural, manufacturing, finishing, cost and service evaluation.

## 8. Comparative decision framework

No numerical scores are assigned before the required evidence exists. Each candidate is to be assessed against the same criteria.

| Criterion | SQ-A rounded-square plate | SQ-B square-organized movement | SQ-C circular core / square outer |
|---|---|---|---|
| Going-train efficiency | Evidence required | Evidence required | Evidence required |
| Chronograph integration | Evidence required | Evidence required | Evidence required |
| Calendar integration | Evidence required | Evidence required | Evidence required |
| Rotor sweep and winding | Evidence required | Evidence required | Evidence required |
| Balance protection | Evidence required | Evidence required | Evidence required |
| Structural stiffness | Evidence required | Evidence required | Evidence required |
| Hand-stack feasibility | Evidence required | Evidence required | Evidence required |
| Dial D compatibility | Evidence required | Evidence required | Evidence required |
| Assembly and serviceability | Evidence required | Evidence required | Evidence required |
| Manufacturability | Evidence required | Evidence required | Evidence required |
| Distinctive square identity | Qualitative review | Qualitative review | Qualitative review |
| Added parts / interfaces | Quantify after layout | Quantify after layout | Quantify after layout |

A recommendation requires documented layouts, interface counts, preliminary kinematics, access review, risk analysis and a reasoned comparison. Aesthetic preference alone is not sufficient to select the movement architecture.

## 9. Principal risks and mitigations

| Risk | Consequence | Required mitigation / evidence |
|---|---|---|
| Square case corners create unusable volume | Larger case without useful mechanical capacity | Overlay real component envelopes and service-access zones |
| Rotor sweep conflicts with square case or bridges | Winding, clearance or shock issues | Model full rotor sweep and verify clearances |
| Four-quadrant dial forces inefficient counter drives | Added losses, parts and adjustment burden | Develop and compare counter kinematic paths |
| Calendar apertures compete with upper-right register | Poor legibility or mechanical interference | Full dial-side aperture and disc-stack study |
| Square bridges reduce access | Longer or riskier service | Assembly/disassembly sequence review |
| Aesthetic symmetry overrides mechanical needs | Unnecessary complexity | Score function, reliability and serviceability separately from appearance |
| New architecture fragments existing C-01 work | Duplicate or inconsistent requirements | Maintain this as a parallel study and trace all baseline interfaces |

## 10. Evidence gates and next engineering sequence

**Gate SQ-0 — Requirements and scope**
- Confirm the C-01 functions and LUNAR boundary remain unchanged.
- Record the intended square/rounded-square design intent.
- Keep all round studies available as comparison references.

**Gate SQ-1 — Envelope and display feasibility**
- Establish candidate case/dial envelopes from explicit user-approved constraints.
- Place dial candidates A/B/C and square candidate D in comparable coordinate systems.
- Check aperture, hand-stack, crown, pusher and case-wall conflicts.

**Gate SQ-2 — Mechanical architecture feasibility**
- Create block layouts for SQ-A, SQ-B and SQ-C.
- Place barrel, rotor, balance, train, chronograph, calendar and supports using real or explicitly provisional component envelopes.
- Identify every transfer stage and interface.

**Gate SQ-3 — Kinematics and energy**
- Verify display ratios and counter behavior.
- Estimate and later measure added loads and energy demand.
- Compare chronograph stopped/running behavior and winding performance.

**Gate SQ-4 — Structure, assembly and service**
- Evaluate plate/bridge stiffness, shock paths, casing supports and service sequence.
- Review manufacturability and replaceable wear components.

**Gate SQ-5 — Design authority decision**
- Present evidence and trade-offs.
- Obtain explicit approval before selecting a square architecture or changing the C-01 baseline.

## 11. Open design-authority questions

1. Should the external form be a rounded-square with visibly softened corners, or a more rectilinear square?
2. Is the priority a square case with mechanically efficient internals, or a genuinely square-organized movement visible through the caseback?
3. Should dial candidate D be developed as the lead square display, or should A/B/C also be adapted to the square case for direct comparison?
4. What case size and wrist-presence envelope should be investigated? No value is assumed in this revision.
5. Should the square concept retain the same automatic-winding requirement, or should any winding alternatives be included strictly as a comparison?

These questions do not block the initial architecture comparison. They must be answered before detailed dimensional design.

## 12. Revision history

| Revision | Date | Change | Status |
|---|---|---|---|
| 0.1 | 2026-11-27 | Initial square architecture and dial concept study; three movement approaches and evidence gates established | Concept / review |

## 13. Current conclusion

A square STEWARD C-01 is mechanically plausible in principle, but its feasibility and quality depend on coordinated packaging and evidence—not on the external shape alone.

SQ-A, SQ-B and SQ-C remain open. Dial candidate D is conceptual. No case size, movement envelope, materials, geometry, component layout, performance or architecture has been approved. Existing round C-01 studies remain valid and unchanged.

**Next recommended work:** produce a comparative square packaging study with the same functional component set across SQ-A, SQ-B and SQ-C, then evaluate whether dial candidate D can be supported without compromising energy transmission, reliability or serviceability.
