# Music Foundry Sound-System Inventory

Audit date: 2026-11-04

Scope: existing music/audio/media-related systems in Turbo Foundry, The Portal, Command Center, Sovereign-Core, Sovereign-Offline, Sovereign-Online, and Virtual Human Engine. This is an integration inventory, not a proposal to create a parallel engine.

## Executive finding

The ecosystem already contains useful sound-generation and DSP pieces, but they serve different purposes. Music Foundry remains the canonical song project, arrangement, stem, vocal-timeline, and mix-assembly path. The strongest reusable DSP implementation found is currently inside the spoken-take assembler. Command Center's Sovereign Studio has a separate browser-local procedural note preview. Portal has spatial game tones, receiver noise/oscillator audio, and the Music Foundry stem player. These should be connected by explicit contracts rather than combined into a second DAW.

No production-grade sampler, soundfont/instrument-bank host, or mastering chain was identified in the audited repository paths. This is a bounded audit, not a claim that no such code exists anywhere in every repository or branch.

## Inventory

### Turbo Foundry — canonical Music Foundry
Branch: `music/somebodys-gotta-do-it`

- `music-foundry/generate.py`, `arrange_project.py`: composition/arrangement and MIDI-oriented project generation.
- `music-foundry/render_instrumental.py`: dependency-free additive preview renderer; creates original stems and a mono mix. Its note voices are simple procedural waveforms, not a sample library or full instrument engine.
- `music-foundry/warehouse_rave_v2.py`: separate 132 BPM procedural arrangement with drum, bass, synth, and FX stems. It has more varied oscillator/noise voices than the original preview but remains a standard-library procedural renderer.
- `music-foundry/assemble_spoken_takes.py`: existing PCM processing and vocal assembly. Includes gain, drive, low-pass filtering, delay with feedback/wet controls, stutter, phrase performance editing, take offsets, and equal-power pan into stereo output. Automation supports gain, low-pass, delay wet, and delay feedback.
- Existing browser/Python vocal effect parity and vocal automation are part of the established workflow. These controls are currently documented and applied to vocal takes, not exposed as a general instrument-bus effects rack.
- Five-lane vocal timeline, recording booth, spoken-take assembly, singing-render import contract, and SoulX adapter boundary remain part of the canonical project. SoulX model inference is not established until weights and a reviewed score are present.

### The Portal — presentation and experience layer
Branch: `main`

- `music-foundry/preview-player.html`: same-origin player for canonical mix/stem assets; synchronized tracks, per-track gain, mute/solo, master level, and shared transport. It is a playback/mix-control surface, not a sound generator or effects processor.
- `games/runtime/spatial-audio.js`: reusable Web Audio helper for short oscillator tones with HRTF panning, distance model, listener position, and master gain. Useful for positional game cues; not a music instrument or song renderer.
- `radio/index.html`: generates white-noise receiver audio plus a simple oscillator whose frequency/level changes with tuning. This is a designed ambience/interaction effect, not a music engine.
- `sound.js`: Portal ambience/interface sound layer; keep its room-tone responsibility separate from song production.
- `undertone/`: narrative/artifact phenomena; no audio DSP or sound-generation engine found in its inspected files.

### Command Center — Sovereign Studio
Branch: `main`

- `sovereign/studio.mjs` creates a deterministic 16-note pitch sequence and plays it locally with Web Audio oscillators and gain envelopes.
- It labels the output as a procedural preview and explicitly says no model inference is involved.
- This is a useful procedural note-generation/preview concept and possible source of sequencing ideas, but it is not a complete instrument engine, arrangement pipeline, or audio export workflow.
- `sovereign/studio-intent.mjs` is a bounded local command parser, not a generative music model.

### Sovereign-Core / Sovereign-Offline / Sovereign-Online
Branches: `main`

- Repository tree audit found no dedicated audio, music, synthesis, sampler, or DSP subsystem in these three repositories.
- Sovereign-Core's `earthchain/ecosphere/media.mjs` validates media metadata and checks SHA-256 integrity for audio/video and other media. It explicitly reports external storage required and streaming not implemented; it is media provenance/manifest logic, not playback or rendering.
- Genesis model/inference work is not an audio engine and should not be treated as one.

### Virtual Human Engine
Branch: `main`

- Eidolon synthesis modules are image/identity research, not audio synthesis.
- Eidolon renderer applies visual facial controls to video and explicitly does not synthesize speech.
- Media jobs/factory coordinate provider-neutral media production; they are not a local music renderer or DSP chain.
- VHE can remain the performer/visual-media side of a future music release, subject to its existing approval and identity contracts.

## Integration map — reuse, do not duplicate

1. Keep Turbo Foundry's song project, tempo, arrangement, vocal timeline, stem naming, and provenance as the source of truth.
2. Extract or generalize the existing PCM DSP primitives from `assemble_spoken_takes.py` into a shared, tested processing layer only when ready. Preserve current vocal output and contracts during any refactor.
3. Apply that shared processing path to instrument stems/buses as an optional, non-destructive stage: filtering, drive/saturation, delay, stutter, gain automation, and stereo placement. Do not silently alter source stems.
4. Keep Portal's player as the iPhone listening/mixer surface. It should consume the canonical processed mix/stems from Turbo Foundry; it should not become a second renderer.
5. Treat Command Center's procedural note preview as a sequencing/prototyping reference. Integrate only through a deliberate MIDI/score contract if it provides value; do not fork its oscillator player into another engine.
6. Use Portal spatial audio only for game/world positional cues, and keep Portal Radio/ambience separate from the song mix.
7. Keep VHE/Eidolon responsible for approved performer visuals and media composition, not music synthesis.

## Implemented since the audit

A non-destructive instrument-stem processing pass now reuses the existing vocal assembler DSP in `music-foundry/process_instrument_stems.py`. It accepts the existing render manifest plus per-stem effect/automation settings, writes separate stereo processed stems and a mix, records SHA-256 source checksums, and never changes dry source files. The existing DSP's stutter timing now accepts the project's BPM rather than assuming 127 BPM.

- Example preset: `music-foundry/warehouse_rave_v2_texture_a.example.json`.
- CLI usage and boundaries: documented in `music-foundry/README.md`.
- Tests: source immutability, stereo PCM format, safe paths, and tempo-aware stutter.
- Verification: Music Foundry test workflow passed after these changes; the full Foundry CI also passed.
- Texture A assets were rendered and uploaded as a separate prerelease tag, `warehouse-rave-texture-a`, preserving the original and Warehouse Rave V2 assets.

The Portal player now has separate Texture A mix and stem modes. Its mirror workflow copies the five processed WAV assets into the same-origin Pages audio tree. The first mirror attempt hit a concurrent-push race; the workflow was made rebase-safe and a subsequent mirror run succeeded. Pages deployment and final public-asset verification are being checked separately.

## Next engineering step

Listen to Texture A against the dry V2 mix on the Portal player, then tune the per-stem preset from actual feedback. Keep the arrangement and dry stems unchanged during this sound-design pass; do not add a new sampler, DAW, or standalone audio service.

## Verification boundaries

- Repository code inspection establishes implementation presence, not perceived sound quality.
- The Portal player has been confirmed by the user to play the refreshed V2 mix on iPhone. Individual stem controls/sliders still need real-device confirmation.
- No claim is made here that SoulX singing inference, a production sampler, professional mastering, or a production-quality synthesizer is operational.
