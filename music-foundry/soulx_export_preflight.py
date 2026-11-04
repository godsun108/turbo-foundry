#!/usr/bin/env python3
"""Preflight canonical vocal scores for a safe SoulX-Singer export.

This deliberately does not generate SoulX metadata. SoulX's word/phoneme
segmentation and note-type semantics must be explicitly authored before a
lossless translator can be enabled.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SUNG = {"sung", "chant"}
NOTE_TYPES = {"normal", "tie", "rest", "slur"}


def preflight(score: Any) -> list[str]:
    blockers: list[str] = []
    if not isinstance(score, dict):
        return ["score root must be an object"]
    if score.get("tempo_status") != "locked":
        blockers.append("tempo_status must be locked")
    if score.get("score_status") != "reviewed":
        blockers.append("score_status must be reviewed")
    phrases = score.get("phrases")
    if not isinstance(phrases, list):
        return blockers + ["phrases must be an array"]

    sung_phrases = [p for p in phrases if isinstance(p, dict) and p.get("delivery") in SUNG]
    if not sung_phrases:
        blockers.append("no sung or chant phrases are present")
    for phrase in sung_phrases:
        pid = phrase.get("id", "<unknown>")
        if phrase.get("alignment_status") != "reviewed":
            blockers.append(f"{pid}: phrase must be human-reviewed")
        if phrase.get("start_beat") is None or phrase.get("duration_beats") is None:
            blockers.append(f"{pid}: phrase timing is incomplete")
        syllables = phrase.get("syllables")
        if not isinstance(syllables, list) or not syllables:
            blockers.append(f"{pid}: syllable map is missing")
            continue
        for index, syllable in enumerate(syllables):
            label = f"{pid}.syllables[{index}]"
            if not isinstance(syllable, dict):
                blockers.append(f"{label}: entry must be an object")
                continue
            if not isinstance(syllable.get("phoneme"), str) or not syllable["phoneme"].strip():
                blockers.append(f"{label}: reviewed phoneme string is missing")
            if syllable.get("onset_beats") is None or syllable.get("duration_beats") is None:
                blockers.append(f"{label}: onset/duration alignment is incomplete")
            notes = syllable.get("notes")
            if not isinstance(notes, list) or not notes:
                blockers.append(f"{label}: note events are missing")
                continue
            for ni, note in enumerate(notes):
                if not isinstance(note, dict) or note.get("note_type") not in NOTE_TYPES:
                    blockers.append(f"{label}.notes[{ni}]: canonical note type is missing or invalid")

    # These are explicit format gaps, not values the exporter may guess.
    blockers.append("SoulX word-boundary segmentation is not represented in the canonical score yet")
    blockers.append("canonical-to-SoulX note_type mapping has not been verified against the official parser")
    blockers.append("SoulX segment grouping and time-boundary policy still require an authored export profile")
    return blockers


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("score", type=Path)
    args = parser.parse_args()
    try:
        score = json.loads(args.score.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read score: {exc}", file=sys.stderr)
        return 2
    blockers = preflight(score)
    if blockers:
        print("SoulX export blocked; no metadata was generated:")
        for blocker in blockers:
            print(f"- {blocker}")
        return 1
    print("SoulX export preflight passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
