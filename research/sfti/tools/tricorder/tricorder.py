#!/usr/bin/env python3
"""Local-first TRICORDER observation simulator and validator.

Uses only the Python standard library. Simulated observations are explicitly
labelled and must never be confused with physical measurements.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = "1.0.0"
QUALITY = {"valid", "stale", "out_of_range", "sensor_fault", "uncalibrated"}


def validate_observation(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version", "device_id", "sensor_id", "sensor_model",
        "measurement", "value", "unit", "observed_at", "quality_status",
        "calibration_id", "accuracy_statement", "firmware_version",
    }
    missing = required - record.keys()
    extra = record.keys() - required
    if missing:
        errors.append("missing fields: " + ", ".join(sorted(missing)))
    if extra:
        errors.append("unknown fields: " + ", ".join(sorted(extra)))
    if record.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    for key, limit in (
        ("device_id", 128), ("sensor_id", 128), ("sensor_model", 128),
        ("measurement", 128), ("unit", 32), ("accuracy_statement", 512),
        ("firmware_version", 64),
    ):
        value = record.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{key} must be a non-empty string")
        elif len(value) > limit:
            errors.append(f"{key} exceeds {limit} characters")
    value = record.get("value")
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        errors.append("value must be a finite number")
    status = record.get("quality_status")
    if not isinstance(status, str) or status not in QUALITY:
        errors.append("quality_status is not a supported status")
    calibration = record.get("calibration_id")
    if calibration is not None and (
        not isinstance(calibration, str) or len(calibration) > 128
    ):
        errors.append("calibration_id must be null or a string up to 128 characters")
    timestamp = record.get("observed_at")
    if not isinstance(timestamp, str):
        errors.append("observed_at must be an ISO-8601 date-time string")
    else:
        try:
            parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                errors.append("observed_at must include a timezone")
        except ValueError:
            errors.append("observed_at must be a valid ISO-8601 date-time")
    return errors


def simulated_records(count: int, seed: int = 7) -> Iterable[dict[str, Any]]:
    if count < 1 or count > 100_000:
        raise ValueError("count must be between 1 and 100000")
    rng = random.Random(seed)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    sensors = [
        ("temp-01", "simulated-temperature", "temperature", "degC", 24.0, 0.35),
        ("rh-01", "simulated-humidity", "relative_humidity", "%RH", 55.0, 1.5),
        ("pressure-01", "simulated-pressure", "pressure", "hPa", 1013.0, 0.8),
        ("light-01", "simulated-light", "illuminance", "lux", 320.0, 18.0),
    ]
    for index in range(count):
        sensor_id, model, measurement, unit, center, spread = sensors[index % len(sensors)]
        yield {
            "schema_version": SCHEMA_VERSION,
            "device_id": "tricorder-sim-001",
            "sensor_id": sensor_id,
            "sensor_model": model,
            "measurement": measurement,
            "value": round(rng.gauss(center, spread), 3),
            "unit": unit,
            "observed_at": (now + timedelta(seconds=index)).isoformat().replace("+00:00", "Z"),
            "quality_status": "uncalibrated",
            "calibration_id": None,
            "accuracy_statement": "Synthetic test data; no physical sensor accuracy is claimed.",
            "firmware_version": "simulator-0.1.0",
        }


def read_jsonl(path: Path) -> Iterable[tuple[int, dict[str, Any] | None, str | None]]:
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError("record must be a JSON object")
                yield line_number, value, None
            except (json.JSONDecodeError, ValueError) as exc:
                yield line_number, None, str(exc)


def command_simulate(args: argparse.Namespace) -> int:
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as stream:
        for record in simulated_records(args.count, args.seed):
            errors = validate_observation(record)
            if errors:
                raise RuntimeError("internal simulator produced invalid record: " + "; ".join(errors))
            stream.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
    print(f"Wrote {args.count} synthetic observations to {output}")
    print("NOTICE: synthetic data only; this is not a physical measurement.")
    return 0


def command_validate(args: argparse.Namespace) -> int:
    path = Path(args.input)
    total = 0
    invalid = 0
    for line_number, record, parse_error in read_jsonl(path):
        total += 1
        errors = [f"invalid JSON: {parse_error}"] if parse_error else validate_observation(record or {})
        if errors:
            invalid += 1
            for error in errors:
                print(f"{path}:{line_number}: {error}", file=sys.stderr)
    print(f"Validated {total} records; {invalid} invalid.")
    return 1 if invalid else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    simulate = subparsers.add_parser("simulate", help="write synthetic JSONL observations")
    simulate.add_argument("--count", type=int, default=100)
    simulate.add_argument("--seed", type=int, default=7)
    simulate.add_argument("--output", default="tricorder-sample.jsonl")
    simulate.set_defaults(func=command_simulate)
    validate = subparsers.add_parser("validate", help="validate a JSONL observation file")
    validate.add_argument("input")
    validate.set_defaults(func=command_validate)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return args.func(args)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
