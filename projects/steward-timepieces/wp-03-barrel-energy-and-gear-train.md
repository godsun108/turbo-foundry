# WP-03 — Barrel, Energy Budget, and Gear-Train Calculation Framework

**Revision:** 0.1  
**Status:** First-principles calculation framework; numerical movement design awaits verified component data.

## 1. Corrected benchmark baseline

The most relevant published day-date automatic chronograph references currently identified are:

| Reference | Day/date | Chronograph | Diameter | Height | Frequency | Typical reserve |
|---|---|---|---:|---:|---:|---:|
| ETA 7750 | Day + date | Cam; 60 s / 30 min / 12 h | 30.00 mm | 7.90 mm | 4 Hz | 54 h |
| Sellita SW500 a | Day + date | Cam; 60 s / 30 min / 12 h | 30.00 mm | 7.90 mm | 4 Hz | 62 h |
| Sellita SW500 b | Date only | Cam; 60 s / 30 min / 12 h | 30.00 mm | 7.90 mm | 4 Hz | 62 h |

Sources:
- ETA 7750 product specification: https://portal.eta.ch/en/7750-7750-5.html
- ETA 7750 technical communication (14 August 2026): https://portal.eta.ch/fr/technicaldocuments/index/pdf/id/2080/
- Sellita catalogue 2022–2023, SW500 family: https://sellita.ch/images/documents/Catalogue2022_ENG.pdf
- Sellita SW500 technical-documentation page: https://www.sellita.ch/scripts/calibres/sc218-generator-cald.php?calid=75&sc218Lng=en

The SW500 a is an especially relevant benchmark because the manufacturer explicitly lists day + date, automatic winding, cam chronograph, 4 Hz, 25 jewels, 30 mm diameter, 7.90 mm height, and 62 h typical reserve.

## 2. Reserve target arithmetic

C-01's earlier 60–70 h reserve target is a design objective, not a measured result.

Relative to the ETA 7750's published 54 h typical reserve:
- 60 h requires 11.1% more elapsed running time.
- 62 h requires 14.8% more elapsed running time.
- 70 h requires 29.6% more elapsed running time.

Relative to Sellita SW500 a's published 62 h typical reserve:
- 60 h is 3.2% below the benchmark.
- 65 h is 4.8% above the benchmark.
- 70 h is 12.9% above the benchmark.

These percentages compare time only. They do **not** prove equivalent stored energy, barrel torque, efficiency, amplitude stability, or chronograph performance. A longer reserve can be achieved in ways that harm torque delivery or timekeeping if the energy curve is not controlled.

## 3. Core energy relationships

### Mainspring usable energy

For a mainspring with torque varying through its unwind:

\[
E_{usable}=\int_{\theta_{min}}^{\theta_{max}} T(\theta)\,d\theta
\]

Where:
- \(T(\theta)\) is delivered barrel torque as a function of unwinding angle.
- \(\theta_{max}-\theta_{min}\) is the usable angular travel.
- The usable range excludes unsafe low-torque and over-wind regions.

The idealized average power available over reserve time \(t\) is:

\[
P_{avg}=\frac{E_{usable}}{t}
\]

The actual train receives less power because of losses in bearings, gear meshes, escapement, automatic-winding interfaces, and complications.

### Gear-train power flow

At each stage:

\[
P_{out}=\eta P_{in}
\]

Where \(\eta\) is the measured or modeled efficiency of that stage. For multiple stages, total efficiency is the product of stage efficiencies:

\[
\eta_{total}=\prod_{i=1}^{n}\eta_i
\]

Do not assign generic efficiency percentages and present them as C-01 facts. Obtain values from validated modeling, supplier data, or prototype measurement.

### Torque and angular speed

\[
P=T\omega
\]

The gear train trades torque for angular speed. Each ratio must be selected from required hand speeds, escapement geometry, available tooth counts, module, center distances, and practical manufacturing limits.

### Oscillator frequency

At 4 Hz:
- Balance full oscillations: 4 per second.
- Alternations (half-oscillations): 8 per second.
- Manufacturer convention: 28,800 vibrations/alternations per hour.

This frequency is established by the benchmarks, but it does not alone determine accuracy. Balance inertia, hairspring behavior, escapement geometry, amplitude, poise, positional errors, temperature sensitivity, magnetism, and regulation all matter.

## 4. Required measured or sourced inputs

| Input | Symbol | Needed for | Current status |
|---|---|---|---|
| Barrel torque vs unwind angle | T(θ) | Energy and amplitude stability | Unknown |
| Usable mainspring travel | Δθ | Reserve estimate | Unknown |
| Barrel arbor/barrel dimensions | — | Packaging and spring capacity | Unknown |
| Mainspring material and geometry | — | Torque curve, fatigue, safety | Unknown |
| Train wheel tooth counts | zᵢ | Ratios and speeds | Not yet verified |
| Pinion leaf counts | pᵢ | Ratios and geometry | Not yet verified |
| Wheel/pinion module and center distances | — | CAD and tolerances | Unknown |
| Stage efficiencies | ηᵢ | Power budget | Unknown |
| Escapement energy demand | — | Power budget | Unknown |
| Balance inertia and hairspring data | I, k | Oscillator design | Unknown |
| Chronograph engaged load | P_chrono | Reserve and rate disturbance | Unknown |
| Calendar changeover load | P_calendar | Midnight disturbance | Unknown |
| Automatic winding efficiency | η_auto | Real-world winding performance | Unknown |

No tooth counts, torque values, spring dimensions, or efficiency values are invented in this document.

## 5. Energy consumers to include

The budget must distinguish:
1. Base timekeeping train and escapement.
2. Running seconds and minute/hour hands (part of the going train load).
3. Automatic winding losses and winding behavior.
4. Chronograph engaged load, including counters and coupling.
5. Calendar changeover load, including day and date.
6. Friction and lubrication changes over service life.
7. Any future display or complication loads.

The chronograph is not necessarily engaged continuously in daily use, but C-01 must operate safely and consistently while it is running. Define both normal reserve (chronograph stopped) and chronograph-running reserve.

## 6. Gear-train calculation worksheet

For each wheel/pinion pair, record:
- Driver wheel tooth count.
- Driven pinion leaf count.
- Speed ratio.
- Input/output rotational speed.
- Input/output torque (ideal and efficiency-adjusted).
- Module, pitch diameters, center distance.
- Material, hardness, surface finish, lubrication.
- Bearing/jewel support and endshake.
- Tolerance and inspection method.

For a simple external wheel driving a pinion:

\[
\frac{\omega_{pinion}}{\omega_{wheel}}=\frac{z_{wheel}}{z_{pinion}}
\]

The sign reverses direction for each external mesh. Compound wheels require ratios to be multiplied stage by stage. Final tooth counts must satisfy integer constraints and geometric packaging.

## 7. Preliminary architecture principles

- Keep the base going train as simple as practical.
- Avoid unnecessary extra meshes and friction interfaces.
- Assess chronograph coupling separately from the base timekeeping train.
- Quantify chronograph amplitude drop and rate shift at full, mid, and low reserve.
- Assess calendar load at changeover, including day/date simultaneous advance.
- Preserve access to the barrel, escapement, calendar, and chronograph for service.
- Consider a larger barrel only after the torque curve, thickness, and case envelope are understood.
- Consider twin barrels or alternative energy architectures only if calculations justify the added complexity.

## 8. Required next measurements / source extraction

1. Obtain exact SW500 a technical drawing and service documentation.
2. Obtain exact ETA 7750 service drawings and parts lists for comparison.
3. Digitize verified gear tooth counts from readable technical drawings or measure an authorized sample.
4. Obtain barrel and mainspring specifications where available.
5. Measure or source barrel torque curves.
6. Establish baseline amplitude and rate with chronograph stopped and running.
7. Establish calendar changeover load and timing.
8. Populate a calculation workbook or script with traceable inputs and uncertainty ranges.

## 9. Decision gate

Do not release a barrel size, tooth-count train, mainspring specification, or reserve guarantee until the energy budget closes with documented assumptions and prototype measurements. The design must meet the required rate stability across the full usable reserve, not merely run for a headline number of hours.
