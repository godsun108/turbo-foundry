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


## Spoken vocal timeline editor

Open `projects/somebodys-gotta-do-it/vocal-timeline.html` from a secure local or HTTPS origin. Import a `turbo.music-foundry.spoken-takes.v1` JSON manifest and the matching WAV files. The browser-local editor displays five vocal lanes, supports horizontal clip dragging and precise offset/layer/gain/pan edits, previews the arrangement, exports an updated manifest, and renders a stereo 48 kHz / 16-bit mix plus populated layer stems through `OfflineAudioContext`. Downloads are separate files; keep them together with the manifest. The editor does not upload audio, persist takes, synthesize speech, or render sung vocals. iPhone/Safari decoding, offline rendering, and multiple-download behavior remain device-test requirements.

The vocal timeline now includes the track's seven arrangement sections mapped to the provisional 127 BPM grid across the full 56-bar / 105.827-second song. The editor preserves that full-song duration when arranging shorter recorded takes, so vocal stems remain aligned to the instrumental arrangement.


## Vocal effects

The spoken-take manifest supports optional per-take `effects`: `drive_db` (0–24), `lowpass_hz` (500–20000), `delay_ms` (0–500), `delay_feedback` (0–75), `delay_wet` (0–100), and `stutter` (`off`, `1/4`, `1/8`, `1/16`). The browser timeline previews and renders saturation, low-pass filtering, feedback delay and a tempo-locked repeat of the take's first beat subdivision. The offline Python assembler applies the same bounded effect settings while leaving source WAV files untouched. These are creative production effects, not mastering or a substitute for listening tests; effects default to neutral when omitted. The stutter repeats the opening slice across the take, so use it selectively for deliberate glitch/chop moments.


## Vocal automation lanes

Each spoken take can carry up to 64 take-relative automation keyframes in the shared spoken-takes manifest. Supported parameters are `gain_db` (-60 to +12 dB), `lowpass_hz` (500–20000 Hz), `delay_wet` (0–100%), and `delay_feedback` (0–75%). The browser editor adds/replaces keyframes at millisecond positions, displays and removes them, and ramps Web Audio parameters during live preview and offline WAV rendering. The Python assembler applies the same linear interpolation to gain, low-pass cutoff, delay wet and feedback, and preserves automation in its render manifest. Keyframes are bounded and source takes remain read-only. These are take-relative automation lanes; global/master automation and pitch automation are not implemented yet.

The timeline draws each take's automation keyframes directly on its clip as small markers, while the selected take's automation list remains editable below its effect controls.


## Phrase performance editing

The spoken vocal timeline supports a bounded phrase edit per take: select a start/end range, insert up to eight repeats, reverse the selected phrase, and optionally fire one extra phrase repeat at the track's first chorus drop (bar 17, 30.236 seconds). Edits are non-destructive and stored as a `performance` object in the spoken-takes manifest. Browser preview and OfflineAudioContext WAV exports render the edits; the Python offline assembler applies the same phrase repeat/reverse/drop behavior. Phrase edits are capped by the 180-second project limit.


## Mute, solo and phrase audition

The browser timeline supports per-take mute/solo and per-layer mute/solo. Layer state is stored in the manifest alongside take flags; the offline Python assembler honors the same precedence (muted tracks remain silent, and active solo flags exclude non-solo tracks). The mix renderer skips empty muted stems. A selected source phrase can be auditioned in isolation with its take effects, and clip start positions can be nudged by 10 ms or 100 ms using touch-friendly buttons. These audition and nudge controls are local to the editor; no network audio transport is used.
