# WP-53 — Chronograph Control Prototype First-Article Engineering Definition

- **Document ID:** SEB-C01-WP-53
- **Revision:** A — initial controlled issue
- **Status:** First-article definition framework; candidate articles and build package not released
- **Project:** STEWARD C-01
- **Repository:** `godsun108/turbo-foundry`
- **Branch:** `steward/c-01-movement-foundation`
- **Companion model:** `tools/c01_first_article.py`
- **Synthetic regression tests:** `tools/test_c01_first_article.py`
- **Predecessors:** WP-31 through WP-53; especially WP-33, WP-41, WP-46 through WP-52
- **Date:** 2026-11-27

## 1. Purpose and boundary

WP-53 defines the engineering data package required to create first-article chronograph-control development mechanisms for the STEWARD C-01 comparative program:

- **CW article:** column-wheel control mechanism.
- **CL article:** cam/lever control mechanism.

The objective is to establish two individually traceable, mechanically representative articles that can be mounted to a common qualified test fixture and evaluated under the WP-52 protocol. This document defines required records, interfaces, component families, drawing/BOM structure, inspection planning and release gates.

It is not a dimensioned design, final component specification, released BOM, manufacturing drawing package, assembly instruction, supplier selection, or authorization to build. It does not assert that either physical article exists.

No dimensions, coordinates, gear tooth counts, materials, heat treatments, finishes, lubricants, forces, spring rates, tolerances, acceptance limits, part numbers or supplier details are invented. Such values must be derived from approved requirements, calculations, source evidence and design review.

## 2. Design basis and configuration strategy

### 2.1 Candidate scope

WP-33 defines four possible integrated chronograph combinations:

| Candidate control | Vertical friction clutch | Horizontal/lateral coupling |
|---|---|---|
| Column wheel | A | C |
| Cam/lever | B | D |

WP-53's first-article comparison isolates the control architecture only if the rest of the mechanism can be held common or its differences are explicitly controlled. The clutch architecture remains a separate unresolved decision. The first article pair must therefore identify its clutch configuration and revision. If a common clutch cannot be used without distorting either candidate, the comparison must be treated as a comparison of complete configurations, with the clutch difference documented as a confounder or separate factor.

No candidate combination is selected here. CW and CL are not assumed to be mechanically interchangeable merely because their functional interfaces are named alike.

### 2.2 Configuration hierarchy

Each physical article shall have a controlled configuration tree:

1. C-01 requirements and interface baseline.
2. Chronograph system configuration.
3. Candidate control assembly configuration (CW or CL).
4. Clutch/coupling configuration.
5. Common drive-source and chronograph-output interface configuration.
6. Fixture/carrier interface configuration.
7. Component and subassembly revisions.
8. Assembly, inspection, lubrication and deviation records.

Every drawing, BOM row, inspection record, raw test run and dashboard record must resolve to a specific configuration revision. Uncontrolled handwritten changes or undocumented substitutions are prohibited.

### 2.3 Article classes

The first article is a controlled experimental mechanism, not a production-intent movement. Its article class and intended representativeness must be recorded.

The design authority must decide whether each article is:
- a mechanism-only bench demonstrator;
- a chronograph module with representative drive and output interfaces; or
- a movement-integrated article.

This scope choice affects what can be concluded from the WP-52 campaign. A mechanism-only bench article may characterize control behavior, but cannot alone establish integrated movement rate impact, full chronograph energy consumption, case/pusher ergonomics or production serviceability.

## 3. Functional requirements and component decomposition

The two articles shall implement the common functional sequence defined in WP-41:

**stopped at zero → start/running → stop/retained → resume/running → stop/retained → reset/stopped at zero.**

Reset while running must be physically prevented. The actual interlock design and proof remain open.

### 3.1 Common functional component families

The article definition shall identify the following functions, whether implemented as separate components or integrated geometry:

| Functional family | Required definition content |
|---|---|
| Drive-source interface | Source arbor/coupling definition, direction, speed and torque evidence, axial/radial datum references |
| Clutch/coupling | Selected candidate type, driving/driven members, engagement and disengagement interfaces, adjustment and inspection needs |
| Central chronograph seconds | Arbor, wheel/hand output, support interfaces and zero datum |
| Minute counter branch | Drive and indication interface; continuous/jumping status remains controlled open decision |
| Hour counter branch | Drive and indication interface; continuous/jumping status remains controlled open decision |
| Stopped retention | Brake/detent/equivalent function, holding interface, release sequence and inspection requirements |
| Control indexing | CW or CL candidate-specific members, input, state retention and output commands |
| Pusher/lever input | Input datum, contact interface, travel envelope, return path and case/fixture interface |
| Reset hammer system | Hammer(s), heart cam(s), contact sequence, return and zeroing interfaces |
| Running-reset interlock | Physical blocking/disengagement function, evidence requirements and post-test inspection |
| Structural support | Plate/carrier, bridges, bearing/support members, fasteners and datum scheme |
| Lubrication | Approved lubrication specification and application/inspection record; values TBD |

This table is a functional decomposition, not a statement that all functions require separate physical parts.

### 3.2 Candidate-specific definition

**CW article** must define, as applicable:
- column wheel body and indexing geometry;
- index/advance and state-retention members;
- control lever(s), pivots, springs and contact interfaces;
- clutch command interface;
- stopped-retention command interface;
- reset-hammer command and physical running-reset interlock;
- pusher input and return path.

**CL article** must define, as applicable:
- cam/control member(s) and working profiles;
- follower/lever members, pivots, springs and contact interfaces;
- state retention and transition sequence;
- clutch command interface;
- stopped-retention command interface;
- reset-hammer command and physical running-reset interlock;
- pusher input and return path.

The exact number of parts, profiles, pivot locations and spring arrangements are design outputs, not assumptions in this document.

## 4. Common interface-control definition

The common fixture strategy in WP-47 uses a shared structural base and interchangeable candidate carriers. WP-53 establishes the article-side interface-control data required to make that strategy measurable.

For every interface, record:
- unique interface ID and function;
- article side and fixture side references;
- datum scheme and coordinate convention;
- nominal geometry only when approved source data exist;
- allowable variation only when approved requirements exist;
- contact type and direction of applied load;
- measurement method and uncertainty requirement;
- installation/removal sequence and access envelope;
- revision, source evidence and approving authority.

### 4.1 Required functional interfaces

The interface register shall cover at least:
- pusher input;
- control state indexing;
- clutch command;
- stopped-retention command;
- reset-hammer command;
- running-reset interlock;
- return/reset;
- drive-source input;
- central seconds output;
- counter branch outputs;
- structural support and mounting;
- fixture carrier and instrument access.

The companion validator enforces the seven core control functions. The remaining interfaces must be included in the controlled project interface register even if not all are required by the software's minimum completeness check.

### 4.2 Common datum and fixture handoff

Movement datum M0 and fixture datums A/B/C are distinct systems. The drawing package shall define a traceable transformation between them; it must not imply that a fixture datum is a movement datum.

The article drawing shall show:
- datum feature identification;
- mounting and locating features;
- pusher input axis and contact point;
- sensor/optical observation access;
- guard and actuator clearance envelope;
- removal and installation direction;
- any interface features whose geometry is still TBD.

No common bolt pattern, hole spacing, center height or envelope is assigned until the fixture and article geometry are jointly reviewed.

### 4.3 Interchangeability criteria

Interchangeability is demonstrated, not declared. Before claiming that CW and CL carriers are interchangeable, establish:
- same qualified fixture reference configuration;
- controlled locating and clamping method;
- repeatable datum transfer;
- pusher actuator alignment and sensor reference;
- no unapproved carrier-specific compliance or stiffness effect;
- repeat installation measurement and uncertainty;
- documented fit and clearance inspection.

If candidate-specific adapters are required, treat them as controlled configuration items and quantify their measurement influence.

## 5. First-article bill of materials structure

Each candidate requires its own BOM with a common top-level schema. BOM records shall include:
- item ID and parent assembly;
- part/document number and revision;
- description and functional role;
- quantity and unit;
- make/buy/existing-controlled/TBD status;
- configuration status;
- material/process specification reference where applicable;
- drawing/specification reference;
- supplier and lot/serial traceability when applicable;
- source evidence and approval record;
- criticality and inspection requirement;
- approved substitution/deviation status.

Use explicit TBD rows for unresolved items; do not silently omit them. A placeholder is not a procurement instruction.

Suggested hierarchy (actual IDs and quantities remain TBD):

| Assembly level | Content |
|---|---|
| Candidate top assembly | CW first article or CL first article |
| Control subassembly | Candidate-specific indexing/control members |
| Input subassembly | Pusher interface, levers and return members |
| Clutch/command subassembly | Approved clutch/coupling and command members |
| Retention subassembly | Stopped-state retention components |
| Reset subassembly | Hammer, heart-cam and interlock components |
| Output subassembly | Central seconds and counter output interfaces |
| Support subassembly | Plate/carrier, bridges, pivots and bearing supports |
| Fasteners and retention | Controlled fasteners, pins and retention features |
| Consumables/process | Approved lubricants, cleaning and assembly process records |

The BOM must distinguish prototype-only tooling/fixture parts from movement mechanism parts. It must also distinguish bought-out standard components from custom parts and unqualified candidate parts.

## 6. Drawing and technical-data package

Each candidate's drawing register shall identify at least the following document types where applicable:

1. General arrangement / top-level assembly.
2. Exploded assembly and parts identification.
3. Candidate-specific control mechanism assembly.
4. Component drawings for all custom mechanism parts.
5. Interface-control drawing(s) to WP-47 fixture and C-01 drive/output interfaces.
6. Datum and coordinate definition.
7. Inspection drawing or characteristic map.
8. Special process/material/lubrication specification references.
9. Assembly and disassembly instructions.
10. Configuration and deviation record.

A drawing shall not be marked approved unless its review and approval record are linked. CAD envelope previews from prior work packages are not production drawings and do not establish physical geometry.

### 6.1 Drawing content requirements

As applicable to the part, drawings must specify:
- units and projection convention;
- drawing scale and views/sections;
- datum reference frame;
- dimensions and geometric controls;
- surface/edge requirements;
- material and condition;
- heat treatment/coating/finish;
- manufacturing process constraints;
- inspection characteristics and method references;
- revision history and approvals.

All numerical design requirements must have an approved source. Tolerances shall be derived from function, manufacturing capability, assembly stack and metrology plan, not inserted as generic values.

## 7. Inspection and acceptance plan

Inspection shall be defined before manufacture and shall be traceable to the approved drawing, requirement or interface control record.

The characteristic register shall include:
- characteristic ID and drawing feature reference;
- measurand and unit;
- method/procedure reference;
- instrument capability and calibration requirement;
- uncertainty/guard-band method;
- approved acceptance requirement reference;
- data-record template;
- source evidence and revision.

Potential inspection domains include:
- identity and revision verification;
- material/process certificates where required;
- critical dimensions and geometric relationships;
- pivot/arbor/support fit and freedom of movement;
- control member engagement and state position;
- clutch and retention engagement/disengagement;
- reset hammer/heart-cam contact and zero datum;
- pusher input alignment and return;
- running-reset interlock geometry and physical function;
- fixture mounting and sensor access;
- visual condition, burrs, contamination and damage.

No numerical acceptance limit is assigned by WP-53. Acceptance criteria must be sourced from approved design requirements or an approved inspection plan. The companion validator rejects invented numeric limits in its generic inspection-plan records and requires a controlled acceptance reference.

Inspection results must record actual values, units, instrument, calibration, uncertainty, inspector, date, article/configuration revision, disposition and linked raw evidence. A structurally complete inspection plan does not imply an inspection pass.

## 8. Assembly, lubrication and configuration control

Before assembly, approve controlled work instructions covering:
- component identity and revision verification;
- cleanliness and contamination control;
- assembly order and required tools;
- handling and protection of pivots, teeth, springs and contact surfaces;
- lubrication specification and application method;
- adjustment and setup procedures;
- in-process inspection and hold points;
- functional checks;
- final inspection and sign-off;
- disassembly, repair and rework controls.

Do not prescribe lubricant type, quantity, application point, spring preload or adjustment until the material pair, contact regime, geometry and supplier/process evidence are established.

Every physical article shall have a build record linking actual component serial/lot identity to BOM revision, operator, date, process instruction, inspection results, lubrication record and deviations.

Any component substitution or rework requires review of affected interfaces, balance/energy behavior, test comparability and configuration revision.

## 9. Risk and failure controls

The article design review shall address at minimum:
- unintended reset while running;
- missed/double state indexing;
- partial engagement or ambiguous intermediate state;
- pusher overtravel or high actuation force;
- clutch drag or unintended chronograph motion;
- stopped-retention loss;
- reset hammer bounce or incomplete zeroing;
- spring/lever release or fracture;
- pivot/bearing seizure or excessive friction;
- gear/cam/lever interference;
- loose fasteners or component migration;
- fixture/carrier displacement;
- instrument contact or sensor misalignment;
- lubrication migration/contamination;
- damage during endurance or repeated test cycles.

For each risk, record cause, effect, severity/likelihood basis, detection/mitigation, owner, verification method and residual-risk approval. WP-53 does not assign risk scores or claim any hazard has been mitigated.

## 10. First-article build and test-release gates

### Gate 0 — definition authorization
- requirements and candidate scope approved;
- CW/CL article classes declared;
- common interfaces and known differences identified;
- open decisions and risk register reviewed.

### Gate 1 — design package review
- candidate assembly and component drawing registers complete;
- BOMs traceable and revision-controlled;
- interface-control documents reviewed;
- all design values linked to approved evidence;
- independent design review complete.

### Gate 2 — manufacturing readiness
- make/buy decisions and supplier/material/process qualification complete as applicable;
- work instructions and lubrication specification approved;
- manufacturing capability and inspection methods established;
- tooling/fixture readiness reviewed.

### Gate 3 — article acceptance
- actual build records complete;
- incoming/in-process/final inspection passed against approved criteria;
- deviations dispositioned;
- configuration audit and independent review signed.

### Gate 4 — WP-52 test release
- article configuration matches the approved campaign definition;
- WP-47/48 fixture and metrology qualification current;
- WP-49 instrument/calibration/data acquisition setup approved;
- WP-52 sample plans, procedures, order schedule and safety approvals approved;
- test-specific physical interlock procedure authorized separately.

No gate is passed by the companion software. First-article manufacture and physical testing require separate human approvals and any applicable safety controls.

## 11. Companion software and verification

`tools/c01_first_article.py` validates record completeness for:
- CW/CL article definitions and distinct identities;
- common requirements/interface/fixture baselines;
- BOM row identity, quantities and controlled status;
- drawing register uniqueness and approval references;
- common interface register coverage and revision consistency;
- inspection characteristic traceability;
- first-article packet completeness.

Run synthetic regression tests from the tools directory:

```sh
python -m unittest test_c01_first_article.py
```

Test fixtures are synthetic. They are not design values, manufacturing instructions, inspection results or evidence of physical articles. The software does not calculate dimensions, tolerances, stress, gear geometry, spring behavior, lubrication, manufacturing process capability or physical fit. It does not approve drawings, authorize manufacturing, pass inspection or release WP-52 tests.

## 12. Open engineering inputs

The following inputs remain necessary before the first articles can be defined for build:

- selected prototype article class and intended representativeness;
- approved control mechanism geometry for CW and CL;
- clutch/coupling architecture and commonality decision;
- source arbor and drive interface definition;
- stopped-retention mechanism;
- reset hammer/heart-cam arrangement;
- physical running-reset interlock geometry;
- counter indication and drive arrangement;
- movement and fixture coordinate transformation;
- component dimensions, materials, processes and tolerances;
- approved lubrication and assembly instructions;
- fixture carrier and actuator interface geometry;
- inspection methods and numerical acceptance criteria;
- suppliers, make/buy status and qualification evidence where applicable;
- safety/risk review and independent design approval.

## 13. Revision control

| Revision | Date | Change | Approval |
|---|---|---|---|
| A | 2026-11-27 | Initial first-article engineering definition framework for CW and CL control prototypes | Pending engineering review |

**Release statement:** WP-53 defines the information required to engineer and control the first CW and CL prototype articles. It does not claim either design is complete, a physical article exists, a BOM or drawing package is released, manufacturing is authorized, inspection has passed, or the WP-52 experimental campaign is approved.
