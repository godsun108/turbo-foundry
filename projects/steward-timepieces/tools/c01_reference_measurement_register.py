#!/usr/bin/env python3
"""Create and validate a traceable reference-movement measurement CSV.

Blank template rows contain no design or measurement data. The tool validates
record structure and evidence traceability; it does not establish measurement
accuracy, calibration validity, physical fit, or C-01 design approval.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable

FIELDS = [
    "observation_id", "caliber", "variant", "specimen_id", "part_interface_id",
    "parameter", "value", "unit", "datum", "method", "instrument",
    "instrument_resolution", "calibration_status", "uncertainty",
    "evidence_class", "source_document", "source_revision", "operator",
    "reviewer", "measurement_date", "notes",
]
EVIDENCE_CLASSES = {
    "manufacturer_published", "supplier_confirmed", "measured",
    "calculated", "provisional", "tbd",
}
REQUIRED = [
    "observation_id", "caliber", "variant", "part_interface_id",
    "parameter", "unit", "evidence_class", "source_document",
]


def blank_record() -> dict[str, str]:
    return {field: "" for field in FIELDS}


def create_template(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerow(blank_record())


def validate_records(records: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    seen: set[str] = set()
    for row_number, record in enumerate(records, start=2):
        if not any((record.get(field) or "").strip() for field in FIELDS):
            continue  # untouched template row
        for field in REQUIRED:
            if not (record.get(field) or "").strip():
                errors.append({"row": str(row_number), "field": field, "error": "required"})
        observation_id = (record.get("observation_id") or "").strip()
        if observation_id:
            if observation_id in seen:
                errors.append({"row": str(row_number), "field": "observation_id", "error": "duplicate"})
            seen.add(observation_id)
        evidence = (record.get("evidence_class") or "").strip()
        if evidence and evidence not in EVIDENCE_CLASSES:
            errors.append({"row": str(row_number), "field": "evidence_class", "error": "unsupported_value"})
        if evidence == "measured":
            for field in ("specimen_id", "datum", "method", "instrument",
                          "instrument_resolution", "calibration_status",
                          "uncertainty", "operator", "measurement_date"):
                if not (record.get(field) or "").strip():
                    errors.append({"row": str(row_number), "field": field, "error": "required_for_measured"})
        if evidence in {"manufacturer_published", "supplier_confirmed"} and not (
            (record.get("source_revision") or "").strip()
        ):
            errors.append({"row": str(row_number), "field": "source_revision", "error": "required_for_documented_source"})
        value = (record.get("value") or "").strip()
        if value:
            try:
                float(value)
            except ValueError:
                errors.append({"row": str(row_number), "field": "value", "error": "must_be_numeric"})
    return errors


def validate_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDS:
            return [{"row": "1", "field": "header", "error": "field_order_or_names_mismatch"}]
        return validate_records(reader)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--create-template", type=Path)
    parser.add_argument("--validate", type=Path)
    args = parser.parse_args()
    if args.create_template:
        create_template(args.create_template)
        print(json.dumps({"created": str(args.create_template), "fields": FIELDS}, indent=2))
        return 0
    if args.validate:
        errors = validate_csv(args.validate)
        print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
        return 1 if errors else 0
    parser.error("choose --create-template or --validate")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
