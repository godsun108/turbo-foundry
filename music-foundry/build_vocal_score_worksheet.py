#!/usr/bin/env python3
"""Generate a blank, non-authoritative worksheet for manually scoring sung phrases."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import Any

def build_worksheet(score: Any) -> str:
    if not isinstance(score, dict) or not isinstance(score.get("phrases"), list):
        raise ValueError("score must be an object with a phrases array")
    lines = [
        "# Sung Hook — Manual Score-Authoring Worksheet", "",
        "> Working aid only. This worksheet does not change the canonical score.",
        "> Fill every field by deliberate musical/phonetic review. Do not treat",
        "> word boundaries as syllable boundaries or infer notes from the demo.", "",
        f"- Project: {score.get('project_id', 'unknown')}",
        f"- Current tempo: {score.get('tempo_bpm', 'unset')} BPM ({score.get('tempo_status', 'unset')})",
        "- Beat positions are quarter-note beats; phrase-relative onset starts at 0.",
        "- MIDI pitch uses integer note numbers (1–127 for pitched words).", ""
    ]
    found = 0
    for phrase in score["phrases"]:
        if not isinstance(phrase, dict) or phrase.get("delivery") not in {"sung", "chant"}:
            continue
        found += 1
        phrase_id = str(phrase.get("id", "unknown"))
        lyric = phrase.get("text")
        if not isinstance(lyric, str) or not lyric.strip():
            raise ValueError(f"{phrase_id}: lyric text must be non-empty")
        lines.extend([
            f"## {phrase_id}", "", f"**Source lyric (verbatim):** {lyric}", "",
            "| # | Word / token (preserve exactly) | ARPABET phones (reviewed) | Onset (beats) | Duration (beats) | MIDI pitch | Note type |",
            "|---:|---|---|---:|---:|---:|---|"
        ])
        for index, word in enumerate(lyric.split(), 1):
            lines.append(f"| {index} | {word} |  |  |  |  | normal / tie / rest |")
        lines.extend(["", "**Phrase start beat:** ______  ", "**Phrase duration (beats):** ______  ",
                      "**Human reviewer / review date:** ____________________", ""])
    if not found:
        raise ValueError("score contains no sung or chant phrases")
    lines.extend([
        "## Completion gate", "",
        "- [ ] Word tokens reproduce the source lyric exactly and in order.",
        "- [ ] Phonemes are explicitly reviewed against the selected English pronunciation.",
        "- [ ] Every onset and duration is authored; any silence is explicit.",
        "- [ ] MIDI pitches and note types are deliberately selected.",
        "- [ ] Phrase timing covers its note units without gaps or overlaps.",
        "- [ ] Tempo is performance-locked and every sung phrase is human-reviewed.", "",
        "Only after review should these values be entered into the canonical vocal_score.json.",
        "This worksheet intentionally contains no generated pitches, phonemes, or timing.", ""
    ])
    return "\n".join(lines)

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
        worksheet = build_worksheet(score)
        args.output.write_text(worksheet, encoding="utf-8")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: worksheet not generated: {exc}", file=sys.stderr)
        return 1
    print(f"Generated blank scoring worksheet: {args.output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
