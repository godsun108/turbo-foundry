# EARTH STUDIO browser adapter

This directory is the canonical Turbo Foundry home for the EARTH STUDIO browser adapter, migrated from Portal draft PR #325.

- `art-studio.html` preserves the initial browser-local multitrack workflow and now connects it to project save/open/autosave.
- `session-schema-v1.json` defines the first portable `.earthsession` manifest.
- `session-store.mjs` validates, serializes, and persists manifests plus audio Blobs in local IndexedDB. Legacy sessions remain valid; optional inline MIDI clips are stored on MIDI/instrument tracks with note timing in 960-PPQ ticks.
- `midi-sequencer.mjs` provides the browser-independent musical clock, polyphonic keyboard recorder, quantization, loop-aware event scheduling, and AudioWorklet MIDI sink. The worklet accepts absolute AudioContext timestamps and applies events at sample-frame offsets. It also exports `MusicalTransport`, a host-neutral play/pause/stop/seek/tempo/loop clock with look-ahead scheduling; browser, desktop, and standalone hosts supply their own monotonic and audio clocks.
- `midi-recording-ui.mjs` connects the performance keyboard to Record/Stop/Overdub controls, capture-time quantization, a touch-editable piano roll, note selection/deletion and velocity editing, four-cycle MIDI loop playback, optional Web MIDI hardware input, and MIDI-track persistence in `.earthsession`. MIDI-only sessions can be played without an audio clip. Hardware MIDI depends on browser Web MIDI support and an allowed secure context.
- `transport-controller.mjs` binds the interface Play/Pause/Stop/Seek/Tempo controls to one `MusicalTransport` instance. It schedules MIDI against the instrument AudioContext with a bounded look-ahead window, resets the scheduling cursor after seeks/edits, and uses the same audio clock for imported audio tracks. The controller is browser-specific; the underlying transport remains host-neutral for the future standalone runtime.
- `../tests/test_earth_studio_midi_sequencer.mjs` covers MIDI recording, note velocity/channel, quantization, loop scheduling, and timestamped native-engine messages.
- `project-package.mjs` exports/imports a dependency-free ZIP-based `.earthsession` package containing the manifest and original audio assets.
- Portable packages use uncompressed ZIP entries for broad compatibility, with CRC-32 and SHA-256 verification; unsafe paths, duplicate entries, encrypted/compressed/ZIP64 archives and unexpected files are rejected.
- `../tests/test_earth_studio_session.mjs` exercises the pure schema/serialization boundary with Node's built-in test runner.

## Project persistence

Create or name a project, import audio, and use Save Project for a manual checkpoint. Track additions, removals, mute/solo, gain, pan, offset, tempo, and project-name edits schedule a local autosave. Open Saved Project restores the manifest and audio assets. The adapter verifies each stored asset's SHA-256 digest before decoding it. Re-saving removes obsolete assets belonging to that project.

All audio remains in browser-local IndexedDB; no cloud service is used. The browser adapter currently limits each project's audio assets to 512 MiB. Browser quota, eviction, interrupted writes, and iPhone/Safari behavior still require device testing. Export important projects as WAV backups; portable `.earthsession` package export/import is available in the current draft branch. Import creates a new local project copy and verifies every audio asset before saving.

The HTML page remains a Web Audio prototype, not the native low-latency engine. The native audio backend and true iPhone offline application remain later milestones.

Run the pure unit tests from the repository root:

```sh
node --test music-foundry/tests/test_earth_studio_session.mjs music-foundry/tests/test_earth_studio_project_package.mjs music-foundry/tests/test_earth_studio_midi_sequencer.mjs
```

Source provenance: `godsun108/The-portal`, `music-foundry/studio.html`, branch `music-foundry/art-studio-foundation`, source blob `6b725fe7c27368dca297d310cfda634fb6884cc8`.
