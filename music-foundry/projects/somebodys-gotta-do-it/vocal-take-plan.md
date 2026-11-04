# Somebody's Gotta Do It — spoken-vocal take plan

**Working tempo:** 127 BPM (provisional) · **Meter:** 4/4 · **Length:** 56 bars / approximately 1:45.8  
**Primary mode:** spoken. The sung mode remains a separate capability for future projects and optional pitched textures; it is not a substitute for this track's spoken lead.

## Recording approach

1. Record one complete dry spoken lead take first. Keep it conversational and confident rather than forcing a sung melody.
2. Record a second lead pass for punch-ins and alternate emphasis. Do not automatically double every phrase.
3. Record gang responses as a separate group layer, especially the repeated title hook.
4. Record optional ad-lib answers ("Eventually", "You better", "ALL PLATFORMS") as independent clips.
5. Record whisper doubles only on the intro and selected build phrases.
6. Create chopped one-shots from approved spoken takes after the clean takes are preserved.

## Bar map

Bar numbers are zero-based and follow the existing 56-bar instrumental arrangement. Each marker in `vocal_timing.json` is an editorial landmark, not a locked syllable grid. Leave room for natural speech swing and bass call-backs.

| Section | Bars | Performance |
|---|---:|---|
| Intro tag | 0–3 | Close whisper repetitions; final "Fuck it, I'll do it" dry and forward |
| Verse 1 | 4–11 | Fast conversational lead; leave gaps for bass and ad-lib answers |
| Pre | 12–15 | Increase urgency; overlap doubles; brief stop before the drop |
| Chorus | 16–23 | Gang-shouted spoken hook; chop title phrase between full statements |
| Verse 2 | 24–31 | More interruptions and bass call-backs than verse 1 |
| Bridge | 32–39 | Half-time robotic word-stack; each short word may become a separate chop |
| Final chorus | 40–51 | Maximum layers; preserve the full hook's intelligibility |
| Outro | 52–55 | Repeated title, then cut the instrumental for "(And I'm not done yet)" |

## Layer and export rules

- **dry_lead:** clean, intelligible primary spoken performance.
- **gang_vocals:** separately recorded group shouts and call-and-response.
- **adlibs:** optional secondary-voice answers and spontaneous reactions.
- **chops:** edits derived from approved spoken takes; retain source phrase references.
- **whisper_double:** quiet texture, not a replacement for the lead.

Keep source takes non-destructive. Export each layer independently before printing the full mix. Do not label a synthetic placeholder, browser speech playback, or MIDI tone as a vocal recording.

## Implementation boundary

This plan and its JSON landmarks do not generate speech. A real spoken renderer must return validated WAV audio before a vocal stem can be marked rendered. A singing renderer must independently declare and demonstrate sung-mode support. No external provider, paid call, credential, or deployment is authorized by this plan.
