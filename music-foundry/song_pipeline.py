#!/usr/bin/env python3
"""One-command Music Foundry orchestrator.

Coordinates existing project, MIDI, score, and local SoulX components. It never
downloads models, contacts hosted APIs, or silently substitutes spoken audio
for singing. A report distinguishes ready, blocked, and completed stages.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def inspect_project(project_dir: Path, soulx_root: Path | None = None) -> dict[str, Any]:
    project_dir = project_dir.expanduser().resolve()
    config_path = project_dir / "project.json"
    if not config_path.is_file():
        raise FileNotFoundError(f"project.json not found in {project_dir}")
    config = _read_json(config_path)
    required_text = ("lyrics", "production_brief", "generation_prompt")
    missing = [key for key in required_text if not isinstance(config.get(key), str)
               or not (project_dir / config[key]).is_file()]
    if missing:
        raise ValueError("project is missing required creative source files: " + ", ".join(missing))

    midi_engine = ROOT / "generate.py"
    score_path = project_dir / "vocal_score.json"
    score = _read_json(score_path) if score_path.is_file() else None
    score_ready = bool(
        score
        and score.get("score_status") == "reviewed"
        and score.get("tempo_status") == "locked"
        and isinstance(score.get("phrases"), list)
        and any(isinstance(p, dict) and p.get("delivery") in {"sung", "chant", "gang_shout"}
                and p.get("alignment_status") == "reviewed"
                and isinstance(p.get("lyric_units"), list) and p["lyric_units"]
                for p in score["phrases"])
    )

    root = soulx_root or (Path(os.environ["SOULX_ROOT"]) if os.environ.get("SOULX_ROOT") else None)
    prompt_wav = project_dir / "vocal-reference.wav"
    prompt_metadata = project_dir / "vocal-reference.metadata.json"
    soulx_files: dict[str, Path] = {}
    if root:
        soulx_files = {
            "inference": root / "cli" / "inference.py",
            "config": root / "soulxsinger" / "config" / "soulxsinger.yaml",
            "phoneset": root / "soulxsinger" / "utils" / "phoneme" / "phone_set.json",
            "checkpoint": root / "pretrained_models" / "SoulX-Singer" / "model.pt",
        }
    missing_soulx = [name for name, path in soulx_files.items() if not path.is_file()]
    prompt_ready = prompt_wav.is_file() and prompt_metadata.is_file()
    renderer_ready = (ROOT / "soulx_local_runner.py").is_file() and (ROOT / "soulx_export.py").is_file()
    singing_ready = bool(score_ready and root and not missing_soulx and prompt_ready and renderer_ready)

    return {
        "schema": "turbo.music-foundry.pipeline-preflight.v1",
        "project_id": config.get("project_id") or project_dir.name,
        "title": config.get("title", project_dir.name),
        "project_dir": str(project_dir),
        "tempo_bpm": config.get("bpm"),
        "arrangement_bars": config.get("arrangement_bars"),
        "duration_seconds": config.get("target_duration_seconds"),
        "stages": {
            "creative_source": {"status": "ready", "files": required_text},
            "midi": {"status": "ready" if midi_engine.is_file() else "blocked",
                     "engine": str(midi_engine)},
            "vocal_score": {"status": "ready" if score_ready else "blocked",
                            "file": str(score_path),
                            "reason": None if score_ready else
                            "requires human-reviewed sung lyric_units and locked tempo"},
            "soulx_runtime": {"status": "ready" if root and not missing_soulx else "blocked",
                              "root": str(root) if root else None,
                              "missing": missing_soulx if root else
                              ["SOULX_ROOT not set; point to the existing local SoulX-Singer checkout"]},
            "singing_reference": {"status": "ready" if prompt_ready else "blocked",
                                  "files": [str(prompt_wav), str(prompt_metadata)],
                                  "reason": None if prompt_ready else
                                  "requires a rights-cleared reference singing WAV and its phoneme metadata"},
            "singing_renderer": {"status": "ready" if renderer_ready else "blocked"},
            "singing_render": {"status": "ready" if singing_ready else "blocked"},
            "mix_master": {"status": "blocked",
                           "reason": "No integrated full-song mix/master stage is configured in this project branch yet."}
        },
        "ready_for_local_singing_render": singing_ready,
        "policy": {
            "no_hosted_provider": True,
            "no_model_download": True,
            "no_spoken_substitution_for_singing": True,
            "source_audio_preserved": True
        }
    }


def run(project_dir: Path, output_dir: Path, soulx_root: Path | None = None,
        execute_midi: bool = False, execute_vocals: bool = False,
        device: str = "cpu") -> dict[str, Any]:
    report = inspect_project(project_dir, soulx_root)
    project_dir = project_dir.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    config = _read_json(project_dir / "project.json")

    if execute_midi:
        engine = ROOT / "generate.py"
        if not engine.is_file():
            raise FileNotFoundError("Music Foundry MIDI generator is missing")
        command = [sys.executable, str(engine), "--output", str(output_dir / "midi"),
                   "--bpm", str(int(config["bpm"])),
                   "--bars", str(int(config["arrangement_bars"]))]
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
        report["midi_execution"] = {"command": command, "returncode": completed.returncode,
                                    "stdout": completed.stdout, "stderr": completed.stderr}
        report["stages"]["midi"]["status"] = "completed" if completed.returncode == 0 else "failed"

    if execute_vocals:
        if not report["ready_for_local_singing_render"]:
            raise RuntimeError("Singing render blocked by preflight; inspect report stages before rendering.")
        root = soulx_root or Path(os.environ["SOULX_ROOT"])
        command = [
            sys.executable, str(ROOT / "soulx_local_runner.py"),
            "--score", str(project_dir / "vocal_score.json"),
            "--engine-root", str(root),
            "--prompt-wav", str(project_dir / "vocal-reference.wav"),
            "--prompt-metadata", str(project_dir / "vocal-reference.metadata.json"),
            "--output-dir", str(output_dir / "soulx-vocals"),
            "--device", device
        ]
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
        report["singing_execution"] = {"command": command, "returncode": completed.returncode,
                                       "stdout": completed.stdout, "stderr": completed.stderr}
        report["stages"]["singing_render"]["status"] = "completed" if completed.returncode == 0 else "failed"

    report_path = output_dir / "pipeline-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    report["report_file"] = str(report_path)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True, help="Project folder containing project.json")
    parser.add_argument("--output", type=Path, required=True, help="New or existing output folder")
    parser.add_argument("--soulx-root", type=Path, help="Existing local SoulX-Singer checkout; no download is performed")
    parser.add_argument("--execute-midi", action="store_true", help="Generate editable MIDI files")
    parser.add_argument("--execute-vocals", action="store_true", help="Run local SoulX only after all singing gates pass")
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    args = parser.parse_args()
    try:
        report = run(args.project, args.output, args.soulx_root,
                     args.execute_midi, args.execute_vocals, args.device)
    except (OSError, ValueError, RuntimeError, KeyError, json.JSONDecodeError) as exc:
        print(f"PIPELINE BLOCKED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return 0 if all(stage["status"] in {"ready", "completed"} for stage in report["stages"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
