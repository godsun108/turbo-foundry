# TRICORDER hardware candidate review — 0.1

**Status:** Desk research; no components selected or purchased  
**Applies to:** SFTI-TRI-001 first bench demonstrator  
**Decision rule:** Prefer documented interfaces, independent verification, local operation, replaceable modules, and honest measurement limits.

## Recommended architecture for the first bench build

1. **Controller candidate — ESP32-S3 development board.** Use it as a replaceable acquisition controller, not as a cloud requirement. The SoC has dual LX7 cores, USB OTG, I²C/SPI/UART and integrated Wi-Fi/Bluetooth LE. Keep radios disabled in the baseline offline test; connectivity can be enabled later as an optional transport. Board-specific power draw, flash/PSRAM configuration, regulator losses, and pin availability must be measured before selecting a board.
2. **Environmental baseline — Bosch BME280 breakout.** One module provides temperature, relative humidity, and barometric pressure over I²C or SPI. Bosch lists 3.6 µA typical at 1 Hz for humidity/pressure/temperature, but breakout-board regulators and pull-ups can dominate system consumption. Humidity tolerance is ±3% RH, so do not market this as a precision humidity reference.
3. **Optional humidity comparison — Sensirion SHT45 breakout.** Sensirion lists typical ±1% RH and ±0.1 °C temperature accuracy, I²C, 1.08–3.6 V supply, and very low average sensor current. This is a candidate for a higher-accuracy temperature/humidity channel or cross-check; it does not measure pressure.
4. **Optional particulate channel — Sensirion SPS30.** The manufacturer specifies PM1.0/PM2.5/PM4/PM10 outputs, 4.5–5.5 V supply, 55 mA average and 80 mA maximum current, I²C/UART, and a 1-second sampling interval. Treat it as a separately powered module with a measured duty cycle; it is not a suitable always-on choice for a tiny battery node without a power budget. It measures particulate matter, not every gas or pollutant.
5. **Ambient light — defer.** Add only after a candidate module is reviewed for range, spectral response, saturation, interface, and calibration method.

## Candidate comparison

| Function | Candidate | Published specification useful to design | Trade-off |
|---|---|---|---|
| Controller | ESP32-S3 | Dual-core MCU; USB OTG; I²C/SPI/UART; Wi-Fi and BLE | Radio capability must not become a network dependency; board power varies |
| Temperature / RH / pressure | Bosch BME280 | 3.6 µA typical at 1 Hz for H/P/T; RH tolerance ±3%; I²C/SPI | Compact integrated baseline; humidity accuracy is moderate |
| Temperature / RH comparison | Sensirion SHT45 | Typical ±1% RH / ±0.1 °C; I²C; 1.08–3.6 V | Better stated RH/T accuracy; pressure requires another sensor |
| Particulate matter | Sensirion SPS30 | PM1/2.5/4/10; 4.5–5.5 V; 55 mA average; I²C/UART | Stronger PM channel, but power and physical size are significant |

## First prototype recommendation

For the first low-complexity bench demonstrator, start with an ESP32-S3 board plus a BME280 breakout, USB power, and a local serial/USB interface. Add local removable storage only after selecting and testing the board's storage interface. Keep the SPS30 as a separately powered optional module for a later power-characterization experiment. Add the SHT45 only if the BME280 humidity performance is insufficient for the intended use.

This is a candidate architecture, not a final bill of materials. No prices, supplier stock, or board-specific electrical characteristics have been verified here.

## Verification plan before purchase or enclosure design

- Record exact manufacturer, part number, breakout vendor, schematic, and revision for each candidate.
- Check logic levels, pull-up voltage, pin conflicts, bus addresses, connector orientation, and current peaks on the actual breakout.
- Measure whole-board current in active, idle, and deep-sleep states; do not substitute chip-only datasheet current for board-level power.
- Compare BME280 and SHT45 temperature/RH readings side by side after thermal stabilization; document conditions and disagreement.
- Compare pressure against a suitable reference and account for altitude/weather differences.
- For SPS30, measure startup current, steady-state current, warm-up/stabilization, fan behavior, and results against an appropriate reference instrument.
- Preserve raw readings and instrument metadata. Do not silently offset or smooth measurements to force agreement.
- Keep all initial tests at USB/low-voltage levels. Battery charging, enclosure thermal behavior, and any mains-connected equipment require separate review.

## Primary manufacturer sources

- Espressif ESP32-S3 overview: https://www.espressif.com/en/products/socs/esp32-s3/
- Espressif ESP32-S3 datasheet: https://documentation.espressif.com/esp32-s3_datasheet_en.pdf
- Bosch BME280 product page: https://www.bosch-sensortec.com/en/products/environmental-sensors/humidity-sensors-bme280
- Bosch BME280 datasheet: https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf
- Sensirion SHT45 product page: https://sensirion.com/products/catalog/SHT45
- Sensirion SPS30 product page: https://sensirion.com/sps30
- Sensirion SPS30 datasheet: https://sensirion.com/en/media/documents/8600FF88/64A3B8D6/Sensirion_PM_Sensors_Datasheet_SPS30.pdf

## Open decisions

- Exact ESP32-S3 development board and memory configuration.
- BME280-only baseline versus BME280 + SHT45 comparison.
- Whether particulate sensing belongs in the portable unit or a separately powered accessory.
- Local storage medium and connector strategy.
- Enclosure, ingress protection, airflow, thermal isolation, and serviceability.
- Target sampling intervals and measured battery-life requirement.
