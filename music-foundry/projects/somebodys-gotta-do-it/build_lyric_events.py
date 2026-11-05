"""Build source-linked vocal events without treating timing hints as locked performance."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_CUE = PROJECT_ROOT / "cue-sheet.md"
DEFAULT_TIMING = PROJECT_ROOT / "vocal_timing.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "lyric-events.json"

SECTION_IDS = {
    "Intro tag": "intro_tag",
    "Verse 1": "verse_1",
    "Pre": "pre",
    "Chorus": "chorus",
    "Verse 2": "verse_2",
    "Bridge — half-time chaos": "bridge_half_time",
    "Final chorus / outro": "final_chorus_outro",
}


def extract_lyric_lines(cue_text: str) -> list[dict]:
    """Extract lyric lines verbatim, keyed to their 1-based cue-sheet line numbers."""
    section = None
    events = []
    for line_number, raw in enumerate(cue_text.splitlines(), start=1):
        if raw.startswith("## "):
            heading = raw[3:].strip()
            section = SECTION_IDS.get(heading)
            continue
        if section is None or not raw.strip():
            continue
        stripped = raw.strip()
        if stripped.startswith(("#", "**", "- ", "|", "```")):
            continue
        # Preserve the complete lyric line, including punctuation and parentheticals.
        events.append({
            "event_id": f"{section}:L{line_number:03d}",
            "section_id": section,
            "source_line": line_number,
            "text": raw,
            "timing": {
                "status": "unplaced",
                "bar": None,
                "beat": None,
                "marker_ref": None,
            },
        })
    return events


def build_manifest(cue_text: str, timing: dict, source_ref: str) -> dict:
    cue_hash = hashlib.sha256(cue_text.encode("utf-8")).hexdigest()
    timing_sections = {item["id"]: item for item in timing.get("sections", [])}
    events = extract_lyric_lines(cue_text)
    for event in events:
        section = timing_sections.get(event["section_id"])
        if section:
            event["section_start_bar"] = section["start_bar"]
            event["section_bars"] = section["bars"]
    return {
        "schema": "turbo.music-foundry.lyric-events.v1",
        "project_id": timing.get("project_id", "unknown"),
        "source_ref": source_ref,
        "source_sha256": cue_hash,
        "lyric_authority": "source_ref",
        "timing_policy": "editorial_grid_not_performance_locked",
        "events": events,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cue", type=Path, default=DEFAULT_CUE)
    parser.add_argument("--timing", type=Path, default=DEFAULT_TIMING)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    cue_text = args.cue.read_text(encoding="utf-8")
    timing = json.loads(args.timing.read_text(encoding="utf-8"))
    source_ref = args.cue.name if args.cue == DEFAULT_CUE else str(args.cue)
    manifest = build_manifest(cue_text, timing, source_ref)
    args.output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(manifest['events'])} source-linked lyric events to {args.output}")


if __name__ == "__main__":
    main()
