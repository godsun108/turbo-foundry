# WP-02 — Functional Teardown Notes and Design Risks

**Revision:** 0.1  
**Status:** Desk-study notes; not a substitute for controlled manufacturer service documentation.

## 1. Reference movement confirmed

ETA's current 7750 product information confirms the exact function set:
- Automatic winding, unidirectional.
- Hours, minutes, small seconds.
- Day and date windows, slow-switching.
- Chronograph counters: 60 seconds, 30 minutes, 12 hours.
- Cam-operated chronograph, two pushers.
- Quick correction of day and date.
- Stop-second time setting.
- 4 Hz, 25 jewels, 54 h typical reserve.
- 30.00 mm diameter, 7.90 mm height.

Manufacturer source: https://portal.eta.ch/en/7750-7750-5.html

ETA technical communication CT 7750 FDE 465595 18 (14 August 2026) is available at:
https://portal.eta.ch/fr/technicaldocuments/index/pdf/id/2081/

## 2. Functional subsystems to map

### Timekeeping and energy
- Mainspring and barrel deliver torque to the going train.
- Going train drives the escapement and oscillator.
- Automatic winding replenishes mainspring energy.
- Chronograph operation introduces an additional load through the chronograph train and coupling.
- C-01 must be tested in both chronograph-off and chronograph-running states at multiple states of wind.

We do not yet have verified tooth counts, gear ratios, barrel torque curves, balance amplitude data, or measured chronograph load. Do not estimate these as facts.

### Chronograph
Map the complete sequence:
1. Pusher input.
2. Switching mechanism changes state.
3. Chronograph brake releases.
4. Coupling engages the chronograph train.
5. Central seconds and minute/hour counters advance.
6. Stop command disengages coupling and applies brake.
7. Reset command releases the hands and reset hammers return heart cams to zero.

The precise component sequence, clearances, spring forces, and lubrication must be taken from the controlled service documentation and confirmed by teardown.

### Day/date calendar
The ETA reference includes two separate calendar indications. Its service information warns that rapid day/date correction must not be attempted while the calendar driving mechanism is engaged during the changeover period. This is a significant human-factors and durability requirement.

Design implications for C-01:
- Clearly define a safe setting procedure.
- Consider a setting interlock or slip-protection strategy, but evaluate complexity and failure modes.
- Test correction behavior near the changeover interval.
- Test calendar operation with chronograph running.
- Define day/date advance torque and spring loads.
- Avoid promising instant or independently adjustable switching unless designed and tested.

Supporting sources:
- ETA 7750 technical communication, calendar and hour-counter assembly information: https://www.beco-technic.ch/media/8a/b8/1e/1619813316/eta_7750-7760_fr_de_en.pdf
- AWCI technical article discussing 7750 day/date driving fingers and quick-set caution: https://www.awci.com/wp-content/uploads/ht/2005/2005-10-web.pdf
- ETA current product specification: https://portal.eta.ch/en/7750-7750-5.html

## 3. Early engineering risks

| Risk | Why it matters | Proposed investigation |
|---|---|---|
| Chronograph load reduces balance amplitude | Can change rate while timing | Measure amplitude/rate with chrono off/on at full and low wind |
| Calendar torque peak at midnight | Can disturb timekeeping or cause incomplete switching | Measure torque and rate during calendar changeover |
| Unsafe quick-set during engagement | Can damage calendar components | Define interlock/slip protection and misuse test |
| Reset hammer/heart-cam wear | Can degrade zero return | Repeated reset endurance and return-error measurement |
| Coupling drag or engagement shock | Can cause hand jump and rate disturbance | High-speed observation and amplitude measurement |
| Excessive component count | Raises assembly and service burden | Parts-count and service-time comparison |
| Long reserve target | Larger barrel or lower energy consumption may affect layout and torque curve | Full barrel/gear-train energy budget |

## 4. Accuracy and durability test matrix — draft

| Test condition | Measurements |
|---|---|
| Chronograph stopped, full wind | Rate, amplitude, beat error |
| Chronograph running, full wind | Rate and amplitude delta |
| Chronograph stopped, mid reserve | Rate, amplitude |
| Chronograph running, mid reserve | Rate and amplitude delta |
| Chronograph running, near end of reserve | Rate, amplitude, stoppage margin |
| Calendar changeover | Rate, amplitude, successful day/date advance |
| Start/stop/reset endurance | Pusher force, function reliability, hand return error |
| Shock exposure | Post-test rate, function, inspection findings |
| Temperature exposure | Rate, lubrication behavior, calendar and chronograph function |

Numerical acceptance thresholds must be established after the architecture and oscillator are defined. The proposed −4/+6 s/day target is not yet a complete test specification.

## 5. Current design conclusion

The ETA 7750 proves that the function combination is technically mature. It also gives C-01 important lessons:
- Do not assume column wheel is necessary; the benchmark is cam-operated.
- Calendar safety is a genuine design issue, not a minor user-manual footnote.
- A 60–70 hour reserve target must be justified by energy calculations, not chosen by aspiration alone.
- Accuracy must be measured with the chronograph engaged and through calendar changeover, not only in a static time-only test.

## 6. Immediate next actions

1. Obtain controlled ETA service documentation and identify exact version/revision.
2. Obtain the exact Sellita SW500 day-date technical sheet and variant code.
3. Build a function/block diagram from manufacturer drawings.
4. Record gear ratios and tooth counts only from legible, verified drawings or direct measurement.
5. Create a spreadsheet or script-based energy budget once barrel and train data are available.
6. Conduct an architecture review before choosing integrated/modular, cam/column wheel, or coupling type.
