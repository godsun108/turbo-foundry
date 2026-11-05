"""Warehouse Rave V3 composition-first MIDI arrangement.

A non-destructive 56-bar rewrite: evolving harmony, recurring hook, bass call/response,
section-specific drum density, a contrasting bridge, and a composed outro. MIDI only.
"""
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
BEAT = PPQ
BAR = 4 * PPQ
BPM = 127

# 56 bars. Harmony is deliberately varied at phrase boundaries, not just looped every bar.
SECTIONS = [
    ("intro", 4), ("verse_1", 8), ("pre_drop", 4), ("drop_1", 8),
    ("verse_2", 8), ("bridge", 8), ("final_drop", 12), ("outro", 4),
]
# MIDI pitches, A-minor center with F/C/G lift and Dm/E tension in the bridge.
PROGRESSION = {
    "intro": [(45, 48, 52), (41, 45, 48), (48, 52, 55), (43, 47, 50)],
    "verse_1": [(45, 48, 52), (41, 45, 48), (48, 52, 55), (43, 47, 50)],
    "pre_drop": [(41, 45, 48), (43, 47, 50), (45, 48, 52), (52, 56, 59)],
    "drop_1": [(45, 48, 52), (41, 45, 48), (48, 52, 55), (43, 47, 50)],
    "verse_2": [(45, 48, 52), (48, 52, 55), (41, 45, 48), (43, 47, 50)],
    "bridge": [(50, 53, 57), (41, 45, 48), (45, 48, 52), (52, 56, 59)],
    "final_drop": [(45, 48, 52), (41, 45, 48), (48, 52, 55), (43, 47, 50)],
    "outro": [(45, 48, 52), (41, 45, 48), (45, 48, 52), (45, 48, 52)],
}
# A short, recognizable four-note hook; later phrases answer and then resolve it.
HOOK = [81, 84, 88, 86]  # A, C, E, D in a bright upper register
ANSWER = [88, 86, 84, 81, 79, 81, 84, 88]
BASS_MOTIF = [(0, 0.48), (0.75, 0.22), (1.5, 0.38), (2.25, 0.22), (3.0, 0.62), (3.75, 0.16)]


def build_notes():
    tracks = {name: [] for name in ("chords", "bass", "lead", "drums", "texture")}
    arrangement = []
    bar_cursor = 0
    for section, bars in SECTIONS:
        start_bar = bar_cursor
        arrangement.append({"name": section, "start_bar": start_bar, "bars": bars})
        progression = PROGRESSION[section]
        for local in range(bars):
            bar = start_bar + local
            base = bar * BAR
            chord_index = (local // 2) % len(progression)
            root, third, fifth = progression[chord_index]
            is_drop = section in ("drop_1", "final_drop")
            is_final = section == "final_drop"
            is_build = section == "pre_drop"
            is_bridge = section == "bridge"
            is_verse = section in ("verse_1", "verse_2")
            is_intro = section == "intro"
            is_outro = section == "outro"

            # Chord voicing evolves: restrained verse, wider drops, open bridge.
            if is_bridge:
                chord_pitches = (root + 12, fifth + 12, third + 24)
                chord_len = int(BAR * 0.92)
            elif is_drop:
                chord_pitches = (root + 12, third + 12, fifth + 12, root + 24)
                chord_len = int(BEAT * 0.72)
            elif is_verse:
                chord_pitches = (root + 12, fifth + 12)
                chord_len = int(BEAT * 1.35)
            else:
                chord_pitches = (root + 12, third + 12, fifth + 12)
                chord_len = int(BEAT * (3.7 if is_intro or is_outro else 1.7))
            chord_positions = (0, 2) if is_drop else ((0,) if is_bridge or is_intro or is_outro else (0, 2))
            for beat_pos in chord_positions:
                for pitch in chord_pitches:
                    tracks["chords"].append((pitch, base + beat_pos * BEAT, chord_len,
                                             76 if is_drop else (52 if is_verse else 62)))

            # Bass is syncopated and phrase-varied; the downbeat is not filled every bar.
            if is_drop:
                for index, (beat_pos, length) in enumerate(BASS_MOTIF):
                    if local % 4 == 3 and index == 0:
                        continue  # leave a breath before the phrase turn
                    pitch = root - 12
                    if index in (2, 5):
                        pitch += 12
                    if is_final and local >= 8 and index in (1, 4):
                        pitch += 7
                    tracks["bass"].append((pitch, base + int(beat_pos * BEAT),
                                           max(48, int(length * BEAT)), 105 if index in (0, 4) else 88))
            elif is_build:
                for beat_pos in (0, 1.5, 2.5, 3.25):
                    tracks["bass"].append((root - 12, base + int(beat_pos * BEAT),
                                           int(BEAT * 0.28), 68 + int(beat_pos * 5)))
            elif is_bridge:
                if local in (0, 2, 4, 6):
                    tracks["bass"].append((root - 24, base, int(BEAT * 2.8), 78))
                if local in (3, 7):
                    tracks["bass"].append((root - 12, base + 3 * BEAT, int(BEAT * 0.6), 72))
            elif is_verse:
                for beat_pos in (0, 1.75, 3.0):
                    tracks["bass"].append((root - 12, base + int(beat_pos * BEAT),
                                           int(BEAT * 0.38), 78))
            elif is_intro and local in (2, 3):
                tracks["bass"].append((root - 12, base + 2 * BEAT, int(BEAT * 0.55), 58))
            elif is_outro and local == 0:
                tracks["bass"].append((root - 12, base, int(BEAT * 1.8), 58))

            # Hook appears in fragments, then full statement, then a changed final answer.
            if section == "intro" and local == 3:
                for i, pitch in enumerate(HOOK[:2]):
                    tracks["lead"].append((pitch, base + (2 + i * 0.5) * BEAT, int(BEAT * 0.28), 60))
            elif section == "verse_1" and local in (3, 7):
                for i, pitch in enumerate(HOOK[:2]):
                    tracks["lead"].append((pitch, base + (3 + i * 0.5) * BEAT, int(BEAT * 0.2), 54))
            elif is_build:
                for i, pitch in enumerate((81, 84, 86, 88)):
                    tracks["lead"].append((pitch, base + (2.0 + i * 0.5) * BEAT,
                                           int(BEAT * 0.18), 58 + i * 5))
            elif is_drop:
                phrase = HOOK if local % 4 < 2 else ANSWER[:4]
                for i, pitch in enumerate(phrase):
                    pos = (i * 0.75) if local % 2 == 0 else (i * 0.5)
                    tracks["lead"].append((pitch + (12 if is_final and local >= 8 else 0),
                                           base + int(pos * BEAT), int(BEAT * 0.24),
                                           84 if is_final else 76))
            elif is_bridge and local in (2, 6):
                for i, pitch in enumerate((76, 79, 81, 84)):
                    tracks["lead"].append((pitch, base + (1.5 + i * 0.5) * BEAT,
                                           int(BEAT * 0.32), 62))
            elif section == "verse_2" and local in (3, 7):
                for i, pitch in enumerate(ANSWER[:3]):
                    tracks["lead"].append((pitch - 12, base + (2.5 + i * 0.5) * BEAT,
                                           int(BEAT * 0.2), 58))

            # Drums use distinct verse/build/drop/bridge pockets and phrase-ending fills.
            if not is_intro and not is_outro:
                if is_bridge:
                    tracks["drums"].extend([
                        (36, base, int(BEAT * 0.22), 92),
                        (38, base + 2 * BEAT, int(BEAT * 0.2), 86),
                        (46, base + BEAT, int(BEAT * 0.35), 58),
                        (46, base + 3 * BEAT, int(BEAT * 0.35), 64),
                    ])
                elif is_verse:
                    for beat_pos in (0, 2):
                        tracks["drums"].append((36, base + beat_pos * BEAT, int(BEAT * .2), 88))
                    for beat_pos in (1, 3):
                        tracks["drums"].append((38, base + beat_pos * BEAT, int(BEAT * .18), 78))
                    for eighth in (1, 3, 5, 7):
                        tracks["drums"].append((42, base + eighth * BEAT // 2, 48, 42))
                else:
                    for beat_pos in range(4):
                        tracks["drums"].append((36, base + beat_pos * BEAT, int(BEAT * .2), 112 if is_drop else 94))
                    for beat_pos in (1, 3):
                        tracks["drums"].append((38, base + beat_pos * BEAT, int(BEAT * .18), 104 if is_drop else 82))
                    for eighth in range(8):
                        if is_drop or eighth % 2:
                            tracks["drums"].append((42, base + eighth * BEAT // 2, 42,
                                                    72 if is_drop else 48))
                    if is_drop and local % 4 == 3:
                        for n, pitch in enumerate((38, 42, 46, 42)):
                            tracks["drums"].append((pitch, base + 3 * BEAT + n * BEAT // 4,
                                                    52, 66 + n * 7))
                    if is_build:
                        for sixteenth in range(8, 16):
                            tracks["drums"].append((38, base + sixteenth * BEAT // 4,
                                                    42, 48 + (sixteenth - 8) * 6))

            # Small ear-candy events are kept on their own MIDI lane.
            if is_build:
                tracks["texture"].append((96, base + 3 * BEAT, int(BEAT * .3), 72))
            if is_drop and local in (0, 4):
                tracks["texture"].append((72, base, int(BEAT * .5), 90))
            if is_bridge and local in (0, 4):
                tracks["texture"].append((69, base, int(BAR * .8), 44))
        bar_cursor += bars
    return tracks, arrangement


def make(output, bpm=BPM):
    if not 40 <= bpm <= 240:
        raise ValueError("bpm out of range")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    tracks, arrangement = build_notes()
    tempo = round(60000000 / bpm)
    meta = GEN.chunk(b"MTrk", b"\x00\xff\x51\x03" + tempo.to_bytes(3, "big") + b"\x00\xff\x2f\x00")
    header = GEN.chunk(b"MThd", struct.pack(">HHH", 1, 2, PPQ))
    config = {
        "chords": (0, 88), "bass": (1, 38), "lead": (2, 81),
        "drums": (9, 0), "texture": (3, 89),
    }
    for name, notes in tracks.items():
        channel, program = config[name]
        (output / f"{name}.mid").write_bytes(header + meta + GEN.track(notes, channel, program))
    manifest = {
        "schema": "turbo.music-foundry.composition.v3",
        "title": "Somebody's Gotta Do It — Warehouse Rave V3",
        "bpm": bpm, "meter": "4/4", "bars": sum(x[1] for x in SECTIONS),
        "approx_duration_seconds": round(sum(x[1] for x in SECTIONS) * 4 * 60 / bpm, 2),
        "key_center": "A minor with D minor / E dominant bridge tension",
        "arrangement": arrangement,
        "tracks": list(tracks),
        "composition_goals": [
            "recognizable four-note hook introduced before the first drop",
            "syncopated bass motif with phrase-ending breathing room",
            "section-specific harmony and drum density",
            "contrasting half-time bridge and harmonic tension",
            "final drop develops the hook rather than merely repeating it",
            "outro resolves to the home chord"
        ],
        "render_status": "MIDI composition only; no audio render or mastering claimed"
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="music-foundry/output/warehouse-rave-v3")
    parser.add_argument("--bpm", type=int, default=BPM)
    args = parser.parse_args()
    print(make(args.output, args.bpm))
