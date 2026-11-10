#!/usr/bin/env python3
"""Local soundfont rendering and measured full-song mix/master for Music Foundry.

Requires operator-installed FluidSynth, FFmpeg (with libmp3lame), and a licensed
SoundFont supplied by the operator. No network access or model downloads occur.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import wave
from pathlib import Path


def _run(command: list[str], *, capture: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(command, check=False, text=True,
                            stdout=subprocess.PIPE if capture else None,
                            stderr=subprocess.PIPE if capture else None)
    if result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}\n{result.stderr or ''}")
    return result


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def render_midi_stems(midi_dir: Path, soundfont: Path, output_dir: Path,
                      sample_rate: int = 48000) -> dict:
    fluidsynth, ffmpeg = shutil.which("fluidsynth"), shutil.which("ffmpeg")
    if not fluidsynth or not ffmpeg:
        raise RuntimeError("Local audio rendering requires installed fluidsynth and ffmpeg executables.")
    midi_dir, soundfont, output_dir = midi_dir.resolve(), soundfont.resolve(), output_dir.resolve()
    if not soundfont.is_file():
        raise FileNotFoundError(f"licensed SoundFont not found: {soundfont}")
    if output_dir.exists():
        raise FileExistsError(f"output folder already exists: {output_dir}")
    midi_files = [midi_dir / f"{name}.mid" for name in ("chords", "bass", "lead", "drums")]
    missing = [str(path) for path in midi_files if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing MIDI tracks: " + ", ".join(missing))
    output_dir.mkdir(parents=True)
    stems = []
    for midi in midi_files:
        wav = output_dir / f"{midi.stem}.wav"
        _run([fluidsynth, "-ni", "-F", str(wav), "-r", str(sample_rate),
              str(soundfont), str(midi)])
        with wave.open(str(wav), "rb") as audio:
            if audio.getnframes() <= 0 or audio.getframerate() != sample_rate:
                raise ValueError(f"invalid FluidSynth stem: {wav}")
        stems.append(wav)
    mix = output_dir / "instrumental_mix.wav"
    inputs = []
    for stem in stems:
        inputs.extend(["-i", str(stem)])
    labels = "".join(f"[{i}:a]" for i in range(len(stems)))
    filter_graph = f"{labels}amix=inputs={len(stems)}:duration=longest:normalize=0,alimiter=limit=0.90[out]"
    _run([ffmpeg, "-y", *inputs, "-filter_complex", filter_graph,
          "-map", "[out]", "-ar", str(sample_rate), "-ac", "2",
          "-c:a", "pcm_s24le", str(mix)])
    manifest = {
        "schema": "turbo.music-foundry.instrumental-audio.v1",
        "renderer": "FluidSynth",
        "soundfont": soundfont.name,
        "soundfont_sha256": _sha(soundfont),
        "sample_rate": sample_rate,
        "bit_depth": 24,
        "channels": 2,
        "stems": [p.name for p in stems],
        "mix": mix.name,
        "source_midi": [p.name for p in midi_files],
    }
    (output_dir / "instrumental_audio_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def mix_master(instrumental: Path, vocal: Path, output_dir: Path,
               target_lufs: float = -10.0, true_peak_db: float = -1.0) -> dict:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("Mastering requires installed ffmpeg with the loudnorm filter and libmp3lame.")
    instrumental, vocal, output_dir = instrumental.resolve(), vocal.resolve(), output_dir.resolve()
    for path in (instrumental, vocal):
        if not path.is_file():
            raise FileNotFoundError(path)
    if output_dir.exists():
        raise FileExistsError(f"output folder already exists: {output_dir}")
    output_dir.mkdir(parents=True)
    filter_expr = (f"[0:a]aresample=48000, aformat=channel_layouts=stereo[i];"
                   f"[1:a]aresample=48000, aformat=channel_layouts=stereo[v];"
                   f"[i][v]amix=inputs=2:duration=longest:normalize=0,"
                   f"loudnorm=I={target_lufs}:TP={true_peak_db}:LRA=7:print_format=json[out]")
    analysis = _run([ffmpeg, "-i", str(instrumental), "-i", str(vocal),
                     "-filter_complex", filter_expr, "-map", "[out]", "-f", "null", "-"])
    matches = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", analysis.stderr or "", re.S)
    if not matches:
        raise RuntimeError("FFmpeg loudnorm analysis did not return measured loudness metadata.")
    measured = json.loads(matches[-1])
    required = ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset")
    if any(key not in measured for key in required):
        raise RuntimeError("FFmpeg loudnorm analysis is missing required measurements.")
    second_filter = (f"[0:a]aresample=48000,aformat=channel_layouts=stereo[i];"
                     f"[1:a]aresample=48000,aformat=channel_layouts=stereo[v];"
                     f"[i][v]amix=inputs=2:duration=longest:normalize=0,"
                     f"loudnorm=I={target_lufs}:TP={true_peak_db}:LRA=7:"
                     f"measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:"
                     f"measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:"
                     f"offset={measured['target_offset']}:linear=true:print_format=json[out]")
    wav = output_dir / "master.wav"
    final = _run([ffmpeg, "-y", "-i", str(instrumental), "-i", str(vocal),
                  "-filter_complex", second_filter, "-map", "[out]",
                  "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", str(wav)])
    mp3 = output_dir / "master.mp3"
    _run([ffmpeg, "-y", "-i", str(wav), "-codec:a", "libmp3lame", "-b:a", "320k", str(mp3)])
    final_matches = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", final.stderr or "", re.S)
    final_measurement = json.loads(final_matches[-1]) if final_matches else measured
    manifest = {
        "schema": "turbo.music-foundry.master.v1",
        "master_wav": wav.name,
        "preview_mp3": mp3.name,
        "sample_rate": 48000,
        "bit_depth": 24,
        "channels": 2,
        "target_lufs": target_lufs,
        "target_true_peak_db": true_peak_db,
        "ffmpeg_loudnorm_measurements": final_measurement,
        "instrumental_sha256": _sha(instrumental),
        "vocal_sha256": _sha(vocal),
        "master_sha256": _sha(wav),
        "note": "Audition and approve before release; measured values are not a substitute for listening."
    }
    (output_dir / "master_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    render = sub.add_parser("render-instrumental")
    render.add_argument("--midi-dir", type=Path, required=True)
    render.add_argument("--soundfont", type=Path, required=True)
    render.add_argument("--output", type=Path, required=True)
    master = sub.add_parser("master")
    master.add_argument("--instrumental", type=Path, required=True)
    master.add_argument("--vocal", type=Path, required=True)
    master.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = (render_midi_stems(args.midi_dir, args.soundfont, args.output)
                  if args.command == "render-instrumental"
                  else mix_master(args.instrumental, args.vocal, args.output))
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        parser.exit(2, f"BLOCKED: {exc}\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
