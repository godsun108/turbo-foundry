# Music Foundry — phase 1

An original, dependency-free MIDI sketch generator for the Turbo ecosystem. **This is not yet a stem separator, audio-to-MIDI transcriber, DAW, or automated storefront.**

## Run

```bash
python3 music-foundry/generate.py --output music-foundry/output --bpm 122 --bars 8
python3 -m unittest discover -s music-foundry/tests -v
```

Produces four editable Standard MIDI Files: chords, bass, lead, drums, plus a JSON manifest. Import the MIDI files into Ableton Live or Logic Pro, assign instruments, and edit notes. Drums use MIDI channel 10 / General MIDI percussion notes. These files contain **no audio**.

## Roadmap

1. Validate MIDI files and add genre, key, seed, and arrangement controls.
2. Add sound synthesis and WAV rendering with explicit sound-asset licenses.
3. Add opt-in audio upload, Demucs-class stem separation, and isolated stem previews.
4. Add audio-to-MIDI transcription per stem with confidence display and human correction.
5. Export per-stem WAV + MIDI + project manifest in a ZIP; later add DAW-specific templates.
6. Develop a mobile-friendly browser piano roll, timeline, and mixer.
7. Add provenance, consent, rights review, and a catalog publishing gate.

Audio separation does not guarantee perfect isolated instruments. Polyphonic transcription requires review. Upload only material you have permission to process; do not distribute separated copyrighted recordings without appropriate rights. Human creative authorship and licensed sound sources matter for commercial products.


## Track project: Somebody's Gotta Do It

A separate, track-specific arranger preserves the original generic sketch generator:

```bash
python3 music-foundry/arrange_project.py --output music-foundry/output/somebodys-gotta-do-it --bpm 127
python3 -m unittest discover -s music-foundry/tests -v
```

It creates four editable MIDI files (chords, bass, lead, drums) and a section map for a 56-bar spoken-led wonky bass-house arrangement. Tempo is provisional. The MIDI is an instrumental sketch: it does not synthesize spoken or sung vocals and does not render WAV audio.


## Vocal rendering contract

`vocal_render_contract.py` defines a provider-neutral request/renderer contract for **both spoken and sung** vocals. It validates WAV format, sample rate, bit depth, channel count, named vocal layers, renderer mode support, and credential-field boundaries.

Example request construction (validation only; no renderer is dispatched):

```python
import importlib.util
from pathlib import Path

path = Path("music-foundry/vocal_render_contract.py")
spec = importlib.util.spec_from_file_location("vocal_render_contract", path)
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)

request = contract.make_render_request(
    project_id="somebodys-gotta-do-it",
    source_ref="projects/somebodys-gotta-do-it/cue-sheet.md",
    mode="spoken",
    layers=["dry_lead", "gang_responses", "adlibs_and_chops"],
)
result = contract.validate_render_request(request)
if not result.ok:
    raise ValueError(result.errors)
```

This is deliberately **not an audio engine**. No provider is configured, no credentials are accepted in browser-facing descriptors, and request dispatch remains unauthorized until a local renderer is implemented and explicitly enabled. The shared contract keeps future sung output compatible with the same workflow without implying that singing or WAV rendering exists today.

Run the contract tests with:

```bash
python3 -m unittest discover -s music-foundry/tests -v
```


## Offline instrumental WAV preview

The track-specific renderer uses only the Python standard library to create a synthesized instrumental preview and four mono WAV stems (chords, bass, lead, drums):

```bash
python3 music-foundry/render_instrumental.py --output music-foundry/output/somebodys-gotta-do-it-audio --bpm 127
python3 -m unittest discover -s music-foundry/tests -v
```

Default output is 22,050 Hz / 16-bit PCM. The renderer is deterministic and offline; it makes no provider calls and requires no credentials. It creates `instrumental_mix.wav`, individual instrument stems, and `audio_manifest.json`. CI generates this preview as part of the existing Music Foundry artifact.

**Important:** this is a basic procedural instrumental sound preview, not a polished commercial mix. It does not render spoken or sung vocals; those remain separate future renderer work.

## Spoken-vocal timing plan

The `projects/somebodys-gotta-do-it/vocal_timing.json` file maps the existing 56-bar arrangement to section-level spoken-vocal recording landmarks. `vocal-take-plan.md` documents the dry lead, gang, ad-lib, chop, and whisper passes. These are editable recording landmarks, not locked syllable timing and not a vocal renderer. The cue sheet remains the lyric source of truth.

The arranger also writes the MIDI tempo meta-event as binary MIDI bytes; the arrangement test checks for that event so a tempo-bearing MIDI track is not mistaken for a valid file merely because it starts with an `MThd` header.

## Recorded spoken-take assembly

`assemble_spoken_takes.py` places original recorded speech WAVs onto the project timeline and exports stereo vocal stems plus a spoken-vocal mix. It is an offline assembler, **not** a speech synthesizer or singing renderer. It does not alter source takes.

Start from `music-foundry/projects/somebodys-gotta-do-it/spoken-takes.example.json` and place your own recorded WAV files under that project folder. The example uses relative paths such as `takes/lead-intro.wav`; edit the offsets and layer assignments to match your takes. The project duration is approximately 105.827 seconds at 127 BPM.

Create a `spoken-takes.json` file beside your recorded WAV files:

```json
{
  "schema": "turbo.music-foundry.spoken-takes.v1",
  "duration_seconds": 105.827,
  "takes": [
    {
      "file": "takes/lead-intro.wav",
      "layer": "dry_lead",
      "offset_ms": 0,
      "gain_db": 0,
      "pan": 0
    },
    {
      "file": "takes/gang-hook.wav",
      "layer": "gang_vocals",
      "offset_ms": 30236,
      "gain_db": -2,
      "pan": 0
    },
    {
      "file": "takes/adlib-eventually.wav",
      "layer": "adlibs",
      "offset_ms": 11200,
      "gain_db": -1,
      "pan": -0.2
    }
  ]
}
```

Paths are relative to the manifest and must remain inside its project folder. Inputs are uncompressed 16-bit PCM WAV, mono or stereo, 8–96 kHz. Stereo sources are folded to mono before placement; pan is then applied in the output. The output defaults to 48 kHz, 16-bit stereo WAV. Offsets are manual editorial placement values in milliseconds; this version does not perform automatic lyric alignment, time stretching, pitch correction, or effects processing.

Run:

```bash
python3 music-foundry/assemble_spoken_takes.py --manifest path/to/spoken-takes.json --output music-foundry/output/spoken-vocals
```

The output contains one WAV per populated layer, `spoken_vocal_mix.wav`, and `spoken_audio_manifest.json`. The manifest records source references and confirms that source takes were not modified. Only use recordings you own or have permission to process. Keep original recordings backed up; the assembler reads but does not overwrite them.

## iPhone-friendly local recording booth

Open `projects/somebodys-gotta-do-it/recording-booth.html` from a secure HTTPS origin in current Safari. The page requests microphone permission only after Record is tapped. It captures one take at a time, lets you choose a vocal layer and manual timeline offset, optionally previews a local instrumental file, converts the recorded audio to mono 48 kHz / 16-bit PCM WAV in the browser, and lets you download each take plus a JSON manifest.

This is a local browser prototype: recordings remain in page memory and are cleared when the page is closed or refreshed. Download each WAV before leaving. No audio is uploaded, no server endpoint is configured, and no provider is called. Microphone access generally requires HTTPS (or localhost); opening the HTML as an ordinary local file may not grant microphone access. Browser/device support for MediaRecorder and audio decoding varies, so verify a short test take before recording the full song.


The recording booth enforces a 180-second per-take limit and a 128-take session limit, uses unique downloaded WAV filenames, and calculates the take-manifest duration from the recorded offsets and durations. These are browser-side guardrails; test microphone permissions and actual WAV decoding on the target iPhone before a full session.
