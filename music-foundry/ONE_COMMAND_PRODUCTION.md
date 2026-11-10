# One-command Music Foundry production pipeline

Music Foundry already contains the score schema/exporter, SoulX local adapter,
singing render importer, spoken-vocal timeline/assembler, MIDI generator,
instrumental renderer and stem DSP on its existing development branch. This
entrypoint is the coordination layer: it reports which existing components are
actually ready for a given song and dispatches the already-installed local
renderer only when all gates pass.

## Run from the repository root

Preflight without generating or downloading anything:

```bash
python3 music-foundry/song_pipeline.py \
  --project music-foundry/projects/fine-china \
  --output music-foundry/output/fine-china
```

Generate the editable MIDI arrangement:

```bash
python3 music-foundry/song_pipeline.py \
  --project music-foundry/projects/fine-china \
  --output music-foundry/output/fine-china \
  --execute-midi
```

When the canonical vocal score has human-reviewed note/phoneme alignment,
and a local SoulX checkout, checkpoint, reference singing WAV and matching
reference metadata are already present:

```bash
python3 music-foundry/song_pipeline.py \
  --project music-foundry/projects/fine-china \
  --output music-foundry/output/fine-china \
  --soulx-root /path/to/SoulX-Singer \
  --execute-midi --execute-vocals --device cpu
```

The local SoulX model is not downloaded by this tool. Set `SOULX_ROOT` or pass
`--soulx-root`; place the rights-cleared reference singer assets in the project
folder as `vocal-reference.wav` and `vocal-reference.metadata.json`.
The score must be named `vocal_score.json`, have `score_status=reviewed`,
`tempo_status=locked`, and include reviewed sung/chant/gang-shout lyric units.

## Truthful stage reporting

The report `pipeline-report.json` separates preflight readiness from completed
work. A MIDI pass does not imply audio. A singing render pass does not imply
that the vocal has been auditioned, arranged, mixed or mastered. No TTS voice
is substituted for singing. No network provider or model download is used.

## Current Fine China gate

Fine China currently has its lyric sheet, production brief, generation prompt,
project metadata and 120-bar MIDI workflow. This integration does not invent a
reviewed sung score or claim that the SoulX model/reference assets are present.
The first required singing task is to finish and review the hook's note/phoneme
score, then supply the local SoulX model and reference assets. The mix/master
stage remains separate and must report measured loudness and true peak values.
