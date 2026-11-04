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
