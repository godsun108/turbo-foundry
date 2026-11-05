#!/usr/bin/env python3
"""Run the official SoulX-Singer score-control CLI as a local Music Foundry render worker.

This adapter never downloads models, installs dependencies, accepts credentials, or
infers lyrics/notes. It requires an explicitly reviewed Music Foundry score and an
operator-authorized reference singing prompt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import wave
from pathlib import Path
from typing import Any

from soulx_export import build_metadata


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _required_file(path: Path, label: str) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise ValueError(f"{label} does not exist or is not a file: {resolved}")
    return resolved


def _validate_prompt_metadata(path: Path) -> None:
    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read prompt metadata JSON: {exc}") from exc
    if not isinstance(data, list) or not data or not isinstance(data[0], dict):
        raise ValueError("Prompt metadata must be a non-empty JSON array of segment objects.")


def _validate_wav(path: Path) -> dict[str, int]:
    try:
        with wave.open(str(path), "rb") as audio:
            info = {
                "channels": audio.getnchannels(),
                "sample_rate": audio.getframerate(),
                "sample_width_bytes": audio.getsampwidth(),
                "frames": audio.getnframes(),
            }
    except (wave.Error, OSError) as exc:
        raise ValueError(f"Renderer output is not a readable PCM WAV: {exc}") from exc
    if info["channels"] != 1 or info["sample_rate"] != 24000:
        raise ValueError(
            "SoulX output contract mismatch: expected mono 24000 Hz WAV; "
            f"received {info['channels']} channel(s) at {info['sample_rate']} Hz."
        )
    if info["sample_width_bytes"] != 2 or info["frames"] <= 0:
        raise ValueError(
            "SoulX output must be non-empty 16-bit PCM WAV because the existing "
            "Music Foundry vocal assembler consumes 16-bit PCM without changing source takes."
        )
    return info


def run_render(
    *,
    score_path: Path,
    engine_root: Path,
    prompt_wav: Path,
    prompt_metadata: Path,
    output_dir: Path,
    model_path: Path | None = None,
    device: str = "cuda",
    timeout_seconds: int = 3600,
    python_executable: str = sys.executable,
) -> dict[str, Any]:
    score_path = _required_file(score_path, "Reviewed vocal score")
    engine_root = engine_root.expanduser().resolve()
    prompt_wav = _required_file(prompt_wav, "Authorized prompt WAV")
    prompt_metadata = _required_file(prompt_metadata, "Prompt metadata")
    inference_script = _required_file(engine_root / "cli" / "inference.py", "SoulX inference CLI")
    config = _required_file(engine_root / "soulxsinger" / "config" / "soulxsinger.yaml", "SoulX config")
    phoneset = _required_file(engine_root / "soulxsinger" / "utils" / "phoneme" / "phone_set.json", "SoulX phoneset")
    checkpoint = _required_file(
        model_path or (engine_root / "pretrained_models" / "SoulX-Singer" / "model.pt"),
        "SoulX-Singer checkpoint",
    )
    if prompt_wav.suffix.lower() != ".wav":
        raise ValueError("The reference singing prompt must be a WAV file.")
    _validate_prompt_metadata(prompt_metadata)
    if device not in {"cuda", "cpu"}:
        raise ValueError("device must be explicitly set to cuda or cpu.")

    output_dir = output_dir.expanduser().resolve()
    if output_dir.exists() and (not output_dir.is_dir() or any(output_dir.iterdir())):
        raise ValueError("Output directory must be new or empty; existing files are never overwritten.")
    output_dir.mkdir(parents=True, exist_ok=True)

    score = json.loads(score_path.read_text(encoding="utf-8"))
    target_metadata = build_metadata(score)
    target_path = output_dir / "target_metadata.json"
    target_path.write_text(json.dumps(target_metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    command = [
        python_executable, "-m", "cli.inference",
        "--device", device,
        "--model_path", str(checkpoint),
        "--config", str(config),
        "--prompt_wav_path", str(prompt_wav),
        "--prompt_metadata_path", str(prompt_metadata),
        "--target_metadata_path", str(target_path),
        "--phoneset_path", str(phoneset),
        "--save_dir", str(output_dir),
        "--auto_shift",
        "--pitch_shift", "0",
        "--control", "score",
    ]
    completed = subprocess.run(
        command,
        cwd=str(engine_root),
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )
    log_path = output_dir / "renderer.log"
    log_path.write_text(
        (completed.stdout or "") + ("\n--- STDERR ---\n" + completed.stderr if completed.stderr else ""),
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"SoulX-Singer exited with code {completed.returncode}; inspect {log_path}."
        )

    generated = output_dir / "generated.wav"
    generated = _required_file(generated, "SoulX generated WAV")
    audio_info = _validate_wav(generated)
    manifest = {
        "schema": "turbo.music-foundry.singing-render.v1",
        "project_id": score["project_id"],
        "engine": "Soul-AILab/SoulX-Singer",
        "control": "score",
        "device": device,
        "source_score": str(score_path),
        "source_score_sha256": sha256_file(score_path),
        "prompt_wav_sha256": sha256_file(prompt_wav),
        "prompt_metadata_sha256": sha256_file(prompt_metadata),
        "target_metadata": str(target_path),
        "target_segments": len(target_metadata),
        "audio_file": str(generated),
        "audio_sha256": sha256_file(generated),
        "audio": audio_info,
        "model_checkpoint": str(checkpoint),
        "model_checkpoint_sha256": sha256_file(checkpoint),
        "status": "rendered",
        "limitations": [
            "Reference prompt recording rights and consent are the operator's responsibility.",
            "The generated WAV must be auditioned and checked for lyric, timing, pitch, and artifact quality.",
            "This renderer creates a mono vocal take; Music Foundry performs subsequent arrangement and mixing.",
        ],
    }
    manifest_path = output_dir / "singing_render_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--score", type=Path, required=True)
    parser.add_argument("--engine-root", type=Path, required=True, help="Existing official SoulX-Singer checkout.")
    parser.add_argument("--prompt-wav", type=Path, required=True, help="Rights-cleared reference singing WAV.")
    parser.add_argument("--prompt-metadata", type=Path, required=True, help="Preprocessed prompt metadata JSON.")
    parser.add_argument("--output-dir", type=Path, required=True, help="New or empty output directory.")
    parser.add_argument("--model", type=Path, help="Optional explicit checkpoint path.")
    parser.add_argument("--device", choices=("cuda", "cpu"), default="cuda")
    parser.add_argument("--timeout", type=int, default=3600)
    args = parser.parse_args()
    try:
        result = run_render(
            score_path=args.score,
            engine_root=args.engine_root,
            prompt_wav=args.prompt_wav,
            prompt_metadata=args.prompt_metadata,
            output_dir=args.output_dir,
            model_path=args.model,
            device=args.device,
            timeout_seconds=args.timeout,
        )
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
