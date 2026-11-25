# EARTH STUDIO browser adapter

This directory is the canonical Turbo Foundry home for the EARTH STUDIO browser adapter, migrated from Portal draft PR #325.

- `art-studio.html` provides a browser-local multitrack arrangement with independent non-destructive audio clip instances: split at the playhead, duplicate, trim, move, and loop. Each instance references the same source asset; project save/open and portable export preserve the clip arrangement.
- `session-schema-v1.json` defines the first portable `.earthsession` manifest.
- `session-store.mjs` validates, serializes, and persists manifests plus audio Blobs in local IndexedDB. Multiple audio clips on one track reference one shared asset; each clip stores timeline start, source offset, duration, and optional loop state. Legacy single-clip sessions remain valid. Optional inline MIDI clips are stored on MIDI/instrument tracks with note timing in 960-PPQ ticks.
- `audio-clip-model.mjs` provides browser-independent validation, split, trim, duplicate, move, loop, tempo-aware snap, clip gain, and fade-envelope operations for source-backed clip instances.
- `midi-sequencer.mjs` provides the browser-independent musical clock, polyphonic keyboard recorder, quantization, loop-aware event scheduling, and AudioWorklet MIDI sink. The worklet accepts absolute AudioContext timestamps and applies events at sample-frame offsets. It also exports `MusicalTransport`, a host-neutral play/pause/stop/seek/tempo/loop clock with look-ahead scheduling; browser, desktop, and standalone hosts supply their own monotonic and audio clocks.
- `midi-recording-ui.mjs` connects the performance keyboard to Record/Stop/Overdub controls, capture-time quantization, a touch-editable piano roll, note selection/deletion and velocity editing, four-cycle MIDI loop playback, optional Web MIDI hardware input, and MIDI-track persistence in `.earthsession`. MIDI-only sessions can be played without an audio clip. Hardware MIDI depends on browser Web MIDI support and an allowed secure context.
- `transport-controller.mjs` binds the interface Play/Pause/Stop/Seek/Tempo controls to one `MusicalTransport` instance. It schedules MIDI against the instrument AudioContext with a bounded look-ahead window, resets the scheduling cursor after seeks/edits, and schedules independent audio clip instances against the same audio clock. The controller is browser-specific; the underlying transport remains host-neutral for the future standalone runtime.
- `performance-surface.mjs` adds a shared audio/MIDI scene launcher and MIDI CC learn controls. Audio tracks can be assigned to one of eight scenes from their timeline row; all audio tracks assigned to a scene launch together with the matching MIDI clip slots. Scene changes queue to the next 4/4 bar while transport is running. Optional audio `sceneIndex` assignments and hardware CC mappings under `performance.midiCCMappings` travel in `.earthsession` packages; legacy sessions default audio tracks to Scene 01.
- `../tests/test_earth_studio_midi_sequencer.mjs` covers MIDI recording, note velocity/channel, quantization, loop scheduling, and timestamped native-engine messages.
- `project-package.mjs` exports/imports a dependency-free ZIP-based `.earthsession` package containing the manifest and original audio assets.
- Portable packages use uncompressed ZIP entries for broad compatibility, with CRC-32 and SHA-256 verification; unsafe paths, duplicate entries, encrypted/compressed/ZIP64 archives and unexpected files are rejected.
- `../tests/test_earth_studio_session.mjs` exercises the schema/serialization boundary and multi-clip project persistence with Node's built-in test runner.
- `../tests/test_earth_studio_audio_clips.mjs` covers clip validation, split continuity, non-destructive trim, move, duplicate identity, and loop state.

## Project persistence

Create or name a project, import audio, and use Save Project for a manual checkpoint. Track additions, removals, mute/solo, gain, pan, offset, tempo, project-name edits, and clip edits schedule a local autosave. Open Saved Project restores the manifest and audio assets. The adapter verifies each stored asset's SHA-256 digest before decoding it. Re-saving removes obsolete assets belonging to that project.

All audio remains in browser-local IndexedDB; no cloud service is used. The browser adapter currently limits each project's audio assets to 512 MiB. Browser quota, eviction, interrupted writes, and iPhone/Safari behavior still require device testing. Export important projects as WAV backups; portable `.earthsession` package export/import is available in the current draft branch. Import creates a new local project copy and verifies every audio asset before saving.

The HTML page remains a Web Audio prototype, not the native low-latency engine. The native audio backend and true iPhone offline application remain later milestones.

Run the pure unit tests from the repository root:

```sh
node --test music-foundry/tests/test_earth_studio_session.mjs music-foundry/tests/test_earth_studio_project_package.mjs music-foundry/tests/test_earth_studio_midi_sequencer.mjs music-foundry/tests/test_earth_studio_audio_clips.mjs
```

Source provenance: `godsun108/The-portal`, `music-foundry/studio.html`, branch `music-foundry/art-studio-foundation`, source blob `6b725fe7c27368dca297d310cfda634fb6884cc8`.

- Audio clip instances support optional portable `gain` (0–2), `fadeInSeconds`, and `fadeOutSeconds` metadata. The shared browser transport applies clip gain and linear fade curves at the AudioContext clock; source audio remains untouched. Older sessions default to unity clip gain and no fades.

- The arrangement timeline has adjustable horizontal zoom (20–160 pixels per second), a fit-to-session action, and scroll-preserving zoom around the current viewport center. Fade-in/fade-out envelopes are drawn over each clip waveform as a visible gain curve; the original waveform and source audio remain unchanged.

- Audio clips optionally carry ordered gainAutomation points (timeSeconds, value) relative to the clip. The arrangement exposes a touch-friendly automation lane: tap to add/remove points and drag points to reshape a linear gain curve. Playback combines the automation curve with clip gain and fades on the shared AudioContext clock; automation remains non-destructive and travels with .earthsession projects.


- MIDI/instrument clips support editable parameter automation lanes for filter cutoff (80–18,000 Hz), pitch bend (−12 to +12 semitones), and vibrato depth (0–20). Points are stored in clip-relative 960-PPQ ticks, validated with each session, interpolated by the sequencer, and sent to the native AudioWorklet with AudioContext timestamps. The worklet applies changes at the corresponding render-frame boundaries; older MIDI clips remain valid.
