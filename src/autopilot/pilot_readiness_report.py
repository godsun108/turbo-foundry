"""Evidence-driven, offline Foundry pilot readiness report.

Reads a local JSON evidence register and refuses to silently approve
production based on synthetic tests, empty citations, or unauthenticated claims.
Never talks to providers, sends messages, deploys, or charges money.
"""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path

from .commercial_release_gate import (
    EvidenceItem, REQUIRED_FOR_DISCOVERY, REQUIRED_FOR_LIVE_PILOT,
    assess_release,
)

KEYS = frozenset(REQUIRED_FOR_DISCOVERY + REQUIRED_FOR_LIVE_PILOT)


def evaluate_evidence(raw: object) -> dict:
    if not isinstance(raw, dict):
        raise ValueError("evidence register must be a JSON object")
    if set(raw) - KEYS:
        raise ValueError("unknown evidence key(s): " + ", ".join(sorted(set(raw) - KEYS)))
    checked = {}
    for key, value in raw.items():
        if not isinstance(value, dict) or set(value) != {"passed", "reference", "verified_by"}:
            raise ValueError(f"invalid evidence record for {key}")
        if (type(value["passed"]) is not bool
                or not isinstance(value["reference"], str)
                or not isinstance(value["verified_by"], str)
                or len(value["reference"]) > 500
                or len(value["verified_by"]) > 100):
            raise ValueError(f"invalid evidence types for {key}")
        checked[key] = EvidenceItem(**value)
    assessment = assess_release(checked)
    return {
        "schema_version": 1,
        "discovery_ready": assessment.discovery_ready,
        "live_pilot_ready": assessment.live_pilot_ready,
        "missing_discovery": list(assessment.missing_discovery),
        "missing_live_pilot": list(assessment.missing_live_pilot),
        "verified_discovery_count": len(REQUIRED_FOR_DISCOVERY) - len(assessment.missing_discovery),
        "verified_live_pilot_count": len(REQUIRED_FOR_LIVE_PILOT) - len(assessment.missing_live_pilot),
        "required_discovery_count": len(REQUIRED_FOR_DISCOVERY),
        "required_live_pilot_count": len(REQUIRED_FOR_LIVE_PILOT),
        "warning": "Human-provided evidence is NOT independently authenticated by this offline tool; security review required.",
    }


def render_report(result: dict) -> str:
    def lines(keys):
        return "".join(f"- [ ] `{key}`\n" for key in keys) or "- None reported\n"
    return (
        "# Foundry customer pilot release gate\n\n"
        "**This report does not authorize live messaging, production rollout, payment collection, or new expenses.**\n\n"
        f"**Discovery:** {'READY FOR HUMAN REVIEW' if result['discovery_ready'] else 'BLOCKED'} "
        f"({result['verified_discovery_count']}/{result['required_discovery_count']} claimed proofs)\n\n"
        f"**Live paid pilot:** {'READY FOR INDEPENDENT APPROVAL REVIEW' if result['live_pilot_ready'] else 'NO-GO'} "
        f"({result['verified_live_pilot_count']}/{result['required_live_pilot_count']} claimed proofs)\n\n"
        "## Missing discovery proof\n\n" + lines(result["missing_discovery"]) +
        "\n## Missing live pilot proof\n\n" + lines(result["missing_live_pilot"]) +
        "\n## Limitations\n\n" + result["warning"] + "\n"
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Offline release assessment; fail closed")
    parser.add_argument("--evidence", type=Path, help="Local JSON evidence register; do not commit customer secrets")
    parser.add_argument("--markdown", type=Path, help="Optional Markdown report destination")
    parser.add_argument("--json", dest="json_output", type=Path, help="Optional JSON report destination")
    args = parser.parse_args(argv)
    try:
        raw = json.loads(args.evidence.read_text(encoding="utf-8")) if args.evidence else {}
        result = evaluate_evidence(raw)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(f"cannot assess evidence: {exc}")
    if args.markdown:
        args.markdown.write_text(render_report(result), encoding="utf-8")
    if args.json_output:
        args.json_output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if not args.markdown and not args.json_output:
        print(render_report(result))
    return 0 if result["live_pilot_ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
