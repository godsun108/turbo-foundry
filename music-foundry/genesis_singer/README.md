# Genesis Singer v0.1 — local neural singing research engine

This is an original, locally trainable score-conditioned acoustic model. It maps aligned phoneme tokens, MIDI pitches, note types, durations and singer identity to log-mel frames. It makes no hosted generation calls and downloads no weights.

## Honest capability boundary

The architecture, dataset validator, trainer, checkpoint format and inference path are implemented here. No trained checkpoint or licensed singing corpus is included. The bundled Griffin-Lim inverse-mel renderer is a baseline decoder for smoke tests, not a production neural vocoder. Natural singing requires a compatible neural vocoder trained on the same acoustic representation. This from-scratch baseline does not claim SoulX-Singer quality; the existing SoulX adapter remains a separate engine. Never train on recordings without explicit singer permission and appropriate rights. Keep raw recordings and checkpoints outside Git.

## Dataset manifest

One JSON object per line, with audio paths relative to the manifest directory. Example fields: audio= takes/lead_001.wav; phoneme_ids=[1,2,3]; pitches=[60,62,64]; note_types=[2,2,2]; durations_frames=[18,20,22]; speaker_id=0; consent_id= signed-release-2026-001. Audio must be mono 24 kHz PCM WAV. Each phoneme needs a human-checked alignment to a MIDI pitch and duration in 256-sample mel frames. Duration sum must equal the mel frame count. Note types: 1=rest, 2=normal, 3=tie; 0 is reserved for padding. Phoneme ID 0 is reserved for padding. Vocabulary JSON maps phoneme strings to unique positive IDs. Include only recordings whose rights and singer consent permit training and intended use.

## Train

From the repository root, install music-foundry/genesis_singer/requirements.txt into a dedicated Python environment, then run:

    python -m music_foundry.genesis_singer.train --manifest /private/data/train.jsonl --vocab /private/data/vocab.json --output /private/models/genesis-singer-v0 --speakers 1 --epochs 100 --device cuda

Use --device cpu if CUDA is unavailable. The trainer writes latest.pt, best.pt and training.json. Begin with a tiny consented dataset to validate alignment and the loop, not to claim production quality.

## Inference

Score JSON fields: phonemes (tokens in vocabulary), pitches (MIDI 0–127), note_types, durations_frames and optional speaker_id.

    python -m music_foundry.genesis_singer.infer --checkpoint /private/models/genesis-singer-v0/best.pt --score /private/projects/song/score.json --output /private/projects/song/lead-vocal.wav --device cuda

## Production quality gate

Before production, add a compatible neural vocoder, train and validate on a properly licensed multi-song corpus, evaluate held-out singers and songs, measure pitch and lyric alignment, test breath and phrase transitions, and audition on target devices. Speaker identity conditioning is explicit; do not clone a real person's voice without permission.
