# One-command Music Foundry production pipeline

This is the coordination layer over the existing Music Foundry components:
MIDI generation, SoulX score-conditioned singing, FluidSynth instrument rendering,
and FFmpeg mix/master. It does not replace the existing voice lab or invent
model weights. It never downloads models or calls a hosted music provider.

## Preflight (safe, no rendering)

```bash
python3 music-foundry/song_pipeline.py \
  --project music-foundry/projects/fine-china \
  --output music-foundry/output/fine-china
```

## Audition the draft chorus melody

The project includes a word-level chorus composition draft and a dependency-free MIDI guide renderer. This creates an immediate-playback melody guide with separate lead and gang-response tracks. It is a composition preview only; it does not mark the vocal score reviewed or send it to SoulX.

```bash
python3 music-foundry/song_pipeline.py \
  --project music-foundry/projects/fine-china \
  --output music-foundry/output/fine-china \
  --execute-vocal-guide
```

Use `--preserve-timeline` with `vocal_score_midi.py` when importing the guide into a full-song DAW session and retaining its original bar-33 start position.

## Generate the editable MIDI

```bash
python3 music-foundry/song_pipeline.py \
  --project music-foundry/projects/fine-china \
  --output music-foundry/output/fine-china \
  --execute-midi
```

## Render all four instruments locally

Requires FluidSynth, FFmpeg and an operator-supplied licensed SoundFont (.sf2):

```bash
python3 music-foundry/song_pipeline.py \
  --project music-foundry/projects/fine-china \
  --output music-foundry/output/fine-china \
  --soundfont /path/to/licensed-soundfont.sf2 \
  --execute-midi --execute-instrumental
```

## Generate vocals and master the complete song

Requires the existing official SoulX-Singer checkout and checkpoint, plus
`vocal_score.json`, `vocal-reference.wav` and
`vocal-reference.metadata.json` inside the project folder. The score must
have human-reviewed note/phoneme alignment and a locked tempo. These gates
prevent fabricated lyrics, notes or pronunciation from being sent to a singer.

```bash
python3 music-foundry/song_pipeline.py \
  --project music-foundry/projects/fine-china \
  --output music-foundry/output/fine-china \
  --soulx-root /path/to/SoulX-Singer \
  --soundfont /path/to/licensed-soundfont.sf2 \
  --execute-midi --execute-vocals --execute-instrumental --execute-master \
  --device cpu
```

The model is not downloaded by this command. The reference singing recording
must be rights-cleared and authorized. Use `--device cuda` only when the
existing local environment has a compatible GPU runtime. You can also pass
`--vocal-wav` to master an already-rendered vocal take.

## Deliverables and truthful reporting

- MIDI: editable chords, bass, lead and drums.
- Instrumental: four 24-bit stems and a stereo instrumental WAV.
- Singing: actual SoulX-generated vocal WAV, never a TTS substitute.
- Master: 24-bit stereo WAV and 320 kbps MP3.
- Reports: stage-by-stage preflight, model/SoundFont hashes and FFmpeg loudness
  measurements (integrated loudness and true peak).

A generated master still needs a human listening pass before release. A green
MIDI test does not imply a finished song; the pipeline reports every blocked
stage rather than marking unfinished work complete.

## Fine China current state

Fine China has lyrics, creative brief, generation prompt, project metadata and a 120-bar MIDI arrangement. The approved hybrid vocal identity is stored as structured project data. A first 13-phrase chorus melody proposal now has 61 word units and 73 explicit pitched syllable events, with beat durations, MIDI pitches and ARPABET phones. A dependency-free MIDI guide renderer validates the syllable-to-word phoneme maps and creates separate lead/gang tracks for immediate audition.

The vocal score remains deliberately marked `composition_draft`; it is not user-approved note-by-note and cannot pass the SoulX export gate. The existing SoulX adapter and score exporter are integrated, but reference singer assets and the installed local model/runtime have not been verified here. The one-command runner reports those gates rather than pretending the song is rendered.
