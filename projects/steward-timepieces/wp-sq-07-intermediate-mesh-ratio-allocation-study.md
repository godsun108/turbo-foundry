# WP-SQ-07 — Intermediate Mesh Ratio Allocation Study

- **Document ID:** SEB-C01-WP-SQ-07
- **Revision:** 0.1
- **Status:** Algebraic trade study; no tooth schedule selected
- **Dependencies:** WP-SQ-03 through WP-SQ-06; WP-18, WP-25, WP-26, WP-38 and WP-39
- **Controlled data:** `data/c01-square-intermediate-ratio-allocations.csv`

## 1. Purpose

WP-SQ-06 established a conditional 60:1 speed-magnitude increase from the center arbor to the fourth arbor, provided that the center arbor is the direct minute-motion interface and the fourth arbor is the direct running-seconds source.

WP-SQ-07 examines how that total ratio could be divided between the center-to-third and third-to-fourth external meshes. This is an algebraic allocation study only. It deliberately does not invent gear tooth counts, gear modules, pressure angles, center distances, materials or tolerances.

## 2. Governing relationship

Let:
- (R_1) = speed ratio magnitude of center-wheel to third-pinion mesh;
- (R_2) = speed ratio magnitude of third-wheel to fourth-pinion mesh.

The required relationship is:

\[
R_1 R_2 = 60
\]

For external spur meshes, each stage reverses rotational direction. Two external stages therefore restore the fourth arbor to the same direction as the center arbor, assuming no intervening idler or alternative mesh.

A ratio allocation is not a tooth-count assignment. For a given stage ratio (R=a/b), infinitely many scaled tooth-count pairs may express that ratio mathematically; physical admissibility depends on minimum tooth form, undercut, contact ratio, strength, inertia, center distance, packaging, lubrication and manufacturing constraints.

## 3. Exact integer-factor allocations

The following table lists the unique unordered positive-integer factor pairs of 60. Each pair is an algebraic split of the total ratio, not a proposed gear specification.

| Allocation | First mesh (R_1) | Second mesh (R_2) | Product | Character |
|---|---:|---:|---:|---|
| A | 1 | 60 | 60 | All speed increase concentrated in second mesh |
| B | 2 | 30 | 60 | Strongly unequal split |
| C | 3 | 20 | 60 | Unequal split |
| D | 4 | 15 | 60 | Unequal split |
| E | 5 | 12 | 60 | Moderately unequal split |
| F | 6 | 10 | 60 | Most balanced integer-factor split |

The reverse order of each pair is also mathematically valid (for example, 10 × 6). Whether a particular order is better depends on the available wheel/pinion envelope and the shared third-arbor packaging; neither is known.

## 4. Trade observations

### 4.1 Balanced ratio distribution

The 6 × 10 split is the most balanced split among the listed integer-factor pairs. It reduces the larger of the two stage ratios compared with the more unequal integer splits.

This is an algebraic observation only. It does not establish lower friction, better efficiency, smaller diameter, improved strength or a more manufacturable design.

### 4.2 Concentrated ratio distribution

The 1 × 60 split places the entire speed increase in one mesh while the other mesh is 1:1. This is not recommended or rejected at this stage: it is simply an endpoint of the factorization space. The 60:1 mesh may be incompatible with watch-scale geometry, but that cannot be concluded without tooth-form and envelope analysis.

### 4.3 Non-integer rational allocations

The ratio factors need not be integers. Any positive rational pair (R_1=a/b), (R_2=c/d) satisfying:

\[
\frac{a}{b}\frac{c}{d}=60
\]

is an exact mathematical allocation. Bounded tooth synthesis can explore such possibilities only after approved integer tooth bounds and gear design assumptions are supplied. The integer-factor table is not an exhaustive list of all rational allocations.

## 5. Shared-arbor constraint

The third arbor carries both:
- the driven pinion for the center-to-third mesh; and
- the driving wheel for the third-to-fourth mesh.

Those two gears rotate together at the same arbor speed but may have different tooth counts and pitch diameters. Any candidate must therefore be evaluated as a compound third-arbor assembly, not as two independent gear pairs.

WP-26 already checks shared gear identity/teeth consistency across connected mesh specifications. It should remain the orchestration authority for future candidate enumeration.

## 6. What can be screened now

| Check | Current status | Why |
|---|---|---|
| Exact total ratio closure | Closed conditionally at 60:1 | WP-SQ-06 |
| Algebraic factor allocation | Completed | This study |
| Tooth-count feasibility | Open | No approved search bounds or gear basis |
| Undercut/contact ratio/interference | Open | Requires tooth geometry and gear standard |
| Center distance and package fit | Open | No approved module or arbor coordinates |
| Shared third-arbor packaging | Open | Requires gear diameters and layout |
| Torque, bearing load and energy loss | Open | Requires measured source/load data and geometry |
| Manufacturing/serviceability | Open | Requires detailed candidate and process review |

## 7. Required inputs before tooth synthesis

1. Approve the functional center and fourth arbor roles and the two-mesh path.
2. Establish explicit minimum/maximum tooth counts and minimum/maximum stage-ratio bounds from an approved gear design basis.
3. Define module, pressure angle, tooth-form/rack coefficients and profile-shift policy.
4. Obtain barrel speed/torque operating data and escapement interface requirements.
5. Establish third-arbor compound wheel/pinion packaging and arbor coordinates.
6. Run WP-18/WP-26 bounded candidate enumeration; close exact speed with WP-25; screen geometry using WP-38/WP-39.
7. Evaluate power, inertia, bearing loads, lubrication, tolerances, service access and manufacturing constraints.

Search bounds must be recorded before results are ranked. A candidate's low mathematical ratio error is not evidence of physical superiority.

## 8. Acceptance criteria

- Each listed factor pair multiplies exactly to 60.
- The table is clearly labeled algebraic and not a tooth schedule.
- Reverse stage ordering is recognized as mathematically possible but not physically ranked.
- The shared third-arbor compound constraint is explicit.
- No tooth counts, modules, dimensions, efficiencies, torque, reserve or physical performance are invented.
- No architecture, ratio allocation or gear candidate is approved by this study.
- C-01 scope remains chronograph + weekday + date; month and moon phase remain assigned to LUNAR.

## 9. Conclusion and disposition

The most balanced positive-integer factor split of 60 is 6 × 10. This gives us a useful reference point for the later bounded synthesis search, but it is not a design recommendation. Non-integer rational splits remain open and may yield better physically constrained candidates.

**Disposition:** Algebraic study complete. No tooth schedule selected. No design freeze, physical test, manufacture, merge or deployment authorized.
