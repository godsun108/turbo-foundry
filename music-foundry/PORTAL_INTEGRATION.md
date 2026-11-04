# Portal ↔ Music Foundry Integration

Status: design checkpoint; no production wiring or deployment.

## Purpose

Reuse Portal's existing creative and interaction systems without creating a second audio engine. Turbo Foundry remains the canonical home for the song project, vocal timing, synthesis adapters, and rendered audio assets. Portal is the experiential front door and optional presentation layer.

## Existing Portal capabilities worth reusing

| Existing system | Useful role | Boundary |
| --- | --- | --- |
| `/genesis-voice/` | iPhone-friendly speech dictation, text conversation, verified model-response handling, and browser speech playback | Browser speech is a convenience interaction layer, not a studio-quality export renderer. Its configured AI endpoint remains optional. |
| `/sound.js` | Small ambient UI tones and room ambience | Not a DAW, sampler, synthesizer, or song playback engine. Keep it out of the audio-render path. |
| `/eidolon-studio/` | Procedural/GLB performer visualization and character presets | Visual performer only; current procedural mouth motion is not phoneme-accurate lip sync and does not generate vocals. |
| Portal creative constitution | Truthful capability labels, browser-local defaults, no duplicated canonical systems | Every room must distinguish a real working capability from a prototype or external dependency. |

## Canonical audio path

1. The song's cue sheet and vocal timing map remain authoritative in Turbo Foundry.
2. Genesis Voice Studio (MediaPipe/Kokoro) creates spoken takes from an operator-selected local model.
3. The exported WAV is imported into the song's vocal timeline and then into the Foundry render pipeline.
4. Portal may launch the studio, present the song/performer experience, or pass a user-approved text prompt into a documented interface. It must not maintain a forked copy of the synthesis engine or silently upload model/audio assets.

## Integration stages

### Stage A — Portal discovery and launch surface
- Add a clearly labeled Music Foundry / Genesis Voice Studio entry in Portal.
- Link only to a verified, actually hosted studio URL. A GitHub source-code page is not a runnable studio.
- Show the present status accurately: browser studio prototype; actual model synthesis and iPhone Safari compatibility still unverified.

### Stage B — Shared handoff contract
- Define a versioned, user-initiated handoff containing only the selected text, track identifier, and optional cue identifier.
- Do not pass credentials, model files, audio blobs, or private conversation history through query strings.
- Require explicit user action before any export, import, or cross-room handoff.
- Keep audio local by default; if a future connector needs network transfer, require a separate visible consent step.

### Stage C — Performer presentation
- Use Eidolon as an optional visual performer for an already-rendered vocal take.
- Add real audio-driven mouth timing only after a local phoneme/viseme timing source exists; do not describe the current idle mouth animation as lip sync.
- Keep the Portal sound layer independent from the song playback and render buses.

## Security and cost rules

- No paid service, paid provider, new Railway service, model download, or deployment without explicit approval.
- No automatic model download. The operator selects a local model bundle.
- No browser credentials or secrets.
- No production merge or Portal-main changes as part of this checkpoint.
- Never label speech synthesis as singing synthesis.
- Never claim the iPhone/Safari path works until tested on the target device.

## Immediate next proof

First verify a real Kokoro model can load and produce a downloadable spoken WAV on the target browser. Then verify that WAV can be imported into the existing vocal timeline. Only after those proofs should Portal receive a launch route or a cross-room handoff.
