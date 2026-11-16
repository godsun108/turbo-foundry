# SFTI-SEN-003 — SENTINEL

**Status:** Requirements / architecture planning  
**Maturity:** M0  
**Priority:** P0  
**System class:** Low-power environmental monitoring node

## Mission
Build a reliable environmental monitoring node that can collect measurements over time, buffer data locally during connectivity loss, and synchronize to a dashboard when a network is available.

## First demonstrator
One indoor or sheltered node measuring temperature, relative humidity, light, and soil moisture. Reuse TRICORDER's observation schema and calibration conventions.

## Architecture
- Sensor modules with per-sensor metadata.
- Low-power controller with watchdog and brownout-aware storage.
- Local timestamping and monotonic sequence numbers.
- Store-and-forward queue with bounded storage and explicit overflow behavior.
- Optional network transport; no network required for acquisition.
- Read-only dashboard with device health, last-seen time, sensor status, and data export.
- Human-configured thresholds; alerts are advisory.

## Acceptance criteria
1. Node records observations during network outage and synchronizes them after reconnection.
2. Duplicate transmissions can be detected using device ID and sequence number.
3. Clock uncertainty and time synchronization state are recorded.
4. Sensor fault, stale data, low battery, and storage pressure are distinct statuses.
5. Firmware update and restart behavior are documented and recoverable.
6. Data export retains original timestamps, units, calibration IDs, and quality flags.
7. Threshold alerts identify their source measurement and never claim certified hazard detection.

## Safety and privacy
Monitoring-only initial release. No irrigation, heating, ventilation, or other physical control. Avoid collecting audio, images, personal identifiers, or unrelated location data. Network credentials are stored securely and never committed to source control.

## Reuse from TRICORDER
SENTINEL should reuse the observation schema, sensor driver interface, calibration record format, parser tests, append-only local store, and read-only sensor-health summary. The shared Python reference implementation currently lives in `research/sfti/tools/tricorder/`:

- `observation.schema.json` — versioned observation contract.
- `tricorder.py` — simulator and validator.
- `tricorder_store.py` — single-writer JSONL store with sequence numbers, SHA-256 record checksums, fsync on append, and recovery of an incomplete trailing write.
- `sensor_health.py` — advisory per-sensor health summary.

SENTINEL should import these shared modules rather than fork them. The present store is a prototype: it is not a multi-process database, signed audit log, or certified safety system. Any future change to storage semantics must preserve the original observation and provenance fields or introduce a documented schema migration.
