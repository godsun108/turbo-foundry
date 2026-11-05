# SoulX-Singer ephemeral GPU worker runbook

Status: preparation only. This document does not provision cloud resources, download weights, or authorize spend.

## Objective

Run the existing Music Foundry adapter against the official SoulX-Singer score-controlled inference CLI on an isolated, temporary GPU worker. Keep model files off the live Virtual Human Engine volume and out of Git.

## Current integration contract

- Adapter: `music-foundry/soulx_local_runner.py`
- Score exporter: `music-foundry/soulx_export.py`
- Read-only score gate: `music-foundry/soulx_export_preflight.py`
- Current score boundary: `music-foundry/SOULX_EXPORT_BOUNDARY.md`

The adapter expects:
1. A reviewed score JSON that passes the existing exporter.
2. An official SoulX-Singer checkout with its CLI/config/phoneset.
3. The official `SoulX-Singer/model.pt` checkpoint.
4. A reference singing WAV and matching prompt metadata.
5. A new or empty output directory.

It does not download models, install dependencies, invent melody/lyrics, create prompt metadata, or overwrite an existing render.

## Infrastructure choice for the first audition

Preferred first test: one on-demand RunPod GPU Pod in a single region, with an isolated workspace and no attachment to Railway or VHE.

- Candidate GPU: A40 (48 GB VRAM) as a conservative first inference target; verify live availability and the actual checkout's memory behavior before launch.
- Published listed rate observed: about $0.59/GPU-hour. Rates and availability can change.
- Candidate storage: 20 GB standard network volume, only if we decide to retain the weights between sessions. Published standard network storage under 1 TB is about $0.07/GB-month (roughly $1.40/month for 20 GB). Confirm the checkout's exact required size and the provider's displayed quote before creating it.
- Lowest-cost alternative for a one-off trial: use only temporary container disk, re-download weights for each session, export the finished WAV and manifest, then terminate the Pod. Temporary disk is not durable.

These are planning estimates, not a spend authorization or a guarantee of availability. No resource may be created until the operator has reviewed the current checkout quote and approved a maximum spend.

## Preflight before any download

On the isolated worker:

```bash
nvidia-smi
df -h /workspace
python --version
```

Use Python 3.10 for the upstream project. Confirm free disk space before downloading. The official model page instructs users to download both repositories:

```bash
hf download Soul-AILab/SoulX-Singer --local-dir pretrained_models/SoulX-Singer
hf download Soul-AILab/SoulX-Singer-Preprocess --local-dir pretrained_models/SoulX-Singer-Preprocess
```

The full official model repository has been listed at approximately 5.6 GB; the separate preprocessing repository adds more. Do not assume a 5 GB volume is sufficient. Record actual directory sizes and checkpoint SHA-256 values after download.

Install dependencies from the official pinned `requirements.txt` in an isolated environment. Confirm the PyTorch/CUDA combination against the selected image before attempting inference; do not silently upgrade the project's pins.

## Render gate

Do not run the production song render until all of these are true:

- The canonical lyric source has been verified by the existing lyric-event manifest.
- A human-reviewed score includes exact lyric units, phonemes, note pitches, durations, and a locked tempo.
- `soulx_export_preflight.py` passes without bypasses.
- The reference singer prompt and its metadata are present and the operator has rights/consent to use that recording.
- The output directory is new or empty.

Then run the existing adapter with explicit paths and `--device cuda`. Preserve the generated WAV, render manifest, logs, and SHA-256 checksums as separate artifacts. Audition the vocal before mixing it into the arrangement.

## Data and security boundaries

- Never mount or write to the production VHE `/data` volume for this task.
- Never commit weights, prompt audio, API tokens, or generated private audio to Git.
- Keep provider API keys in the provider's secret store or local environment, never in a checked-in file or build argument.
- Do not expose an unauthenticated inference endpoint. The first audition is a single operator-run job, not a public API.
- Upload only the reviewed output artifacts needed by Music Foundry; delete temporary prompt assets when no longer required.

## Shutdown and cost control

- Set a short worker idle timeout and a hard job timeout.
- Start the GPU only for setup/inference; stop or terminate it immediately after artifact verification.
- If using a persistent network volume, review its ongoing monthly charge and delete it after the audition if it is no longer needed.
- Verify the provider dashboard shows no running Pods or retained volumes after cleanup.
- Record actual GPU runtime, storage charges, model revisions, checkpoint hashes, and output hashes.

## Current blockers (do not bypass)

The current canonical score scaffold is intentionally incomplete: it has no reviewed `lyric_units`, no locked tempo, and no authored melody. The existing exporter must reject it until a human completes and reviews those fields.

The adapter also requires a reference singing WAV plus matching prompt metadata. The official upstream demo uses example prompt assets, but this runbook does not assume those are approved for this song or for voice identity use.

Therefore, infrastructure readiness alone does not mean a song render is ready. The next creative gate is to finish the reviewed score and choose/prepare an authorized reference singer prompt.
