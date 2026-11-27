# WP-31 — C-01 Prototype Definition and Manufacturing Readiness

- **Document ID:** SEB-C01-WP-31
- **Revision:** A — initial controlled issue
- **Status:** Manufacturing-readiness framework; prototype definition incomplete; not a production release
- **Branch:** `steward/c-01-movement-foundation`
- **Software:** `tools/c01_manufacturing_readiness.py`
- **Verification:** `tools/test_c01_manufacturing_readiness.py`
- **Dependencies:** WP-13, WP-14, WP-16, WP-20 through WP-24, WP-26 through WP-30

## 1. Purpose and boundary

WP-31 establishes the controlled records needed to define, source, assemble, inspect and disposition a first STEWARD C-01 prototype. It turns the preceding engineering studies into a manufacturing-readiness workflow without pretending that unresolved design inputs are known.

This issue is a **framework and prototype definition pack**, not a released bill of materials, a set of production drawings, a supplier selection, a validated lubrication schedule or authorization to manufacture. Every design-dependent field remains open until supported by an approved upstream engineering record.

The first prototype should be treated as an engineering development article. Its objective is to expose fit, function, energy, chronograph interaction, calendar behavior, serviceability and manufacturing risks under controlled test conditions. It is not automatically representative of a production-intent movement.

## 2. Configuration baseline and unresolved decisions

The current functional intent includes automatic mechanical winding, timekeeping, running seconds, central chronograph seconds, elapsed minute/hour counters, weekday and date. The preliminary frequency target is 4 Hz / 28,800 vph. The 60–70 hour reserve is an aspiration, not an accepted or demonstrated performance value.

The following decisions remain open and shall not be silently converted into manufacturing requirements:

| Decision | Current control |
|---|---|
| Dial/display arrangement A, B or C | Preserve alternatives pending approved selection |
| Chronograph clutch: vertical or horizontal/lateral | WP-16 trade study; no winner selected |
| Chronograph control: column wheel or cam/lever | WP-16 trade study; no winner selected |
| Counter indication: continuous or jumping | Requires explicit decision and load/energy evidence |
| Month window | User preference; C-01 versus separate LUNAR scope decision remains open |
| Gear tooth counts, modules and center distances | No C-01 schedule released |
| Plate, bridge, arbor and bearing geometry | No physical geometry baseline released |
| Materials, heat treatments, coatings and lubricants | No selections or qualified process records released |
| Case envelope, dimensions and tolerances | Not established by this work package |

The requirements baseline and architecture baseline must be formally approved before any drawing or part can be marked released.

## 3. Prototype article strategy

Use a staged build strategy with explicit configuration identity:

1. **P0 — Engineering fit and mechanism article:** verify critical interfaces, gear engagement, arbor support, chronograph sequencing, calendar clearances and assembly access. Parts may be development-grade and individually traceable. No performance claim.
2. **P1 — Integrated functional prototype:** incorporate P0 dispositions and approved component revisions; conduct WP-30 procedures for timekeeping, winding, chronograph, calendar and energy behavior.
3. **P2 — Design-validation article:** only after P1 findings are closed or formally dispositioned; use controlled material/process routes and representative components where justified.
4. **Production-intent definition:** separate approval gate after design validation, supplier/process qualification, repeatability evidence and service documentation.

These are proposed article classes, not a commitment to build all stages or an assertion that any stage exists.

## 4. Controlled deliverable register

### 4.1 Prototype bill of materials (BOM)

Each BOM row shall include:
- unique item ID and part name;
- functional description and quantity per movement;
- unit of measure and assembly parent;
- drawing/specification ID and revision;
- configuration status (candidate, selected, released, superseded);
- material and condition status;
- supplier/source and qualification status;
- make/buy and process route when known;
- criticality, traceability and inspection class;
- evidence status and approved change/release records.

The software validates core identity and status fields. It deliberately does not create C-01 part rows, quantities beyond a controlled placeholder, materials, vendors or costs. A released row requires its approval evidence; material/supplier approval requires separate qualification records.

### 4.2 Drawing and specification register

Drawing families to be developed after geometry freeze:
- movement assembly and interface-control drawing;
- main plate and bridge detail drawings;
- arbor/pivot and bearing/jewel detail drawings;
- gear and pinion drawings;
- barrel, mainspring and bridle drawings;
- automatic winding and reversing works;
- chronograph clutch, control, hammer and counter components;
- calendar works and dial-side components;
- hands, dial interfaces and case interfaces;
- inspection drawings and critical-characteristic maps.

Each drawing must identify units, datum scheme, source geometry revision, projection/scale as applicable, material/condition, surface/edge requirements, geometric dimensioning and tolerancing where justified, critical characteristics, inspection method, revision and approval record. Do not assign numerical dimensions or tolerances until the responsible designer has released the underlying geometry and tolerance analysis.

A drawing is not manufacturing-ready merely because it renders or has dimensions. It requires design review, manufacturability review, inspection-method review and configuration approval.

### 4.3 Supplier qualification

Qualification is scoped to a specific part family and process, not a supplier name in isolation. Evidence should address:
- process capability and relevant equipment;
- quality management and document control;
- material and lot traceability;
- calibration and measurement systems;
- special processes and subcontractor controls;
- nonconformance, corrective action and change notification;
- sample/first-article inspection capability;
- confidentiality, data ownership and retention as contractually required.

A candidate supplier is not a qualified supplier. A quotation, catalogue listing or verbal capability statement is not qualification evidence. Supplier approval requires a documented assessment and approved scope.

### 4.4 Material and process qualification

For each selected material/process combination, retain the exact designation/specification revision, source, certificate or test evidence, condition/heat treatment, relevant properties, process compatibility, inspection method and approval record.

Evaluate material and process interactions where relevant: hardness and wear, corrosion, magnetic behavior, thermal stability, dimensional stability, surface finish, friction, lubricant compatibility, fatigue and manufacturability. These are review topics, not claims that any material has been selected or tested.

### 4.5 Assembly and adjustment work instructions

Separate instructions should cover:
- incoming inspection and part cleaning/handling;
- plate and bearing preparation;
- going-train assembly and endshake/side-shake measurement;
- escapement and balance installation/adjustment;
- barrel and mainspring installation;
- automatic winding and bridle installation;
- chronograph assembly, engagement and reset adjustment;
- calendar assembly, weekday/date setting and correction safeguards;
- hand/dial installation and case interface;
- final functional inspection and data capture.

Every instruction must specify applicable part revisions, approved tools/fixtures, prerequisites, ordered steps, critical controls, inspection points, safety/stop conditions, allowed adjustment range by reference to an approved specification, records to retain and rework disposition. No adjustment values are invented in this package.

### 4.6 Lubrication instruction

Lubrication is a controlled engineering process, not a generic list of oils. The eventual instruction must identify each lubrication point by drawing/BOM reference, approved lubricant designation and supplier, application method, quantity or controlled application criterion, surface preparation, contamination controls, shelf-life/lot traceability, inspection and re-lubrication/service rules.

Lubricant selection and quantities remain open pending material, contact, speed, load, temperature, wear and supplier compatibility evidence. Do not substitute lubricant brands or mix products without engineering approval.

### 4.7 Inspection and acceptance records

The inspection plan shall identify:
- characteristic/requirement ID and source revision;
- measurement method, instrument and calibration status;
- sampling plan and measurement uncertainty;
- acceptance rule and responsible inspector;
- actual result, units, source record and disposition;
- nonconformance/deviation reference where applicable.

First-article inspection should cover every drawing characteristic designated critical or key, plus all interfaces whose failure can damage the movement or invalidate functional tests. The actual sampling strategy and numerical acceptance limits require approved drawings and requirements; WP-30 governs the test evidence and uncertainty framework.

## 5. Manufacturing-readiness calculations and controls

This work package does not calculate gear geometry or mechanical performance. Those remain in WP-18 through WP-29 and must use approved design inputs.

The present software provides record-integrity checks:
- unique BOM item and drawing IDs;
- allowed configuration and qualification states;
- evidence required before a row is marked released/approved;
- supplier/material approval records and scope;
- ordered work-instruction steps and approval status;
- fail-closed prototype documentation gate.

No numerical manufacturing tolerance, process capability index, yield, cost, lead time, supplier capacity or production rate is assumed. Such quantities require actual supplier and inspection data.

## 6. Prototype assembly sequence — planning level only

The sequence below is a planning skeleton. The detailed order may change after access, interference, lubrication and serviceability reviews.

1. Verify current released configuration, part identity and incoming inspection status.
2. Confirm clean work area, controlled handling, approved tools and calibration status.
3. Prepare plate, bearing locations and structural members per released drawings.
4. Install and inspect going-train arbors and gears; record mesh and endshake/side-shake measurements.
5. Install barrel and winding components; verify free movement and approved bridle behavior.
6. Install escapement and balance; perform specified static and dynamic checks.
7. Assemble chronograph drive, clutch, control, counters and reset system; verify start/stop/reset interlocks.
8. Assemble calendar and dial-side works; verify weekday/date advancement and safe correction.
9. Apply approved lubrication per controlled instruction; record lubricant lot and operator.
10. Complete dial/hand/case-interface work as applicable to the article.
11. Perform independent final inspection and configuration audit.
12. Transfer the article to WP-30 verification only after required build records and safety checks are accepted.

No step authorizes forcing, filing, polishing, bending, staking, reaming or other irreversible rework without an approved operation and disposition.

## 7. Required manufacturing and quality records

| Record | Minimum contents | Owner / approval |
|---|---|---|
| BOM baseline | Item, quantity, revision, material, source, status | Design / configuration control |
| Drawing register | Drawing revision, datums, geometry source, review | Design / manufacturing / inspection |
| Supplier qualification | Scope, audit/capability, traceability, approval | Supply quality / engineering |
| Material qualification | Specification, condition, certificates/tests, scope | Materials engineering / quality |
| Work instructions | Steps, tools, controls, checks, safety, revision | Manufacturing engineering / quality |
| Lubrication instruction | Point map, product, method, controls, lots | Design authority / quality |
| First-article report | Actual measurements, instruments, uncertainty, disposition | Inspection / design |
| Assembly traveler | Serial/lot traceability, operator, steps, deviations | Manufacturing |
| Nonconformance report | Requirement, evidence, containment, root cause, disposition | Quality / design authority |
| Deviation/waiver | Scope, risk, expiry, compensating controls, approval | Design authority / quality |
| Final acceptance record | Configuration, tests, open items, signatures | Independent quality / engineering |

## 8. Acceptance criteria and release gates

A prototype documentation packet is ready for formal review only when:
1. Requirements and architecture baselines are approved and mutually consistent.
2. Every BOM item is traceable to a released drawing/specification or an explicitly controlled development-part definition.
3. Drawings have approved geometry, datums, tolerances and inspection methods appropriate to their intended use.
4. Material and supplier qualification evidence is complete for the proposed article scope.
5. Assembly and lubrication instructions are approved and identify applicable revisions.
6. Inspection plan, instrument register and uncertainty budgets are approved.
7. Risks have owners and dispositions; open hazards and nonconformances are visible.
8. Deviations are approved, bounded, traceable and time-limited where appropriate.
9. WP-30 verification procedures and acceptance criteria are approved for the article.
10. Independent design/manufacturing/quality review is complete and recorded.

The software's release evaluator checks only that the named records and boolean gates are present. It cannot establish that the evidence is technically adequate. Even a complete packet is not self-authorizing: the responsible engineering, quality and safety authorities must explicitly approve the build.

## 9. Risks and hold points

| Risk | Consequence | Required control / hold point |
|---|---|---|
| Geometry not frozen | Unbuildable or conflicting parts | No detail drawing release before geometry baseline |
| Unresolved chrono architecture | Rework across plates, bridges and drive train | WP-16 selection and interface review |
| Month window scope unresolved | Calendar packaging churn | Explicit C-01/LUNAR decision before calendar release |
| Unqualified material/process | Wear, distortion, corrosion or failure | Material/process qualification before production-intent parts |
| Supplier capability assumed | Nonconforming or untraceable parts | Scope-specific supplier qualification |
| Lubricant selected generically | Excess friction, migration, wear or instability | Contact-specific lubrication approval |
| Uncontrolled hand fitting | Irreproducible geometry and loss of traceability | Approved rework instructions and before/after records |
| Inadequate measurement capability | False acceptance or rejection | WP-30 uncertainty and instrument readiness gate |
| Configuration drift | Invalid test results and mixed revisions | Serial/lot-level configuration audit |

## 10. Revision control and change management

This is Revision A, initial controlled issue. Proposed changes shall identify affected BOM items, drawings, software validators, work instructions, verification procedures, risks and already-built prototype serials. Changes affecting interfaces, energy loads, chronograph behavior, calendar scope, materials or dimensions require impact review against the relevant earlier work packages.

No released item may be silently overwritten. Superseded revisions remain retrievable and must be segregated from current build stock. Deviations apply only to their stated article, quantity, scope and duration.

## 11. Software validation

Run from the tools directory:

```bash
python -m unittest test_c01_manufacturing_readiness.py
```

Tests use synthetic records and deliberately incomplete placeholder data. They verify register validation and fail-closed behavior only; they are not evidence of physical C-01 manufacturability or test performance.

## 12. Open actions for the next engineering issue

1. Resolve the C-01 display arrangement and month-window scope.
2. Complete WP-16 chronograph architecture selection with explicit weighted criteria and approved evidence.
3. Freeze the functional and spatial interfaces from WP-20 through WP-26.
4. Produce the first approved geometry baseline and tolerance strategy.
5. Populate a real BOM from the released architecture, not from assumed watch-industry part counts.
6. Identify candidate manufacturing processes and qualify suppliers against the actual part scope.
7. Author detailed assembly, lubrication and inspection procedures from approved drawings and supplier data.
8. Approve WP-30 test procedures and measurement capability before prototype acceptance.

**Disposition:** WP-31 establishes the controlled path from engineering definition to a prototype build packet. C-01 remains in engineering development; no manufacturing release, physical build, supplier award or performance certification is issued by this document.
