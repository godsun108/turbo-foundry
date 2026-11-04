#!/usr/bin/env python3
"""Build deterministic SoulX-Singer score-control target metadata from a reviewed score.

No G2P, note, timing, F0, or word-boundary inference is performed.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

SOULX_NOTE_TYPES = {"rest": 1, "normal": 2, "tie": 3}
ARPABET = re.compile(r"^[A-Z]+[0-2]?$")


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def build_metadata(score: Any) -> list[dict[str, Any]]:
    errors: list[str] = []
    if not isinstance(score, dict):
        raise ValueError("score root must be an object")
    bpm = score.get("tempo_bpm")
    if not _finite_number(bpm) or bpm <= 0:
        errors.append("tempo_bpm must be a positive finite number")
    if score.get("tempo_status") != "locked":
        errors.append("tempo_status must be locked")
    if score.get("score_status") != "reviewed":
        errors.append("score_status must be reviewed")
    phrases = score.get("phrases")
    if not isinstance(phrases, list):
        errors.append("phrases must be an array")
        phrases = []
    if errors:
        raise ValueError("; ".join(errors))

    records: list[tuple[float, float, dict[str, Any]]] = []
    for phrase in phrases:
        if not isinstance(phrase, dict) or phrase.get("delivery") not in {"sung", "chant"}:
            continue
        pid = phrase.get("id", "<unknown>")
        if phrase.get("alignment_status") != "reviewed":
            errors.append(f"{pid}: alignment_status must be reviewed")
            continue
        start = phrase.get("start_beat")
        span = phrase.get("duration_beats")
        if not _finite_number(start) or start < 0 or not _finite_number(span) or span <= 0:
            errors.append(f"{pid}: phrase start/duration is invalid")
            continue
        units = phrase.get("lyric_units")
        if not isinstance(units, list) or not units:
            errors.append(f"{pid}: explicit lyric_units word/rest map is required")
            continue

        words: list[str] = []
        phonemes: list[str] = []
        durations: list[float] = []
        pitches: list[int] = []
        note_types: list[int] = []
        cursor = 0.0
        for index, unit in enumerate(units):
            label = f"{pid}.lyric_units[{index}]"
            if not isinstance(unit, dict):
                errors.append(f"{label}: must be an object")
                continue
            text = unit.get("text")
            phones = unit.get("phonemes")
            onset = unit.get("onset_beats")
            duration = unit.get("duration_beats")
            pitch = unit.get("midi_pitch")
            kind = unit.get("note_type")
            if not isinstance(text, str) or not text.strip():
                errors.append(f"{label}: text is required")
                continue
            if not isinstance(phones, list) or not phones or any(not isinstance(p, str) or not p for p in phones):
                errors.append(f"{label}: explicit phoneme array is required")
                continue
            if not _finite_number(onset) or not _finite_number(duration) or duration <= 0:
                errors.append(f"{label}: finite onset and positive duration are required")
                continue
            if abs(onset - cursor) > 1e-7:
                errors.append(f"{label}: onset must be contiguous at beat {cursor:g}; encode rests explicitly")
            if not isinstance(pitch, int) or isinstance(pitch, bool) or not 0 <= pitch <= 127:
                errors.append(f"{label}: MIDI pitch must be an integer from 0 to 127")
                continue
            if kind not in SOULX_NOTE_TYPES:
                errors.append(f"{label}: note_type must be normal, tie, or rest")
                continue
            if kind == "rest":
                if text != "<SP>" or phones != ["<SP>"] or pitch != 0:
                    errors.append(f"{label}: rest must use text <SP>, phonemes [<SP>], and pitch 0")
            else:
                if text == "<SP>" or any(not ARPABET.fullmatch(p) for p in phones):
                    errors.append(f"{label}: English word units require explicit ARPABET phoneme tokens")
            words.append(text)
            if kind == "rest":
                phonemes.append("<SP>")
            else:
                phonemes.append("en_" + "-".join(phones))
            durations.append(float(duration) * 60.0 / float(bpm))
            pitches.append(pitch)
            note_types.append(SOULX_NOTE_TYPES[kind])
            cursor = float(onset + duration)

        if abs(cursor - float(span)) > 1e-6:
            errors.append(f"{pid}: lyric-unit durations must exactly cover phrase duration")
        spoken_words = [word for word in words if word != "<SP>"]
        if " ".join(spoken_words) != " ".join(str(phrase.get("text", "")).split()):
            errors.append(f"{pid}: lyric-unit words do not exactly reproduce phrase text")
        if errors and any(error.startswith(pid + ":") or error.startswith(pid + ".") for error in errors):
            continue

        start_ms = int(round(float(start) * 60000.0 / float(bpm)))
        end_ms = int(round((float(start) + float(span)) * 60000.0 / float(bpm)))
        duration_string = " ".join(f"{value:.6f}".rstrip("0").rstrip(".") for value in durations)
        record = {
            "index": "music_foundry_" + str(pid),
            "language": "English",
            "time": [start_ms, end_ms],
            "duration": duration_string,
            "text": " ".join(words),
            "phoneme": " ".join(phonemes),
            "note_pitch": " ".join(str(value) for value in pitches),
            "note_type": " ".join(str(value) for value in note_types),
        }
        records.append((float(start), float(start) + float(span), record))

    if not any(isinstance(p, dict) and p.get("delivery") in {"sung", "chant"} for p in phrases):
        errors.append("score contains no sung or chant phrases")
    records.sort(key=lambda item: item[0])
    for previous, current in zip(records, records[1:]):
        if current[0] < previous[1] - 1e-7:
            errors.append(f"overlapping sung phrases: {previous[2]['index']} and {current[2]['index']}")
    if errors:
        raise ValueError("\n".join(errors))
    if not records:
        raise ValueError("no exportable sung segments")
    return [record for _, _, record in records]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("score", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.output.exists() and not args.overwrite:
        print("ERROR: output exists; pass --overwrite explicitly", file=sys.stderr)
        return 2
    try:
        score = json.loads(args.score.read_text(encoding="utf-8"))
        metadata = build_metadata(score)
        args.output.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: SoulX export blocked: {exc}", file=sys.stderr)
        return 1
    print(f"Exported {len(metadata)} score-control segment(s) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
