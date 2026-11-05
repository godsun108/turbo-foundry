#!/usr/bin/env python3
"""Prepare an operator-authorized English singing prompt for the local SoulX-Singer worker.

This wrapper calls the official preprocessing pipeline already installed in an
existing SoulX checkout. It never downloads weights or installs dependencies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prepare_prompt(
    *,
    source_audio: Path,
    engine_root: Path,
    output_dir: Path,
    device: str = "cuda",
    python_executable: str = sys.executable,
    timeout_seconds: int = 3600,
) -> dict[str, Any]:
    source_audio = source_audio.expanduser().resolve()
    engine_root = engine_root.expanduser().resolve()
    if not source_audio.is_file():
        raise ValueError(f"Reference singing recording not found: {source_audio}")
    if source_audio.suffix.lower() not in {".wav", ".mp3", ".flac"}:
        raise ValueError("Reference recording must be WAV, MP3, or FLAC.")
    pipeline = engine_root / "preprocess" / "pipeline.py"
    if not pipeline.is_file():
        raise ValueError(f"Official SoulX preprocessing pipeline not found: {pipeline}")
    if device not in {"cuda", "cpu"}:
        raise ValueError("device must be explicitly set to cuda or cpu.")

    output_dir = output_dir.expanduser().resolve()
    if output_dir.exists() and (not output_dir.is_dir() or any(output_dir.iterdir())):
        raise ValueError("Output directory must be new or empty; existing files are never overwritten.")
    output_dir.mkdir(parents=True, exist_ok=True)

    staged_audio = output_dir / ("reference_prompt" + source_audio.suffix.lower())
    shutil.copy2(source_audio, staged_audio)
    command = [
        python_executable, "-m", "preprocess.pipeline",
        "--audio_path", str(staged_audio),
        "--save_dir", str(output_dir),
        "--language", "English",
        "--device", device,
        "--vocal_sep", "False",
        "--max_merge_duration", "30000",
        "--midi_transcribe", "True",
    ]
    completed = subprocess.run(
        command,
        cwd=str(engine_root),
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )
    log_path = output_dir / "preprocess.log"
    log_path.write_text(
        (completed.stdout or "") + ("\n--- STDERR ---\n" + completed.stderr if completed.stderr else ""),
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"SoulX prompt preprocessing exited with code {completed.returncode}; inspect {log_path}."
        )

    metadata_path = output_dir / "metadata.json"
    if not metadata_path.is_file():
        raise ValueError("SoulX preprocessing completed without producing metadata.json.")
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"SoulX produced invalid prompt metadata JSON: {exc}") from exc
    if not isinstance(metadata, list) or not metadata or not isinstance(metadata[0], dict):
        raise ValueError("SoulX prompt metadata must be a non-empty array of segment objects.")
    vocal_path = output_dir / "vocal.wav"
    if not vocal_path.is_file() or vocal_path.stat().st_size == 0:
        raise ValueError("SoulX preprocessing did not produce a non-empty vocal.wav.")

    manifest = {
        "schema": "turbo.music-foundry.singing-prompt.v1",
        "engine": "Soul-AILab/SoulX-Singer",
        "language": "English",
        "device": device,
        "source_audio_sha256": sha256_file(source_audio),
        "staged_audio": str(staged_audio),
        "staged_audio_sha256": sha256_file(staged_audio),
        "prompt_wav": str(vocal_path),
        "prompt_metadata": str(metadata_path),
        "prompt_metadata_sha256": sha256_file(metadata_path),
        "segments": len(metadata),
        "status": "prepared",
        "rights_notice": "Operator must retain permission and consent for the reference singer recording.",
    }
    (output_dir / "singing_prompt_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-audio", type=Path, required=True, help="Rights-cleared reference singing recording.")
    parser.add_argument("--engine-root", type=Path, required=True, help="Existing official SoulX-Singer checkout.")
    parser.add_argument("--output-dir", type=Path, required=True, help="New or empty output directory.")
    parser.add_argument("--device", choices=("cuda", "cpu"), default="cuda")
    parser.add_argument("--timeout", type=int, default=3600)
    args = parser.parse_args()
    try:
        result = prepare_prompt(
            source_audio=args.source_audio,
            engine_root=args.engine_root,
            output_dir=args.output_dir,
            device=args.device,
            timeout_seconds=args.timeout,
        )
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
