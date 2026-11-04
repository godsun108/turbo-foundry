"""Track-specific wonky bass-house arrangement for Somebody's Gotta Do It.

Uses Music Foundry's existing dependency-free MIDI primitives. MIDI only; no audio.
"""
import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
_SPEC = importlib.util.spec_from_file_location("music_foundry_generate", HERE.parent.parent / "generate.py")
_GENERATOR = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_GENERATOR)

PPQ = _GENERATOR.PPQ
BAR = PPQ * 4
SECTIONS = [
    ("intro_tag", 4),
    ("verse_1", 8),
    ("pre", 4),
    ("chorus", 8),
    ("verse_2", 8),
    ("bridge_half_time", 8),
    ("final_chorus", 12),
    ("outro", 4),
]
PROGRESSION = [(45, 48, 52), (41, 45, 48), (36, 40, 43), (43, 47, 50)]


def build_notes():
    chords, bass, lead, drums = [], [], [], []
    section_starts = {}
    bar_index = 0
    for section, length in SECTIONS:
        section_starts[section] = bar_index
        for local_bar in range(length):
            bar = bar_index + local_bar
            base = bar * BAR
            root, third, fifth = PROGRESSION[bar % len(PROGRESSION)]
            is_intro = section == "intro_tag"
            is_pre = section == "pre"
            is_chorus = section in ("chorus", "final_chorus")
            is_bridge = section == "bridge_half_time"
            is_outro = section == "outro"

            # Chord stabs leave room for the spoken lead; longer holds in the bridge.
            chord_len = BAR - 18 if is_bridge or is_intro else int(PPQ * 1.65)
            chord_velocity = 62 if is_intro else (84 if is_chorus else 70)
            for pitch in (root + 12, third + 12, fifth + 12):
                chords.append((pitch, base, chord_len, chord_velocity))

            # Rubber-band bass: syncopated offbeats and occasional octave punctuation.
            if not is_intro and not is_outro:
                if is_bridge:
                    hits = [(0, .72, 88), (2, .62, 80)]
                elif is_pre:
                    hits = [(0, .55, 78), (1.5, .42, 76), (2.75, .35, 82), (3.5, .30, 90)]
                else:
                    hits = [(0, .58, 100), (.75, .30, 86), (1.5, .42, 92),
                            (2.5, .34, 84), (3.25, .42, 96)]
                    if is_chorus:
                        hits.extend([(3.75, .18, 104)])
                for beat_pos, duration, velocity in hits:
                    pitch = root - 12
                    if is_chorus and beat_pos == 3.75:
                        pitch += 12
                    bass.append((pitch, base + int(beat_pos * PPQ),
                                 max(60, int(duration * PPQ)), velocity))

            # Club drums, with reduced density in intro/pre and a half-time bridge.
            if not is_intro and not is_outro:
                if is_bridge:
                    drums.append((36, base, int(PPQ * .22), 108))
                    drums.append((38, base + 2 * PPQ, int(PPQ * .20), 92))
                    for beat_pos in (1, 3):
                        drums.append((46, base + int(beat_pos * PPQ), 180, 58))
                else:
                    kick_beats = (0, 1, 2, 3) if not is_pre else (0, 2)
                    for beat_pos in kick_beats:
                        drums.append((36, base + beat_pos * PPQ, 105, 112 if is_chorus else 100))
                    for beat_pos in (1, 3):
                        drums.append((38, base + beat_pos * PPQ, 100, 104 if is_chorus else 90))
                    if not is_pre:
                        for eighth in range(8):
                            velocity = 76 if eighth % 2 else 48
                            drums.append((42, base + eighth * (PPQ // 2), 55, velocity))
                        if is_chorus:
                            for beat_pos in (1.5, 3.5):
                                drums.append((46, base + int(beat_pos * PPQ), 150, 72))

            # Short, sparse synth punctuation; vocal remains the lead instrument.
            if is_chorus and local_bar % 2 == 1:
                for step, pitch in enumerate((69, 72, 76, 72)):
                    lead.append((pitch, base + (step * PPQ), int(PPQ * .22), 72))
            elif is_pre and local_bar >= 2:
                lead.append((76, base + 3 * PPQ, int(PPQ * .18), 58))
            elif is_bridge and local_bar in (3, 7):
                lead.append((81, base + 3 * PPQ, int(PPQ * .16), 64))

            # One-bar turnaround fill at the end of major sections.
            if local_bar == length - 1 and section in ("pre", "verse_2", "bridge_half_time"):
                for step, pitch in enumerate((42, 42, 38, 46)):
                    drums.append((pitch, base + 3 * PPQ + step * (PPQ // 4), 65, 88))

        bar_index += length

    return {"chords": (chords, 0, 88), "bass": (bass, 1, 38),
            "lead": (lead, 2, 80), "drums": (drums, 9, 0)}, section_starts, bar_index


def make(output, bpm=127):
    if not 40 <= bpm <= 240:
        raise ValueError("bpm out of range")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    parts, section_starts, bars = build_notes()
    tempo = round(60000000 / bpm)
    meta = _GENERATOR.chunk(b"MTrk", b"\\x00\\xff\\x51\\x03" + tempo.to_bytes(3, "big") + b"\\x00\\xff\\x2f\\x00")
    header = _GENERATOR.chunk(b"MThd", __import__("struct").pack(">HHH", 1, 2, PPQ))
    for name, (notes, channel, program) in parts.items():
        (output / f"{name}.mid").write_bytes(header + meta + _GENERATOR.track(notes, channel, program))
    manifest = {
        "title": "Somebody's Gotta Do It",
        "bpm": bpm,
        "meter": "4/4",
        "bars": bars,
        "approx_duration_seconds": round(bars * 4 * 60 / bpm, 2),
        "key_center": "A minor (provisional)",
        "arrangement": [{"name": name, "start_bar": section_starts[name], "bars": length}
                        for name, length in SECTIONS],
        "tracks": list(parts),
        "note": "Original procedural MIDI arrangement; no audio or vocals are rendered."
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="music-foundry/output/somebodys-gotta-do-it")
    parser.add_argument("--bpm", type=int, default=127)
    args = parser.parse_args()
    print(make(args.output, args.bpm))
