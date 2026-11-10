# SoulX-Singer local singing setup

Music Foundry uses the official [SoulX-Singer](https://github.com/Soul-AILab/SoulX-Singer) score-conditioned singing synthesizer. The upstream code is Apache-2.0 licensed; model weights and any example/reference recordings must be checked against their own terms before use. This integration does not send audio to a hosted generator.

## Current gates

- The Music Foundry adapter is implemented.
- The Fine China chorus score is still a composition draft. It must be auditioned and reviewed before it can be promoted to `score_status: reviewed`.
- SoulX needs a real singing reference recording and matching metadata. Speech audio is not a substitute.
- Model weights and preprocessing weights are not stored in Git and are not automatically downloaded by Music Foundry.
- Run inference on a compatible local compute host. An iPhone can record the reference, but the official PyTorch SoulX stack is not an iPhone-native app.

## Install the official engine on the local compute host

Use Python 3.10 in a dedicated environment, following upstream setup:

```bash
git clone https://github.com/Soul-AILab/SoulX-Singer.git
cd SoulX-Singer
conda create -n soulxsinger -y python=3.10
conda activate soulxsinger
pip install -r requirements.txt
pip install -U huggingface_hub
hf download Soul-AILab/SoulX-Singer --local-dir pretrained_models/SoulX-Singer
hf download Soul-AILab/SoulX-Singer-Preprocess --local-dir pretrained_models/SoulX-Singer-Preprocess
```

The preprocessing stack has additional dependencies. Install them in the same environment from `preprocess/requirements.txt` as directed by upstream. The official repository and model cards are the source of truth for model terms, hardware compatibility, and current setup requirements.

## Prepare the singing reference

Record a clean 5–20 second WAV of the intended singer actually singing (not speaking), dry/close-mic, with no backing track if possible. Only use a voice you own or have explicit permission to use. Put the file at:

`music-foundry/projects/fine-china/vocal-reference.wav`

Run the official preprocessing pipeline on that recording with singing/MIDI transcription enabled and vocal separation disabled for a dry solo recording. For example, from the SoulX-Singer checkout:

```bash
python -m preprocess.pipeline \
  --audio_path /absolute/path/vocal-reference.wav \
  --save_dir /absolute/path/prompt-transcription \
  --language English \
  --device cpu \
  --vocal_sep False \
  --max_merge_duration 30000 \
  --midi_transcribe True
```

Review the generated metadata for correct words, phonemes, notes, and timing. Copy the generated JSON (same basename as the input audio) to:

`music-foundry/projects/fine-china/vocal-reference.metadata.json`

The reference is used for singer timbre/style. The target lyrics and notes come from the reviewed Fine China score. Do not use an unreviewed automatic transcript as the final score.

## Render after the score is reviewed

From the Music Foundry repository, point the pipeline at the SoulX checkout and the Python interpreter in its dedicated environment:

```bash
python3 music-foundry/song_pipeline.py \
  --project music-foundry/projects/fine-china \
  --output music-foundry/output/fine-china \
  --soulx-root /absolute/path/SoulX-Singer \
  --python-executable /absolute/path/to/conda/envs/soulxsinger/bin/python \
  --device cpu \
  --execute-vocals
```

Use `--device cuda` only when the host has a compatible CUDA/PyTorch setup. The output is `music-foundry/output/fine-china/soulx-vocals/generated.wav`. Listen for pronunciation, pitch, timing, artifacts, and singer consistency before using it in a mix.

## Upstream references

- Official code and setup: https://github.com/Soul-AILab/SoulX-Singer
- Official preprocessing workflow: https://github.com/Soul-AILab/SoulX-Singer/tree/main/preprocess
- Official model weights: https://huggingface.co/Soul-AILab/SoulX-Singer