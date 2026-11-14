# Genesis Kokoro score-conditioned singing

Status: implementation prototype with automatic model installation. This connects the Kokoro / MediaPipe TTS voice to Music Foundry's spoken and note-level sung vocal paths. It does not introduce another hosted voice provider or ask the user to record vocals.

## Render path

1. Choose GPU or CPU in Genesis Voice Studio. The studio loads the pinned Kokoro `.litertlm` model directly from its Apache-2.0 Hugging Face release; no manual file picker is required. The first download is about 295 MB.
2. Select a Music Foundry vocal-score JSON with tempo and placed syllables (text, MIDI pitch, onset beats, and duration beats).
3. The existing neural TTS model synthesizes each syllable using the selected voice.
4. Local JavaScript DSP analyzes voiced periods and applies pitch-synchronous overlap-add (PSOLA) to retune the vowel region to the score's MIDI pitch. Consonant onset/coda are kept outside the pitch-synchronous region as much as possible.
5. Each note is placed on the score timeline; overlapping events are mixed, peak-limited, and exported as 48 kHz mono 16-bit PCM WAV.
6. The WAV can be auditioned and imported into the existing Music Foundry vocal timeline.

No user voice, reference singer, reference WAV, or cloud inference is needed. The TTS model is downloaded from the published Apache-2.0 release and inference/DSP run in the browser worker. The prototype loads the pinned MediaPipe runtime/WASM from jsDelivr on first use. A same-origin service worker caches the app shell, score fixture, DSP module, pinned runtime responses, and the exact Kokoro model URLs where browser quota permits. The first install requires network access, and iOS may evict cached assets; this is warm-cache offline-capable, not guaranteed permanent storage.

## Run tests on Sovereign's internal execution system

This is designed for the existing Sovereign-Offline controlled executor, not a macOS or GitHub-hosted runner.

1. Put the Turbo Foundry checkout inside a read-write root already authorized in Sovereign-Offline's workspace policy.
2. Ensure that policy allowlists `node` and includes the checkout in `cwdRoots`. Example:
   ```json
   {
     "command": "node",
     "cwdRoots": ["/path/to/turbo-foundry"],
     "maxArgs": 8,
     "maxTimeoutMs": 120000
   }
   ```
3. Call the existing local Sovereign Node executor:
   ```http
   POST http://127.0.0.1:7777/v1/execute
   Content-Type: application/json
   ```
   ```json
   {
     "command": "node",
     "args": ["music-foundry/run-singing-internal.mjs"],
     "cwd": "/path/to/turbo-foundry",
     "timeoutMs": 120000
   }
   ```
4. The runner performs module syntax checks and deterministic DSP/score tests. It uses Node child processes with `shell:false`, bounded output, per-check timeouts, and no network calls. Sovereign-Offline enforces the outer command allowlist, workspace boundary, process timeout, and audit record.

The response should end with schema `sovereign.music-foundry.internal-run.v1` and `ok: true` only when all checks pass. No run is claimed until that response is observed.

## Bundled real-song fixture

The studio can load the bundled Fine China chorus draft with one tap. The fixture contains 73 placed syllables at 126 BPM, from beat 128 through beat 186, with no overlapping lead events. It is still marked composition_draft and must be auditioned and approved; the fixture test proves score import and timing integrity, not vocal quality or artistic approval.

The renderer descriptor is intentionally registered with verification status pending and no verified modes. The existing provider-neutral contract therefore continues to block sung dispatch until independent evidence is recorded.

## Score requirements

- `tempo_bpm` between 40 and 240.
- Each phrase containing syllables must have a numeric `start_beat`.
- Every sung syllable must have text, `midi_pitch`, `onset_beats`, and `duration_beats`.
- Unplaced scaffold scores are rejected; melody and timing are never invented.
- Maximum 512 syllables and 180 seconds per render.

## Important limits

- This is melodic TTS, not a separately trained singing-only neural model. It reuses the current neural speech voice and uses PSOLA to impose melody while preserving much of the voice's formant character.
- One syllable is synthesized at a time, so natural coarticulation between words may need a later phrase-level alignment model.
- Very short/unvoiced syllables may be rejected if there is no stable vowel pitch to track.
- Harmony layers can overlap and are mixed, but each note currently uses the same selected voice identity.
- The real model load, target iPhone memory/thermal behavior, and listening quality must be verified on-device. A passing DSP test is not evidence of a finished commercial vocal.

## Existing project integration

The canonical song project, cue sheet, MIDI/score, vocal timeline, effects, and mix remain in Music Foundry. This engine is a new renderer lane in the existing Genesis Voice Studio, not a parallel DAW.
