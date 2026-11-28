# WP-57 — Integrated Chronograph Control Prototype Engineering Package

- **Document ID:** SEB-C01-WP-57
- **Revision:** A — initial controlled issue
- **Status:** Integrated prototype package framework; candidate packages not released
- **Branch:** \`steward/c-01-movement-foundation\`
- **Software:** \`tools/c01_integrated_prototype_package.py\`
- **Verification:** \`tools/test_c01_integrated_prototype_package.py\`
- **Dependencies:** WP-31, WP-33, WP-35 through WP-41, WP-46 through WP-56

## 1. Purpose and release boundary

WP-57 consolidates the engineering definition for two separate chronograph-control development articles:
- **CW:** column-wheel control prototype package.
- **CL:** cam/lever control prototype package.

Each package must contain a traceable component register, BOM, functional interface register, drawing register, assembly sequence, inspection characteristics, verification plan, and release-gate disposition. Both packages share a controlled requirements revision, interface baseline, fixture revision and test-protocol revision to support a fair future comparison.

This is a package-definition and completeness framework. It is not a dimensioned design, released BOM, manufacturing drawing set, approved work instruction, physical article, or authorization to build or test. The model cannot establish geometry correctness, physical fit, strength, safety, wear life, or compliance with acceptance limits.

## 2. Candidate architecture boundary

The packages preserve separate candidate identities and the WP-33 combinations:

| Combination | Clutch | Control |
|---|---|---|
| A | Vertical friction clutch | Column wheel |
| B | Vertical friction clutch | Cam/lever |
| C | Horizontal/lateral coupling | Column wheel |
| D | Horizontal/lateral coupling | Cam/lever |

WP-57 defines the control prototype package and its interfaces. It does not select a clutch, control architecture, or integrated combination. Each control candidate requires a separate clutch compatibility review.

## 3. Package architecture

Each candidate package shall include:

1. Candidate configuration and article identity.
2. Functional component register.
3. Candidate BOM and configuration status.
4. Functional interface-control register.
5. Assembly and component drawing register.
6. Assembly and lubrication work-instruction sequence.
7. Inspection and metrology characteristic plan.
8. Verification and test-procedure matrix.
9. Evidence index and source revision traceability.
10. Candidate-specific release-gate disposition.

The CW and CL packages remain separate configuration items. Shared interfaces and test conditions are controlled once at the common baseline, then referenced by each candidate package. Candidate-specific geometry, component records, and measurements must never be silently pooled.

## 4. Component register

### 4.1 Shared functional roles

Each candidate package must define, at minimum:
- pusher input member;
- control state indexing or state-control member;
- clutch command interface;
- stopped-train retention command;
- reset hammer;
- heart cam;
- running-reset interlock;
- return element;
- structural support members.

These roles are functional placeholders until approved geometry and detailed part definitions exist.

### 4.2 Column-wheel candidate-specific roles

The CW package must separately identify:
- column-wheel body/indexing member;
- indexing columns and their working surfaces;
- indexer or operating finger;
- jumper and state-retention interface;
- pivot, bore and support interfaces.

The register must identify which physical component performs each role; a role label alone does not define the geometry.

### 4.3 Cam/lever candidate-specific roles

The CL package must separately identify:
- cam body/profile;
- follower;
- operating lever(s);
- detent or state-retention element;
- pivot and support interfaces;
- return element and spring interfaces.

Cam/follower geometry and lever motion laws remain TBD pending approved design inputs and WP-55 evidence.

## 5. Bill of materials and configuration control

Every BOM row requires a unique item ID, component mapping, description, quantity, unit, part/document reference, revision, make/buy status, configuration status and source evidence ID.

Permitted planning statuses distinguish TBD placeholders, candidate definitions, reviewed items and approved items. A placeholder is not a purchasable specification. No part numbers, suppliers, costs, quantities beyond explicitly approved BOM data, materials, finishes, heat treatments, lubricants or dimensions are invented in this package.

BOM rows must reconcile to the component register. Subassemblies, fasteners, springs, jewels, pins, washers and other detail items must be added when the actual design establishes their need; the framework does not imply their final count or specification.

## 6. Interface control

Each interface record identifies:
- interface ID and functional type;
- source and destination component IDs;
- controlled interface document and revision;
- evidence ID and source revision.

The required functional interfaces cover pusher input, control-state indexing, clutch command, stopped-train retention, reset-hammer command, running-reset block and return/reset behavior.

Interface control must include the mechanical datum, direction of actuation, motion range, force/travel envelope, engagement timing, clearance, tolerance, lubrication and inspection method when those values become approved design inputs. WP-57 does not assign numerical values.

## 7. Drawing and CAD package

The drawing register must include:
- assembly drawing;
- component drawings;
- interface-control drawing;
- inspection drawing or characteristic map.

Drawings carry unique IDs, revisions, status, source evidence and component references. Candidate geometry must be traceable to WP-54 component definitions and WP-55 motion/contact analysis. Assembly layout and envelope review must also reference applicable WP-35/WP-40 evidence.

A drawing marked approved must be supported by the project’s controlled review and approval records. A generated OpenSCAD envelope preview is not a dimensioned manufacturing drawing and is not proof of physical fit.

## 8. Assembly and lubrication work instructions

The assembly plan shall be ordered and revision-controlled. It must identify:
- preparation and cleanliness controls;
- component and revision verification;
- datum establishment and support installation;
- pivots, arbors and moving-member installation;
- springs and return elements;
- control indexing and state-retention installation;
- clutch-command and stopped-retention interface setup;
- reset hammer/heart-cam assembly;
- running-reset interlock inspection;
- endshake, side-shake and clearance checks where defined by approved drawings;
- lubrication points and approved lubricant specification;
- functional checks and controlled hold points.

No lubricant, quantity, application location, assembly torque, press fit, adjustment value or acceptance limit is specified without approved engineering evidence. Assembly instructions remain planned until reviewed and released.

## 9. Inspection and metrology plan

Each inspection characteristic must link to a component, characteristic definition, inspection method, acceptance reference, instrument/gauge reference, evidence ID and source revision.

The inspection plan must cover, as applicable:
- dimensional and geometric conformity to approved drawings;
- pivot, bore, support and datum relationships;
- working profiles and contact surfaces;
- spring and return-element characteristics;
- control indexing and state retention;
- reset-to-zero geometry and repeatability;
- physical running-reset interlock;
- assembly clearances and movement;
- visual condition, burrs, finish and wear;
- configuration and material identity.

Inspection results require actual calibrated equipment, approved methods, recorded uncertainty where relevant, and authorized disposition. The software validates record completeness only; it cannot accept a part or substitute for an inspector.

## 10. Verification and test handoff

Each candidate package must reference approved procedures and acceptance criteria for:
1. functional start/stop/resume/reset state sequence;
2. pusher force and travel;
3. partial/interrupted actuation;
4. reset-to-zero repeatability;
5. physical running-reset interlock;
6. stopped elapsed-time retention;
7. wear inspection and serviceability;
8. timekeeping and energy impact.

The WP-46 bench and WP-47/48 fixture/metrology qualification remain prerequisites. WP-49 supplies immutable acquisition records; WP-50 analysis and WP-51 dashboard provide derived review outputs; WP-52 governs the comparative campaign. WP-55 motion/contact screening must be correlated with actual physical behavior before it is treated as validated.

A simulation, CAD preview, logical state machine, dashboard or software validator cannot prove the physical running-reset interlock. That function requires direct inspection and physical testing of the controlled article.

## 11. Common comparison baseline

The package set requires a common:
- requirements revision;
- shared interface baseline ID;
- fixture revision;
- test protocol revision;
- movement interface revision.

Each candidate package must match these identifiers. This is configuration traceability, not proof that the two articles are physically equivalent. Independent review must confirm that the fixture, instrumentation, test conditions, lubrication state, operating procedure and relevant geometry support a fair comparison.

## 12. Mandatory release gates

Each candidate package requires explicit disposition of:
1. requirements baseline;
2. candidate architecture approval;
3. interface control;
4. dimensioned geometry and tolerances;
5. BOM and configuration control;
6. assembly and lubrication instructions;
7. inspection plan and acceptance;
8. fixture and metrology qualification;
9. physical running-reset interlock;
10. motion, contact and clearance review;
11. risk and failure review;
12. independent engineering review.

A gate may be open, pass, fail or not applicable. Not-applicable requires an approved rationale and approval ID. A complete record with open gates remains incomplete. Even when all gates are recorded as passing, WP-57 reports only eligibility for a separate release review; it never authorizes a build, inspection acceptance, test, or manufacturing release.

## 13. Executable model and regression tests

Files:
- \`tools/c01_integrated_prototype_package.py\`
- \`tools/test_c01_integrated_prototype_package.py\`

The validator checks candidate identity, required component roles, BOM-to-component mapping, interface coverage and endpoints, drawing types, ordered assembly steps, inspection traceability, verification coverage, shared baseline consistency and candidate-specific release gates.

Run from the tools directory:

\`\`\`sh
python -m unittest test_c01_integrated_prototype_package.py
\`\`\`

All test records are synthetic software fixtures. They are not actual C-01 components, drawings, BOM items, inspection results, measurements, physical prototypes, or approvals.

## 14. Current status and next engineering inputs

The CW and CL packages are structured but remain unpopulated with approved physical geometry, production-capable drawings, actual BOM items, qualified materials, released assembly instructions, inspection limits, or test results.

The next inputs required before physical article release include:
- approved control and clutch compatibility decision;
- dimensioned candidate geometry and tolerance analysis;
- detailed spring, pivot, bearing and contact design;
- completed structural and motion/contact reviews;
- controlled drawings and BOM;
- qualified fixture and metrology system;
- approved assembly, lubrication, inspection and test procedures;
- independent engineering and safety review.

No C-01 control architecture or clutch has been selected. No physical prototype build or test is authorized by WP-57.

## 15. Acceptance criteria

| ID | Acceptance criterion | Evidence |
|---|---|---|
| WP57-AC-01 | Separate CW and CL candidate package identities | Configuration records |
| WP57-AC-02 | Complete candidate component roles | Approved component registers |
| WP57-AC-03 | BOM reconciles to component register | Controlled BOM |
| WP57-AC-04 | Shared and candidate-specific interfaces defined | Interface-control records |
| WP57-AC-05 | Assembly/component/interface/inspection drawing registers complete | Reviewed drawing index |
| WP57-AC-06 | Ordered assembly and lubrication instructions approved | Released work instructions |
| WP57-AC-07 | Inspection characteristics and acceptance references approved | Inspection plan |
| WP57-AC-08 | All required verification families have approved procedures | Verification matrix |
| WP57-AC-09 | Fixture and metrology qualifications complete | WP-47/48 records |
| WP57-AC-10 | Physical running-reset interlock verified | Actual-article test evidence |
| WP57-AC-11 | All risks and independent review actions closed | Risk/review records |
| WP57-AC-12 | Separate release authority approves each candidate package | Signed release record |

## 16. Revision history

| Revision | Description | Status |
|---|---|---|
| A | Initial integrated CW/CL prototype package framework | Issued for engineering development |
