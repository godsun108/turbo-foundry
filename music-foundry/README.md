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
