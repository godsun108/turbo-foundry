"""Dependency-free offline WAV synthesizer for the original instrumental MIDI arrangement.

This renders instrumental sound only. It does not synthesize spoken or sung vocals.
"""
import argparse
import array
import importlib.util
import json
import math
import random
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("project_arranger", HERE / "arrange_project.py")
ARRANGER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ARRANGER)

DEFAULT_RATE = 22050
MAX_SECONDS = 900
MAX_FRAMES = DEFAULT_RATE * MAX_SECONDS


def midi_hz(note):
    return 440.0 * (2.0 ** ((note - 69) / 12.0))


def _synth_note(target, start, duration, pitch, velocity, sample_rate, kind, rng):
    end = min(len(target), start + duration)
    if start >= end:
        return
    freq = midi_hz(pitch)
    amp = (velocity / 127.0) * 0.22
    phase_step = 2.0 * math.pi * freq / sample_rate
    for frame in range(start, end):
        t = frame - start
        progress = t / max(1, duration)
        if kind == "drums":
            if pitch == 36:  # kick: descending sine with fast transient
                phase = 2.0 * math.pi * (freq * 0.55 * (t / sample_rate) +
                                          34.0 * (1.0 - math.exp(-t / (sample_rate * 0.035))) * 0.035)
                env = math.exp(-t / (sample_rate * 0.19))
                sample = math.sin(phase) * env
            elif pitch in (38, 40):  # snare/clap: noise plus a short tonal body
                env = math.exp(-t / (sample_rate * 0.075))
                sample = (rng.random() * 2.0 - 1.0) * 0.72 * env
                sample += math.sin(2.0 * math.pi * 185.0 * t / sample_rate) * 0.2 * env
            else:  # hats/cymbals
                env = math.exp(-t / (sample_rate * 0.045))
                sample = (rng.random() * 2.0 - 1.0) * env * 0.45
        elif kind == "bass":
            env = min(1.0, t / max(1, int(sample_rate * 0.006))) * math.exp(-progress * 3.0)
            phase = (t * freq / sample_rate) % 1.0
            sample = (2.0 * phase - 1.0) * env
        elif kind == "lead":
            env = min(1.0, t / max(1, int(sample_rate * 0.004))) * math.exp(-progress * 5.0)
            sample = (math.sin(2.0 * math.pi * freq * t / sample_rate) * 0.75 +
                      math.sin(2.0 * math.pi * freq * 2.01 * t / sample_rate) * 0.25) * env
        else:  # warm, softly detuned chord layer
            attack = min(1.0, t / max(1, int(sample_rate * 0.035)))
            release = min(1.0, max(0.0, (duration - t) / max(1, int(sample_rate * 0.08))))
            sample = (math.sin(2.0 * math.pi * freq * t / sample_rate) * 0.7 +
                      math.sin(2.0 * math.pi * freq * 1.003 * t / sample_rate) * 0.3) * attack * release
        target[frame] += int(sample * amp * 32767)


def _render_part(notes, total_frames, sample_rate, bpm, kind, seed):
    pcm = array.array("i", [0]) * total_frames
    rng = random.Random(seed)
    for pitch, start_tick, duration_tick, velocity in notes:
        start = round(start_tick * sample_rate * 60 / (ARRANGER.PPQ * bpm))
        duration = max(1, round(duration_tick * sample_rate * 60 / (ARRANGER.PPQ * bpm)))
        _synth_note(pcm, start, duration, pitch, velocity, sample_rate, kind, rng)
    return pcm


def _write_wav(path, samples, sample_rate):
    out = array.array("h")
    for value in samples:
        out.append(max(-32768, min(32767, int(value))))
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(out.tobytes())


def render(output, bpm=127, sample_rate=DEFAULT_RATE):
    if not 40 <= bpm <= 240:
        raise ValueError("bpm out of range")
    if not 8000 <= sample_rate <= 48000:
        raise ValueError("sample_rate must be between 8000 and 48000")
    parts, _, bars = ARRANGER.build_notes()
    seconds = bars * 4 * 60 / bpm
    total_frames = math.ceil(seconds * sample_rate)
    if total_frames > sample_rate * MAX_SECONDS:
        raise ValueError("render exceeds maximum duration")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    mix = array.array("i", [0]) * total_frames
    for index, (name, (notes, _channel, _program)) in enumerate(parts.items()):
        kind = "drums" if name == "drums" else name
        stem = _render_part(notes, total_frames, sample_rate, bpm, kind, 127 + index)
        _write_wav(output / f"{name}.wav", stem, sample_rate)
        for frame, value in enumerate(stem):
            mix[frame] += value
    peak = max((abs(value) for value in mix), default=0)
    gain = min(1.0, 29490 / peak) if peak else 1.0
    if gain < 1.0:
        mix = array.array("i", (round(value * gain) for value in mix))
    _write_wav(output / "instrumental_mix.wav", mix, sample_rate)
    manifest = {
        "title": "Somebody's Gotta Do It",
        "render_type": "procedural_instrumental",
        "bpm": bpm,
        "sample_rate": sample_rate,
        "channels": 1,
        "bit_depth": 16,
        "duration_seconds": round(seconds, 3),
        "stems": [f"{name}.wav" for name in parts],
        "mix": "instrumental_mix.wav",
        "vocals_rendered": False,
        "mix_peak_normalized": True,
        "note": "Original synthesized instrumental preview. No spoken or sung vocals are included."
    }
    (output / "audio_manifest.json").write_text(json.dumps(manifest, indent=2))
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="music-foundry/output/somebodys-gotta-do-it-audio")
    parser.add_argument("--bpm", type=int, default=127)
    parser.add_argument("--sample-rate", type=int, default=DEFAULT_RATE)
    args = parser.parse_args()
    print(render(args.output, args.bpm, args.sample_rate))
