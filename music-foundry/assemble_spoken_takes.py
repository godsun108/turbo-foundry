"""Assemble consented recorded spoken takes into aligned WAV vocal stems.

This is an editor/assembler, not a speech synthesizer or sung-vocal renderer.
Source WAV files are read only and never modified.
"""
import argparse
import array
import json
import math
import wave
from pathlib import Path

LAYERS = ("dry_lead", "gang_vocals", "adlibs", "chops", "whisper_double")
DEFAULT_RATE = 48000
MAX_SECONDS = 180
MAX_TAKES = 128


def _read_pcm16(path):
    with wave.open(str(path), "rb") as wav:
        channels = wav.getnchannels()
        width = wav.getsampwidth()
        rate = wav.getframerate()
        frames = wav.getnframes()
        compression = wav.getcomptype()
        if compression != "NONE":
            raise ValueError(f"{path}: compressed WAV is not supported")
        if channels not in (1, 2) or width != 2:
            raise ValueError(f"{path}: expected 16-bit mono or stereo PCM WAV")
        if not 8000 <= rate <= 96000:
            raise ValueError(f"{path}: sample rate must be between 8000 and 96000 Hz")
        raw = wav.readframes(frames)
    values = array.array("h")
    values.frombytes(raw)
    if len(values) != frames * channels:
        raise ValueError(f"{path}: truncated WAV data")
    if channels == 1:
        mono = [int(v) for v in values]
        return mono, rate
    mono = [(int(values[i]) + int(values[i + 1])) // 2 for i in range(0, len(values), 2)]
    return mono, rate


def _resample(samples, source_rate, target_rate):
    if source_rate == target_rate:
        return samples
    if not samples:
        return []
    output_count = max(1, round(len(samples) * target_rate / source_rate))
    result = []
    ratio = source_rate / target_rate
    last = len(samples) - 1
    for index in range(output_count):
        position = index * ratio
        left = min(last, int(position))
        right = min(last, left + 1)
        fraction = position - left
        result.append(round(samples[left] * (1.0 - fraction) + samples[right] * fraction))
    return result


def _write_stereo(path, left, right, sample_rate, gain=1.0):
    frames = array.array("h")
    for l_value, r_value in zip(left, right):
        frames.append(max(-32768, min(32767, round(l_value * gain))))
        frames.append(max(-32768, min(32767, round(r_value * gain))))
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(frames.tobytes())


def assemble(manifest_path, output, sample_rate=DEFAULT_RATE):
    manifest_path = Path(manifest_path).resolve()
    if not 8000 <= sample_rate <= 96000:
        raise ValueError("sample_rate must be between 8000 and 96000 Hz")
    config = json.loads(manifest_path.read_text())
    if config.get("schema") != "turbo.music-foundry.spoken-takes.v1":
        raise ValueError("unsupported spoken-takes manifest schema")
    duration = config.get("duration_seconds")
    if not isinstance(duration, (int, float)) or not 0 < duration <= MAX_SECONDS:
        raise ValueError(f"duration_seconds must be greater than 0 and at most {MAX_SECONDS}")
    takes = config.get("takes")
    if not isinstance(takes, list) or len(takes) > MAX_TAKES:
        raise ValueError(f"takes must be a list with no more than {MAX_TAKES} entries")
    total_frames = math.ceil(duration * sample_rate)
    used_layers = {take.get("layer") for take in takes if isinstance(take, dict)}
    unknown_layers = used_layers - set(LAYERS)
    if unknown_layers:
        raise ValueError(f"unsupported vocal layers: {sorted(unknown_layers)}")
    layer_buffers = {
        name: (array.array("d", [0.0]) * total_frames,
               array.array("d", [0.0]) * total_frames)
        for name in used_layers
    }
    source_root = manifest_path.parent
    take_records = []
    for index, take in enumerate(takes):
        if not isinstance(take, dict):
            raise ValueError(f"take {index} must be an object")
        layer = take.get("layer")
        if layer not in LAYERS:
            raise ValueError(f"take {index}: unsupported layer {layer!r}")
        relative_path = take.get("file")
        if not isinstance(relative_path, str) or not relative_path.strip():
            raise ValueError(f"take {index}: file must be a non-empty relative path")
        source_path = (source_root / relative_path).resolve()
        if source_root not in source_path.parents:
            raise ValueError(f"take {index}: source file must remain inside the project folder")
        offset_ms = take.get("offset_ms", 0)
        gain_db = take.get("gain_db", 0)
        pan = take.get("pan", 0)
        if not isinstance(offset_ms, (int, float)) or offset_ms < 0:
            raise ValueError(f"take {index}: offset_ms must be non-negative")
        if not isinstance(gain_db, (int, float)) or not -60 <= gain_db <= 12:
            raise ValueError(f"take {index}: gain_db must be between -60 and 12")
        if not isinstance(pan, (int, float)) or not -1 <= pan <= 1:
            raise ValueError(f"take {index}: pan must be between -1 and 1")
        if not source_path.is_file():
            raise ValueError(f"take {index}: source WAV not found: {relative_path}")
        samples, source_rate = _read_pcm16(source_path)
        samples = _resample(samples, source_rate, sample_rate)
        start = round(offset_ms * sample_rate / 1000)
        if start >= total_frames:
            raise ValueError(f"take {index}: offset starts after project duration")
        gain = 10.0 ** (gain_db / 20.0)
        left_pan = math.sqrt((1.0 - pan) / 2.0) * math.sqrt(2.0)
        right_pan = math.sqrt((1.0 + pan) / 2.0) * math.sqrt(2.0)
        left, right = layer_buffers[layer]
        count = min(len(samples), total_frames - start)
        for frame in range(count):
            value = samples[frame] * gain
            left[start + frame] += value * left_pan
            right[start + frame] += value * right_pan
        take_records.append({
            "file": relative_path, "layer": layer, "offset_ms": offset_ms,
            "gain_db": gain_db, "pan": pan, "source_sample_rate": source_rate,
            "frames_placed": count
        })
    mix_left = array.array("d", [0.0]) * total_frames
    mix_right = array.array("d", [0.0]) * total_frames
    for left, right in layer_buffers.values():
        for frame in range(total_frames):
            mix_left[frame] += left[frame]
            mix_right[frame] += right[frame]
    peak = max(
        max((abs(v) for v in mix_left), default=0.0),
        max((abs(v) for v in mix_right), default=0.0)
    )
    normalization_gain = min(1.0, 29490.0 / peak) if peak else 1.0
    output = Path(output).resolve()
    if output == source_root:
        raise ValueError("output folder must be separate from the source-take folder")
    output.mkdir(parents=True, exist_ok=True)
    rendered = []
    for name, (left, right) in layer_buffers.items():
        if any(left) or any(right):
            filename = f"{name}.wav"
            _write_stereo(output / filename, left, right, sample_rate, normalization_gain)
            rendered.append(filename)
    _write_stereo(output / "spoken_vocal_mix.wav", mix_left, mix_right,
                  sample_rate, normalization_gain)
    result = {
        "schema": "turbo.music-foundry.spoken-takes-render.v1",
        "render_type": "recorded_spoken_take_assembly",
        "sample_rate": sample_rate,
        "channels": 2,
        "bit_depth": 16,
        "duration_seconds": duration,
        "take_count": len(take_records),
        "stems": rendered,
        "mix": "spoken_vocal_mix.wav",
        "normalization_gain": round(normalization_gain, 8),
        "source_takes_modified": False,
        "speech_synthesized": False,
        "sung_vocals_rendered": False,
        "takes": take_records
    }
    (output / "spoken_audio_manifest.json").write_text(json.dumps(result, indent=2))
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, help="Path to spoken-takes.json")
    parser.add_argument("--output", required=True)
    parser.add_argument("--sample-rate", type=int, default=DEFAULT_RATE)
    args = parser.parse_args()
    print(assemble(args.manifest, args.output, args.sample_rate))
