# C-01 Benchmark Study — First Reference Set

**Revision:** 0.1  
**Status:** Preliminary desk research; manufacturer data must be rechecked against current technical documents before design release.

## Executive finding

The ETA 7750 and Sellita SW500 a are direct functional benchmarks. Both combine an automatic chronograph with weekday and date display, 30-minute and 12-hour chronograph counters, and running seconds. Sellita's published SW500 a specification lists a typical 62-hour reserve, compared with ETA's 54-hour typical reserve for the 7750.

This changes the benchmark priority. The ETA 7750 and its day-date derivatives should be studied before treating the date-only SW510 as the nearest comparator.

## Manufacturer-published comparison

| Caliber | Calendar | Chronograph | Diameter | Height | Frequency | Typical reserve |
|---|---|---|---:|---:|---:|---:|
| ETA 7750 | Day + date | Cam; 60 s / 30 min / 12 h | 30.00 mm | 7.90 mm | 4 Hz | 54 h |
| Sellita SW510 a | Date only | Cam; 60 s / 30 min / 12 h | 30.00 mm | 7.90 mm | 4 Hz | 62 h |
| Sellita SW510 b | No calendar | Cam; 60 s / 30 min / 12 h | 30.00 mm | 7.90 mm | 4 Hz | 62 h |

**Important:** The SW510 family entries in Sellita's 2024–2025 catalogue list date-only and no-calendar variants. They do not establish a day-date SW510. The day-date Sellita chronograph family to investigate is SW500, not SW510. Exact current variant documentation must be obtained before specifying it.

## Source notes

### ETA 7750 — official ETA product page

ETA lists:
- 13¼ lignes; 30.00 mm diameter.
- 7.90 mm height.
- Hours, minutes, small seconds.
- Day and date in a slow-switching window.
- 60-second, 30-minute, and 12-hour chronograph counters.
- Cam-operated chronograph with two pushers.
- Quick correction of day and date.
- Stop-second time setting.
- Unidirectional automatic winding.
- 28,800 vibrations/hour (4 Hz).
- 25 jewels.
- Typical power reserve: 54 hours.

Source: https://portal.eta.ch/en/7750-7750-5.html

ETA technical communication, document CT 7750 FDE 465595 18, dated 14 August 2026, gives 48 h minimum and 54 h typical reserve, 30.00 mm diameter, 7.90 mm height and 4 Hz:
https://portal.eta.ch/fr/technicaldocuments/index/pdf/id/2081/

### Sellita SW510 — official catalogue

Sellita's 2024–2025 English catalogue lists:
- SW510 a: automatic chronograph with date, cam operated, 30 mm diameter, 7.90 mm height, 4 Hz, 27 jewels, 62 h typical reserve.
- SW510 b: automatic chronograph without calendar, same listed size/frequency/reserve.

Source: https://www.sellita.ch/images/documents/Catalogue2024_ENG.pdf

### Sellita SW500 — next manufacturer document to obtain

Sellita's official site lists SW500 as a separate movement family and lists day, date, and chronograph as supported function categories. We need the exact SW500 day-date technical sheet and variant code before recording a complete specification.

Source: https://sellita.ch/index.php/en/movements

## What this means for C-01

1. Day + date + automatic chronograph is a demonstrated mechanical architecture, not an unproven combination.
2. A 60–70 h reserve is an ambitious target. The 7750's 54 h typical figure and SW510's 62 h typical figure provide realistic reference points, but neither proves what a new C-01 can achieve.
3. A 4 Hz oscillator is established in these benchmark movements.
4. The 7750's cam-operated chronograph shows that a column wheel is not a functional necessity. We must compare control feel, robustness, adjustment, parts count, and service burden with evidence.
5. The benchmark chronograph architecture must be examined as a whole: coupling, switching, brake, heart cams, reset hammers, counters, and power draw.
6. The day-date calendar is an integrated design challenge. We need to investigate calendar torque, changeover timing, quick-setting safety, and the additional energy demand.

## Preliminary architecture direction — not a design freeze

Keep the following as open candidates:
- Integrated chronograph versus modular chronograph.
- Cam versus column-wheel control.
- Vertical versus horizontal coupling.
- Day/date discs versus alternate display layouts.
- Single barrel versus alternative energy-storage arrangements.

Do not select vertical clutch or column wheel solely because they sound premium. The final architecture must be justified by calculations, teardown study, service evidence, and prototype tests.

## Correction log\n\nRevision 0.2 corrects the Sellita benchmark identification: SW500 a is the day-date variant; SW500 b is date-only. The initial draft mistakenly attributed the day-date investigation to the SW500 family without recording the exact variant, and incorrectly implied SW510 might be the relevant day-date family. The SW500 a variant is now explicitly identified from Sellita's published catalogue.\n\n## Next work package

**WP-02: Functional teardown and energy budget**
- Map the 7750 chronograph sequence from pusher actuation through coupling, brake release, running, stopping, and reset.
- Map day/date drive and correction path.
- Identify the base timekeeping train and energy path.
- Compare exact SW500 day-date documentation when obtained.
- Create a first-pass C-01 power and torque budget.
- Record which design improvements are measurable and testable.

## Decision still open

C-01 remains a new movement design. The 7750 is a benchmark, not a donor movement commitment or a claim of originality. Any use of licensed, sourced, or third-party components must be explicit in the eventual design and product documentation.
