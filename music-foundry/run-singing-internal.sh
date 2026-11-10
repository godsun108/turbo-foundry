#!/usr/bin/env bash
# Internal Linux validation for the local score-conditioned singing engine.
# No GitHub Actions, network, model download, or cloud service is used.
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
NODE="$(command -v node || true)"
BWRAP="$(command -v bwrap || true)"
TIMEOUT="$(command -v timeout || true)"
if [[ -z "$NODE" || -z "$BWRAP" || -z "$TIMEOUT" ]]; then
  echo "BLOCKED: internal runner requires Node.js >=22, bubblewrap (bwrap), and GNU timeout." >&2
  exit 2
fi
NODE_MAJOR="$("$NODE" -p 'process.versions.node.split(".")[0]')"
if [[ "$NODE_MAJOR" -lt 22 ]]; then
  echo "BLOCKED: Node.js >=22 required; found $("$NODE" --version)." >&2
  exit 2
fi
(
  ulimit -t 180
  ulimit -f 65536
  ulimit -u 128
  ulimit -n 64
  "$BWRAP" \
    --die-with-parent \
    --unshare-net \
    --ro-bind /usr /usr \
    --ro-bind /usr/local /usr/local \
    --ro-bind /bin /bin \
    --ro-bind /lib /lib \
    --ro-bind /lib64 /lib64 \
    --ro-bind /etc /etc \
    --proc /proc \
    --dev /dev \
    --tmpfs /tmp \
    --ro-bind "$ROOT" "$ROOT" \
    --chdir "$ROOT" \
    --clearenv \
    --setenv PATH "/usr/local/bin:/usr/bin:/bin" \
    --setenv HOME "/tmp" \
    --setenv TMPDIR "/tmp" \
    "$TIMEOUT" --signal=TERM --kill-after=10 180s \
    "$NODE" --test music-foundry/tests/test_genesis_singing_dsp.mjs
)
