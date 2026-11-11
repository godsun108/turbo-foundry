"""End-to-end local Genesis Singer score-to-WAV command."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--score", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--griffin-lim-iterations", type=int, default=48)
    args = parser.parse_args()

    checkpoint = args.checkpoint.expanduser().resolve()
    score = args.score.expanduser().resolve()
    output = args.output.expanduser().resolve()
    for label, path in (("checkpoint", checkpoint), ("score", score)):
        if not path.is_file():
            parser.error(f"{label} file does not exist: {path}")
    if output.exists():
        parser.error(f"refusing to overwrite existing output: {output}")
    if args.griffin_lim_iterations < 1:
        parser.error("--griffin-lim-iterations must be positive")

    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable, "-m", "genesis_singer.infer",
        "--checkpoint", str(checkpoint),
        "--score", str(score),
        "--output", str(output),
        "--device", args.device,
        "--griffin-lim-iterations", str(args.griffin_lim_iterations),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        return result.returncode
    if not output.is_file():
        print("inference returned success but did not create the requested WAV", file=sys.stderr)
        return 2

    report = {
        "schema": "genesis-singer.pipeline.v1",
        "status": "rendered_experimental",
        "engine": "GenesisSinger",
        "checkpoint": str(checkpoint),
        "checkpoint_sha256": digest(checkpoint),
        "score": str(score),
        "score_sha256": digest(score),
        "output": str(output),
        "output_sha256": digest(output),
        "renderer": "Griffin-Lim baseline; not production neural vocoder",
        "stdout": result.stdout,
    }
    report_path = output.with_suffix(output.suffix + ".manifest.json")
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
