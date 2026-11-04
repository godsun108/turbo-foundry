#!/usr/bin/env python3
"""Read-only readiness check for the deterministic SoulX score-control exporter."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from soulx_export import build_metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("score", type=Path)
    args = parser.parse_args()
    try:
        score = json.loads(args.score.read_text(encoding="utf-8"))
        metadata = build_metadata(score)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"SoulX export blocked; no metadata was written:\n{exc}")
        return 1
    print(f"SoulX score-control preflight passed ({len(metadata)} segment(s)); no files written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
