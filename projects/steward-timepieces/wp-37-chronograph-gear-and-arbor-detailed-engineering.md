# WP-37 — Chronograph Gear and Arbor Detailed Engineering Framework

- **Document ID:** SEB-C01-WP-37
- **Revision:** A — initial controlled issue
- **Status:** Engineering calculation framework; no C-01 gear schedule or arbor dimensions approved
- **Branch:** `steward/c-01-movement-foundation`
- **Software:** `tools/c01_gear_arbor_detail.py`
- **Verification:** `tools/test_c01_gear_arbor_detail.py`
- **Predecessors:** WP-18, WP-19, WP-20, WP-22, WP-23, WP-24, WP-25, WP-26, WP-30, WP-32, WP-34, WP-36

## 1. Purpose and scope

WP-37 extends the C-01 evidence-controlled engineering chain from functional gear topology and primitive CAD placeholders into a detailed gear/arbor input and calculation framework. It provides nominal reference-geometry calculations, nominal mesh center distances, exact signed kinematic ratios, worst-case shaft/bore clearance intervals, arithmetic axial tolerance stacks, support-register validation and axial interval-overlap screening.

It does **not** create a C-01 tooth schedule, select a module or pressure angle, dimension an arbor, select a bearing/jewel, assign a fit class, freeze a tolerance, or release a drawing. All physical design inputs remain TBD until sourced, reviewed and approved.

## 2. Design basis and inherited constraints

1. WP-18 provides bounded integer tooth-count synthesis, not a selected C-01 tooth schedule.
2. WP-23 defines nominal arbor coordinates and external/internal spur mesh relationships.
3. WP-24 defines the arbor-to-support-to-structural-member traceability chain.
4. WP-20/WP-21 control functional component IDs, coordinate convention and master datum M0.
5. WP-22/WP-36 provide neutral CAD source and primitive component geometry, not detailed involute teeth or released part drawings.
6. WP-25/WP-26 define kinematic closure and candidate synthesis without certifying physical performance.
7. WP-30/WP-32 require verification evidence and approved configuration before release.
8. WP-34 defines chronograph drive/reset functions while source arbor, clutch and counter implementation remain open.

C-01's four WP-33 chronograph architecture combinations remain unresolved. This framework is architecture-neutral where possible and does not imply a winner.

## 3. Units, datums and provenance

- Linear dimensions: mm.
- Angular pressure angle: degrees.
- Gear module: mm.
- Tooth counts: positive integers.
- Axial coordinates: mm relative to the approved realization of WP-21 M0.
- Every candidate calculation input must carry an evidence ID and source revision.
- Test fixtures are synthetic software data only and are not C-01 design values.

No coordinate or datum realization is inferred. A valid record can still be physically wrong; engineering review remains mandatory.

## 4. Gear reference geometry

For a declared standard spur gear with module (m), tooth count (z), and pressure angle (alpha):

[
d=mz,qquad r=rac{mz}{2}
]

[
d_b=dcos(alpha)
]

where (d) is reference pitch diameter, (r) is reference pitch radius, and (d_b) is base-circle diameter.

The software accepts addendum coefficient, dedendum coefficient and profile shift only when explicitly supplied. Under the simplified declared coefficient convention it reports:

[
d_a=d+2m(h_a^*+x)
]

[
d_f=d-2m(h_f^*-x)
]

These are nominal screening expressions, not a validated tooth profile. The generator does not create involute curves, root fillets, tip relief, backlash, profile shift optimization or manufacturing geometry. Pressure-angle compatibility, tooth system, rack standard, profile modifications and tool geometry must be confirmed by a qualified gear designer.

### 4.1 Mesh center distance

For compatible module (m), external spur gears:

[
a=rac{m(z_1+z_2)}{2}
]

For a compatible internal spur gear and pinion, where ring tooth count exceeds pinion tooth count:

[
a=rac{m(z_r-z_p)}{2}
]

The calculation is nominal only. It does not include profile shift corrections, backlash, center-distance modification, tooth thickness, runout, eccentricity, deformation or manufacturing tolerance. Mixed modules and invalid internal pairs fail validation.

### 4.2 Exact kinematic ratio

For an ordered sequence of simple gear meshes, the signed output/input angular-speed ratio is the exact rational product of driver/driven tooth counts. External meshes reverse direction; internal meshes preserve direction. Compound shafts and gear identity continuity must be represented explicitly by the upstream topology/register and reviewed; this helper does not infer a compound train from labels.

## 5. Arbor, pivot and bearing interfaces

Each support record is required to identify:
- unique support ID and arbor ID;
- support type (jewel bearing, bushing, plain bearing or other);
- bore diameter and shaft/pivot diameter;
- optional axial position relative to M0;
- evidence ID and source revision.

For explicit bore and shaft limit dimensions, worst-case diametral clearance is:

[
C_{min}=D_{bore,min}-D_{shaft,max}
]

[
C_{max}=D_{bore,max}-D_{shaft,min}
]

A negative value indicates an interference region in the stated limit stack; it is not automatically acceptable or unacceptable. The software does not assign a fit class or infer radial clearance, press fit, running clearance, jewel geometry, endshake, side shake, lubrication film, pivot finish or shock setting.

Bearing selection requires separate load, speed, friction, wear, shock, lubrication, service and supplier evidence.

## 6. Axial stack and tolerance method

For a signed linear stack with nominal terms (s_i x_i), where (s_i) is +1 or -1, the arithmetic worst-case bounds are calculated by applying each term's explicit positive and negative tolerance in the adverse direction:

[
X_{nom}=sum_i s_i x_i
]

[
X_{min}=sum_i min(s_i(x_i-T_i^-),s_i(x_i+T_i^+))
]

[
X_{max}=sum_i max(s_i(x_i-T_i^-),s_i(x_i+T_i^+))
]

The software reports the arithmetic worst-case interval. It does not assume statistical independence or use RSS. Any statistical stack requires a separately justified distribution, process capability, correlation model and approved risk basis.

Axial component interval overlap is reported from explicit z-min/z-max limits. An overlap flag is not a collision conclusion; non-overlap is not a complete functional clearance certification. Rotating swept envelopes, deflection, endshake, thermal effects and assembly sequence remain outside this model.

## 7. Required C-01 source inputs — currently TBD

| Input | Required source/evidence | C-01 status |
|---|---|---|
| Gear module and tooth system | Approved gear design basis / supplier or gear specialist | TBD |
| Pressure angle and rack standard | Approved gear specification | TBD |
| Tooth counts and compound identities | WP-26 candidate + approved kinematic closure | TBD |
| Profile shift, addendum/dedendum and backlash | Detailed gear design and tool standard | TBD |
| Arbor center coordinates | WP-23 candidate tied to WP-21 M0 | TBD |
| Arbor/pivot diameters and lengths | Detailed shaft drawing, loads and bearing design | TBD |
| Bearing type, bore and jewel/bushing specification | Bearing supplier and design analysis | TBD |
| Endshake/side shake and axial clearances | Axial stack and functional test requirements | TBD |
| Plate/bridge support geometry | WP-21/WP-22 structural design | TBD |
| Material, heat treatment, finish and lubrication | Approved materials/process specification | TBD |
| Dimensional tolerances and datum scheme | Drawing/GD&T review and process capability | TBD |
| Strength, fatigue, contact ratio, undercut and wear | Specialist gear calculations and verification | TBD |

No numerical C-01 values are assigned in this register.

## 8. Calculation model and acceptance criteria

The executable model fails closed for missing/invalid provenance, nonpositive module or diameters, noninteger tooth counts, incompatible modules, invalid internal gear tooth ordering, invalid fit limits, malformed tolerance stacks, duplicate/missing arbor-support identifiers and invalid axial intervals.

| ID | Acceptance criterion | Evidence |
|---|---|---|
| WP37-AC-01 | Gear inputs include explicit module, integer teeth, pressure angle and provenance | Controlled gear candidate |
| WP37-AC-02 | Nominal reference geometry reproduces hand calculations within numerical precision | Independent calculation review |
| WP37-AC-03 | Mesh center distance uses compatible modules and declared mesh type | Gear specification and WP-23 coordinates |
| WP37-AC-04 | Kinematic ratio preserves exact rational value and mesh direction | WP-25 closure record |
| WP37-AC-05 | Arbor/support IDs and support dimensions resolve with evidence | WP-20/WP-21/WP-24 register |
| WP37-AC-06 | Bore/shaft clearance interval uses explicit limit dimensions | Approved bearing/pivot drawings |
| WP37-AC-07 | Axial stack terms have signed direction and explicit bilateral tolerances | Datum-controlled stack drawing |
| WP37-AC-08 | All axial planes have unique IDs, finite intervals and provenance | Controlled component/structure drawings |
| WP37-AC-09 | Specialist checks address tooth form, undercut, contact ratio, strength, fatigue, wear and lubrication | Approved gear engineering report |
| WP37-AC-10 | Independent review and WP-30 verification evidence are complete before design release | Signed review and verification packet |

Software pass means calculation/register integrity only. It does not constitute physical design acceptance.

## 9. Verification procedure

From `projects/steward-timepieces/tools`:

```sh
python -m unittest test_c01_gear_arbor_detail.py
```

Tests cover nominal gear geometry, explicit optional tooth-height coefficients, external/internal center distances, exact signed ratio, worst-case diametral clearance, arithmetic signed tolerance stack, arbor/support traceability, axial interval overlap and fail-closed invalid inputs. All numerical test values are synthetic fixtures.

## 10. Engineering risks and limitations

- Nominal pitch geometry is not a manufacturable involute tooth design.
- Center-distance agreement does not prove contact ratio, backlash, interference, strength or quiet operation.
- A bore/shaft clearance interval does not establish an appropriate horological fit.
- A valid support register does not prove bearing load capacity or arbor stiffness.
- Arithmetic stack bounds do not cover elastic deflection, thermal effects, wear, assembly variation or correlated process behavior.
- Primitive CAD geometry is not detailed gear/arbor CAD.
- No rate, amplitude, chronograph energy, reserve or service-life claim follows from this package.

## 11. Revision control and release disposition

| Revision | Date | Change | Approval |
|---|---|---|---|
| A | 2026-11-27 | Initial controlled gear/arbor calculation framework, verification fixtures and interface requirements | Pending independent engineering review |

**Disposition:** WP-37 establishes the next traceable engineering layer. It does not freeze architecture, dimensions, tooth counts, materials, tolerances or a manufacturing configuration. No physical build, merge or deployment is authorized by this work package.
