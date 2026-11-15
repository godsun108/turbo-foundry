# SFTI-TRI-001 — TRICORDER

**Status:** Requirements / bench-prototype planning  
**Maturity:** M0 → M1 target  
**Priority:** P0  
**System class:** Low-voltage, portable, non-certified scientific instrument

## Mission
Create a modular, locally operable scientific instrument that collects environmental measurements, reports units and uncertainty, preserves calibration metadata, and can be extended with additional sensor modules. Genesis may explain observations but must not turn unvalidated readings into safety, medical, or regulatory claims.

## First demonstrator scope
Initial bench configuration:
- Temperature and relative humidity.
- Barometric pressure.
- Ambient light.
- One particulate or air-quality indicator module selected after a sensor accuracy and interface review.
- Local display or phone-connected local interface.
- Timestamped local data logging.
- Sensor identity, firmware version, calibration status, and health flags.

Explicitly deferred: certified toxic-gas detection, potable-water certification, medical diagnosis, radiation protection, autonomous interventions, and cloud dependence.

## System architecture
1. **Sensor layer:** Replaceable modules with documented range, resolution, accuracy, warm-up, drift, environmental limits, and interface.
2. **Acquisition layer:** Microcontroller samples sensors, validates ranges, timestamps observations, and reports sensor faults.
3. **Power layer:** Protected low-voltage supply; battery chemistry and charging design reviewed before enclosure integration.
4. **Local interface:** Displays values with units, freshness, and status. No network required for basic acquisition.
5. **Data layer:** Append-only local records in a documented format (JSON Lines or CSV plus metadata).
6. **Interpretation layer:** Genesis consumes exported observations and metadata; it must preserve uncertainty and distinguish measurement from inference.
7. **Extension interface:** Each sensor module has a versioned capability description and calibration record.

## Observation record (minimum fields)
- schema_version
- device_id
- sensor_id
- sensor_model
- measurement
- value
- unit
- observed_at
- quality_status (valid, stale, out_of_range, sensor_fault, uncalibrated)
- calibration_id (nullable)
- accuracy_statement
- firmware_version

## Acceptance tests
1. Every measurement includes value, unit, timestamp, sensor identity, and quality status.
2. Disconnecting a sensor produces a visible fault, not a plausible-looking zero.
3. Stale data is clearly marked and never presented as current.
4. At least 100 consecutive records can be exported and parsed without loss or malformed entries.
5. Temperature/humidity readings are compared against a suitable reference instrument; observed differences and reference uncertainty are documented.
6. Basic acquisition and local display/logging work with internet and cellular connectivity disabled.
7. Power loss does not silently corrupt the last completed record; recovery behavior is tested.
8. Sensor replacement does not silently reuse another sensor's calibration metadata.

## Design constraints
- Prefer documented, replaceable modules and common interfaces.
- Keep sensor drivers separate from presentation and AI interpretation.
- Use units explicitly; store raw values without rounding away useful precision.
- Make calibration status and measurement age visible.
- Do not make life-safety claims from hobby-grade modules.
- Do not expose control outputs in the first demonstrator.

## Next engineering tasks
1. Compare candidate MCU boards by power, local storage, interface support, documentation, and long-term availability.
2. Select reference instruments and define calibration/verification procedure.
3. Create the observation schema and parser tests.
4. Build a sensor simulator for offline software development before hardware arrives.
5. Draft enclosure and power architecture only after component selection.
6. Run a bench test and publish raw observations, analysis, and limitations.

## Integration boundary
The initial TRICORDER is a standalone instrument. Genesis integration begins with read-only import/export of observation records. No physical actuation or device-control permission is included.
