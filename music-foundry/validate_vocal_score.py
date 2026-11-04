#!/usr/bin/env python3
"""Dependency-free validator for Music Foundry's canonical vocal score."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


DELIVERIES = {"spoken", "chant", "sung", "gang_shout", "whisper", "adlib"}
ALIGNMENTS = {"unaligned", "phrase_aligned", "syllable_aligned", "reviewed"}
NOTE_TYPES = {"normal", "tie", "rest", "slur"}
SUNG_DELIVERIES = {"sung", "chant"}


def _number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate_score(score: Any, require_singing_ready: bool = False) -> list[str]:
    errors: list[str] = []
    if not isinstance(score, dict):
        return ["score root must be an object"]

    required = ("schema", "project_id", "source_ref", "tempo_bpm", "tempo_status",
                "meter", "ppq", "score_status", "phrases")
    for key in required:
        if key not in score:
            errors.append(f"missing required root field: {key}")

    if score.get("schema") != "turbo.music-foundry.vocal-score.v1":
        errors.append("unsupported or missing schema identifier")
    if not isinstance(score.get("project_id"), str) or not score.get("project_id", "").strip():
        errors.append("project_id must be a non-empty string")
    if not isinstance(score.get("source_ref"), str) or not score.get("source_ref", "").strip():
        errors.append("source_ref must be a non-empty string")
    if not _number(score.get("tempo_bpm")) or score["tempo_bpm"] <= 0:
        errors.append("tempo_bpm must be a positive finite number")
    if score.get("tempo_status") not in {"provisional", "locked"}:
        errors.append("tempo_status must be provisional or locked")
    if not isinstance(score.get("meter"), str) or "/" not in score.get("meter", ""):
        errors.append("meter must be a fraction-like string such as 4/4")
    if not isinstance(score.get("ppq"), int) or isinstance(score.get("ppq"), bool) or score["ppq"] < 1:
        errors.append("ppq must be a positive integer")
    if score.get("score_status") not in {"scaffold", "phrase_aligned", "syllable_aligned", "reviewed"}:
        errors.append("invalid score_status")

    phrases = score.get("phrases")
    if not isinstance(phrases, list):
        return errors + ["phrases must be an array"]

    seen_ids: set[str] = set()
    for index, phrase in enumerate(phrases):
        label = f"phrases[{index}]"
        if not isinstance(phrase, dict):
            errors.append(f"{label} must be an object")
            continue
        phrase_id = phrase.get("id")
        if not isinstance(phrase_id, str) or not phrase_id.strip():
            errors.append(f"{label}.id must be a non-empty string")
        elif phrase_id in seen_ids:
            errors.append(f"{label}.id is duplicated: {phrase_id}")
        else:
            seen_ids.add(phrase_id)
        if not isinstance(phrase.get("text"), str) or not phrase.get("text", "").strip():
            errors.append(f"{label}.text must be non-empty")
        if phrase.get("delivery") not in DELIVERIES:
            errors.append(f"{label}.delivery is invalid")
        if not isinstance(phrase.get("layer"), str) or not phrase.get("layer", "").strip():
            errors.append(f"{label}.layer must be non-empty")
        alignment = phrase.get("alignment_status")
        if alignment not in ALIGNMENTS:
            errors.append(f"{label}.alignment_status is invalid")
        syllables = phrase.get("syllables")
        if not isinstance(syllables, list):
            errors.append(f"{label}.syllables must be an array")
            syllables = []

        start, duration = phrase.get("start_beat"), phrase.get("duration_beats")
        if start is not None and (not _number(start) or start < 0):
            errors.append(f"{label}.start_beat must be null or a non-negative finite number")
        if duration is not None and (not _number(duration) or duration <= 0):
            errors.append(f"{label}.duration_beats must be null or a positive finite number")
        if alignment in {"phrase_aligned", "syllable_aligned", "reviewed"} and (start is None or duration is None):
            errors.append(f"{label} claims phrase alignment but lacks start_beat or duration_beats")
        if alignment in {"syllable_aligned", "reviewed"} and not syllables:
            errors.append(f"{label} claims syllable alignment but has no syllable entries")

        for si, syllable in enumerate(syllables):
            slabel = f"{label}.syllables[{si}]"
            if not isinstance(syllable, dict):
                errors.append(f"{slabel} must be an object")
                continue
            if not isinstance(syllable.get("text"), str) or not syllable.get("text", "").strip():
                errors.append(f"{slabel}.text must be non-empty")
            phoneme = syllable.get("phoneme")
            if phoneme is not None and (not isinstance(phoneme, str) or not phoneme.strip()):
                errors.append(f"{slabel}.phoneme must be null or non-empty text")
            onset, syl_duration = syllable.get("onset_beats"), syllable.get("duration_beats")
            if onset is not None and (not _number(onset) or onset < 0):
                errors.append(f"{slabel}.onset_beats must be null or non-negative")
            if syl_duration is not None and (not _number(syl_duration) or syl_duration <= 0):
                errors.append(f"{slabel}.duration_beats must be null or positive")
            notes = syllable.get("notes")
            if not isinstance(notes, list):
                errors.append(f"{slabel}.notes must be an array")
                notes = []
            for ni, note in enumerate(notes):
                nlabel = f"{slabel}.notes[{ni}]"
                if not isinstance(note, dict):
                    errors.append(f"{nlabel} must be an object")
                    continue
                pitch = note.get("midi_pitch")
                if not isinstance(pitch, int) or isinstance(pitch, bool) or not 0 <= pitch <= 127:
                    errors.append(f"{nlabel}.midi_pitch must be an integer from 0 to 127")
                nduration = note.get("duration_beats")
                if not _number(nduration) or nduration <= 0:
                    errors.append(f"{nlabel}.duration_beats must be positive")
                if note.get("note_type") not in NOTE_TYPES:
                    errors.append(f"{nlabel}.note_type is invalid")
                f0 = note.get("f0_hz")
                if f0 is not None and (not _number(f0) or f0 <= 0):
                    errors.append(f"{nlabel}.f0_hz must be null or positive")

            if alignment in {"syllable_aligned", "reviewed"}:
                if not isinstance(phoneme, str) or not phoneme.strip():
                    errors.append(f"{slabel} lacks phoneme for claimed syllable alignment")
                if onset is None or syl_duration is None:
                    errors.append(f"{slabel} lacks onset/duration for claimed syllable alignment")
            if phrase.get("delivery") in SUNG_DELIVERIES and alignment == "reviewed":
                if not notes:
                    errors.append(f"{slabel} has no note events for reviewed sung phrase")

        if require_singing_ready and phrase.get("delivery") in SUNG_DELIVERIES:
            if alignment != "reviewed":
                errors.append(f"{label} is not human-reviewed for singing export")
            if not syllables:
                errors.append(f"{label} has no syllable map for singing export")

    if require_singing_ready:
        if score.get("score_status") != "reviewed":
            errors.append("score_status must be reviewed for singing export")
        if score.get("tempo_status") != "locked":
            errors.append("tempo_status must be locked for singing export")
        if not any(p.get("delivery") in SUNG_DELIVERIES for p in phrases if isinstance(p, dict)):
            errors.append("score contains no sung or chant phrases")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("score", type=Path, help="path to vocal_score.json")
    parser.add_argument("--for-singing", action="store_true",
                        help="apply the stricter human-reviewed singing-export gate")
    args = parser.parse_args()
    try:
        score = json.loads(args.score.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read score: {exc}", file=sys.stderr)
        return 2
    errors = validate_score(score, require_singing_ready=args.for_singing)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Vocal score valid." if not args.for_singing else "Vocal score passes singing-export gate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
