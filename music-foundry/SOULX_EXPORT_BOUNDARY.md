# SoulX-Singer score-control export

## Verified upstream contract

The official SoulX-Singer `DataProcessor` consumes one duration, phoneme token,
MIDI pitch, and note type per note/lyric unit. For English units it expands
`en_` plus a hyphen-separated ARPAbet sequence into phoneme tokens and creates
the internal frame-to-note (`mel2note`) map. The official MIDI parser confirms
the numeric note types: `1 = <SP>/rest`, `2 = normal`, and `3 = tie`.
A tie is represented in MIDI lyric data as `-` and restored from the previous
lyric. This exporter maps only canonical `rest/normal/tie`; `slur` is not
supported.

The score-control path uses MIDI pitch and does not require an authored F0
curve. The generated target metadata intentionally omits `f0`. Inference
still requires a separately prepared prompt WAV and prompt metadata for an
authorized reference singer.

## Canonical lyric units

A reviewed sung, chant, or gang-shout phrase may carry `lyric_units`. Each unit represents one
SoulX note-aligned English word or explicit silence:
- `text`: exact word from the source lyric, or `<SP>` for silence.
- `phonemes`: explicitly reviewed ARPAbet phones, without the SoulX `en_`
  prefix. The exporter adds the prefix and joins phones with hyphens.
- `onset_beats`: phrase-relative onset; units must be contiguous.
- `duration_beats`: positive note duration.
- `midi_pitch`: MIDI pitch 0–127; explicit silence uses 0.
- `note_type`: `normal`, `tie`, or `rest`.

The exporter does not run G2P, infer syllabification, invent melody, create
F0, or fill gaps. Silence must be authored as an explicit `<SP>` unit.
Concatenated word text must reproduce the phrase lyric exactly.

## Export

```bash
python music-foundry/soulx_export.py \
  music-foundry/projects/somebodys-gotta-do-it/vocal_score.json \
  /path/to/soulx-target.json
```

The destination is not overwritten unless `--overwrite` is supplied. Output
is a SoulX target-metadata JSON array. It is not audio and does not include the
prompt recording or prompt metadata.

Segment `time` is derived from locked global beat position and BPM in
milliseconds. Per-unit `duration` is derived from beat duration and BPM in
seconds. Each phrase is one segment; overlapping synthesized vocal phrases are rejected.
All conversions are deterministic.

## Current status

The canonical chorus scaffold has no reviewed `lyric_units`, no locked tempo,
and no authored melody. It must fail export until a human completes and reviews
those fields. Tests use synthetic fixtures only; no model weights, dependencies,
prompt recordings, or audio were downloaded or synthesized.

## Browser score editor

The track-local `vocal-score-editor.html` is linked from the existing vocal
timeline. It imports the canonical score or a saved workbench file, preserves
incomplete drafts separately, and exports a reviewed score only after explicit
tempo locking and per-phrase human review. Its browser-side ARPABET allowlist
is maintained in `projects/somebodys-gotta-do-it/soulx-phone-inventory.mjs`
and is tested by `tests/test_soulx_phone_inventory.mjs`. The Python exporter
remains the authoritative final validation gate; browser validation does not
replace it.
