# Sovereign Deploy Agent

**Status: v0.1 foundation — local release verification and atomic activation.**

A provider-neutral deployment primitive for Sovereign and Turbo Foundry. It is deliberately small, dependency-free, and built on Node.js standard libraries.

## Guarantees in this version

- Release manifests are schema-versioned and list every payload file with a SHA-256 digest and byte length.
- Production verification fails closed unless the manifest has a valid Ed25519 signature and a trusted public key is configured.
- File paths are constrained to the release root; symlinks, path traversal, oversized files, duplicate paths, and unlisted entrypoints are rejected.
- Installation copies only verified files into a unique staging directory, re-verifies the copy, then atomically renames it into the immutable release store.
- The active release pointer is atomically replaced. The previous release is retained for explicit rollback.
- No provider SDK, shell execution, hosted database, or runtime package dependency is required.

## Commands

Run from this directory:

```sh
npm test
SOVEREIGN_RELEASE_PUBLIC_KEY="$(cat release-public.pem)" node src/cli.mjs verify ./release-bundle
SOVEREIGN_RELEASE_PUBLIC_KEY="$(cat release-public.pem)" node src/cli.mjs install ./release-bundle ./var/deploy
node src/cli.mjs status ./var/deploy
node src/cli.mjs rollback ./var/deploy
```

For isolated local development only, set `SOVEREIGN_ALLOW_UNSIGNED_LOCAL=1`. Never use that setting in staging or production.

## Release format

A bundle contains `release.json`, `manifest.sig`, and exactly the files listed in the manifest. The detached signature is base64-encoded Ed25519 over the exact UTF-8 bytes of `release.json`. The public key is supplied out-of-band via `SOVEREIGN_RELEASE_PUBLIC_KEY`; private signing keys must never be committed or placed on an application host.

```json
{
  "schema": "sovereign.release.v1",
  "releaseId": "portal-2026-11-11.1",
  "createdAt": "2026-11-11T12:00:00.000Z",
  "entrypoint": "server.mjs",
  "files": [
    { "path": "server.mjs", "sha256": "<64 lowercase hex>", "size": 1234 }
  ]
}
```

## Important boundary

This version verifies, stores, activates and rolls back immutable release directories. It does **not** yet supervise application processes, route live traffic, provision machines, replicate storage, or replace Railway/GitHub hosting. Those require a runtime supervisor and provider adapters, which must consume this same signed release contract. A successful local activation is not proof of a healthy public deployment.

## Next integration gates

1. Add a supervised Node runtime and health-gated traffic switch.
2. Add a Railway adapter that deploys the same verified release contract (no Railway-only application code).
3. Add a self-hosted Linux adapter and encrypted backup/restore.
4. Add signed deployment authorization and append-only audit receipts.
5. Prove portability by deploying one app to two different adapters and comparing identical release digests.
