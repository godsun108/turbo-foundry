# Fine China — chorus melody proposal (DRAFT)

**Creative vocal direction D is approved:** relaxed, warm spoken swagger in the verses; speech-shaped rhythmic lift in the pre-chorus; big, joyful soulful house singing in the chorus; intimate spoken bridge; human-feeling gang responses.

**The note-by-note melody below is a proposal, not yet approved.** It is saved as `vocal_score_draft.json` and is intentionally not the production score. Do not mark it reviewed or send it to SoulX until we listen and approve it together.

## Musical frame

- 126 BPM, 4/4, A minor.
- Chorus harmony proposal: one bar each of Am – F – C – G, repeated.
- The 16-bar chorus occupies arrangement bars 33–48 (source beats 128–192).
- Lead guide range: E4–D5. Gang response range: E4–A4.
- The MIDI audition guide starts immediately at beat zero for quick listening. Its report preserves the original arrangement start at beat 128 (bar 33). Use the renderer's `--preserve-timeline` option when importing into the full arrangement.

## First hook — exact proposed note contour

| Phrase | Proposed notes (one word per note) | Rhythm |
|---|---|---|
| Don't save the fine China | E4 – G4 – A4 – G4 – E4 | ½ + ½ + ½ + ½ + 2 beats |
| EAT ON IT! | A4 – G4 – E4 | ¾ + ½ + ¾ beats |
| Pour the good wine | E4 – G4 – A4 – G4 | 1 + ½ + ½ + 2 beats |
| DRINK ON IT! | A4 – G4 – E4 | ¾ + ½ + ¾ beats |

The response should feel like a small, joyful group of friends around the table, not a stadium chant. Let the lead phrase smile and lift on “fine”, then settle on “China”. Leave the two-beat gaps after each gang response for the bass and instrumental answer.

## Full chorus phrase map

| Arrangement bars | Phrase | Length |
|---|---|---:|
| 33 | Don't save the fine China | 4 beats |
| 34 | EAT ON IT! + response gap | 4 beats |
| 35 | Pour the good wine | 4 beats |
| 36 | DRINK ON IT! + response gap | 4 beats |
| 37–38 | Wear your Sunday shoes on a Tuesday night | 8 beats |
| 39–41 | If you got a little love you got a reason to celebrate life | 12 beats |
| 42–43 | Don't save it for later don't wait in line | 8 beats |
| 44–45 | The world's too beautiful to leave it behind | 8 beats |
| 46 | Don't save the fine China | 4 beats |
| 47 | EAT ON IT! + response gap | 4 beats |
| 48 | Instrumental turnaround / breath | 4 beats |

The melody opens up on “Sunday”, “Tuesday”, and especially “celebrate”, then returns to the simple hook contour for the final payoff. The guide includes 13 phrase events and 64 word/rest units.

## MIDI audition guide

The project now has a dependency-free MIDI writer:

```bash
python3 music-foundry/song_pipeline.py \
  --project music-foundry/projects/fine-china \
  --output music-foundry/output/fine-china \
  --execute-vocal-guide
```

It writes `fine-china-vocal-melody-draft.mid` with separate lead and gang tracks, plus a report. It is a pitch/rhythm guide, not a sung recording. The current draft includes explicit draft ARPABET phones for every lyric word so we can inspect the proposed pronunciation mapping, but those phones still require human review.

## What remains before singing

1. Listen to the MIDI guide and decide whether the hook feels right.
2. Adjust any pitches, rhythms, word stresses, and rests that don't feel natural.
3. Review the exact pronunciation/ARPABET mapping and phoneme-to-note alignment.
4. Only after that approval, promote a reviewed score into `vocal_score.json` and allow the existing SoulX exporter to run.

The production gate remains closed: `score_status` is `composition_draft`, and every phrase alignment is also `composition_draft`. The pipeline must not mistake a MIDI sketch for a human-reviewed singing score.
