# SoulX-Singer export boundary

SoulX-Singer is a research candidate for the optional sung-hook lane. Its
official metadata contains segment timing, text, phonemes, per-note durations,
MIDI pitches, note types, and (for melody control) frame-level F0. The
canonical Music Foundry score intentionally does not invent those annotations.

## Preflight

Run:

```bash
python music-foundry/soulx_export_preflight.py music-foundry/projects/somebodys-gotta-do-it/vocal_score.json
```

The command is a safety gate only. It never writes metadata or audio. It checks
that the tempo and sung phrases are human-reviewed and that syllable/phoneme/
note alignment exists. It also reports three format gaps that must be resolved
before a translator can be implemented:

1. Word-boundary segmentation: SoulX uses explicit `<SP>` boundaries, while
   the current canonical score has syllable entries but no reviewed word grouping.
2. Note-type semantics: the canonical `normal/tie/rest/slur` enum must be
   mapped to SoulX's numeric values only after verifying the official parser.
3. Segment grouping and time boundaries: the export profile must explicitly
   define how phrase timing becomes SoulX segment `time` ranges.

Do not fill these gaps by guessing. SoulX's score-control path uses MIDI note
pitches; its melody-control path uses frame-level F0. This project is targeting
score control first, so no synthetic F0 curve should be fabricated.

The current chorus scaffold is expected to fail this preflight. A failure is
the correct result until the score is aligned and the export profile is
reviewed. No model weights, dependencies, or reference audio are downloaded
or installed by this tool.
