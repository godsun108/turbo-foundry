"""Track-specific wonky bass-house MIDI arrangement; MIDI only, no audio."""
import argparse
import importlib.util
import json
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("music_foundry_generator", HERE / "generate.py")
GEN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GEN)
PPQ = GEN.PPQ
BAR = PPQ * 4
SECTIONS = [
    ("intro_tag", 4), ("verse_1", 8), ("pre", 4), ("chorus", 8),
    ("verse_2", 8), ("bridge_half_time", 8), ("final_chorus", 12), ("outro", 4)
]
PROGRESSION = [(45, 48, 52), (41, 45, 48), (36, 40, 43), (43, 47, 50)]


def build_notes():
    chords, bass, lead, drums = [], [], [], []
    section_map, bar_index = {}, 0
    for section, length in SECTIONS:
        section_map[section] = bar_index
        for local in range(length):
            base = (bar_index + local) * BAR
            root, third, fifth = PROGRESSION[(bar_index + local) % 4]
            intro, pre = section == "intro_tag", section == "pre"
            chorus = section in ("chorus", "final_chorus")
            bridge, outro = section == "bridge_half_time", section == "outro"
            for pitch in (root + 12, third + 12, fifth + 12):
                chords.append((pitch, base, BAR - 18 if bridge or intro else int(PPQ * 1.65),
                               82 if chorus else (62 if intro else 70)))
            if not intro and not outro:
                hits = ([(0, .72, 88), (2, .62, 80)] if bridge else
                        ([(0, .55, 78), (1.5, .42, 76), (2.75, .35, 82), (3.5, .3, 90)] if pre else
                         [(0, .58, 100), (.75, .30, 86), (1.5, .42, 92), (2.5, .34, 84), (3.25, .42, 96)]))
                if chorus and not bridge:
                    hits.append((3.75, .18, 104))
                for pos, dur, vel in hits:
                    pitch = root - 12 + (12 if chorus and pos == 3.75 else 0)
                    bass.append((pitch, base + int(pos * PPQ), max(60, int(dur * PPQ)), vel))
            if not intro and not outro:
                if bridge:
                    drums.extend([(36, base, 105, 108), (38, base + 2 * PPQ, 95, 92),
                                  (46, base + PPQ, 180, 58), (46, base + 3 * PPQ, 180, 58)])
                else:
                    for beat in ((0, 2) if pre else (0, 1, 2, 3)):
                        drums.append((36, base + beat * PPQ, 105, 110 if chorus else 100))
                    for beat in (1, 3):
                        drums.append((38, base + beat * PPQ, 100, 104 if chorus else 90))
                    if not pre:
                        for eighth in range(8):
                            drums.append((42, base + eighth * (PPQ // 2), 55, 76 if eighth % 2 else 48))
                    if chorus:
                        for pos in (1.5, 3.5):
                            drums.append((46, base + int(pos * PPQ), 150, 72))
            if chorus and local % 2:
                for step, pitch in enumerate((69, 72, 76, 72)):
                    lead.append((pitch, base + step * PPQ, int(PPQ * .22), 72))
            elif pre and local >= 2:
                lead.append((76, base + 3 * PPQ, int(PPQ * .18), 58))
            elif bridge and local in (3, 7):
                lead.append((81, base + 3 * PPQ, int(PPQ * .16), 64))
            if local == length - 1 and section in ("pre", "verse_2", "bridge_half_time"):
                for step, pitch in enumerate((42, 42, 38, 46)):
                    drums.append((pitch, base + 3 * PPQ + step * (PPQ // 4), 65, 88))
        bar_index += length
    return {"chords": (chords, 0, 88), "bass": (bass, 1, 38),
            "lead": (lead, 2, 80), "drums": (drums, 9, 0)}, section_map, bar_index


def make(output, bpm=127):
    if not 40 <= bpm <= 240:
        raise ValueError("bpm out of range")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    parts, starts, bars = build_notes()
    tempo = round(60000000 / bpm)
    meta = GEN.chunk(b"MTrk", b"\\x00\\xff\\x51\\x03" + tempo.to_bytes(3, "big") + b"\\x00\\xff\\x2f\\x00")
    header = GEN.chunk(b"MThd", struct.pack(">HHH", 1, 2, PPQ))
    for name, (notes, channel, program) in parts.items():
        (output / f"{name}.mid").write_bytes(header + meta + GEN.track(notes, channel, program))
    manifest = {
        "title": "Somebody's Gotta Do It", "bpm": bpm, "meter": "4/4", "bars": bars,
        "approx_duration_seconds": round(bars * 4 * 60 / bpm, 2),
        "key_center": "A minor (provisional)",
        "arrangement": [{"name": name, "start_bar": starts[name], "bars": length}
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
