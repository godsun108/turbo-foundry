#!/usr/bin/env python3
"""Create a clearly labeled MIDI audition guide from Music Foundry syllable-level score data.

This is a melody sketch for listening and review, not a SoulX render or a
substitute for an approved phoneme-aligned singing score. No external MIDI
package or audio service is required.
"""
from __future__ import annotations
import argparse
import json
import math
import struct
from pathlib import Path
from typing import Any


def _vlq(value: int) -> bytes:
    if value < 0:
        raise ValueError("MIDI delta time cannot be negative")
    buffer = value & 0x7F
    out = bytearray()
    while (value := value >> 7):
        buffer <<= 8
        buffer |= ((value & 0x7F) | 0x80)
    while True:
        out.append(buffer & 0xFF)
        if buffer & 0x80:
            buffer >>= 8
        else:
            break
    return bytes(out)


def _meta(kind: int, payload: bytes) -> bytes:
    return bytes((0xFF, kind)) + _vlq(len(payload)) + payload


def _track(events: list[tuple[int, int, bytes]], end_tick: int) -> bytes:
    ordered = sorted(events, key=lambda item: (item[0], item[1]))
    data = bytearray()
    previous = 0
    for tick, _priority, message in ordered:
        data.extend(_vlq(tick - previous))
        data.extend(message)
        previous = tick
    data.extend(_vlq(max(0, end_tick - previous)))
    data.extend(b"\xFF\x2F\x00")
    return b"MTrk" + struct.pack(">I", len(data)) + data


def build_midi(score: Any, preserve_timeline: bool = False) -> tuple[bytes, dict[str, Any]]:
    if not isinstance(score, dict):
        raise ValueError("score root must be an object")
    bpm = score.get("tempo_bpm")
    if not isinstance(bpm, (int, float)) or isinstance(bpm, bool) or not math.isfinite(bpm) or bpm <= 0:
        raise ValueError("tempo_bpm must be a positive finite number")
    phrases = score.get("phrases")
    if not isinstance(phrases, list):
        raise ValueError("phrases must be an array")
    ppq = int(score.get("ppq", 480))
    if ppq <= 0 or ppq > 32767:
        raise ValueError("ppq must be between 1 and 32767")

    eligible_starts = [float(p["start_beat"]) for p in phrases
                       if isinstance(p, dict) and p.get("delivery") in {"sung", "chant", "gang_shout"}
                       and isinstance(p.get("start_beat"), (int, float)) and p.get("lyric_units")]
    origin_beat = 0.0 if preserve_timeline or not eligible_starts else min(eligible_starts)
    tracks: dict[str, list[tuple[int, int, bytes]]] = {"lead": [], "gang": []}
    words = 0
    syllable_events = 0
    notes = 0
    max_tick = 0
    for phrase in phrases:
        if not isinstance(phrase, dict):
            raise ValueError("each phrase must be an object")
        if phrase.get("delivery") not in {"sung", "chant", "gang_shout"}:
            continue
        start = phrase.get("start_beat")
        units = phrase.get("lyric_units")
        syllables = phrase.get("syllables")
        if not isinstance(start, (int, float)) or not math.isfinite(start) or start < 0:
            raise ValueError(f"{phrase.get('id', 'phrase')}: invalid start_beat")
        if not isinstance(units, list) or not units:
            continue
        if not isinstance(syllables, list) or not syllables:
            syllables = units
        layer = "gang" if phrase.get("delivery") == "gang_shout" else "lead"
        cursor = 0.0
        for unit in syllables:
            if not isinstance(unit, dict):
                raise ValueError("syllable units must be objects")
            onset, duration = unit.get("onset_beats"), unit.get("duration_beats")
            pitch, text = unit.get("midi_pitch"), unit.get("text")
            if not isinstance(onset, (int, float)) or not isinstance(duration, (int, float)) or duration <= 0:
                raise ValueError(f"{phrase.get('id')}: invalid syllable timing")
            if abs(float(onset) - cursor) > 1e-6:
                raise ValueError(f"{phrase.get('id')}: syllables must be contiguous; encode rests explicitly")
            if not isinstance(text, str) or not text:
                raise ValueError(f"{phrase.get('id')}: syllable text is required")
            start_tick = int(round((float(start) + float(onset) - origin_beat) * ppq))
            end_tick = int(round((float(start) + float(onset) + float(duration) - origin_beat) * ppq))
            max_tick = max(max_tick, end_tick)
            if text != "<SP>":
                if not isinstance(pitch, int) or isinstance(pitch, bool) or not 1 <= pitch <= 127:
                    raise ValueError(f"{phrase.get('id')}: {text} needs a MIDI pitch from 1 to 127")
                channel = 1 if layer == "gang" else 0
                tracks[layer].append((start_tick, 2, bytes((0x90 | channel, pitch, 92 if layer == "gang" else 82))))
                tracks[layer].append((end_tick, 0, bytes((0x80 | channel, pitch, 0))))
                label = f"{unit.get('word', text)}:{text}"
                tracks[layer].append((start_tick, 3, _meta(0x05, label.encode("utf-8"))))
                syllable_events += 1
                notes += 1
            cursor += float(duration)
        declared = phrase.get("duration_beats")
        if declared is not None and abs(cursor - float(declared)) > 1e-6:
            raise ValueError(f"{phrase.get('id')}: syllable durations do not match phrase duration")
        words += sum(1 for item in units if isinstance(item, dict) and item.get("text") != "<SP>")

    tempo = int(round(60_000_000 / float(bpm)))
    header = b"MThd" + struct.pack(">IHHH", 6, 1, 3, ppq)
    tempo_events = [
        (0, 0, _meta(0x03, b"Fine China - draft vocal melody")),
        (0, 1, _meta(0x51, tempo.to_bytes(3, "big"))),
        (0, 2, _meta(0x58, bytes((4, 2, 24, 8)))),
    ]
    lead_events = [(0, 0, _meta(0x03, b"Lead melody guide"))] + tracks["lead"]
    gang_events = [(0, 0, _meta(0x03, b"Gang response guide"))] + tracks["gang"]
    midi = header + _track(tempo_events, max_tick) + _track(lead_events, max_tick) + _track(gang_events, max_tick)
    report = {
        "schema": "turbo.music-foundry.vocal-midi-guide.v1",
        "project_id": score.get("project_id"),
        "status": "draft_preview_only",
        "score_status": score.get("score_status"),
        "tempo_bpm": bpm,
        "ppq": ppq,
        "word_events": words,
        "syllable_events": syllable_events,
        "note_events": notes,
        "start_beat_in_source": origin_beat,
        "end_beat_in_source": origin_beat + max_tick / ppq,
        "duration_beats": max_tick / ppq,
        "preserved_timeline": preserve_timeline,
        "tracks": ["conductor", "lead", "gang"],
        "warning": "MIDI guide is a composition preview only; not an approved SoulX score or a rendered vocal recording."
    }
    return midi, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--score", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--preserve-timeline", action="store_true", help="Keep the source-song beat offset instead of starting the preview at beat zero.")
    args = parser.parse_args()
    try:
        score = json.loads(args.score.read_text(encoding="utf-8"))
        midi, report = build_midi(score, preserve_timeline=args.preserve_timeline)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(midi)
        report_path = args.output.with_suffix(".report.json")
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
