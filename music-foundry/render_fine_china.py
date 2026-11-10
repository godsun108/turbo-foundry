"""Render Fine China through Music Foundry's existing offline synthesizer.

126 BPM, A minor, 120 bars (~3:49). This is a mono composition audition,
not a mastered release. It intentionally renders no vocals.
"""
import argparse
import importlib.util
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, HERE / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

COMPOSE = load("fine_china_arrangement", "fine_china_arrangement.py")
SYNTH = load("music_foundry_existing_renderer", "render_instrumental.py")


def render(output, bpm=126, sample_rate=22050):
    if not 40 <= bpm <= 240:
        raise ValueError("bpm out of range")
    if not 8000 <= sample_rate <= 48000:
        raise ValueError("sample_rate must be between 8000 and 48000")
    parts, arrangement = COMPOSE.build_notes()
    bars = sum(section["bars"] for section in arrangement)
    seconds = bars * 4 * 60 / bpm
    frames = math.ceil(seconds * sample_rate)
    if frames > sample_rate * SYNTH.MAX_SECONDS:
        raise ValueError("render exceeds maximum duration")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    mix = __import__("array").array("i", [0]) * frames
    for index, (name, notes) in enumerate(parts.items()):
        kind = "drums" if name == "drums" else ("lead" if name in ("lead", "texture") else name)
        stem = SYNTH._render_part(notes, frames, sample_rate, bpm, kind, 521 + index)
        SYNTH._write_wav(output / f"{name}.wav", stem, sample_rate)
        for frame, value in enumerate(stem):
            mix[frame] += value
    peak = max((abs(value) for value in mix), default=0)
    gain = min(1.0, 29490 / peak) if peak else 1.0
    if gain < 1.0:
        mix = __import__("array").array("i", (round(value * gain) for value in mix))
    SYNTH._write_wav(output / "instrumental_mix.wav", mix, sample_rate)
    manifest = {
        "schema": "turbo.music-foundry.audio-preview.v1",
        "project_id": "fine-china",
        "title": "Fine China (Eat On It)",
        "render_type": "original_procedural_soulful_bass_house_audition",
        "bpm": bpm, "meter": "4/4", "bars": bars,
        "key_center": "A minor", "chord_progression": ["Am", "F", "C", "G"],
        "duration_seconds": round(seconds, 3), "sample_rate": sample_rate,
        "channels": 1, "bit_depth": 16,
        "arrangement": arrangement,
        "stems": [f"{name}.wav" for name in parts],
        "mix": "instrumental_mix.wav", "vocals_rendered": False,
        "peak_gain_applied": round(gain, 6),
        "note": "Unmastered original composition audition. No vocals are included."
    }
    (output / "audio_manifest.json").write_text(json.dumps(manifest, indent=2))
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="music-foundry/output/fine-china-audio")
    parser.add_argument("--bpm", type=int, default=126)
    parser.add_argument("--sample-rate", type=int, default=22050)
    args = parser.parse_args()
    print(render(args.output, args.bpm, args.sample_rate))
