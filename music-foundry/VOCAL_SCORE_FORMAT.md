# Canonical Vocal Score v1

Music Foundry owns the engine-neutral vocal score. The cue sheet remains the lyric authority; this file is a structured performance/score layer, not a rewrite.

## Files
- `vocal_score.schema.json`: JSON Schema Draft 2020-12 contract.
- `projects/somebodys-gotta-do-it/vocal_score.json`: first chorus scaffold.

## Alignment contract
- A phrase can be anchored to an existing timing marker without pretending that its syllables or notes are aligned.
- Syllable entries carry explicit phoneme text, onset, duration, and zero or more note events.
- Note pitches use MIDI note numbers (0–127); note durations and syllable timing use quarter-note beats.
- Missing alignment stays empty/null. No model adapter may infer missing pitches, phonemes, or timing from section labels.
- The canonical score is renderer-neutral. SoulX, OpenUtau/DiffSinger, or another engine gets a derived export profile; renderer-specific JSON never replaces this source.
- Spoken phrases remain valid without note events. A sung phrase must reach syllable alignment and human review before export.

## Current hook scaffold
The eight chorus lyric lines are copied verbatim from the cue sheet. Existing section markers are attached only where the timing grid supplies a corresponding marker. All note and syllable alignment remains intentionally empty.

## Validation gates
1. Validate JSON against the schema.
2. Check every phrase text against its cue-sheet source excerpt.
3. Require phrase alignment before syllable alignment; require human review before singing export.
4. Reject a sung export if any syllable lacks phoneme, onset, duration, or required note data.
5. Keep tempo provisional until the arrangement is performance-locked.

No notes, phonemes, durations, or melody have been invented in the scaffold.
