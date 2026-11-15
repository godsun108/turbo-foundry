# TRICORDER local data tool

A dependency-free Python standard-library tool for generating clearly labelled
synthetic observations and validating newline-delimited JSON (JSONL) records.

## Requirements

- Python 3.10 or newer
- No third-party packages
- No network access

## Generate a sample dataset

From this directory:

```sh
python tricorder.py simulate --count 100 --seed 7 --output sample.jsonl
python tricorder.py validate sample.jsonl
```

The simulator creates synthetic temperature, humidity, pressure, and light
records. Every record is marked `uncalibrated`, has a null calibration ID,
and states that it is synthetic. Do not use it as a substitute for sensor data.

## Run tests

```sh
python -m unittest -v
```

## Contract

The normative field shape is in `observation.schema.json`. The Python
validator additionally enforces timezone-aware timestamps, finite numeric
values, supported quality states, and rejection of unknown fields.

## Data and safety boundaries

- JSONL is append-friendly and easy to inspect or process offline.
- This tool has no device-control functionality.
- It does not calibrate sensors or certify accuracy.
- It makes no air-quality, medical, potable-water, or life-safety claims.
- Physical sensor adapters must preserve device/sensor identity, units,
  timestamp, quality status, and calibration provenance.
- Keep exported records read-only when passing them to Genesis in the
  initial integration phase.
