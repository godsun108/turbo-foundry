# WP-24 — Integrated Gear Train, Bearing and Structural Support Architecture

- **Document ID:** SEB-C01-WP-24
- **Project:** STEWARD C-01
- **Revision:** A (initial controlled issue)
- **Status:** Preliminary integration method; no bearing or support geometry approved
- **Branch:** `steward/c-01-movement-foundation`
- **Software:** `tools/c01_bearing_architecture.py`
- **Verification:** `tools/test_c01_bearing_architecture.py`
- **Predecessors:** WP-20, WP-21, WP-22 and WP-23

## 1. Purpose

WP-24 integrates three previously separate engineering interfaces:
1. WP-23 arbors, candidate gear meshes and coordinate records;
2. WP-21 structural members, bearing-axis and support relationships;
3. WP-22 CAD bearing-bore input contract.

The objective is a consistent, traceable candidate register from functional arbor through support member to CAD bore input. This is not a detailed bearing/jewel design, a structural calculation, a rendered CAD assembly or a physical-fit certification.

## 2. Architecture boundary

The evaluator accepts an explicit candidate containing:
- arbor records with WP-20 component IDs and WP-21 axis IDs;
- support records linking each arbor to a structural member;
- structural member records identifying main plate, bridge, cock or other support;
- optional WP-23 gear mesh records and candidate XY coordinates;
- optional bearing-bore specifications keyed by arbor ID;
- optional WP-22 CAD configuration for handoff comparison;
- candidate-level evidence and source revision.

No support count, jewel arrangement, bridge count, bearing dimensions or structural layout is selected by this package.

## 3. Interface model

The required traceability chain is:

`WP-20 component → WP-21 axis → WP-23 arbor → support record → structural member → WP-22 bearing bore`

The software validates IDs, declared component support, axis consistency, evidence and source revision. A structural member ID is a controlled register reference; the code does not infer its geometry.

### 3.1 Structural member types

Permitted member types are:
- `main_plate`
- `bridge`
- `cock`
- `other`

Bridge and cock records must explicitly list the components they support. A support record assigned to a bridge/cock is rejected if that component is absent from the member's supported-component list.

### 3.2 Arbor support topology

Support records may carry an axial coordinate `z_mm` referenced to the approved WP-21 M0 datum. When two or more distinct support planes are supplied, the tool reports their axial span. If positions are absent or only one plane is supplied, the span remains unevaluated.

The software deliberately does not impose a universal two-jewel/two-support rule. Actual support arrangement depends on arbor function, loading, geometry, shock protection, assembly and service requirements and must be approved per arbor.

## 4. Gear-train integration

WP-23 remains the source of nominal gear center-distance and XY coordinate checks. WP-24 calls its candidate evaluator and preserves the distinction between:
- nominal gear-center consistency;
- arbor/support register integrity;
- physical bearing and structural adequacy.

A passing nominal mesh check does not establish tooth contact, bearing alignment, pivot stiffness, friction, rate stability or power reserve. Chronograph source/take-off alternatives remain open.

## 5. Bearing-bore and CAD handoff

A bore definition is supplied by arbor ID and must include:
- bore ID (optional; otherwise a deterministic register identifier is assigned);
- diameter in mm;
- evidence;
- source revision.

WP-23 maps only explicitly positioned arbors with explicit bore definitions into the WP-22 `bearing_bores` shape. No bore diameter is inferred from pivot size, jewel convention, support type or component name.

If a WP-22 CAD configuration is supplied, WP-24 validates it using the existing WP-22 input validator and compares every generated bore handoff field against the matching CAD bore. It does not synthesize plate outline, thickness, bridge geometry or keepout dimensions.

## 6. Calculations

### 6.1 Axial support span

For an arbor with two or more supplied support-plane coordinates:
[
L_s=z_{max}-z_{min}
]

This is a coordinate separation only. It is not a bearing load calculation, pivot length, endshake, side shake or a stiffness measure.

### 6.2 Gear mesh

Gear center distance and coordinate deviation continue to be calculated by WP-23:
[
a=m(z_1+z_2)/2 quad 	ext{(external spur mesh)}
]
[
a_{xy}=\sqrt{(x_2-x_1)^2+(y_2-y_1)^2}
]

The actual mesh type, tooth counts, module, coordinates and tolerance must be explicit, traceable inputs.

## 7. Assumptions and input status

| Input | Source / requirement | C-01 status |
|---|---|---|
| Functional component IDs | WP-20 | Defined as functional register |
| Axis IDs and M0 | WP-21 | Physical datum/axis assignments TBD |
| Arbor XY coordinates | WP-23 controlled candidate | TBD |
| Gear module/tooth counts | Approved gear design | TBD |
| Structural member identities | Approved plate/bridge architecture | TBD |
| Support topology and z positions | Detailed arbor/bearing design | TBD |
| Jewel/bore diameter | Bearing and pivot design evidence | TBD |
| CAD plate/bridge geometry | WP-22 controlled input | TBD |
| Bearing load, friction and wear limits | Analysis, supplier data and test | TBD |

No dimensions, materials, load limits, clearances, support counts, coordinates or tolerances are invented.

## 8. Acceptance criteria

| ID | Acceptance criterion | Evidence |
|---|---|---|
| WP24-AC-01 | Every arbor references a valid WP-20 component and WP-21 axis | Controlled arbor/axis register |
| WP24-AC-02 | Every support references a declared arbor and structural member | Support interface register |
| WP24-AC-03 | Bridge/cock support assignments include the supported component | Approved support/member schedule |
| WP24-AC-04 | Arbor-declared support IDs match the support register | Automated validation |
| WP24-AC-05 | Supplied support z positions are finite and referenced to controlled M0 | Datum-controlled source |
| WP24-AC-06 | Every CAD bore has explicit diameter, location and provenance | Bearing design input and WP-22 comparison |
| WP24-AC-07 | WP-23 gear meshes meet supplied approved nominal center-distance tolerances | Gear definition and coordinate review |
| WP24-AC-08 | Bearing load, fit, endshake, wear, lubrication and structural performance are separately verified | Detailed calculations, supplier data and physical tests |

Software acceptance confirms register consistency only. It does not pass physical design acceptance criteria.

## 9. Verification

Run from the tools directory:
```sh
python -m unittest test_c01_bearing_architecture.py
```

Tests cover member references, bridge component declarations, axis matching, support-register consistency, one-plane vs multi-plane reporting, explicit bore handoff and traceability. All numerical values and IDs in tests are synthetic fixtures, not C-01 design data.

## 10. Risks and limitations

- A structurally valid support map may still be mechanically inadequate.
- Axial support span alone does not establish pivot geometry or bearing performance.
- A CAD bore can be correctly linked yet still be the wrong engineering size.
- WP-22 input validation is not CAD rendering or geometric interference checking.
- No bearing stress/contact, jewel selection, friction, lubrication, shock, bridge stiffness, fastener, thermal or tolerance analysis is performed.
- No production layout, architecture or support scheme is selected.

## 11. Revision control

| Revision | Date | Change | Approval |
|---|---|---|---|
| A | 2026-11-26 | Initial integrated bearing/support architecture model, tests and controlled document | Pending engineering review |

**Release gate:** no bearing or bridge design is frozen until the arbor geometry, support scheme, bearing specification, tolerances, structural checks and CAD review are supported by controlled evidence and approved. No merge or deployment is authorized by this work package.
