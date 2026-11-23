# EARTH STUDIO browser adapter

This directory is the canonical Turbo Foundry home for the first ART STUDIO browser adapter, migrated from Portal draft PR #325.

- `art-studio.html` preserves the initial browser-local multitrack workflow and now connects it to project save/open/autosave.
- `session-schema-v1.json` defines the first portable `.earthsession` manifest.
- `session-store.mjs` validates, serializes, and persists manifests plus audio Blobs in local IndexedDB.
- `../tests/test_earth_studio_session.mjs` exercises the pure schema/serialization boundary with Node's built-in test runner.

## Project persistence

Create or name a project, import audio, and use Save Project for a manual checkpoint. Track additions, removals, mute/solo, gain, pan, offset, tempo, and project-name edits schedule a local autosave. Open Saved Project restores the manifest and audio assets. The adapter verifies each stored asset's SHA-256 digest before decoding it. Re-saving removes obsolete assets belonging to that project.

All audio remains in browser-local IndexedDB; no cloud service is used. The browser adapter currently limits each project's audio assets to 512 MiB. Browser quota, eviction, interrupted writes, and iPhone/Safari behavior still require device testing. Export important projects as WAV backups; this first pass does not yet provide a portable project-package download/import.

The HTML page remains a Web Audio prototype, not the native low-latency engine. The native audio backend and true iPhone offline application remain later milestones.

Run the pure unit tests from the repository root:

```sh
node --test music-foundry/tests/test_earth_studio_session.mjs
```

Source provenance: `godsun108/The-portal`, `music-foundry/studio.html`, branch `music-foundry/art-studio-foundation`, source blob `6b725fe7c27368dca297d310cfda634fb6884cc8`.
