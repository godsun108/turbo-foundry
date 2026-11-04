# Singing Synthesis Engine Evaluation

Status: research checkpoint only. No model weights downloaded, no new dependencies installed, and no external service or deployment authorized.

## Recommendation

Use a two-lane architecture:

1. **Spoken lead now:** continue with the browser-local MediaPipe/Kokoro path. It is an actual TTS model family, not a singing renderer.
2. **Sung notes and hooks:** evaluate OpenUtau + the OpenVPI-maintained DiffSinger implementation as the first open-source singing-synthesis candidate. Treat it as a desktop/offline render worker that exports WAV into Music Foundry, not as an iPhone-native runtime.

## Candidate evidence

### OpenUtau
- MIT-licensed open-source singing editor.
- Score/MIDI editing, lyric phonemizers, vibrato/expression editing, pre-rendering, and pluggable resamplers.
- Runs on Windows, macOS, and Linux; no iOS/iPhone runtime is documented.
- Supports ENUNU AI singers and can act as an editing/hosting layer for supported AI singer workflows.
- Not a DAW replacement; rendered vocals should return to Music Foundry for arrangement and mixing.

Source: https://github.com/openutau/OpenUtau

### DiffSinger / OpenVPI DiffSinger
- Purpose-built singing voice synthesis conditioned on lyrics plus pitch/F0 or MIDI.
- The OpenVPI-maintained fork describes expressive controls including pitch, energy, and breathiness, improved 44.1 kHz output, and deployment compatibility through OpenUtau.
- Apache-2.0 code license is stated by the OpenVPI fork. Every pretrained checkpoint, voice bank, and dataset still needs its own license and consent review.
- Python/PyTorch/CUDA-oriented setup makes it a desktop/GPU candidate, not a lightweight iPhone/browser candidate.

Sources:
- https://github.com/openvpi/DiffSinger
- https://github.com/MoonInTheRiver/DiffSinger

## Integration design

- Music Foundry remains canonical for cue sheet, MIDI, lyric timing, takes, stems, and final mix.
- A singing adapter should accept a validated score package: lyric syllables, note pitches, note durations, tempo map, voice/model identifier, and explicit authorization.
- Render to WAV offline, validate sample rate/channels/bit depth, then import as a non-destructive take into the vocal timeline.
- Keep spoken and sung render contracts separate.
- No voice cloning or training on a person's voice without explicit consent and documented rights.
- Do not bundle model weights in Git or automatically download them.

## Next proof gates

1. Inspect OpenVPI DiffSinger model/checkpoint availability and per-asset licenses.
2. Determine whether an existing supported voice can sing original English lyrics acceptably.
3. Build a local adapter only after the model and voice asset pass license, reproducibility, and hardware checks.
4. Generate a short original test phrase from MIDI + lyrics; inspect timing, consonants, pitch stability, and WAV quality.
5. Import the take into the existing vocal timeline and verify alignment.

## iPhone-first decision

Do not force a heavy diffusion singing model into iPhone Safari. Keep the iPhone as the lyric/score editor, controller, and review surface; let a user-owned local desktop/GPU renderer produce the WAV until a genuinely supported mobile singing runtime is proven.
