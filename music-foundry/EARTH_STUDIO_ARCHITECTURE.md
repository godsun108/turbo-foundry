# EARTH STUDIO — Architecture and Baseline Audit

**Status:** Architecture proposal / Milestone 0 audit  
**Canonical engineering repository:** `godsun108/turbo-foundry`  
**Experience and navigation layer:** `godsun108/The-portal`  
**Product direction:** Hybrid DAW + performance instrument; standalone-first  
**Release posture:** Draft only. No merge, deployment, hardware commitment, or production claim.

## 1. Product contract

EARTH STUDIO is a first-party music production environment combining:

- A professional multitrack DAW (audio, MIDI, arrangement, automation, mixing, export).
- A performance workstation (pads, clips, step sequencing, live capture).
- First-party instruments and effects (synthesizers, drum machines, sampler, processors).
- Genesis Producer (project-aware composition and production assistance).
- A standalone operating environment for future dedicated hardware.

The same project must remain portable across supported iPhone/iPad, desktop, and dedicated standalone hardware. Core production must not require a cloud account, subscription, external DAW, or internet connection.

## 2. Repository ownership and integration boundary

### Turbo Foundry — canonical source

Turbo Foundry owns the music-production domain: project model, audio/DSP engine, MIDI and sequencing, instruments, effects, renderers, Genesis integration contracts, tests, and release artifacts.

### The Portal — experience layer

The Portal provides navigation, mobile-first presentation, and preview surfaces. It may mirror or host a client interface, but it must not become a second canonical audio engine or a divergent copy of production logic.

### Current ART Studio exception to resolve

The first ART Studio multitrack page currently exists in The Portal draft PR #325 on branch `music-foundry/art-studio-foundation`, not yet in the Turbo Foundry canonical repository. Its source should be migrated into Turbo Foundry under the Music Foundry domain, then exposed through Portal as a synchronized experience surface. Do not merge or deploy PR #325 as an independent permanent implementation before this ownership is resolved.

## 3. Verified baseline

### ART Studio multitrack foundation — Portal PR #325

Source: `The-portal/music-foundry/studio.html`  
Branch: `music-foundry/art-studio-foundation`  
PR: [#325](https://github.com/godsun108/The-portal/pull/325)  
PR status at audit: open, draft, unmerged.

Implemented in the inspected source:

- Browser-local import of multiple audio files using Web Audio decoding.
- In-memory track records with audio buffer, name, start offset, gain, pan, mute, and solo.
- Basic horizontal arrangement lanes and a seek/playback transport.
- Browser playback using AudioBufferSourceNode, GainNode, and StereoPannerNode where available.
- Offline stereo mix rendering at 48 kHz.
- 16-bit PCM WAV encoding and browser download.
- Mobile-oriented responsive layout and no audio upload path.

Explicit limitations documented in the page and confirmed by source inspection:

- No persistent project/session storage; audio and track state are lost on refresh/close.
- No MIDI recording, piano roll, MIDI instruments, or step sequencer.
- Tempo is a display/session marker; imported audio is not time-stretched.
- No plugin hosting, automation lanes, buses, or full mixer.
- No Genesis project editing integration.
- No waveform display or non-destructive clip editing model.
- No actual iPhone/Safari device verification recorded.
- Audio processing is browser Web Audio, not a native low-latency standalone engine.

Engineering observations to address during migration:

- Playback creates and closes an AudioContext for each play pass; lifecycle and latency need a deliberate engine/session policy.
- Track parameter edits are reflected on subsequent playback/render rather than being guaranteed sample-accurate live automation.
- Seek updates the playhead state; a robust transport must define seeking during active playback.
- In-memory decoded AudioBuffers are not a viable long-session persistence strategy on mobile devices.
- WAV export is bounded to 20 minutes and uses 16-bit PCM; future export needs explicit format/bit-depth options and memory-safe offline rendering.

### Existing Music Foundry capabilities — Turbo Foundry

The inspected Turbo Foundry Music Foundry branch includes:

- MIDI sketch and project-specific arrangement generation.
- Offline procedural instrumental WAV and stem rendering (documented as preview-quality, not a finished commercial mix).
- Spoken-take recording and offline assembly workflows.
- Browser-local vocal timeline editing with multiple lanes, clip placement, gain/pan, and effects/automation capabilities documented in the canonical README.
- Genesis Voice Studio prototype for local spoken synthesis and score-conditioned singing experiments.
- A provider-neutral vocal-render contract and tests.
- A local rendering/service prototype with explicit deployment and verification boundaries.

Important distinction: these Music Foundry capabilities are not yet equivalent to a complete DAW or production-grade standalone audio engine. Vocal generation prototypes and procedural audio previews must not be represented as verified production-grade instruments or singing models.

## 4. Architecture decisions

### 4.1 Separate the engine from every interface

The session model and audio engine must not depend on Portal DOM, React/browser UI, or a particular hardware screen. Interfaces issue validated commands and subscribe to engine state/events.

Proposed logical layers:

1. **EARTH CORE** — lifecycle, timing, device abstraction, storage, scheduling, crash recovery.
2. **EARTH AUDIO** — real-time DSP graph, audio I/O, routing, mixing, offline rendering.
3. **EARTH SESSION** — project schema, tracks, clips, MIDI, automation, assets, undo/redo.
4. **EARTH PLAY** — pads, clip launcher, step sequencer, live performance.
5. **EARTH INSTRUMENTS** — first-party synth, drum machine, sampler, and effects.
6. **GENESIS PRODUCER** — separate local intelligence process/service using bounded project-edit commands.
7. **Experience adapters** — iPhone/iPad, desktop, Portal web preview, and future hardware controls.

### 4.2 Native audio engine is the long-term source of truth

Keep the current Web Audio implementation as a prototype and compatibility/preview adapter. Do not mistake it for the final hardware engine.

Build a portable native DSP core (C++ is the initial candidate) with explicit platform audio backends. Keep the audio callback real-time safe: no blocking I/O, unbounded work, heap allocation, or unpredictable locks in the callback. Browser support may use a Web Audio/WebAssembly adapter where appropriate, but the dedicated standalone device must use the native engine and native audio I/O.

### 4.3 Versioned portable session format

Proposed extension: `.earthsession`.

The format should be a versioned, documented package containing:

- Session manifest (schema version, tempo, meter, sample rate, project identity).
- Track, bus, clip, and routing graph.
- MIDI events and automation.
- Instrument/effect state with versioned identifiers.
- Managed audio assets and checksums.
- Arrangement markers and loop regions.
- Recovery journal / autosave metadata.
- Optional thumbnails and UI state, kept non-authoritative.

Use relative asset references within the package; validate paths and sizes; never require a cloud URL to reopen a project. Define deterministic migrations between schema versions and preserve unknown optional metadata when safe.

### 4.4 Genesis must not run in the audio callback

Genesis Producer operates out-of-process or on a separate worker/service. It reads a bounded project snapshot and proposes typed operations (e.g. create MIDI clip, alter instrument parameter, add automation, suggest mix change). The host validates the operation, shows a preview/diff, and requires user approval before committing consequential edits. Undo must restore the exact previous project state.

### 4.5 Standalone-first, but staged realistically

The first target is an offline-capable mobile/desktop software workflow. A dedicated hardware release requires a native audio engine, selected supported hardware platform, drivers, thermal/power management, storage durability, and physical latency testing. Do not claim browser-only iPhone operation is equivalent to a Push-class standalone computer.

## 5. Proposed initial engineering stack

These are candidates to validate, not already-implemented facts:

- Portable DSP/audio core: C++ with a narrow C ABI or equivalent stable boundary.
- Browser preview: current web UI with a Web Audio adapter; consider WebAssembly for shared DSP where it provides measurable value.
- iOS: native app shell and native audio backend when required for reliable low latency and background/device integration.
- Desktop: native shell around the same session model and audio core.
- Hardware: dedicated Linux-based environment is a candidate, subject to audio driver/latency/boot/recovery evaluation.
- Persistence: versioned project package, atomic save, write-ahead/recovery journal, asset checksums.
- Tests: DSP unit tests, golden render tests, session round-trip/migration tests, fuzzing of project import, real-time safety checks, and physical-device acceptance tests.

Do not select a third-party framework or plugin format as a foundational dependency until licensing, portability, performance, offline operation, and long-term ownership have been reviewed.

## 6. Milestone 0 exit criteria

Milestone 0 is complete only when:

1. The ART Studio source and its exact PR/branch provenance are documented.
2. Existing Portal music/vocal workflows are mapped to their Turbo Foundry canonical source.
3. The first multitrack implementation has a reproducible baseline and known limitations.
4. Turbo Foundry is confirmed as the canonical owner of future DAW logic and engine code.
5. Portal's role is limited to experience/navigation and synchronized presentation.
6. A migration plan exists that preserves the current vocal timeline and recording booth.
7. No draft work is merged or deployed merely to make the architecture look complete.

## 7. Next implementation sequence

1. Port the ART Studio page into Turbo Foundry as a clearly marked browser adapter, preserving the original Portal implementation until parity is verified.
2. Add source-level tests for import, track model, offsets, mute/solo, gain/pan, transport, WAV format, clipping, and export limits.
3. Introduce a versioned session model and local persistence/autosave before adding more UI features.
4. Separate transport/session logic from DOM rendering and Web Audio node creation.
5. Define the portable audio-engine interface and native DSP proof-of-concept.
6. Add MIDI events, piano roll, step sequencer, and first-party drum instrument on top of the shared session model.
7. Only then expand toward full mixing, Genesis Producer, and standalone hardware.

## 8. Release and verification rules

- Draft branches and PRs remain unmerged until their own tests pass and dependencies are understood.
- No production deployment without explicit approval and device validation.
- Distinguish source inspection, automated test success, browser smoke test, physical iPhone test, and standalone hardware test.
- Do not claim offline persistence until a project survives reload/restart and is recoverable after interruption.
- Do not claim low latency until measured on target hardware.
- Do not claim Genesis is fully local until model/runtime assets are installed, cached, and verified usable offline.
