# Genesis Music Capability Plan

Status: architecture and implementation plan; no model training, model promotion, or external provider dispatch is authorized by this document.

## Mission

Make Genesis capable of helping create original, high-quality music while preserving the existing Turbo Foundry / Music Foundry architecture. The first proving project is **Somebody's Gotta Do It**. The goal is a complete, compelling, vocal-led house / wonky bass-house track using the user's original lyric draft, not another MIDI-only technical demo.

## Source of truth and creative constraints

- Canonical lyrics: `music-foundry/projects/somebodys-gotta-do-it/cue-sheet.md`.
- Timing landmarks: `music-foundry/projects/somebodys-gotta-do-it/vocal_timing.json`.
- Performance plan: `music-foundry/projects/somebodys-gotta-do-it/vocal-take-plan.md`.
- Keep the supplied lyric wording intact. Changes require explicit human approval.
- Primary lead is spoken, mischievous, conversational, and confidently reckless.
- Performance: whispered intro; fast conversational verses; rising/overlapping pre; gang-shouted/chopped chorus; half-time robotic word-stack bridge; maximum layered final chorus; exposed spoken outro tag.
- Musical direction: club / warehouse house with wonky bass and dubstep influence; strong groove, memorable hook, purposeful contrast, richer sound design, and a mix that supports vocal intelligibility.
- Tempo 127 BPM is provisional, not a creative law.

## Verified current implementation

### Music Foundry

- `arrange_project.py` and `warehouse_rave_v3.py` generate MIDI arrangements.
- `render_instrumental.py` is a dependency-free procedural preview synthesizer. Its own manifest explicitly says vocals are not rendered. It is not a production sampler or commercial-quality instrument engine.
- `assemble_spoken_takes.py` assembles consented, recorded PCM WAV takes into vocal layers and a mix. It is an editor/assembler, not a speech or singing synthesizer.
- `vocal_render_contract.py` defines a provider-neutral request/renderer contract; a contract is not a working renderer.
- The vocal cue sheet, take plan, timing map, recording booth, and vocal timeline provide an existing project workflow. Preserve these contracts.
- Existing DSP includes gain, drive, low-pass, delay, stutter, phrase edits, and automation. It can be extended deliberately; avoid a parallel DAW or audio engine.

### Genesis Voice Studio

- `genesis-voice-studio.js` and `genesis-voice-worker.js` implement a browser-local spoken TTS prototype.
- The worker uses MediaPipe Tasks Audio TextToSpeech and expects a user-selected `.litertlm` model bundle.
- It synthesizes text chunks and exports a spoken WAV. It is not singing synthesis, does not create a sung melody, and does not prove that a singing model is installed.
- The browser worker imports its runtime from a CDN. Therefore this prototype is not yet a fully offline/private deployment, even though the selected model file is processed locally.
- Do not relabel TTS output as singing or as a real human vocal performance.

### Singing model boundary

### Singing model candidate: SoulX-Singer (research candidate, not integrated)

Repository and model-card inspection confirms that SoulX-Singer is more than an empty adapter placeholder:

- Upstream publishes inference code and pretrained SVS weights under Apache-2.0; review the license for every separately downloaded preprocessing asset before use.
- The model card describes zero-shot singing voice synthesis with both F0/melody conditioning and score/MIDI-note conditioning. It supports English, Mandarin, and Cantonese.
- The upstream example requires a prompt vocal WAV, prompt metadata, target lyric/note metadata, and a phone-set file. The README warns that automatic lyric/note alignment can be imperfect and recommends manual correction in its MIDI editor.
- The published example invokes inference with `--device cuda` and `--fp16`; its documented environment uses Python 3.10 and a pinned PyTorch / torchaudio stack. Do not assume iPhone, CPU-only, or offline portability until tested.
- The repository's README describes a 42,000+ hour aligned training corpus and zero-shot synthesis, so the first experiment should be inference with released weights, not training a new singer model.
- The current Music Foundry adapter is not yet wired to this inference CLI; no weights have been downloaded and no local inference has been run.

**Recommended role:** test SoulX-Singer for optional pitched hook/chant textures or a sung layer, not as a replacement for the track's predominantly spoken lead. First prove a short English phrase with manually checked score/lyric alignment, then measure quality, latency, VRAM, and deployment constraints. Keep spoken lead recording/TTS on its separate path.

Sources inspected: `https://github.com/Soul-AILab/SoulX-Singer` and `https://huggingface.co/Soul-AILab/SoulX-Singer`.

- The SoulX-Singer integration is an adapter/prototype boundary only. Model weights and an end-to-end singing inference run have not been verified in this project.
- No training run, fine-tune, validated music dataset, model registry, or quality-based promotion pipeline is established by the evidence inspected for this plan.
- Do not claim Genesis can currently sing or train a singing model.

## Target architecture

Keep Music Foundry as the canonical project, arrangement, vocal timeline, stems, mix, and provenance workflow. Genesis is the supervised creative director / agent that can propose, generate, compare, and evaluate assets through explicit contracts.

1. **Creative planning:** lyrics, section map, reference attributes described in words, BPM/key options, energy curve, hook and arrangement proposals.
2. **Score and arrangement:** MIDI/score generation with deterministic seeds, section-aware composition, and editable human-readable manifests.
3. **Instrument rendering:** a replaceable instrument backend with licensed sample/instrument assets, expressive articulations, synthesis, and deterministic offline rendering. Preserve MIDI and stem contracts.
4. **Vocal rendering:** separate spoken and sung renderer capabilities. A renderer must declare its mode and return validated audio plus alignment/metadata. Spoken TTS must never satisfy a sung capability check.
5. **Vocal production:** multi-take selection, lyric/phoneme alignment, timing edits, pitch/time processing where appropriate, gang layers, ad-libs, chops, effects, and non-destructive source preservation.
6. **Mix and master:** stem/bus processing, headroom, loudness and true-peak measurement, tonal/dynamic checks, stereo checks, and human audition. A normalized preview is not a master.
7. **Delivery:** mix, stems, MIDI/score, lyrics/cue sheet, manifest, model/provider provenance, asset licenses, and test/evaluation report.

## Phased implementation

### Phase 0 — protect the song source

- Treat the existing cue sheet as immutable source material unless the user explicitly approves lyric edits.
- Keep the existing timing and performance documents aligned to that source.
- Add tests that verify required sections and protect the cue sheet from accidental rewriting.
- Build a lyric-to-performance event representation that references exact lyric lines rather than copying or paraphrasing them.

**Acceptance:** all original sections and lyric lines remain present; every vocal event points to a source line; no lyric rewrite is introduced by automation.

### Phase 1 — deliver a real vocal demo

- Use the existing spoken renderer only if a compatible model bundle is supplied and its actual output is auditioned. Otherwise record a human lead through the existing recording booth.
- Record or render separate dry lead, gang vocals, ad-libs, whisper doubles, and chops.
- Align vocal events to the existing 56-bar timing map; leave performer swing and manual editing possible.
- Arrange the instrumental around the vocal: create space under lines, call-and-response bass gaps, transitions, fills, breakdown, half-time bridge, and final-drop lift.
- Produce separate vocal and instrument stems and a first stereo mix.
- Do not publish or call it finished until the user auditions it.

**Acceptance:** a playable complete song contains the original lyrics as audible vocals; all requested vocal layers are separately inspectable; no placeholder tone or silent vocal track is accepted.

### Phase 2 — improve instrument quality

- Benchmark the current procedural renderer against the desired musical brief; document its limitations.
- Evaluate compatible, locally runnable synthesis / sampler / soundfont backends and their licenses before selecting one.
- Keep a backend-neutral MIDI/score-to-stems interface so Music Foundry does not become locked to one renderer.
- Add expressive drum kits, bass instruments, chord/synth layers, risers, impacts, transitions, and sidechain/pumping behavior where appropriate.
- Extend existing DSP and automation in a non-destructive way.
- Use reference listening and blind A/B comparisons; technical tests alone do not establish musical quality.

**Acceptance:** rendered stems have convincing timbre, dynamics, stereo depth, transitions, and groove; the user prefers the result in a direct A/B audition.

### Phase 3 — validated singing capability

- Inventory candidate singing models and their actual licenses, supported languages, voice/identity permissions, hardware requirements, offline support, and inference interfaces.
- Start with inference using an existing pretrained model; do not train from scratch as the first move.
- Build a singing-renderer adapter that accepts lyric text plus explicit melody/score, timing, language, and permitted voice selection.
- Validate output WAV metadata, duration, alignment, intelligibility, pitch/melody adherence, and provenance.
- Test a short, user-approved section before attempting a full song.
- Fine-tuning is a separate later decision requiring rights-cleared voice/data, documented consent, a reproducible dataset, compute budget, and evaluation set.

**Acceptance:** a short sung passage is generated by a real singing model, matches the supplied melody and words to an agreed threshold, and is audibly reviewed. This is not satisfied by speech TTS.

### Phase 4 — Genesis-assisted music learning and evaluation

- Give Genesis structured tools to propose compositions, inspect MIDI/audio metrics, run bounded experiments, and compare versions.
- Create a rights-cleared dataset registry with source, license, consent, permitted uses, hashes, splits, and deletion/retention policy.
- Build evaluation sets for rhythm, pitch, lyric intelligibility, structure, clipping, loudness, stereo compatibility, and human preference.
- Begin with retrieval, prompting, adapters, or fine-tuning of existing models where justified; reserve training a foundation model from scratch for a later evidence-based decision.
- Record every experiment: model/version, dataset version, configuration, seed, compute, outputs, metrics, and reviewer decision.
- Keep training and deployment separate. A model may propose its own improvement experiment, but it cannot approve its own dataset, promote itself, alter its authority policy, or deploy itself.

**Acceptance:** reproducible experiment reports, held-out evaluation, rights checks, rollback path, and explicit human approval before model promotion.

## AEGIS-Q authority and safety requirements

- Genesis may propose and prepare training jobs; a separate authorized controller must approve consequential execution.
- No model may modify its own authorization policy or grant itself permissions.
- Dataset ingestion, external provider calls, GPU/cloud spend, model promotion, publishing, and public release require explicit authorization.
- Default to local/offline processing when practical. Clearly disclose any CDN, external model download, hosted inference, telemetry, or network dependency.
- Do not train on copyrighted recordings, lyrics, or identifiable voices without documented rights and consent for the intended use.
- Preserve original user assets and dry stems. All generated assets are versioned and non-destructive.

## Immediate next engineering tasks

1. Wire the generated source-linked lyric event manifest into the vocal timeline / recording workflow while keeping cue-sheet.md canonical.
2. Build a local SoulX-Singer inference spike in an isolated, reproducible environment; verify weights, preprocessing assets, GPU requirements, alignment, and English phrase quality before integrating it.
3. Add an end-to-end spoken-vocal smoke test using a supplied compatible local model or a recorded WAV fixture. The test must not pretend that the renderer has generated a sung take.
4. Add an audio audition checklist and objective render checks to the Music Foundry workflow.
5. Benchmark a licensed instrument backend and capture a user-auditioned vocal/instrument mix before choosing any fine-tuning or training path.

## Non-goals

- Do not replace the existing Music Foundry architecture.
- Do not create a second DAW, audio service, or duplicate renderer without an explicit architecture decision.
- Do not merge or publish a new song version solely because CI passes.
- Do not call a MIDI sketch, oscillator preview, or spoken TTS output a finished song or sung vocal.
