# WP-32 — C-01 Design Freeze and Prototype Configuration Baseline

- Document ID: SEB-C01-WP-32
- Revision: A — initial controlled issue
- Status: Design-freeze framework; C-01 is not frozen
- Branch: steward/c-01-movement-foundation
- Software: tools/c01_design_freeze.py
- Verification: tools/test_c01_design_freeze.py
- Dependencies: WP-13 through WP-31

## 1. Purpose and authority

WP-32 defines the controlled process for establishing the first STEWARD C-01 prototype configuration and deciding when the design is mature enough for a formal design freeze review.

This document does not itself freeze C-01. Existing engineering records identify unresolved decisions and incomplete geometry, material, tolerance and verification evidence. No component is promoted to released status by this work package.

A design freeze is a configuration-control decision by an authorized human design authority after multidisciplinary review. The software in this package validates record structure and gates only; it cannot judge engineering adequacy or grant authority.

## 2. Configuration levels

- Functional baseline: approved user-visible functions and measurable requirements.
- Architecture baseline: approved mechanism alternatives, subsystem boundaries and interfaces.
- Prototype configuration baseline: exact component, drawing, material, process and software revisions for one named article.
- As-built baseline: actual serial/lot-level components, deviations and inspection results installed in the physical article.

Each baseline has its own identifier and approval record. A prototype article may contain explicitly approved development parts, but those parts must be traceable and their limitations recorded. A candidate or selected component is not automatically released.

## 3. Existing design intent and unresolved decisions

The current functional intent carries automatic mechanical winding, timekeeping, running seconds, central chronograph seconds, elapsed minute/hour counters, weekday and date. The preliminary rate target is 4 Hz / 28,800 vph. The 60–70 hour reserve remains an aspiration, not a demonstrated requirement.

The following remain decision-controlled and block a full design freeze until resolved or explicitly excluded by an approved scope decision:

| Decision | Current evidence state | Required disposition |
|---|---|---|
| Dial arrangement A/B/C | Alternatives retained | Select with dial/package evidence |
| Vertical vs horizontal/lateral chronograph clutch | WP-16 trade study, no winner | Approved weighted decision and prototype evidence plan |
| Column wheel vs cam/lever control | WP-16 trade study, no winner | Approved weighted decision |
| Continuous vs jumping totalizers | Open | Requirement, load and packaging decision |
| Month window | User preference; WP-20 and WP-31 keep scope open | Explicit C-01 inclusion or separate LUNAR allocation |
| Going-train and chronograph tooth schedule | No C-01 schedule | Kinematic closure and geometry review |
| Movement envelope, axes, plate/bridge geometry | Parametric frameworks only | Dimensioned and tolerance-controlled baseline |
| Materials, heat treatments, coatings, lubricants | Not selected/qualified | Evidence-based engineering approval |
| Case and dial interfaces | Not dimensioned | Controlled interface definition |
| Performance acceptance limits | Not fully approved | Requirement and WP-30 procedure approval |

A scope exclusion is a formal decision, not an assumption. In particular, this package does not decide the month-window question on the user's behalf.

## 4. Required baseline records

### 4.1 Requirements baseline

Every requirement shall have a unique ID, source, rationale, measurable statement, units, operating conditions, verification method, priority, owner and approval status. Aspirations must be distinguished from requirements. A target without a defined measurement method and acceptance rule is not a verified requirement.

Requirements that affect chronograph start/stop/reset, hand alignment, counter behavior, calendar rollover, winding, reserve, rate or serviceability must trace to WP-30 verification procedures.

### 4.2 Decision register

Every architecture or scope decision shall record:
- unique decision ID and title;
- alternatives considered and option definitions;
- evaluation criteria and approved weights where trade scoring is used;
- evidence source and revision;
- selected option or explicit defer/exclusion;
- rationale and residual risks;
- affected requirements, models, drawings and tests;
- decision owner, approving authority, date and record ID.

An approved decision requires complete evidence and a traceable approval record. A tool-generated ranking is advisory; it is not a decision.

### 4.3 Prototype configuration baseline

For each prototype article, record:
- prototype ID and article class (P0, P1, P2 or production-intent);
- movement and configuration revision;
- requirements and architecture baseline IDs;
- BOM and drawing register revisions;
- material and supplier qualification revisions;
- software/calculation model versions used to define or verify the configuration;
- each component ID, installed part revision, source record and status;
- approved deviations and nonconformance dispositions;
- configuration owner and approval record.

The baseline must distinguish released parts from development parts. Any development part must have a controlled definition, inspection plan, known limitations and approval for the specific prototype scope.

### 4.4 Interface baseline

Each mechanical, kinematic, energy, electrical-if-any, dial, case and service interface shall identify its source and destination, type, definition revision, governing dimensions or behavior, tolerance/allowance where applicable, verification reference, evidence status and owner. Candidate interfaces remain candidate until reviewed and released.

Energy interfaces must state measurement plane, direction, units, operating state and measurement boundary. Geometry interfaces must identify datum references and coordinate conventions. Interfaces cannot be released on descriptive prose alone when dimensional or behavioral definition is required.

## 5. Design-freeze review gates

The following gates are conjunctive; unresolved gates remain visible and block a freeze recommendation.

1. Requirements baseline approved, measurable and traceable.
2. Architecture baseline approved; major mechanism alternatives resolved.
3. All required scope and architecture decisions approved, including explicit month-window disposition.
4. Prototype configuration baseline complete and internally consistent.
5. Interfaces released with dimensional/kinematic/energy definitions appropriate to the interface.
6. Geometry, tolerance stack, dynamic envelopes, assembly access and service access reviewed.
7. Energy and load interfaces reconciled across going train, chronograph, calendar and winding; no unsupported reserve claim.
8. WP-30 verification plan, procedures, limits, instrumentation and uncertainty approach approved.
9. WP-31 manufacturing review complete for the exact prototype scope.
10. Risks, hazards, deviations and open nonconformances dispositioned with owners.
11. Independent design, manufacturing and quality review complete.
12. Design authority approval record issued with scope, revision, date and conditions.

A freeze may be limited to a subsystem or prototype stage if the authority explicitly defines the boundary and prevents downstream use of unfrozen interfaces. A partial freeze must not be represented as a complete movement freeze.

## 6. Change control after freeze

After approval, any change to requirements, component geometry, material, process, supplier, lubrication, tolerance, software model, interface or test method must enter formal change control.

Impact analysis shall identify:
- affected requirement IDs and verification results;
- affected components, drawings, BOM rows and prototype serials;
- stack-up, gear-mesh, clearance and dynamic implications;
- energy, rate, amplitude and chronograph interaction implications;
- supplier/process and inspection implications;
- service documentation and spare-part implications;
- whether re-verification or a new prototype revision is required.

No change may be silently incorporated into an existing baseline. Approved changes create a new revision and preserve the prior baseline.

## 7. Calculations and executable controls

The software does not calculate mechanical performance. It validates:
- unique decision IDs and complete approval evidence;
- evidence completeness for approved decisions;
- unique configuration component IDs and permitted status values;
- released component state for an approved configuration;
- interface identity, endpoints, release state and evidence completeness;
- fail-closed design-freeze gate completeness.

No design values, dimensions, tolerances, tooth counts, materials, supplier data or measured performance values are created by this package.

Run the synthetic software tests from the tools directory:

    python -m unittest test_c01_design_freeze.py

These tests verify register integrity and gate behavior only. They do not establish that the engineering evidence is sufficient or that C-01 is frozen.

## 8. Acceptance criteria

WP32-AC-01: Every required decision has a unique ID, owner, scope, evidence state and disposition.
WP32-AC-02: An approved decision has a selected option or explicit scope disposition, rationale, complete evidence and approval record.
WP32-AC-03: A prototype baseline identifies exact revisions and source records for every installed component.
WP32-AC-04: An approved configuration contains only released or explicitly justified not-applicable component statuses.
WP32-AC-05: Every released interface has complete evidence and a verification reference.
WP32-AC-06: All design-freeze gates are explicitly true and linked to approved records.
WP32-AC-07: Independent review and design-authority approval are recorded.
WP32-AC-08: Software evaluation never declares the movement frozen or authorizes manufacture by itself.

## 9. Revision control

Revision A is the initial framework issue. Changes shall preserve decision history, prior configuration baselines and as-built article records. Superseded baselines remain retrievable and are clearly marked. A freeze applies only to its named revision and scope.

## 10. Recommended next engineering sequence

1. Resolve the user-facing dial and month-window scope decisions.
2. Complete WP-16 weighted chronograph trade study using approved criteria and actual packaging/energy evidence.
3. Confirm counter indication behavior.
4. Close going-train and chronograph kinematic paths and create a candidate tooth schedule only from approved constraints.
5. Develop dimensioned plate, bridge, arbor, bearing and case-interface geometry.
6. Establish tolerance stack and inspection strategy.
7. Select and qualify materials/processes and prototype suppliers.
8. Complete WP-30 test procedures and WP-31 manufacturing packet for the chosen P0 configuration.
9. Conduct independent review and submit a defined freeze packet to the design authority.

**Disposition:** WP-32 establishes how C-01 will be frozen and how its prototype configuration will be controlled. The movement remains unfrozen; no manufacturing authorization, architecture selection or performance certification is issued.
