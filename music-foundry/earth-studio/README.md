# EARTH STUDIO browser adapter

This directory is the canonical Turbo Foundry home for the first ART STUDIO browser adapter, migrated from Portal draft PR #325.

- `art-studio.html` preserves the initial browser-local multitrack workflow.
- `session-schema-v1.json` defines the first portable `.earthsession` manifest.
- `session-store.mjs` validates, serializes, and persists manifests plus audio Blobs in local IndexedDB.
- `../tests/test_earth_studio_session.mjs` exercises the pure schema/serialization boundary with Node's built-in test runner.

The HTML page is intentionally still a prototype: it has not yet been wired to the new persistence module. The store is an independently testable foundation, not a claim that the existing page autosaves. Browser IndexedDB quota and real iPhone/Safari behavior require device testing. The store caps each project's binary assets at 512 MiB and keeps project assets local.

Run the unit tests from the repository root:

```sh
node --test music-foundry/tests/test_earth_studio_session.mjs
```

Source provenance: `godsun108/The-portal`, `music-foundry/studio.html`, branch `music-foundry/art-studio-foundation`, source blob `6b725fe7c27368dca297d310cfda634fb6884cc8`.
