#!/usr/bin/env python3
"""Import a verified SoulX singing render into Music Foundry's existing vocal-take timeline.

The source render is copied unchanged. This creates the existing spoken-takes manifest
format so the current offline assembler and browser timeline can consume the take.
No model is run, no audio is modified, and no output is overwritten.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, sys, wave
from pathlib import Path
from typing import Any

LAYERS = ("dry_lead", "gang_vocals", "adlibs", "chops", "whisper_double")
RENDER_SCHEMA = "turbo.music-foundry.singing-render.v1"
TAKE_SCHEMA = "turbo.music-foundry.spoken-takes.v1"

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def _read_render(render_manifest: Path) -> tuple[dict[str, Any], Path, float]:
    try:
        manifest = json.loads(render_manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read singing render manifest: {exc}") from exc
    if not isinstance(manifest, dict) or manifest.get("schema") != RENDER_SCHEMA:
        raise ValueError("Unsupported singing render manifest schema.")
    if manifest.get("status") != "rendered":
        raise ValueError("Only a completed singing render can be imported.")
    if manifest.get("project_id") != "somebodys-gotta-do-it":
        raise ValueError("This importer currently targets Somebody's Gotta Do It only.")
    audio_value, expected_hash = manifest.get("audio_file"), manifest.get("audio_sha256")
    if not isinstance(audio_value, str) or not audio_value:
        raise ValueError("Singing render manifest is missing audio_file.")
    if not isinstance(expected_hash, str) or len(expected_hash) != 64:
        raise ValueError("Singing render manifest is missing a valid audio SHA-256.")
    audio_path = Path(audio_value)
    if not audio_path.is_absolute():
        audio_path = render_manifest.parent / audio_path
    audio_path = audio_path.resolve()
    if not audio_path.is_file():
        raise ValueError(f"Rendered audio file does not exist: {audio_path}")
    if sha256_file(audio_path) != expected_hash:
        raise ValueError("Singing render audio checksum does not match its manifest.")
    try:
        with wave.open(str(audio_path), "rb") as wav:
            channels, rate, width = wav.getnchannels(), wav.getframerate(), wav.getsampwidth()
            frames, compression = wav.getnframes(), wav.getcomptype()
    except (wave.Error, OSError) as exc:
        raise ValueError(f"Rendered audio is not a readable WAV: {exc}") from exc
    if compression != "NONE" or channels != 1 or rate != 24000 or width != 2 or frames <= 0:
        raise ValueError("Timeline import requires non-empty mono 24 kHz 16-bit PCM WAV; source render was not changed.")
    return manifest, audio_path, frames / rate

def import_render(*, render_manifest_path: Path, output_manifest_path: Path,
                  offset_ms: int, project_duration_seconds: float, layer: str = "gang_vocals",
                  gain_db: float = 0, pan: float = 0) -> dict[str, Any]:
    render_manifest_path = render_manifest_path.expanduser().resolve()
    output_manifest_path = output_manifest_path.expanduser().resolve()
    if output_manifest_path.exists():
        raise ValueError("Output manifest already exists; refusing to overwrite.")
    if not isinstance(offset_ms, int) or offset_ms < 0:
        raise ValueError("offset_ms must be a non-negative integer.")
    if not isinstance(project_duration_seconds, (int, float)) or not 0 < project_duration_seconds <= 180:
        raise ValueError("project_duration_seconds must be greater than 0 and at most 180.")
    if layer not in LAYERS:
        raise ValueError(f"layer must be one of: {', '.join(LAYERS)}.")
    if not isinstance(gain_db, (int, float)) or not -60 <= gain_db <= 12:
        raise ValueError("gain_db must be between -60 and 12.")
    if not isinstance(pan, (int, float)) or not -1 <= pan <= 1:
        raise ValueError("pan must be between -1 and 1.")
    render, source_audio, audio_duration = _read_render(render_manifest_path)
    if offset_ms / 1000 + audio_duration > project_duration_seconds:
        raise ValueError("Singing take would extend beyond the declared song duration.")
    output_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    takes_dir = output_manifest_path.parent / "takes"
    takes_dir.mkdir(exist_ok=True)
    filename = f"soulx-{render['audio_sha256'][:12]}.wav"
    copied_audio = takes_dir / filename
    if copied_audio.exists():
        raise ValueError("Destination take already exists; refusing to overwrite.")
    shutil.copy2(source_audio, copied_audio)
    if sha256_file(copied_audio) != render["audio_sha256"]:
        copied_audio.unlink(missing_ok=True)
        raise ValueError("Copied singing take failed checksum verification.")
    output = {
        "schema": TAKE_SCHEMA,
        "duration_seconds": round(float(project_duration_seconds), 3),
        "takes": [{
            "file": f"takes/{filename}", "layer": layer, "offset_ms": offset_ms,
            "gain_db": float(gain_db), "pan": float(pan),
            "source": {
                "engine": render.get("engine", "unknown"),
                "render_manifest_sha256": sha256_file(render_manifest_path),
                "audio_sha256": render["audio_sha256"],
                "score_sha256": render.get("source_score_sha256"),
                "imported_unchanged": True
            }
        }]
    }
    output_manifest_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render-manifest", type=Path, required=True)
    parser.add_argument("--output-manifest", type=Path, required=True)
    parser.add_argument("--offset-ms", type=int, required=True)
    parser.add_argument("--project-duration", type=float, required=True)
    parser.add_argument("--layer", choices=LAYERS, default="gang_vocals")
    parser.add_argument("--gain-db", type=float, default=0)
    parser.add_argument("--pan", type=float, default=0)
    args = parser.parse_args()
    try:
        import_render(render_manifest_path=args.render_manifest, output_manifest_path=args.output_manifest,
                      offset_ms=args.offset_ms, project_duration_seconds=args.project_duration,
                      layer=args.layer, gain_db=args.gain_db, pan=args.pan)
    except (OSError, ValueError) as exc:
        print(f"Singing take import blocked: {exc}", file=sys.stderr)
        return 1
    print(f"Imported one verified singing take into {args.output_manifest}; source audio unchanged.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
