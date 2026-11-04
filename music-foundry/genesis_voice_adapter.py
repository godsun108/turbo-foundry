"""Offline Piper bridge for Genesis/Music Foundry spoken-vocal rendering.

This adapter invokes an explicitly installed local Piper executable and a
locally supplied voice model. It never downloads models or calls a network
service. Singing synthesis is deliberately outside this adapter.
"""
from __future__ import annotations

import os
import shutil
import struct
import subprocess
import tempfile
import wave
from pathlib import Path
from typing import Callable

from vocal_render_contract import validate_render_request

ENGINE_SCHEMA = "turbo.music-foundry.local-voice-engine.v1"
MAX_TEXT_CHARS = 4000
MIN_SOURCE_RATE = 8000
MAX_SOURCE_RATE = 96000


class VoiceRenderError(RuntimeError):
    """A local voice render could not be completed safely."""


def validate_engine_descriptor(descriptor: dict) -> tuple[str, ...]:
    errors: list[str] = []
    if not isinstance(descriptor, dict):
        return ("engine descriptor must be an object",)
    if descriptor.get("schema") != ENGINE_SCHEMA:
        errors.append(f"schema must be {ENGINE_SCHEMA}")
    if descriptor.get("engine") != "piper-cli":
        errors.append("engine must be piper-cli")
    if descriptor.get("execution") != "local":
        errors.append("execution must be local")
    if descriptor.get("modes") != ["spoken"]:
        errors.append("this adapter supports spoken mode only")
    if descriptor.get("credential_handling") != "none":
        errors.append("local Piper must not require credentials")
    executable = descriptor.get("executable")
    if not isinstance(executable, str) or not executable.strip():
        errors.append("executable must identify an installed local Piper command")
    model_path = descriptor.get("model_path")
    if not isinstance(model_path, str) or not model_path.strip():
        errors.append("model_path must identify a local voice model")
    timeout = descriptor.get("timeout_seconds", 60)
    if not isinstance(timeout, int) or isinstance(timeout, bool) or not 1 <= timeout <= 180:
        errors.append("timeout_seconds must be an integer from 1 to 180")
    forbidden = {"api_key", "token", "secret", "password", "authorization", "access_token"}
    if any(str(key).lower().replace("-", "_") in forbidden for key in descriptor):
        errors.append("engine descriptor contains a forbidden credential field")
    return tuple(errors)


def _resolve_executable(value: str) -> str:
    candidate = Path(value).expanduser()
    if candidate.parent != Path(".") or candidate.is_absolute():
        resolved = candidate.resolve()
        if not resolved.is_file() or not os.access(resolved, os.X_OK):
            raise VoiceRenderError("configured Piper executable is not an executable local file")
        return str(resolved)
    resolved = shutil.which(value)
    if not resolved:
        raise VoiceRenderError("Piper executable is not installed or not on PATH")
    return resolved


def _normalize_wav(source: Path, destination: Path, sample_rate: int, channels: int) -> None:
    try:
        with wave.open(str(source), "rb") as reader:
            if reader.getcomptype() != "NONE" or reader.getsampwidth() != 2:
                raise VoiceRenderError("Piper output must be uncompressed 16-bit PCM WAV")
            if reader.getnchannels() != 1:
                raise VoiceRenderError("Piper output must be mono WAV")
            source_rate = reader.getframerate()
            if not MIN_SOURCE_RATE <= source_rate <= MAX_SOURCE_RATE:
                raise VoiceRenderError("Piper output sample rate is outside the accepted range")
            raw = reader.readframes(reader.getnframes())
    except (wave.Error, EOFError) as exc:
        raise VoiceRenderError("Piper did not produce a valid WAV file") from exc

    if not raw:
        raise VoiceRenderError("Piper produced an empty WAV file")
    samples = struct.unpack("<" + "h" * (len(raw) // 2), raw)
    if source_rate == sample_rate:
        converted = samples
    else:
        output_count = max(1, round(len(samples) * sample_rate / source_rate))
        last = len(samples) - 1
        converted_list = []
        for index in range(output_count):
            position = index * source_rate / sample_rate
            left = min(int(position), last)
            right = min(left + 1, last)
            fraction = position - left
            value = round(samples[left] * (1 - fraction) + samples[right] * fraction)
            converted_list.append(max(-32768, min(32767, value)))
        converted = tuple(converted_list)

    if channels == 1:
        output_samples = converted
    else:
        output_samples = tuple(value for sample in converted for value in (sample, sample))
    packed = struct.pack("<" + "h" * len(output_samples), *output_samples)

    destination.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(destination), "wb") as writer:
        writer.setnchannels(channels)
        writer.setsampwidth(2)
        writer.setframerate(sample_rate)
        writer.writeframes(packed)


def render_spoken(
    *,
    text: str,
    request: dict,
    descriptor: dict,
    output_path: str | Path,
    authorized: bool = False,
    overwrite: bool = False,
    runner: Callable = subprocess.run,
) -> dict:
    """Render spoken text to PCM WAV using a local Piper installation.

    Dispatch is denied by default. The caller must explicitly authorize this
    local render. No shell is used and no model is downloaded.
    """
    if authorized is not True:
        raise VoiceRenderError("local voice dispatch is not authorized")
    errors = validate_engine_descriptor(descriptor)
    if errors:
        raise VoiceRenderError("; ".join(errors))
    request_check = validate_render_request(request)
    if not request_check.ok:
        raise VoiceRenderError("; ".join(request_check.errors))
    if request.get("mode") != "spoken":
        raise VoiceRenderError("Piper adapter cannot render sung vocals")
    if request.get("bit_depth") != 16:
        raise VoiceRenderError("Piper adapter currently exports 16-bit PCM only")
    if not isinstance(text, str) or not text.strip() or len(text) > MAX_TEXT_CHARS or "\x00" in text:
        raise VoiceRenderError(f"text must contain 1–{MAX_TEXT_CHARS} printable characters")

    model = Path(descriptor["model_path"]).expanduser().resolve()
    if not model.is_file() or model.suffix.lower() != ".onnx":
        raise VoiceRenderError("configured Piper model must be an existing local .onnx file")
    executable = _resolve_executable(descriptor["executable"])
    destination = Path(output_path).expanduser().resolve()
    if destination.exists() and not overwrite:
        raise VoiceRenderError("output already exists; set overwrite=True to replace it")
    if destination.suffix.lower() != ".wav":
        raise VoiceRenderError("output path must end in .wav")
    if not destination.parent.is_dir():
        raise VoiceRenderError("output directory must already exist")

    with tempfile.TemporaryDirectory(prefix="genesis-voice-") as work:
        generated = Path(work) / "piper-output.wav"
        command = [executable, "--model", str(model), "--output_file", str(generated)]
        try:
            result = runner(
                command,
                input=text,
                text=True,
                capture_output=True,
                timeout=descriptor.get("timeout_seconds", 60),
                check=False,
                shell=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise VoiceRenderError("local Piper render timed out") from exc
        except OSError as exc:
            raise VoiceRenderError("could not start the local Piper executable") from exc
        if result.returncode != 0:
            raise VoiceRenderError("local Piper returned a non-zero exit status")
        if not generated.is_file():
            raise VoiceRenderError("local Piper completed without producing a WAV file")

        staged = Path(work) / "normalized.wav"
        _normalize_wav(
            generated, staged, request["sample_rate"], request["channels"]
        )
        if destination.exists() and not overwrite:
            raise VoiceRenderError("output appeared during rendering; refusing to replace it")
        shutil.copyfile(staged, destination)

    with wave.open(str(destination), "rb") as rendered:
        return {
            "schema": "turbo.music-foundry.voice-render-result.v1",
            "engine": "piper-cli",
            "execution": "local",
            "mode": "spoken",
            "path": str(destination),
            "sample_rate": rendered.getframerate(),
            "bit_depth": rendered.getsampwidth() * 8,
            "channels": rendered.getnchannels(),
            "frames": rendered.getnframes(),
            "dispatch_authorized": True,
        }
