# Genesis Kokoro score-conditioned singing

Status: implementation prototype. This connects the existing local Kokoro / MediaPipe TTS voice to Music Foundry's note-level vocal score. It does not introduce another hosted voice provider or ask the user to record vocals.

## What it does

1. Load the existing .litertlm voice bundle into Genesis Voice Studio on the iPhone/browser.
2. Select a Music Foundry vocal-score JSON with a tempo and placed syllables (text, MIDI pitch, onset beats, and duration beats).
3. The existing neural TTS model synthesizes each syllable using the selected voice.
4. Local JavaScript DSP analyzes voiced periods and applies pitch-synchronous overlap-add (PSOLA) to retune the vowel region to the score's MIDI pitch. Consonant onset/coda are kept outside the pitch-synchronous region as much as possible.
5. Each note is placed on the score timeline; overlapping events are mixed, peak-limited, and exported as 24 kHz mono 16-bit PCM WAV.
6. The WAV can be auditioned and imported into the existing Music Foundry vocal timeline.

No user voice, reference singer, reference WAV, cloud inference, or network rendering is needed. The TTS model is loaded from a local file selected by the operator. The existing MediaPipe runtime/WASM is still fetched from a pinned CDN in this prototype, so fully network-independent startup requires vendoring those runtime assets. Inference itself runs in the local browser worker.

## Internal runner

Run on the project's Linux internal execution host from the repository root:

```bash
bash music-foundry/run-singing-internal.sh
```

It requires Node.js 22+, bubblewrap, and GNU timeout. It executes the pure DSP/score tests in a network-isolated sandbox. It does not use GitHub Actions or macOS. Tests use generated harmonic signals and mocked local TTS output; they validate the DSP and score contract, not perceived singing quality or iPhone performance.

## Score requirements

- tempo_bpm between 40 and 240.
- Each phrase containing syllables must have a numeric start_beat.
- Every sung syllable must have text, midi_pitch, onset_beats, and duration_beats.
- Unplaced scaffold scores are rejected; melody and timing are never invented.
- Maximum 512 syllables and 180 seconds per render.

## Important limits

- This is melodic TTS, not a separately trained singing-only neural model. It reuses the current neural speech voice and uses PSOLA to impose melody while preserving much of the voice's formant character.
- One syllable is synthesized at a time, so natural coarticulation between words may need a later phrase-level alignment model.
- Very short/unvoiced syllables may be rejected if there is no stable vowel pitch to track.
- Harmony layers can overlap and are mixed, but each note currently uses the same selected voice identity.
- The existing Studio runtime uses a pinned MediaPipe CDN import; vendor the exact package/WASM assets before claiming completely offline startup.
- The real .litertlm file, iPhone memory/thermal behavior, and listening quality must be verified on the target device. A passing DSP test is not evidence of a finished commercial vocal.

## Existing project integration

The canonical project, cue sheet, MIDI/score, vocal timeline, effects, and mix remain in Music Foundry. This engine is a new renderer lane in the existing Genesis Voice Studio, not a parallel DAW.
