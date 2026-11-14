# Fine China (Eat On It)

## Composition identity

- Tempo: 126 BPM, 4/4
- Tonal center: A minor
- Harmony: Am – F – C – G
- Style: soulful bass/disco-house; joyful, mischievous, communal, and life-affirming
- Core sound: warm Rhodes/organ stabs, disco-guitar offbeats, rounded rubber-band syncopated bass, four-on-the-floor kick, claps, shuffled-feel hats, hand-percussion accents, a rising soulful lead, and a large gang-response “EAT ON IT!” drop
- Full arrangement: 120 bars, approximately 3:49

## Render

```bash
python3 music-foundry/render_fine_china.py --output music-foundry/output/fine-china-audio --bpm 126
```

The renderer reuses the existing Music Foundry synthesis primitives and writes editable WAV stems, an instrumental mix, and an audio manifest. The output is an original composition audition, not a mastered release.

## Vocal direction

The Fine China score draft contains the chorus with 73 placed syllable events, separate dry-lead and gang-vocal layers, and rests around the “EAT ON IT!” responses. The Genesis Voice Studio loads this score and uses the local Kokoro TTS voice with score-conditioned PSOLA pitch placement. The score is still a composition draft: listen to and approve the melody and vocal quality before treating it as final.

## Production intent

This song is about treating life as the special occasion: stop preserving the good things so carefully that you forget to use them. It should feel soulful, playful, wise without preaching, and irresistibly danceable.
