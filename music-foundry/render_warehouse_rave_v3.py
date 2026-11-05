"""Render the V3 MIDI composition through Music Foundry's existing offline synth.

This reuses render_instrumental.py synthesis primitives; it does not introduce a new
audio engine. Output is an unmastered composition audition, not a release master.
"""
import argparse
import importlib.util
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V3 = load_module("warehouse_rave_v3", "warehouse_rave_v3.py")
RENDER = load_module("music_foundry_existing_renderer", "render_instrumental.py")


def render(output, bpm=127, sample_rate=22050):
    if not 40 <= bpm <= 240:
        raise ValueError("bpm out of range")
    if not 8000 <= sample_rate <= 48000:
        raise ValueError("sample_rate must be between 8000 and 48000")
    parts, arrangement = V3.build_notes()
    bars = sum(section["bars"] for section in arrangement)
    seconds = bars * 4 * 60 / bpm
    frames = math.ceil(seconds * sample_rate)
    if frames > sample_rate * RENDER.MAX_SECONDS:
        raise ValueError("render exceeds maximum duration")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    mix = __import__("array").array("i", [0]) * frames
    kinds = {"chords": "chords", "bass": "bass", "lead": "lead",
             "drums": "drums", "texture": "chords"}
    for index, (name, notes) in enumerate(parts.items()):
        stem = RENDER._render_part(notes, frames, sample_rate, bpm, kinds[name], 127 + index)
        RENDER._write_wav(output / f"{name}.wav", stem, sample_rate)
        for frame, value in enumerate(stem):
            mix[frame] += value
    peak = max((abs(value) for value in mix), default=0)
    gain = min(1.0, 29490 / peak) if peak else 1.0
    if gain < 1.0:
        mix = __import__("array").array("i", (round(value * gain) for value in mix))
    RENDER._write_wav(output / "instrumental_mix.wav", mix, sample_rate)
    manifest = {
        "schema": "turbo.music-foundry.audio-preview.v1",
        "title": "Somebody's Gotta Do It — Warehouse Rave V3",
        "render_type": "composition_audition_existing_procedural_synth",
        "bpm": bpm, "meter": "4/4", "bars": bars,
        "duration_seconds": round(seconds, 3), "sample_rate": sample_rate,
        "channels": 1, "bit_depth": 16,
        "stems": [f"{name}.wav" for name in parts],
        "mix": "instrumental_mix.wav", "vocals_rendered": False,
        "peak_gain_applied": round(gain, 6),
        "note": "Unmastered composition audition rendered through existing Music Foundry synthesis primitives. Not a release master."
    }
    (output / "audio_manifest.json").write_text(json.dumps(manifest, indent=2))
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="music-foundry/output/warehouse-rave-v3-audio")
    parser.add_argument("--bpm", type=int, default=127)
    parser.add_argument("--sample-rate", type=int, default=22050)
    args = parser.parse_args()
    print(render(args.output, args.bpm, args.sample_rate))
