# WP-38 — Detailed Involute Gear Tooth Design and Verification

- **Document ID:** SEB-C01-WP-38
- **Revision:** A — initial controlled issue
- **Status:** Analytical design and screening framework; no C-01 gear pair approved
- **Branch:** `steward/c-01-movement-foundation`
- **Software:** `tools/c01_gear_tooth_design.py`
- **Verification:** `tools/test_c01_gear_tooth_design.py`
- **Predecessors:** WP-18, WP-23, WP-25, WP-26, WP-30, WP-32, WP-34, WP-36, WP-37

## 1. Purpose

WP-38 adds an evidence-gated analytical involute spur-gear model. It calculates reference/base/addendum/root geometry from explicit inputs, samples a single involute flank, estimates external spur-pair transverse contact ratio, provides a limited zero-profile-shift undercut risk screen, and compares measured backlash with an explicitly approved target/tolerance.

This is not a complete tooth-generation system, gear standard implementation, strength calculation, manufacturing drawing, or proof of C-01 suitability.

## 2. Scope and assumptions

Supported model: parallel-axis external involute spur gears with compatible equal module and common nominal pressure angle. Inputs include module, tooth count, pressure angle, addendum/dedendum coefficients, profile shift, evidence ID and source revision.

No default module, pressure angle, coefficients, profile shift, minimum contact ratio, backlash or tooth count is selected for C-01. All test values are synthetic fixtures.

Internal gears, helical gears, bevel gears, cycloidal gears, non-standard rack forms, tip relief, root fillets, crowning, microgeometry, manufacturing cutter geometry and detailed contact stress are out of scope.

## 3. Governing geometry

Let module (m), tooth count (z), reference pressure angle (alpha), profile shift coefficient (x), addendum coefficient (h_a^*), and dedendum coefficient (h_f^*) be explicitly specified.

[
r=rac{mz}{2},quad r_b=rcosalpha
]

[
r_a=r+m(h_a^*+x),quad r_f=r-m(h_f^*-x)
]

The base circle radius is (r_b), addendum radius (r_a), and root radius (r_f). These radii are reference inputs to the analytical screen; the root transition and generated trochoid are not modeled.

### 3.1 Involute curve

For base radius (r_b) and involute parameter (t):

[
x(t)=r_b(cos t+tsin t)
]
[
y(t)=r_b(sin t-tcos t)
]
[
0le tle sqrt{(r_a/r_b)^2-1}
]

The software returns points for one flank only. It does not close the tooth, generate the opposite flank, create a root fillet, enforce tooth thickness around the full wheel, or output a certified CAD solid.

### 3.2 Involute function and tooth thickness screen

[
inv(alpha)=	analpha-alpha
]

The calculated tip thickness is derived from the explicitly declared basic rack coefficient/profile-shift convention and the involute angular thickness at the addendum circle. It is a screening result. A gear designer must check actual cutter/rack geometry, tip sharpness, root form, tooth thickness, backlash and manufacturing allowance.

## 4. External spur mesh contact ratio

For two external gears at working center distance (a), base radii (r_{b1},r_{b2}), and addendum radii (r_{a1},r_{a2}):

[
alpha_w=cos^{-1}left(rac{r_{b1}+r_{b2}}{a}ight)
]

[
L=sqrt{r_{a1}^2-r_{b1}^2}+sqrt{r_{a2}^2-r_{b2}^2}-asinalpha_w
]

[
p_b=pi mcosalpha,qquad epsilon_alpha=rac{L}{p_b}
]

The model reports transverse contact ratio (epsilon_alpha) and optionally compares it with a caller-supplied threshold. It does not choose a minimum threshold for C-01. The result assumes the declared external involute spur geometry and does not account for dynamic deflection, misalignment, tooth modifications, manufacturing error, load sharing, lubrication or elastic contact.

## 5. Undercut screening

For an idealized standard full-depth rack and zero profile shift, the classical theoretical minimum tooth count screen is:

[
z_{min}approxrac{2}{sin^2alpha}
]

The model flags a possible undercut risk when the tooth count is below this estimate and profile shift is not positive. This is not a definitive undercut calculation. Actual undercut/interference depends on the generating rack/cutter geometry, addendum, profile shift, root fillet and gear system. Positive profile shift does not automatically certify the gear.

## 6. Backlash

The model only compares a measured backlash value with an explicitly supplied approved target and tolerance:

[
Delta j=j_{measured}-j_{target}
]

It does not infer backlash from center distance or tooth thickness, and does not recommend a target. Measurement method, temperature, angular position, runout, support compliance and uncertainty must be documented in the associated test record.

## 7. Inputs and source register — C-01 TBD

| Parameter | Required authority | Current status |
|---|---|---|
| Module and tooth system | Approved gear standard/design basis | TBD |
| Reference pressure angle | Approved gear design basis | TBD |
| Addendum/dedendum coefficients | Selected rack/cutter system | TBD |
| Profile shift | Gear-pair optimization and undercut/interference analysis | TBD |
| Tooth counts and pair identity | Approved WP-26 candidate and WP-25 closure | TBD |
| Center distance and tolerance | WP-23 coordinates and WP-37 stack | TBD |
| Minimum contact ratio | C-01 requirement and gear specialist review | TBD |
| Backlash target and tolerance | Functional requirement and measurement plan | TBD |
| Materials, hardness and finish | Material/process qualification | TBD |
| Lubricant and application | Tribology and supplier qualification | TBD |

No C-01 gear dimensions or acceptance limits are assigned in this package.

## 8. Software validation and acceptance

The model rejects missing provenance, nonfinite/nonpositive geometry, invalid tooth counts, invalid pressure angles, nonpositive root radius, addendum radius not exceeding base radius, incompatible module, invalid center distance, and malformed flank point requests.

| ID | Acceptance criterion | Evidence |
|---|---|---|
| WP38-AC-01 | Inputs and provenance complete | Controlled gear record |
| WP38-AC-02 | Reference/base/addendum/root geometry agrees with independent hand calculation | Calculation review |
| WP38-AC-03 | Involute sample endpoints lie on base/addendum circles | Coordinate verification |
| WP38-AC-04 | Contact ratio independently reproduced for declared external pair | Gear calculation review |
| WP38-AC-05 | Undercut screen limitations acknowledged and specialist analysis supplied | Gear specialist report |
| WP38-AC-06 | Backlash target approved before measurement comparison | Requirement and calibrated measurement |
| WP38-AC-07 | Tooth strength, bending fatigue, contact stress, wear and lubrication evaluated separately | Signed engineering analysis |
| WP38-AC-08 | Gear-pair center distance, runout, backlash and mesh quality verified in prototype | WP-30 test records |

Software pass is not physical acceptance.

## 9. Verification

From `projects/steward-timepieces/tools`:

```sh
python -m unittest test_c01_gear_tooth_design.py
```

Synthetic fixtures cover involute function, nominal geometry, profile shift, flank sample endpoints, contact ratio, zero-shift undercut risk flag, backlash comparison, invalid geometry, incompatible modules and provenance rejection. Fixtures are not C-01 dimensions.

## 10. Exclusions and engineering risks

- No complete tooth outline, wheel CAD, cutter path or manufacturing profile is generated.
- No root fillet/trochoid or cutter interference simulation is implemented.
- No minimum pinion size is approved for C-01.
- No contact ratio threshold or backlash target is selected.
- No tooth bending/contact stress, fatigue, wear, efficiency, noise or life calculation is performed.
- No tolerance, runout, deflection, thermal or dynamic mesh analysis is certified.
- The analytical result does not select a gear architecture or resolve WP-33 chronograph architecture options.

## 11. Revision control and disposition

| Revision | Date | Change | Approval |
|---|---|---|---|
| A | 2026-11-27 | Initial involute geometry, mesh screening, backlash comparison, test fixtures and acceptance framework | Pending independent engineering review |

**Disposition:** WP-38 is a calculation and screening milestone only. No gear pair is selected, no C-01 dimensions are frozen, and no drawing or manufacturing release is authorized.
