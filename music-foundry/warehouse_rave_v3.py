"""Warehouse Rave V3: a composition-led rework using the existing V2 renderer.

The V3 arrangement changes harmony, bass phrasing, melodic motifs, density and
section energy. It reuses the established procedural renderer; it is not a new
audio engine and does not synthesize vocals.
"""
import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("warehouse_rave_v2", HERE / "warehouse_rave_v2.py")
RENDERER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RENDERER)

PPQ = RENDERER.PPQ
BEAT = PPQ
BAR = 4 * BEAT
BPM = 127

# 68 bars: a shorter opening, two contrasting drops, and a clear final tag.
SECTIONS = [
    ("cold_open", 4), ("verse_a", 8), ("pre_drop_a", 4),
    ("drop_a", 12), ("verse_b", 8), ("breakdown", 8),
    ("build_b", 4), ("final_drop", 16), ("outro_tag", 4),
]

# A-minor family with a deliberate F -> G lift into the drops.
HARMONY = [
    (45, (57, 60, 64)),  # Am
    (41, (53, 57, 60)),  # F
    (48, (55, 60, 64)),  # C
    (43, (55, 59, 62)),  # G
]
# A compact four-note identity motif, varied by section rather than looped unchanged.
MOTIF = (0, 3, 7, 10, 7, 5, 3, 2)


def build_events():
    events = {name: [] for name in ("drums", "bass", "synth", "lead", "fx")}
    section_starts = {}
    bar_number = 0

    for section, bars in SECTIONS:
        section_starts[section] = bar_number
        for local in range(bars):
            bar = bar_number + local
            root, chord = HARMONY[(bar // 2) % len(HARMONY)]
            base = bar * BAR
            is_drop = section in ("drop_a", "final_drop")
            is_final = section == "final_drop"
            is_build = section in ("pre_drop_a", "build_b")
            is_break = section == "breakdown"
            is_verse = section in ("verse_a", "verse_b")
            is_open = section == "cold_open"
            is_outro = section == "outro_tag"

            # Harmonic bed: sustained in the breakdown, short syncopated stabs elsewhere.
            if is_break:
                for pitch in chord:
                    events["synth"].append(("pad", base, 3.7, 58, pitch + 12))
            elif not is_open and not is_outro:
                stab_beats = (0, 2) if is_drop else (1.5, 3.5)
                for beat in stab_beats:
                    for pitch in chord:
                        events["synth"].append(("stab", base + int(beat * BEAT), 0.30,
                                                88 if is_drop else 58, pitch + 12))

            # Bass has distinct verse, drop and final-drop phrases; avoid a single repeated pulse.
            if is_drop:
                pattern = (0, 3, 5, 7) if not is_final else (0, 2, 3, 5, 7)
                for step in pattern:
                    offset = step * BEAT // 2
                    pitch = root - 12
                    if is_final and step in (3, 7):
                        pitch += 12
                    duration = 0.24 if step in (3, 7) else 0.31
                    events["bass"].append(("bass", base + offset, duration,
                                            112 if is_final else 101, pitch))
                if local % 4 == 3:
                    events["bass"].append(("bass", base + 3 * BEAT + BEAT // 4,
                                            0.16, 92, root - 24))
            elif is_verse and local % 2 == 1:
                for beat in (0, 1.75, 2.5):
                    events["bass"].append(("bass", base + int(beat * BEAT), 0.22, 72, root - 12))
            elif is_build and local >= bars - 2:
                for eighth in range(8):
                    events["bass"].append(("bass", base + eighth * BEAT // 2,
                                            0.16, 58 + eighth * 4, root - 12))

            # Drums: intentional negative space before drops, halftime breakdown, evolving fills.
            if section not in ("cold_open", "outro_tag"):
                if is_break:
                    if local in (0, 4):
                        events["drums"].append(("kick", base, 0.42, 82))
                    events["drums"].append(("clap", base + 2 * BEAT, 0.18, 65))
                    if local % 2 == 1:
                        events["drums"].append(("hat", base + 3 * BEAT, 0.08, 45))
                else:
                    kick_beats = (0, 2) if is_build else (0, 1.5, 2.75) if is_verse else (0, 1, 2, 3)
                    for beat in kick_beats:
                        events["drums"].append(("kick", base + int(beat * BEAT), 0.40,
                                                110 if is_drop else 90))
                    if not is_build:
                        for beat in (1, 3):
                            events["drums"].append(("clap", base + beat * BEAT, 0.18,
                                                    98 if is_drop else 78))
                    if is_drop:
                        for eighth in range(8):
                            events["drums"].append(("hat", base + eighth * BEAT // 2,
                                                    0.055, 72 if eighth % 2 else 48))
                        if local % 4 == 3:
                            for sixteenth in (12, 13, 14, 15):
                                events["drums"].append(("openhat", base + sixteenth * BEAT // 4,
                                                        0.10, 65 + sixteenth))
                    elif is_verse:
                        for eighth in (2, 6):
                            events["drums"].append(("hat", base + eighth * BEAT // 2,
                                                    0.05, 46))
                if is_build:
                    # A measured snare roll accelerates in the last two bars.
                    subdivisions = 4 if local < bars - 1 else 8
                    for n in range(subdivisions):
                        events["drums"].append(("clap", base + n * BAR // subdivisions,
                                                0.07, 42 + n * 5))

            # Signature melodic hook: rhythmically varied answers, not a constant eighth-note loop.
            if is_drop or (is_verse and local in (3, 7)):
                phrase = MOTIF if not is_final else (0, 3, 7, 10, 12, 10, 7, 5)
                rhythm = (0, 1, 2, 3, 5, 6, 7, 7.5)
                for index, (degree, beat) in enumerate(zip(phrase, rhythm)):
                    pitch = root + 24 + degree
                    if is_verse and index % 2:
                        continue
                    events["lead"].append(("arp", base + int(beat * BEAT), 0.16,
                                           78 if is_final else 66, pitch))
            elif is_build and local >= bars - 2:
                events["lead"].append(("arp", base + 3 * BEAT, 0.18, 70, root + 36 + 10))

            # Transitions: short fills, risers, and impacts placed at section boundaries.
            if is_build:
                for sixteenth in range(16):
                    events["fx"].append(("riser", base + sixteenth * BEAT // 4,
                                         0.16, 26 + sixteenth * 3, 0))
            if is_drop and local == 0:
                events["fx"].append(("impact", base, 1.1, 118, 0))
            if is_drop and local == bars - 1:
                events["fx"].append(("riser", base + 3 * BEAT, 0.8, 75, 0))

        bar_number += bars

    return events, section_starts, bar_number


def render(output, bpm=BPM, sample_rate=RENDERER.RATE):
    if not 100 <= bpm <= 150:
        raise ValueError("V3 tempo must be 100–150 BPM")
    if not 8000 <= sample_rate <= 48000:
        raise ValueError("sample rate must be 8000–48000 Hz")

    # Reuse the established stem renderer and its sound-generation primitives.
    RENDERER.build_events = build_events
    out = RENDERER.render(output, bpm, sample_rate)
    events, starts, bars = build_events()
    seconds = round(bars * 4 * 60 / bpm, 3)
    manifest = {
        "title": "Somebody's Gotta Do It — Warehouse Rave V3 Composition",
        "render_type": "composition_led_procedural_instrumental",
        "version": 3,
        "bpm": bpm,
        "meter": "4/4",
        "key_center": "A minor (provisional)",
        "bars": bars,
        "duration_seconds": seconds,
        "sample_rate": sample_rate,
        "channels": 1,
        "bit_depth": 16,
        "section_starts": starts,
        "sections": [{"name": name, "bars": length} for name, length in SECTIONS],
        "harmony": ["Am", "F", "C", "G"],
        "melodic_motif_semitones": list(MOTIF),
        "stems": [f"{name}.wav" for name in events],
        "mix": "instrumental_mix.wav",
        "vocals_rendered": False,
        "note": "Non-destructive V3 composition experiment. Reuses the established V2 procedural renderer; not mastered and contains no vocals."
    }
    (out / "audio_manifest.json").write_text(json.dumps(manifest, indent=2))
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="music-foundry/output/warehouse-rave-v3")
    parser.add_argument("--bpm", type=int, default=BPM)
    parser.add_argument("--sample-rate", type=int, default=RENDERER.RATE)
    args = parser.parse_args()
    print(render(args.output, args.bpm, args.sample_rate))
