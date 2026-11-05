# Music Foundry — local singing renderer integration

Status: adapter scaffold committed; no model, dependency, reference recording, or remote service was downloaded or configured.

## Purpose

Music Foundry remains canonical for lyrics, arrangement, reviewed vocal score, takes, stems, and mix. SoulX-Singer is an optional local render worker behind a narrow adapter. The browser remains the iPhone-first authoring and review surface; the large singing model runs on an operator-controlled desktop/GPU or other explicitly provisioned local host.

## Prepare a reference singing prompt

The first-time prompt preparation wrapper stages a copy of an authorized English singing recording inside a new output folder, then invokes the official SoulX preprocessing pipeline with English lyric/note transcription. It does not touch the original recording or overwrite an existing output folder.

```bash
python3 music-foundry/soulx_prepare_prompt.py \
  --source-audio /absolute/path/to/authorized-reference.wav \
  --engine-root /absolute/path/to/SoulX-Singer \
  --output-dir music-foundry/output/somebodys-gotta-do-it/reference-prompt
```

On success, use `reference-prompt/vocal.wav` and `reference-prompt/metadata.json` as the `--prompt-wav` and `--prompt-metadata` inputs to `soulx_local_runner.py`. Preprocessing requires the upstream preprocessing checkpoints and runtime dependencies to already exist in the local SoulX checkout. It does not download or install them.

## Data flow

1. Author the sung phrase in the track-local Vocal Score Editor.
2. Preserve exact source lyric words and manually review ARPABET phones, MIDI pitch, note type, onset, and duration for every unit.
3. Lock the performance tempo and mark each phrase reviewed.
4. Run `soulx_export.py` through the adapter to derive SoulX target metadata. The canonical score is never rewritten.
5. Supply an operator-authorized reference singing WAV and its non-empty SoulX prompt metadata.
6. The adapter invokes the official SoulX-Singer CLI in score-control mode, without shell interpolation or implicit FP16.
7. Validate the resulting mono 24 kHz PCM WAV and write a provenance manifest with SHA-256 hashes.
8. Import the WAV as a new non-destructive take on the matching vocal lane; audition it before mixing or release.

## Local setup boundary

The adapter expects an already installed official SoulX-Singer checkout with:

- `cli/inference.py`
- `soulxsinger/config/soulxsinger.yaml`
- `soulxsinger/utils/phoneme/phone_set.json`
- `pretrained_models/SoulX-Singer/model.pt`

The reference WAV, prompt metadata, model checkpoint, and runtime dependencies must be provided locally by the operator. The adapter does not clone repositories, download model weights, install Python packages, access cloud services, or store credentials.

Example (run from the Turbo Foundry repository root):

```bash
python3 music-foundry/soulx_local_runner.py \
  --score music-foundry/projects/somebodys-gotta-do-it/vocal_score.reviewed.json \
  --engine-root /absolute/path/to/SoulX-Singer \
  --prompt-wav /absolute/path/to/authorized-reference.wav \
  --prompt-metadata /absolute/path/to/authorized-reference.json \
  --output-dir music-foundry/output/somebodys-gotta-do-it/soulx-hook-a
```

Use `--device cpu` only if the installed upstream runtime and available memory support it; CUDA is the upstream example path. The adapter deliberately does not enable FP16 automatically. Upstream inference currently writes `generated.wav` at 24 kHz mono. The Music Foundry manifest records that source format; any later resampling or stereo placement belongs to a separately validated import/mix stage.

## Security, consent, and rights

- Use only a reference singer recording the operator owns or is explicitly authorized to use. Do not clone or imitate an identifiable person without permission.
- The official project documents Apache-2.0 for its code and model weights; this does not grant rights to a prompt recording, lyrics, datasets, or other supplied assets. Keep each asset's rights evidence separately.
- The upstream inference implementation loads a PyTorch checkpoint with `weights_only=False`. Only load a checkpoint obtained from the official, trusted model source after verifying its provenance. Never load an arbitrary user-uploaded checkpoint.
- Model files and reference recordings must stay outside Git. No auto-downloads, cloud inference, secrets, or silent deployment.
- A successful render is not an approved performance. Human audition must verify pronunciation, timing, pitch, artifacts, and artistic quality.

## Current song-specific status

The current `vocal_score.json` remains a scaffold: tempo is provisional and sung phrases have no completed note-level `lyric_units`. Therefore the adapter must reject the current song score. This is intentional. The first practical proof should be one short, reviewed phrase from the chorus, not an unreviewed full-song render.

## Tests

```bash
python3 -m unittest music-foundry/tests/test_soulx_local_runner.py -v
```

The tests use synthetic fixtures and a mocked process invocation. They do not require the SoulX model, install dependencies, download assets, or claim that a real singing render has passed.
