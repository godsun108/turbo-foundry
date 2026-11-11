# Genesis Singer — local neural singing system

Genesis Singer now has two distinct execution paths:

1. **SoulX-Singer adapter (quality engine):** launches the official Apache-2.0 SoulX-Singer inference implementation against locally installed code and weights.
2. **Genesis-native model (independent engine):** the original score-conditioned trainable model in this package. It is a research baseline until trained on suitable data and paired with a production neural vocoder.

No hosted generation API, automatic model download, paid service, or GPU spend is required by this repository. You choose where to install the model and run inference.

## Free high-quality singing path: SoulX-Singer

The upstream authors explicitly license their code and model weights under Apache-2.0. The official checkpoint is large (the main model file is about 2.8 GB), and inference is designed around a local Python 3.10 environment. See the upstream README for current dependencies and setup:

- Code and license: https://github.com/Soul-AILab/SoulX-Singer
- Model card and weights: https://huggingface.co/Soul-AILab/SoulX-Singer
- Official preprocessing models: https://huggingface.co/Soul-AILab/SoulX-Singer-Preprocess

Install upstream code and weights yourself on a machine with adequate storage and compatible compute. This project intentionally does not clone the upstream repository, download weights, or install heavyweight dependencies automatically.

After installing upstream dependencies and downloading the model, prepare:
- a prompt vocal WAV and matching prompt metadata, using a singer recording you have permission to use;
- target metadata with human-reviewed English phonemes, note pitches, note types and durations, using SoulX's preprocessing pipeline and MIDI editor;
- the local SoulX model checkpoint.

The prompt audio is a voice-identity reference. Use an original synthetic voice or a recording with explicit permission; do not use an identifiable person's voice without authorization.

Run from the repository root:

    python music-foundry/genesis_singer/soulx_adapter.py \
      --soulx-root /path/to/SoulX-Singer \
      --model /path/to/SoulX-Singer/pretrained_models/SoulX-Singer/model.pt \
      --prompt-wav /path/to/consented-prompt.wav \
      --prompt-metadata /path/to/prompt.json \
      --target-metadata /path/to/target.json \
      --output-dir /path/to/output \
      --device cpu

Use `--device cuda --fp16` only when CUDA is installed and supported. CPU mode avoids GPU rental but may be slow. The adapter validates paths and metadata JSON, invokes the official upstream CLI without a shell, and writes `genesis-soulx-run.json` with the result. SoulX's upstream output files remain in the chosen output directory.

The adapter expects SoulX's own metadata schema; it does not pretend that Genesis's compact phoneme/pitch score JSON is already compatible. Use the upstream alignment/editor workflow to produce target metadata. The official inference example uses the `cli.inference` module with score or melody control and the model/config/phoneset paths.

## Genesis-native model

This is an original locally trainable score-conditioned acoustic model. It maps aligned phoneme tokens, MIDI pitches, note types, durations and singer identity to log-mel frames. It makes no hosted generation calls and downloads no weights.

### Honest capability boundary

The architecture, dataset validator, trainer, checkpoint format and inference path are implemented. No trained checkpoint or singing corpus is included. The bundled Griffin-Lim inverse-mel renderer is a baseline decoder for smoke tests, not a production neural vocoder. Natural singing requires a compatible neural vocoder trained on the same acoustic representation. This from-scratch baseline does not claim SoulX-Singer quality.

### Dataset manifest

One JSON object per line, with audio paths relative to the manifest directory. Example fields: `audio= takes/lead_001.wav`; `phoneme_ids=[1,2,3]`; `pitches=[60,62,64]`; `note_types=[2,2,2]`; `durations_frames=[18,20,22]`; `speaker_id=0`; `consent_id=signed-release-2026-001`. Audio must be mono 24 kHz PCM WAV. Each phoneme needs a human-checked alignment to a MIDI pitch and duration in 256-sample mel frames. Duration sum must equal the mel frame count. Note types: 1=rest, 2=normal, 3=tie; 0 is reserved for padding. Phoneme ID 0 is reserved for padding. Vocabulary JSON maps phoneme strings to unique positive IDs. Include only recordings whose rights and singer consent permit training and intended use.

### Train

From the repository root, install `music-foundry/genesis_singer/requirements.txt` into a dedicated Python environment. Then change directory into `music-foundry` and run:

    python -m genesis_singer.train --manifest /private/data/train.jsonl --vocab /private/data/vocab.json --output /private/models/genesis-singer-v0 --speakers 1 --epochs 100 --device cpu

Use `--device cuda` only if CUDA is available. The trainer writes `latest.pt`, `best.pt` and `training.json`. Begin with a tiny consented dataset to validate alignment and the loop, not to claim production quality.

### Genesis-native inference

Score JSON fields: `phonemes` (tokens in vocabulary), `pitches` (MIDI 0–127), `note_types`, `durations_frames` and optional `speaker_id`.

    python -m genesis_singer.pipeline --checkpoint /private/models/genesis-singer-v0/best.pt --score /private/projects/song/score.json --output /private/projects/song/lead-vocal.wav --device cpu

The command writes a WAV plus a SHA-256 provenance manifest. It refuses to overwrite an existing WAV.

## Production quality gate

Before calling Genesis-native production-ready, add a compatible neural vocoder, train and validate on a properly licensed multi-song corpus, evaluate held-out singers and songs, measure pitch and lyric alignment, test breath and phrase transitions, and audition on target devices. Speaker identity conditioning is explicit; do not clone a real person's voice without permission.

## License and data boundaries

The Genesis-native code in this directory is original project code. SoulX-Singer is a separately installed Apache-2.0 dependency; retain its license and notices when using or redistributing it. Dataset licenses are separate from model/code licenses: check each recording and dataset before training or commercial use. Noncommercial datasets must not enter a commercial training pipeline.
