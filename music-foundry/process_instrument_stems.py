"""Non-destructive instrument-stem processing using Music Foundry's existing DSP.

Reads an existing stem manifest and PCM WAV stems, applies the same bounded
drive/filter/delay/automation primitives used by the vocal assembler, and
writes processed stereo stems plus a mix to a separate output folder.
Dry source stems are never modified. This is an optional processing pass,
not a new DAW or synthesis engine.
"""
import argparse
import hashlib
import json
import math
import wave
import array
from pathlib import Path

from assemble_spoken_takes import (
    _apply_effects,
    _automation_value,
    _read_pcm16,
    _validate_automation,
)

SCHEMA = "turbo.music-foundry.instrument-stem-processing.v1"
TARGET_PEAK = 29490


def _write_stereo(path, samples_left, samples_right, sample_rate, gain=1.0):
    frames = array.array("h")
    for left, right in zip(samples_left, samples_right):
        frames.append(max(-32768, min(32767, round(left * gain))))
        frames.append(max(-32768, min(32767, round(right * gain))))
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(frames.tobytes())


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def process(config_path, output_path):
    config_path = Path(config_path).resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("schema") != SCHEMA:
        raise ValueError("unsupported instrument stem processing schema")
    source_manifest_rel = config.get("source_manifest")
    if not isinstance(source_manifest_rel, str) or not source_manifest_rel.strip():
        raise ValueError("source_manifest must be a relative path")
    config_root = config_path.parent
    source_manifest = (config_root / source_manifest_rel).resolve()
    if config_root not in source_manifest.parents or not source_manifest.is_file():
        raise ValueError("source_manifest must resolve to a file inside the project folder")
    source_root = source_manifest.parent
    source = json.loads(source_manifest.read_text(encoding="utf-8"))
    stem_files = source.get("stems")
    if not isinstance(stem_files, list) or not stem_files or len(stem_files) > 32:
        raise ValueError("source manifest must contain 1–32 stem filenames")
    bpm = source.get("bpm", 127)
    if not isinstance(bpm, (int, float)) or not 40 <= bpm <= 240:
        raise ValueError("source manifest bpm must be between 40 and 240")
    settings = config.get("stems", {})
    if not isinstance(settings, dict) or set(settings) - set(stem_files):
        raise ValueError("stems settings must be an object keyed only by source stem filenames")

    rendered = {}
    sample_rate = None
    for filename in stem_files:
        if not isinstance(filename, str) or Path(filename).name != filename or not filename.lower().endswith(".wav"):
            raise ValueError("stem entries must be plain WAV filenames")
        source_path = (source_root / filename).resolve()
        if source_root not in source_path.parents or not source_path.is_file():
            raise ValueError(f"source stem not found inside project folder: {filename}")
        samples, rate = _read_pcm16(source_path)
        if sample_rate is None:
            sample_rate = rate
        elif rate != sample_rate:
            raise ValueError("all source stems must use the same sample rate")
        stem_settings = settings.get(filename, {})
        if not isinstance(stem_settings, dict):
            raise ValueError(f"settings for {filename} must be an object")
        effects = stem_settings.get("effects", {})
        if not isinstance(effects, dict):
            raise ValueError(f"{filename}: effects must be an object")
        automation = _validate_automation(stem_settings.get("automation", []))
        gain_db = stem_settings.get("gain_db", 0)
        pan = stem_settings.get("pan", 0)
        if not isinstance(gain_db, (int, float)) or not -60 <= gain_db <= 12:
            raise ValueError(f"{filename}: gain_db must be between -60 and 12")
        if not isinstance(pan, (int, float)) or not -1 <= pan <= 1:
            raise ValueError(f"{filename}: pan must be between -1 and 1")
        processed = _apply_effects(samples, rate, effects, automation, tempo_bpm=bpm)
        for index, value in enumerate(processed):
            time_ms = index * 1000.0 / rate
            automated_db = _automation_value(automation, "gain_db", time_ms, gain_db)
            processed[index] = value * (10.0 ** (automated_db / 20.0))
        left_pan = math.sqrt((1.0 - pan) / 2.0) * math.sqrt(2.0)
        right_pan = math.sqrt((1.0 + pan) / 2.0) * math.sqrt(2.0)
        left = [value * left_pan for value in processed]
        right = [value * right_pan for value in processed]
        rendered[filename] = {
            "left": left, "right": right, "source": source_path,
            "settings": {"effects": effects, "automation": automation, "gain_db": gain_db, "pan": pan},
        }

    mix_length = max(len(item["left"]) for item in rendered.values())
    mix_left = [0.0] * mix_length
    mix_right = [0.0] * mix_length
    for item in rendered.values():
        for index, value in enumerate(item["left"]):
            mix_left[index] += value
        for index, value in enumerate(item["right"]):
            mix_right[index] += value
    peak = max(max((abs(value) for value in mix_left), default=0),
               max((abs(value) for value in mix_right), default=0))
    normalization_gain = min(1.0, TARGET_PEAK / peak) if peak else 1.0

    output = Path(output_path).resolve()
    if output == source_root or source_root in output.parents:
        raise ValueError("output folder must be outside the source stem folder")
    output.mkdir(parents=True, exist_ok=False)
    output_stems = []
    records = []
    for filename, item in rendered.items():
        stem_path = output / filename
        _write_stereo(stem_path, item["left"], item["right"], sample_rate, normalization_gain)
        output_stems.append(filename)
        records.append({
            "file": filename,
            "source_sha256": _sha256(item["source"]),
            "effects": item["settings"]["effects"],
            "automation": item["settings"]["automation"],
            "gain_db": item["settings"]["gain_db"],
            "pan": item["settings"]["pan"],
        })
    _write_stereo(output / "instrumental_mix.wav", mix_left, mix_right, sample_rate, normalization_gain)
    result = {
        "schema": "turbo.music-foundry.instrument-stem-render.v1",
        "render_type": "non_destructive_instrument_stem_processing",
        "source_manifest": str(source_manifest.relative_to(config_root)),
        "source_stems_modified": False,
        "bpm": bpm,
        "sample_rate": sample_rate,
        "channels": 2,
        "bit_depth": 16,
        "stems": output_stems,
        "mix": "instrumental_mix.wav",
        "normalization_gain": round(normalization_gain, 8),
        "stems_processed": records,
    }
    (output / "instrument_stem_manifest.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to instrument-stem-processing.json")
    parser.add_argument("--output", required=True, help="Separate output folder; must not already exist")
    args = parser.parse_args()
    print(process(args.config, args.output))
