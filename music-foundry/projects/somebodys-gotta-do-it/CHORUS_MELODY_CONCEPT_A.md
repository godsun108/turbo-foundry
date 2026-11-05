# Somebody's Gotta Do It — chorus melody concept A

**Status: composition proposal only — NOT approved, NOT canonical, NOT export-ready.**

This is an original melodic sketch prepared against the current procedural backing arrangement. It does not change `vocal_score.json`, lock the song key or tempo, or claim human review of pronunciation. The source lyric remains `cue-sheet.md` and must be preserved verbatim.

## Musical frame

- Groove target: 127 BPM, 4/4 (still provisional)
- Backing reference: current arrangement generator's provisional A-minor-centered loop: Am / F / C / G
- Chorus location: bars 17–24 in one-based counting (zero-based bars 16–23)
- Vocal layout: the four title lines remain gang-shouted; the four response lines are optional pitched textures, consistent with the project's spoken-led identity.
- Concept: short, punchy word attacks, mostly chord tones, with the final response resolving downward rather than turning the track into a fully sung pop chorus.

The project metadata still says key undecided; A minor is only the current MIDI generator's provisional center. Do not treat it as locked.

## Candidate word-level pitches

MIDI note numbers use standard numbering (A4 = 69). Each response phrase occupies one 4/4 bar in this sketch. Word durations add to four beats per phrase. These are proposed note choices, not a final melody.

### chorus_02 — “Make the speakers scream” (F-major backing bar)

| Word | Candidate ARPABET (unreviewed) | Onset | Duration | MIDI | Note |
|---|---|---:|---:|---:|---|
| Make | M EY1 K | 0 | 0.75 | 69 | A4 |
| the | DH AH0 | 0.75 | 0.25 | 69 | A4 |
| speakers | S P IY1 K ER0 Z | 1 | 1 | 72 | C5 |
| scream | S K R IY1 M | 2 | 2 | 77 | F5 |

Shape: two quick pickups, a lift on “speakers,” then hold “scream” over the bar.

### chorus_04 — “Make the lights go mean” (G-major backing bar)

| Word | Candidate ARPABET (unreviewed) | Onset | Duration | MIDI | Note |
|---|---|---:|---:|---:|---|
| Make | M EY1 K | 0 | 0.5 | 71 | B4 |
| the | DH AH0 | 0.5 | 0.5 | 71 | B4 |
| lights | L AY1 T S | 1 | 1 | 74 | D5 |
| go | G OW1 | 2 | 0.5 | 74 | D5 |
| mean | M IY1 N | 2.5 | 1.5 | 79 | G5 |

Shape: compact repeated pickup, then a rising answer that peaks on “mean.”

### chorus_06 — “Keep the freaks alive” (F-major backing bar)

| Word | Candidate ARPABET (unreviewed) | Onset | Duration | MIDI | Note |
|---|---|---:|---:|---:|---|
| Keep | K IY1 P | 0 | 0.75 | 69 | A4 |
| the | DH AH0 | 0.75 | 0.25 | 69 | A4 |
| freaks | F R IY1 K S | 1 | 1 | 72 | C5 |
| alive | AH0 L AY1 V | 2 | 2 | 77 | F5 |

Shape: reuse the first response contour to create a recognizable hook motif.

### chorus_08 — “And tonight that somebody's me” (G-major backing bar)

| Word | Candidate ARPABET (unreviewed) | Onset | Duration | MIDI | Note |
|---|---|---:|---:|---:|---|
| And | AE1 N D | 0 | 0.5 | 74 | D5 |
| tonight | T AH0 N AY1 T | 0.5 | 1 | 74 | D5 |
| that | DH AE1 T | 1.5 | 0.5 | 71 | B4 |
| somebody's | S AH1 M B AA2 D IY0 Z | 2 | 1 | 69 | A4 |
| me | M IY1 | 3 | 1 | 67 | G4 |

Shape: start high and confident, step downward through the final words, and land on G4. This is intended as a strong spoken/sung hybrid resolution, not a sustained ballad note.

## Production direction

- Keep the four “Somebody's gotta do it” lines as forceful gang shouts on the kick; do not replace them with this pitched melody.
- Double the response phrases with a tight unison gang layer only after the lead contour works.
- Keep the vocal dry and forward in the first pass; test a short delay throw on “scream,” “mean,” and “alive.”
- Let the bass answer the vocal gaps. Do not fill every gap with extra notes.
- Compare this proposal against a fully spoken chorus. The song's identity is spoken-led wonky bass house; singing is optional color.

## Required human review before canonical score update

- [ ] Confirm the contour feels right against the actual backing MIDI/audio.
- [ ] Confirm every pronunciation and ARPABET token with the chosen vocalist.
- [ ] Confirm word-level note granularity is musically adequate, especially “speakers,” “tonight,” and “somebody's.”
- [ ] Confirm the four-bar phrase timing and chorus placement against the actual arrangement.
- [ ] Decide whether 127 BPM and A minor are retained or changed.
- [ ] Record reviewer and review date.

Only after those decisions should approved values be copied into `vocal_score.json`, and only after full score validation should the SoulX exporter be allowed to run.
