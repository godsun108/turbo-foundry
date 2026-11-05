#!/usr/bin/env python3
"""Safe, explicit local adapter for SoulX-Singer score-conditioned inference.

This module performs preflight validation and prints a command by default.
It never downloads weights, contacts a hosted service, or executes inference
unless --execute is explicitly supplied.
"""
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


def _load_metadata(path: Path, label: str) -> list[dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} metadata cannot be read: {exc}") from exc
    if not isinstance(data, list) or not data:
        raise ValueError(f"{label} metadata must be a non-empty JSON array")
    for index, item in enumerate(data):
        prefix = f"{label}[{index}]"
        if not isinstance(item, dict):
            raise ValueError(f"{prefix} must be an object")
        for key in ("index", "language", "time", "duration", "text", "phoneme", "note_pitch", "note_type"):
            if key not in item:
                raise ValueError(f"{prefix} is missing {key}")
        timing = item["time"]
        if (
            not isinstance(timing, list) or len(timing) != 2
            or any(not isinstance(v, int) or isinstance(v, bool) for v in timing)
            or timing[0] < 0 or timing[1] <= timing[0]
        ):
            raise ValueError(f"{prefix}.time must be [start_ms, end_ms] with positive duration")
        token_counts = {
            "text": len(str(item["text"]).split()),
            "phoneme": len(str(item["phoneme"]).split()),
            "duration": len(str(item["duration"]).split()),
            "note_pitch": len(str(item["note_pitch"]).split()),
            "note_type": len(str(item["note_type"]).split()),
        }
        if len(set(token_counts.values())) != 1:
            raise ValueError(f"{prefix} token counts do not align: {token_counts}")
        try:
            durations = [float(value) for value in str(item["duration"]).split()]
            pitches = [int(value) for value in str(item["note_pitch"]).split()]
            note_types = [int(value) for value in str(item["note_type"]).split()]
        except ValueError as exc:
            raise ValueError(f"{prefix} contains invalid numeric score values") from exc
        if any(value <= 0 for value in durations):
            raise ValueError(f"{prefix} durations must be positive")
        if any(value < 0 or value > 127 for value in pitches):
            raise ValueError(f"{prefix} MIDI pitches must be in range 0..127")
        if any(value not in (1, 2, 3) for value in note_types):
            raise ValueError(f"{prefix} note types must be 1, 2, or 3")
    return data


def preflight(
    *, soulx_root: Path, model: Path, config: Path, prompt_wav: Path,
    prompt_metadata: Path, target_metadata: Path, phoneset: Path,
) -> None:
    required = {
        "SoulX-Singer inference module": soulx_root / "cli" / "inference.py",
        "model checkpoint": model,
        "model config": config,
        "prompt WAV": prompt_wav,
        "prompt metadata": prompt_metadata,
        "target score metadata": target_metadata,
        "phoneme set": phoneset,
    }
    missing = [f"{label}: {path}" for label, path in required.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError("SoulX-Singer preflight failed; missing files:\n- " + "\n- ".join(missing))
    _load_metadata(prompt_metadata, "prompt")
    _load_metadata(target_metadata, "target")


def build_command(
    *, python: str, device: str, model: Path, config: Path, prompt_wav: Path,
    prompt_metadata: Path, target_metadata: Path, phoneset: Path,
    save_dir: Path, control: str = "score", fp16: bool = False,
) -> list[str]:
    if control not in {"score", "melody"}:
        raise ValueError("control must be score or melody")
    command = [
        python, "-m", "cli.inference",
        "--device", device,
        "--model_path", str(model),
        "--config", str(config),
        "--prompt_wav_path", str(prompt_wav),
        "--prompt_metadata_path", str(prompt_metadata),
        "--target_metadata_path", str(target_metadata),
        "--phoneset_path", str(phoneset),
        "--save_dir", str(save_dir),
        "--control", control,
        "--auto_shift",
    ]
    if fp16:
        if not device.startswith("cuda"):
            raise ValueError("--fp16 is only enabled for CUDA devices")
        command.append("--fp16")
    return command


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--soulx-root", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--prompt-wav", type=Path, required=True)
    parser.add_argument("--prompt-metadata", type=Path, required=True)
    parser.add_argument("--target-metadata", type=Path, required=True)
    parser.add_argument("--phoneset", type=Path, required=True)
    parser.add_argument("--save-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--control", choices=("score", "melody"), default="score")
    parser.add_argument("--fp16", action="store_true")
    parser.add_argument("--execute", action="store_true", help="Actually run local inference; otherwise print a dry-run command.")
    args = parser.parse_args()

    try:
        preflight(
            soulx_root=args.soulx_root, model=args.model, config=args.config,
            prompt_wav=args.prompt_wav, prompt_metadata=args.prompt_metadata,
            target_metadata=args.target_metadata, phoneset=args.phoneset,
        )
        command = build_command(
            python=sys.executable, device=args.device, model=args.model,
            config=args.config, prompt_wav=args.prompt_wav,
            prompt_metadata=args.prompt_metadata, target_metadata=args.target_metadata,
            phoneset=args.phoneset, save_dir=args.save_dir,
            control=args.control, fp16=args.fp16,
        )
    except (ValueError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(("EXECUTING: " if args.execute else "DRY RUN (not executed): ") + shlex.join(command))
    if not args.execute:
        return 0
    args.save_dir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(command, cwd=args.soulx_root, check=False)
    if result.returncode != 0:
        print(f"ERROR: SoulX-Singer exited with status {result.returncode}", file=sys.stderr)
        return result.returncode
    output = args.save_dir / "generated.wav"
    if not output.is_file() or output.stat().st_size == 0:
        print("ERROR: inference returned success but generated.wav is missing or empty", file=sys.stderr)
        return 3
    print(f"Verified generated audio file: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
