"""Assemble consented recorded vocal takes into aligned WAV vocal stems.

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
        return [int(v) for v in values], rate
    return [(int(values[i]) + int(values[i + 1])) // 2 for i in range(0, len(values), 2)], rate


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


def _automation_value(points, parameter, time_ms, base):
    lane = sorted((point for point in points if point["param"] == parameter), key=lambda point: point["time_ms"])
    if not lane:
        return float(base)
    previous_time, previous_value = 0.0, float(base)
    for point in lane:
        point_time, point_value = float(point["time_ms"]), float(point["value"])
        if time_ms <= point_time:
            span = point_time - previous_time
            if span <= 0:
                return point_value
            ratio = (time_ms - previous_time) / span
            return previous_value + (point_value - previous_value) * ratio
        previous_time, previous_value = point_time, point_value
    return previous_value


def _validate_automation(points):
    if not isinstance(points, list) or len(points) > 64:
        raise ValueError("automation must be a list with no more than 64 points")
    ranges = {"gain_db": (-60, 12), "lowpass_hz": (500, 20000), "delay_wet": (0, 100), "delay_feedback": (0, 75), "drive_db": (0, 24), "pan": (-1, 1)}
    for point in points:
        if not isinstance(point, dict) or point.get("param") not in ranges:
            raise ValueError("automation point has an unsupported parameter")
        time_ms, value = point.get("time_ms"), point.get("value")
        low, high = ranges[point["param"]]
        if not isinstance(time_ms, (int, float)) or not 0 <= time_ms <= 180000:
            raise ValueError("automation time_ms must be between 0 and 180000")
        if not isinstance(value, (int, float)) or not low <= value <= high:
            raise ValueError(f"automation {point['param']} value is out of range")
    return sorted(points, key=lambda point: point["time_ms"])


def _apply_phrase_performance(samples, sample_rate, performance, offset_ms):
    if performance is None:
        return samples
    if not isinstance(performance, dict):
        raise ValueError("performance must be an object")
    start_ms, end_ms = performance.get("start_ms"), performance.get("end_ms")
    repeats, reverse, drop_repeat = performance.get("repeats", 1), performance.get("reverse", False), performance.get("drop_repeat", False)
    if (not isinstance(start_ms, (int, float)) or not isinstance(end_ms, (int, float))
            or start_ms < 0 or end_ms <= start_ms or end_ms > 180000
            or not isinstance(repeats, int) or not 1 <= repeats <= 8
            or not isinstance(reverse, bool) or not isinstance(drop_repeat, bool)):
        raise ValueError("performance phrase edit is outside allowed bounds")
    start, end = min(len(samples), round(start_ms * sample_rate / 1000)), min(len(samples), round(end_ms * sample_rate / 1000))
    if end <= start:
        raise ValueError("performance phrase range does not overlap the take")
    phrase = samples[start:end]
    if reverse:
        phrase = list(reversed(phrase))
    result = samples[:start] + phrase * (repeats + 1) + samples[end:]
    if drop_repeat:
        drop_seconds = 16 * 4 * 60 / 127
        relative_seconds = drop_seconds - offset_ms / 1000
        if relative_seconds >= 0:
            drop_at = round(relative_seconds * sample_rate)
            if drop_at + len(phrase) > 180 * sample_rate:
                raise ValueError("drop-triggered phrase repeat exceeds the 180-second project limit")
            result = result[:drop_at] + [0] * max(0, drop_at - len(result)) + phrase + result[drop_at:]
    if len(result) > 180 * sample_rate:
        raise ValueError("phrase performance edit exceeds the 180-second project limit")
    return result


def _apply_effects(samples, sample_rate, effects, automation=None, tempo_bpm=127):
    if not isinstance(tempo_bpm, (int, float)) or not 40 <= tempo_bpm <= 240:
        raise ValueError("tempo_bpm must be between 40 and 240")
    effects = effects or {}
    automation = _validate_automation(automation or [])
    drive_db, lowpass_hz = effects.get("drive_db", 0), effects.get("lowpass_hz", 20000)
    delay_ms, delay_feedback, delay_wet = effects.get("delay_ms", 0), effects.get("delay_feedback", 25), effects.get("delay_wet", 0)
    stutter = effects.get("stutter", "off")
    if not isinstance(drive_db, (int, float)) or not 0 <= drive_db <= 24:
        raise ValueError("effects.drive_db must be between 0 and 24")
    if not isinstance(lowpass_hz, (int, float)) or not 500 <= lowpass_hz <= 20000:
        raise ValueError("effects.lowpass_hz must be between 500 and 20000")
    if not isinstance(delay_ms, (int, float)) or not 0 <= delay_ms <= 500:
        raise ValueError("effects.delay_ms must be between 0 and 500")
    if not isinstance(delay_feedback, (int, float)) or not 0 <= delay_feedback <= 75:
        raise ValueError("effects.delay_feedback must be between 0 and 75")
    if not isinstance(delay_wet, (int, float)) or not 0 <= delay_wet <= 100:
        raise ValueError("effects.delay_wet must be between 0 and 100")
    if stutter not in ("off", "1/4", "1/8", "1/16"):
        raise ValueError("effects.stutter must be off, 1/4, 1/8 or 1/16")
    output = [float(value) for value in samples]
    if stutter != "off" and output:
        divisor = {"1/4": 4, "1/8": 8, "1/16": 16}[stutter]
        slice_frames = max(1, round((60.0 / tempo_bpm / divisor) * sample_rate))
        first_slice = output[:slice_frames]
        output = [first_slice[index % len(first_slice)] for index in range(len(output))]
    if drive_db or any(point["param"] == "drive_db" for point in automation):
        shaped = []
        for index, value in enumerate(output):
            time_ms = index * 1000.0 / sample_rate
            current_drive = _automation_value(automation, "drive_db", time_ms, drive_db)
            if current_drive <= 0:
                shaped.append(value)
                continue
            amount = 10.0 ** (current_drive / 20.0)
            normalizer = math.tanh(amount)
            shaped.append(math.tanh((value / 32768.0) * amount) / normalizer * 32768.0)
        output = shaped
    if output and (lowpass_hz < 19999 or any(p["param"] == "lowpass_hz" for p in automation)):
        previous, filtered = 0.0, []
        for index, value in enumerate(output):
            time_ms = index * 1000.0 / sample_rate
            cutoff = _automation_value(automation, "lowpass_hz", time_ms, lowpass_hz)
            alpha = 1.0 - math.exp(-2.0 * math.pi * cutoff / sample_rate)
            previous += alpha * (value - previous)
            filtered.append(previous)
        output = filtered
    if delay_ms and (delay_wet or any(p["param"] == "delay_wet" for p in automation)) and output:
        delay_frames = max(1, round(delay_ms * sample_rate / 1000.0))
        ring, delayed = [0.0] * delay_frames, []
        for index in range(len(output) + delay_frames * 8):
            time_ms = index * 1000.0 / sample_rate
            value = output[index] if index < len(output) else 0.0
            echo = ring[index % delay_frames]
            wet = _automation_value(automation, "delay_wet", time_ms, delay_wet) / 100.0
            feedback = _automation_value(automation, "delay_feedback", time_ms, delay_feedback) / 100.0
            delayed.append(value * (1.0 - wet) + echo * wet)
            ring[index % delay_frames] = value + echo * feedback
        output = delayed
    return output


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
    layer_states = config.get("layer_states", {})
    if not isinstance(layer_states, dict) or set(layer_states) - set(LAYERS):
        raise ValueError("layer_states must contain only supported vocal layers")
    normalized_layer_states = {}
    for name in LAYERS:
        state = layer_states.get(name, {})
        if not isinstance(state, dict) or any(key not in ("muted", "solo") for key in state):
            raise ValueError(f"invalid layer state for {name}")
        if any(not isinstance(value, bool) for value in state.values()):
            raise ValueError(f"layer state flags for {name} must be booleans")
        normalized_layer_states[name] = {"muted": state.get("muted", False), "solo": state.get("solo", False)}
    if any(not isinstance(take, dict) for take in takes):
        raise ValueError("every take must be an object")
    if any(not isinstance(take.get("muted", False), bool) or not isinstance(take.get("solo", False), bool) for take in takes):
        raise ValueError("take mute and solo flags must be booleans")
    if any(take.get("solo", False) and take.get("muted", False) for take in takes):
        raise ValueError("a take cannot be both muted and soloed")
    if unknown_layers:
        raise ValueError(f"unsupported vocal layers: {sorted(unknown_layers)}")
    solo_active = any(take.get("solo", False) and not take.get("muted", False) and not normalized_layer_states[take["layer"]]["muted"] for take in takes) or any(state["solo"] and not state["muted"] for state in normalized_layer_states.values())
    layer_buffers = {name: (array.array("d", [0.0]) * total_frames, array.array("d", [0.0]) * total_frames) for name in used_layers}
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
        offset_ms, gain_db, pan = take.get("offset_ms", 0), take.get("gain_db", 0), take.get("pan", 0)
        if not isinstance(offset_ms, (int, float)) or offset_ms < 0:
            raise ValueError(f"take {index}: offset_ms must be non-negative")
        if not isinstance(gain_db, (int, float)) or not -60 <= gain_db <= 12:
            raise ValueError(f"take {index}: gain_db must be between -60 and 12")
        if not isinstance(pan, (int, float)) or not -1 <= pan <= 1:
            raise ValueError(f"take {index}: pan must be between -1 and 1")
        if not source_path.is_file():
            raise ValueError(f"take {index}: source WAV not found: {relative_path}")
        source_metadata = take.get("source", {})
        if not isinstance(source_metadata, dict):
            raise ValueError(f"take {index}: source metadata must be an object")
        vocal_type = source_metadata.get("vocal_type", "spoken")
        if vocal_type not in ("spoken", "sung", "chant", "gang_shout"):
            raise ValueError(f"take {index}: unsupported source vocal_type")
        samples, source_rate = _read_pcm16(source_path)
        samples = _resample(samples, source_rate, sample_rate)
        effects, automation, performance = take.get("effects", {}), _validate_automation(take.get("automation", [])), take.get("performance")
        if not isinstance(effects, dict):
            raise ValueError(f"take {index}: effects must be an object")
        samples = _apply_effects(samples, sample_rate, effects, automation)
        samples = _apply_phrase_performance(samples, sample_rate, performance, offset_ms)
        take_muted, take_solo = take.get("muted", False), take.get("solo", False)
        audible = not take_muted and not normalized_layer_states[layer]["muted"] and (not solo_active or take_solo or normalized_layer_states[layer]["solo"])
        start = round(offset_ms * sample_rate / 1000)
        if start >= total_frames:
            raise ValueError(f"take {index}: offset starts after project duration")
        left, right = layer_buffers[layer]
        count = min(len(samples), total_frames - start) if audible else 0
        for frame in range(count):
            time_ms = frame * 1000.0 / sample_rate
            automated_gain = _automation_value(automation, "gain_db", time_ms, gain_db)
            automated_pan = _automation_value(automation, "pan", time_ms, pan)
            value = samples[frame] * (10.0 ** (automated_gain / 20.0))
            left_pan = math.sqrt((1.0 - automated_pan) / 2.0) * math.sqrt(2.0)
            right_pan = math.sqrt((1.0 + automated_pan) / 2.0) * math.sqrt(2.0)
            left[start + frame] += value * left_pan
            right[start + frame] += value * right_pan
        take_records.append({
            "file": relative_path, "layer": layer, "offset_ms": offset_ms,
            "gain_db": gain_db, "pan": pan, "effects": effects, "automation": automation,
            "performance": performance, "source_sample_rate": source_rate,
            "source": source_metadata, "vocal_type": vocal_type,
            "frames_placed": count, "muted": take_muted, "solo": take_solo, "audible": audible
        })
    mix_left, mix_right = array.array("d", [0.0]) * total_frames, array.array("d", [0.0]) * total_frames
    for left, right in layer_buffers.values():
        for frame in range(total_frames):
            mix_left[frame] += left[frame]
            mix_right[frame] += right[frame]
    peak = max(max((abs(v) for v in mix_left), default=0.0), max((abs(v) for v in mix_right), default=0.0))
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
    _write_stereo(output / "spoken_vocal_mix.wav", mix_left, mix_right, sample_rate, normalization_gain)
    sung_vocals_rendered = any(record["vocal_type"] in ("sung", "chant") and record["audible"] for record in take_records)
    render_type = "vocal_take_assembly" if sung_vocals_rendered else "recorded_spoken_take_assembly"
    result = {
        "schema": "turbo.music-foundry.spoken-takes-render.v1",
        "render_type": render_type,
        "sample_rate": sample_rate, "channels": 2, "bit_depth": 16, "duration_seconds": duration,
        "take_count": len(take_records), "audible_take_count": sum(record["audible"] for record in take_records),
        "solo_active": solo_active, "layer_states": normalized_layer_states,
        "stems": rendered, "mix": "spoken_vocal_mix.wav",
        "normalization_gain": round(normalization_gain, 8), "source_takes_modified": False,
        "speech_synthesized": False, "sung_vocals_rendered": sung_vocals_rendered,
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
