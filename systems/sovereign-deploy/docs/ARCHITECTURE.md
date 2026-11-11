# Sovereign Deploy v0.1 architecture

## Trust boundaries

- **Builder:** creates the release bundle and signs the exact manifest bytes with an Ed25519 private key.
- **Verifier/agent:** receives a bundle and trusted public key; it never receives the signing key.
- **Release store:** contains immutable, content-verified release directories.
- **State pointer:** a single atomically replaced JSON record identifies active and previous releases.
- **Provider adapter (future):** translates the same release contract into provider-specific operations. Provider APIs are not the release format or source of truth.

## Install transaction

1. Parse and validate the manifest.
2. Verify Ed25519 signature against the configured public key.
3. Reject unsafe paths, symlinks, duplicate entries, size-limit violations and hash mismatches.
4. Copy listed payload files into a unique staging directory.
5. Verify the staged copy again.
6. Rename the staging directory to its immutable release ID.
7. Atomically replace state.json, retaining the previous active release ID.

A failure before step 7 leaves the active pointer unchanged. If state publication succeeds, rollback is an explicit second atomic state transition. The agent never deletes the prior release during install.

## Deliberate non-goals in v0.1

No arbitrary shell hooks, remote command execution, secrets in manifests, self-granted authority, automatic production promotion, or implicit minting/financial actions. The agent has no network listener and cannot grant itself permissions.

## Portability criterion

The release bundle and its digest must be identical regardless of destination. Railway, a self-hosted host, or another provider may differ only in the adapter that runs the verified release. Application code must not branch on provider identity.
