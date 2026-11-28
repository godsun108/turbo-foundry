# WP-58 — Detailed Chronograph Control Prototype Geometry and Dimensioning

- **Document ID:** SEB-C01-WP-58
- **Revision:** A — initial controlled issue
- **Status:** Geometry and dimensioning framework; no C-01 dimensions approved or released
- **Branch:** \`steward/c-01-movement-foundation\`
- **Software:** \`tools/c01_control_geometry.py\`
- **Verification:** \`tools/test_c01_control_geometry.py\`
- **Dependencies:** WP-21, WP-23, WP-35 through WP-40, WP-43, WP-47/48, WP-54/55/57

## 1. Purpose and boundary

WP-58 defines the controlled method for establishing detailed geometry for the two chronograph control candidates:
- **CW:** column-wheel indexing and jumper/state retention.
- **CL:** cam profile, follower, lever and state retention.

It establishes datum requirements, component dimension registers, axis/pivot feature coordinates, working-profile definition, spring anchor interfaces, axial stack references, clearance pairs and tolerance-stack calculations. All numerical values are caller-supplied, evidence-linked engineering inputs. No nominal dimensions or tolerances are assigned to STEWARD C-01 in this work package.

The model performs deterministic geometry and arithmetic screening. It does not prove physical fit, contact mechanics, dynamic behavior, fatigue, shock resistance, manufacturability or safety. It does not authorize manufacture or prototype assembly.

## 2. Governing references and coordinate convention

WP-21's movement master datum M0 and XY/Z reference architecture remain controlling. WP-23's arbor and support coordinate method remains the source for axis relationships. WP-35/WP-36/WP-40 define the envelope and parametric CAD handoff. WP-43 defines the pusher/lever force path. WP-54 defines candidate component families and interfaces. WP-55 defines sampled motion/contact analysis. WP-57 defines the separate CW and CL prototype package records.

The WP-58 datum register requires:
- **M0:** movement axial master datum reference;
- **XY_ORIGIN:** approved movement planar origin;
- **Z_REFERENCE:** approved axial reference plane;
- **ANGULAR_ZERO:** approved angular orientation reference.

These identifiers are required references, not proof that their physical realization has been selected. Each datum requires a definition, realization method, evidence ID, source revision and approval reference. Proposed or reviewed datums remain non-approved until formally released.

## 3. Dimension register and tolerance convention

Every dimension record identifies component, characteristic, unit, nominal value, lower and upper deviation magnitudes, drawing reference, evidence ID, source revision and status. Supported units are explicitly limited by the model to mm, degrees, N, N·mm and N/mm.

For nominal \(d\), lower deviation magnitude \(t_L\) and upper deviation magnitude \(t_U\):

\[
d_{\min}=d-t_L,\qquad d_{\max}=d+t_U
\]

The schema requires a bilateral-magnitude convention to avoid ambiguity about signed deviations. Positive-only dimensions can require \(d_{\min}>0\). The model validates input completeness and interval arithmetic; it does not determine which tolerance is functionally adequate.

Dimensions may be TBD, candidate, reviewed or approved. A candidate value is not a released drawing dimension. Approval requires the project drawing and change-control process, independent engineering review and evidence traceability.

## 4. Required geometric feature register

Both candidate packages require explicit feature coordinates and datum references for:
1. control axis;
2. pusher contact;
3. clutch command contact;
4. stopped-retention contact;
5. reset command contact;
6. reset-hammer pivot;
7. heart-cam axis;
8. running-reset interlock contact;
9. return-element anchor;
10. structural support reference.

Each feature has a unique ID, component, role, datum ID, XYZ coordinate in mm, optional orientation in degrees, definition, evidence/source revision and status. This is the minimum functional geometry interface set, not a completed physical layout. Exact coordinates, bearing spans, support heights, pivot diameters and clearances remain TBD.

## 5. Candidate-specific geometry definition

### 5.1 CW — column wheel

The detailed CW geometry package must define, when supported by approved evidence:
- wheel axis and bearing/pivot interface;
- wheel body envelope and axial thickness;
- column count and angular pitch;
- column profile, height, width and working faces;
- indexer/pawl contact geometry and travel;
- jumper geometry, engagement depth and retention force interface;
- state-transition angular positions;
- pusher-to-indexer lever/pivot geometry;
- clutch, stopped-retention and reset command interfaces;
- reset hammer/heart-cam and running-reset interlock geometry;
- return spring anchor points and working travel;
- plate/bridge support and assembly access.

No column count, angular pitch, wheel diameter, tooth/column dimensions, jumper spring rate, index force or material is selected in WP-58.

### 5.2 CL — cam/lever

The detailed CL geometry package must define, when supported by approved evidence:
- cam axis, base envelope and axial stack;
- cam profile and angular state sectors;
- follower contact geometry and path;
- operating lever pivot and effective arm lengths;
- detent/state-retention geometry;
- pusher-to-lever transmission and lost motion;
- clutch, stopped-retention and reset command interfaces;
- reset hammer/heart-cam and running-reset interlock geometry;
- return spring anchor points and working travel;
- plate/bridge support and assembly access.

The profile validator checks a supplied simple closed polygon for repeated vertices, self-intersection and nonzero area. It does not generate an optimized cam law, guarantee curvature continuity, check pressure angle, undercut, follower acceleration, contact stress or dynamic impact. No cam coordinates, lift, dwell angle, follower diameter, lever arms, spring rate or material is selected.

## 6. Lever and force-transmission geometry

For a planar rigid lever, the effective moment arm for a force line at angle \(\theta\) to the radius is:

\[
r_{\mathrm{eff}}=r|\sin\theta|
\]

For input and output force lines, ideal quasi-static force ratio is:

\[
\frac{F_{\mathrm{out}}}{F_{\mathrm{in}}}
=\frac{r_{\mathrm{in,eff}}}{r_{\mathrm{out,eff}}}
\]

The model screens this ideal ratio and a corresponding ideal output travel after explicitly supplied lost motion. It excludes friction, compliance, spring loads, contact geometry changes, inertia and elastic deformation. WP-43's measured force/travel campaign remains the source for actual actuation work and efficiency.

## 7. Spring and return-element interfaces

Every spring interface requires:
- interface/component identity;
- anchor and moving feature IDs;
- spring type;
- two explicit endpoint coordinates;
- drawing/evidence/source references;
- status.

Spring rate and preload may be recorded only when supported by controlled data. Endpoint distance is a geometric screening result, not a spring working length unless the geometry definition establishes that interpretation. Spring force, stress, fatigue, buckling, coil bind, hysteresis and life require separate design analysis and physical validation.

## 8. Axial stack and clearance

Axial relationships must be referenced to the approved Z datum and component drawing revisions. WP-58 provides worst-case arithmetic stack calculation for explicit signed terms. For each dimension interval \([d_{\min},d_{\max}]\), positive and negative stack contributions are combined conservatively. The method does not assume statistical independence or RSS.

Planar circle-envelope clearance is:

\[
c=\sqrt{(x_2-x_1)^2+(y_2-y_1)^2}-r_1-r_2
\]

Positive \(c\) indicates nominal separation; zero indicates nominal contact; negative \(c\) indicates overlapping circular envelopes. The check is only a 2D envelope screen. Every clearance pair must cite an explicit axial-overlap review. The model does not evaluate swept volume, complete solids, tolerance extremes, deflection or motion unless a separate analysis provides those inputs.

## 9. Tolerance stack and dimensional review

Critical stacks should be derived from functional requirements, datum scheme and inspection strategy. Review must identify:
- functional gap or engagement being controlled;
- contributing dimensions and signs;
- worst-case limits;
- measurement method and uncertainty;
- adjustment or selective-assembly strategy, if any;
- sensitivity to wear, lubrication and temperature;
- drawing and inspection characteristic traceability.

WP-58's arithmetic helper returns a conservative interval only for the dimensions supplied. It does not determine stack direction, select tolerances, or establish acceptance. A signed engineering review must approve the stack definition.

## 10. Geometry data and CAD handoff

Each candidate geometry package contains:
- candidate/package/configuration identity;
- requirements, datum and interface baseline revisions;
- datum register;
- dimension register;
- feature/axis/pivot coordinate register;
- spring-interface register;
- working-profile register;
- clearance-pair register;
- evidence and source revision references.

These records can feed WP-36's component geometry and WP-22's neutral CAD skeleton after the data are reviewed and mapped. No CAD model is rendered or certified by this WP-58 validator.

## 11. Executable model and synthetic tests

Files:
- \`tools/c01_control_geometry.py\`
- \`tools/test_c01_control_geometry.py\`

The model validates both candidate records, required datums and features, dimension intervals, spring interfaces, closed polygon profiles, clearance pairs and common baseline consistency. It provides worst-case tolerance stack and ideal planar lever screening.

Run from the tools directory:

\`\`\`sh
python -m unittest test_c01_control_geometry.py
\`\`\`

All regression fixtures use synthetic values solely to exercise software behavior. They are not C-01 dimensions, tolerances, profiles, spring rates, coordinates, or measured results.

## 12. Acceptance criteria

| ID | Acceptance criterion | Evidence |
|---|---|---|
| WP58-AC-01 | Movement datum realization approved | Datum-control records |
| WP58-AC-02 | CW and CL dimension registers complete and traceable | Controlled dimension registers |
| WP58-AC-03 | Required functional axes and feature coordinates defined | Axis/feature register |
| WP58-AC-04 | Candidate-specific wheel or cam/follower profiles reviewed | Profile drawings and analysis |
| WP58-AC-05 | Pusher, clutch, retention and reset interfaces dimensioned | Interface-control drawings |
| WP58-AC-06 | Spring anchor and working geometry defined | Spring/interface specification |
| WP58-AC-07 | Critical axial stacks and clearances reviewed | Signed stack/clearance reports |
| WP58-AC-08 | Tolerances tied to function and inspection capability | Tolerance and metrology review |
| WP58-AC-09 | CAD handoff reconciles with WP-57 package records | Controlled CAD source and revision |
| WP58-AC-10 | Independent engineering review complete | Signed review and disposition |

## 13. Current status and release boundary

No actual C-01 geometry or dimensions are populated. The tool does not select CW or CL, choose a clutch, freeze the movement, certify physical fit, or authorize manufacture. Both candidate geometry packages remain engineering definitions awaiting approved design inputs and review.

## 14. Revision history

| Revision | Description | Status |
|---|---|---|
| A | Initial detailed geometry and dimensioning framework for CW and CL candidates | Issued for engineering development |
