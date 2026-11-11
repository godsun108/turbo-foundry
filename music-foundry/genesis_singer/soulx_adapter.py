"""Thin, safe launcher for the official SoulX-Singer score-conditioned inference CLI.

This adapter deliberately does not vendor upstream code or download multi-GB weights.
Prepare aligned SoulX metadata with the upstream tools/MIDI editor, then point this
launcher at a local clone and local model files.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def existing_file(parser: argparse.ArgumentParser, value: str, label: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        parser.error(f"{label} does not exist or is not a file: {path}")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--soulx-root", required=True, type=Path,
                        help="Local clone of https://github.com/Soul-AILab/SoulX-Singer")
    parser.add_argument("--model", required=True, help="Path to local model.pt")
    parser.add_argument("--prompt-wav", required=True, help="Consented/licensed prompt vocal WAV")
    parser.add_argument("--prompt-metadata", required=True, help="SoulX prompt metadata JSON")
    parser.add_argument("--target-metadata", required=True, help="SoulX target metadata JSON")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--device", choices=("cuda", "cpu"), default="cpu")
    parser.add_argument("--pitch-shift", type=int, default=0)
    parser.add_argument("--fp16", action="store_true",
                        help="Use only with a compatible CUDA device")
    args = parser.parse_args()

    root = args.soulx_root.expanduser().resolve()
    required = {
        "inference module": root / "cli" / "inference.py",
        "config": root / "soulxsinger" / "config" / "soulxsinger.yaml",
        "phoneset": root / "soulxsinger" / "utils" / "phoneme" / "phone_set.json",
    }
    for label, path in required.items():
        if not path.is_file():
            parser.error(f"SoulX {label} not found: {path}; check --soulx-root")

    model = existing_file(parser, args.model, "model")
    prompt = existing_file(parser, args.prompt_wav, "prompt WAV")
    prompt_meta = existing_file(parser, args.prompt_metadata, "prompt metadata")
    target_meta = existing_file(parser, args.target_metadata, "target metadata")
    for label, path in (("prompt metadata", prompt_meta), ("target metadata", target_meta)):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            parser.error(f"invalid {label} JSON: {exc}")
        if not isinstance(data, list) or not data:
            parser.error(f"{label} must be a non-empty list of aligned segment objects")

    if args.fp16 and args.device != "cuda":
        parser.error("--fp16 requires --device cuda")

    output = args.output_dir.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable, "-m", "cli.inference",
        "--device", args.device,
        "--model_path", str(model),
        "--config", str(required["config"]),
        "--prompt_wav_path", str(prompt),
        "--prompt_metadata_path", str(prompt_meta),
        "--target_metadata_path", str(target_meta),
        "--phoneset_path", str(required["phoneset"]),
        "--save_dir", str(output),
        "--auto_shift",
        "--pitch_shift", str(args.pitch_shift),
    ]
    if args.fp16:
        command.append("--fp16")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(root) + os.pathsep + env.get("PYTHONPATH", "")
    completed = subprocess.run(command, cwd=root, env=env, check=False)
    report = {
        "schema": "genesis-singer.soulx-adapter.v1",
        "status": "completed" if completed.returncode == 0 else "failed",
        "engine": "SoulX-Singer",
        "upstream": "https://github.com/Soul-AILab/SoulX-Singer",
        "device": args.device,
        "output_dir": str(output),
        "return_code": completed.returncode,
        "note": "Upstream output filenames and audio quality are determined by SoulX-Singer.",
    }
    (output / "genesis-soulx-run.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
