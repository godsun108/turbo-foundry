# Singing Synthesis Engine Evaluation

Status: research checkpoint only. No model weights downloaded, no new dependencies installed, and no external service or deployment authorized.

## Recommendation

Use a two-lane architecture:

1. **Spoken lead now:** continue with the browser-local MediaPipe/Kokoro path. It is an actual TTS model family, not a singing renderer.
2. **Sung notes and hooks:** evaluate OpenUtau + the OpenVPI-maintained DiffSinger implementation as the first open-source singing-synthesis candidate. Treat it as a desktop/offline render worker that exports WAV into Music Foundry, not as an iPhone-native runtime.

## Candidate evidence

### OpenUtau
- MIT-licensed open-source singing editor.
- Score/MIDI editing, lyric phonemizers, vibrato/expression editing, pre-rendering, and pluggable resamplers.
- Runs on Windows, macOS, and Linux; no iOS/iPhone runtime is documented.
- Supports ENUNU AI singers and can act as an editing/hosting layer for supported AI singer workflows.
- Not a DAW replacement; rendered vocals should return to Music Foundry for arrangement and mixing.

Source: https://github.com/openutau/OpenUtau

### DiffSinger / OpenVPI DiffSinger
- Purpose-built singing voice synthesis conditioned on lyrics plus pitch/F0 or MIDI.
- The OpenVPI-maintained fork describes expressive controls including pitch, energy, and breathiness, improved 44.1 kHz output, and deployment compatibility through OpenUtau.
- Apache-2.0 code license is stated by the OpenVPI fork. Every pretrained checkpoint, voice bank, and dataset still needs its own license and consent review.
- Python/PyTorch/CUDA-oriented setup makes it a desktop/GPU candidate, not a lightweight iPhone/browser candidate.

Sources:
- https://github.com/openvpi/DiffSinger
- https://github.com/MoonInTheRiver/DiffSinger

## Integration design

- Music Foundry remains canonical for cue sheet, MIDI, lyric timing, takes, stems, and final mix.
- A singing adapter should accept a validated score package: lyric syllables, note pitches, note durations, tempo map, voice/model identifier, and explicit authorization.
- Render to WAV offline, validate sample rate/channels/bit depth, then import as a non-destructive take into the vocal timeline.
- Keep spoken and sung render contracts separate.
- No voice cloning or training on a person's voice without explicit consent and documented rights.
- Do not bundle model weights in Git or automatically download them.

## Next proof gates

1. Inspect OpenVPI DiffSinger model/checkpoint availability and per-asset licenses.
2. Determine whether an existing supported voice can sing original English lyrics acceptably.
3. Build a local adapter only after the model and voice asset pass license, reproducibility, and hardware checks.
4. Generate a short original test phrase from MIDI + lyrics; inspect timing, consonants, pitch stability, and WAV quality.
5. Import the take into the existing vocal timeline and verify alignment.

## iPhone-first decision

Do not force a heavy diffusion singing model into iPhone Safari. Keep the iPhone as the lyric/score editor, controller, and review surface; let a user-owned local desktop/GPU renderer produce the WAV until a genuinely supported mobile singing runtime is proven.


## Asset and licensing audit — 2026-11-04

### Runtime and workflow findings
- OpenVPI DiffSinger's current Getting Started guide requires Python 3.10+, PyTorch >=2.4.0 (recommended), and the repository requirements. Inference is a two-stage path: variance-model inference and acoustic-model inference, with an ONNX export path for deployment.
- The documented production workflow recommends OpenUtau for DiffSinger and says OpenUtau can export DS score files. DiffSinger's DS format carries phoneme sequences, phoneme durations, music scores, and curve parameters.
- The acoustic model produces a mel-spectrogram; a compatible vocoder is required to reconstruct the final waveform. This means a model checkpoint alone is not a complete voice-rendering asset.
- The official OpenUtau support page documents DiffSinger support on Windows and macOS (macOS 11+), with CPU rendering by default and CoreML/DirectML options on supported setups. This reinforces the desktop-render-worker design.

### Licensing gate — do not treat the current community vocoder as cleared for commercial release
- OpenVPI DiffSinger source code declares Apache-2.0. That license applies to the code repository, not automatically to model weights or training datasets.
- The OpenVPI Community Vocoders release page explicitly states that its pretrained vocoder weights are CC BY-NC-SA 4.0. The 2025 PC-NSF-HiFiGAN release is 44.1 kHz and pitch-shift capable, but carries that same non-commercial/share-alike license notice.
- Therefore, this vocoder is **not approved for a commercial-use production pipeline** on the evidence reviewed. Do not download, integrate, or use it for a release-bound track unless a separate applicable permission/license is confirmed.
- A usable DiffSinger voice also needs a compatible acoustic/variance checkpoint and any supporting assets. The public docs reviewed here do not establish a specific English voice checkpoint with terms suitable for this project. Treat voice checkpoint availability and rights as unresolved, not assumed.
- Review each voice model, vocoder, phoneme dictionary, and training dataset independently. The code license is not a substitute for those checks.

### Decision update
DiffSinger remains a technically promising research candidate, but **the default public vocoder asset is a licensing blocker** for any commercial-release path. Do not build the production adapter around that specific pretrained vocoder. The next candidate search should prioritize a complete English singing voice + vocoder package whose model-weight and dataset terms explicitly permit the intended use, or a route to train a fully rights-cleared voice from properly licensed/consented material.

### Track-specific implications
- The current song is spoken-led, so the Kokoro spoken path remains the nearer-term route to hearing a complete vocal arrangement.
- The current cue sheet and timing grid remain authoritative. Do not synthesize the entire track as one undifferentiated passage; render separate lead, gang hook, ad-lib/chop, and whisper groups as distinct takes.
- The first hook starts at zero-based bar 16 in the canonical timing grid. At 127 BPM in 4/4, each bar is approximately 1.8898 seconds; bar 16 begins at approximately 30.236 seconds. Keep this as an editorial grid until performance timing is locked.

### Sources reviewed
- OpenVPI DiffSinger Getting Started: https://github.com/openvpi/DiffSinger/blob/main/docs/GettingStarted.md
- OpenVPI DiffSinger Best Practices: https://github.com/openvpi/DiffSinger/blob/main/docs/BestPractices.md
- OpenUtau DiffSinger support: https://www.openutau.com/DiffSinger-support/
- OpenVPI Community Vocoders releases and license notice: https://github.com/openvpi/vocoders/releases
- Community vocoder license overview: https://openvpi.github.io/vocoders/

No model weights were downloaded, no dependencies were installed, and no runtime synthesis was performed during this audit.


## SoulX-Singer candidate audit — 2026-11-04

### Why it is now the leading singing candidate
- Official project: https://github.com/Soul-AILab/SoulX-Singer
- Official model card: https://huggingface.co/Soul-AILab/SoulX-Singer
- The official README describes zero-shot singing voice synthesis (SVS) with either melody/F0 conditioning or score/MIDI conditioning, plus a separate singing voice conversion (SVC) model.
- English, Mandarin, and Cantonese are listed as supported languages. The project reports 42,000+ hours of aligned multilingual vocal training data.
- The official repository README explicitly says its Apache-2.0 license applies to code and model weights. The official Hugging Face model card also labels the model Apache-2.0. The official preprocessing model repository is likewise labeled Apache-2.0. This is a materially cleaner starting point than the DiffSinger community vocoder license found in the previous audit.
- Main SVS checkpoint model.pt is 2.82 GB (official Hugging Face file metadata). The full model repository is listed at approximately 5.61 GB because it also includes SVC assets and other files. Do not download the SVC checkpoint for this track unless SVC is specifically needed.

### Important practical constraints
- Official example inference invokes --device cuda and --fp16; the published reference path is NVIDIA CUDA/GPU, not an iPhone or browser runtime.
- The requirements include PyTorch 2.2.0, NeMo 2.6.1, SageAttention, audio preprocessing, and other substantial packages. This is a large desktop environment, not a lightweight install.
- The synthesis input is not simply raw lyrics plus MIDI. It requires a prompt singing WAV, prompt metadata, target metadata, and a phoneme set. The project recommends manually correcting metadata alignment in its MIDI editor because automatic lyric/note alignment can be imperfect.
- The official WebUI lists a reference prompt WAV and separate prompt/target metadata, and provides English example prompt/target assets. That makes an English proof-of-concept plausible, but it still needs a rights-cleared reference singing recording and validated score/lyric metadata.
- The official model card says code and weights are Apache-2.0; keep separate rights records for any prompt/reference singer recording, generated performance, lyrics, and other user-supplied material. The model's zero-shot timbre transfer must only use a voice recording the operator is authorized to use.
- Model files are PyTorch .pt checkpoints. Download and load only from the official upstream project/model repository after explicit user approval; never accept untrusted pickle checkpoints.

### Apple Silicon investigation (not yet adopted)
- A community MLX conversion is published at https://huggingface.co/mlx-community/SoulX-Singer and documents a 2.6 GB BF16 model variant.
- Its own model card explicitly says this is not yet a pure end-to-end MLX audio runtime: full audio generation still uses the official PyTorch model structure through a separate bridge project. It is therefore not evidence of native iPhone support and is not yet an approved simplification of the official CUDA workflow.
- Do not assume that Apple Silicon conversion means iOS/iPhone compatibility. No iOS runtime has been verified.

### Proposed proof gate before any integration
1. Confirm the user's available local render hardware and available disk/RAM/VRAM; do not install anything yet.
2. If a compatible NVIDIA desktop/GPU is available, request explicit approval before downloading the 2.82 GB official SVS checkpoint and only the preprocessing assets required for the selected manual/automatic workflow.
3. Prepare one short original English test phrase with a manually checked target score/lyric alignment.
4. Use only an operator-owned or explicitly licensed reference singing sample; no third-party voice cloning by default.
5. Render one short WAV, inspect pitch, timing, pronunciation, intelligibility, artifacts, sample rate, and stem import into Music Foundry.
6. Only after this proof succeeds should we design a production adapter. Preserve the existing Music Foundry project as canonical and keep model assets out of Git.

### Current decision
SoulX-Singer is the leading research candidate for sung hooks because the official project documents MIDI-conditioned English SVS and Apache-2.0 code/weights. It is not yet a production-approved or locally verified engine: it requires a large model, a singing reference prompt, aligned metadata, and a GPU-oriented runtime. The immediate song path remains spoken-vocal synthesis through Kokoro; SoulX-Singer is the separate sung-hook lane to validate later.

No SoulX-Singer weights or dependencies were downloaded or installed, and no inference was run during this audit.

### Sources reviewed
- Official inference code and license: https://github.com/Soul-AILab/SoulX-Singer
- Official model card and checkpoint metadata: https://huggingface.co/Soul-AILab/SoulX-Singer
- Official inference script: https://github.com/Soul-AILab/SoulX-Singer/blob/main/example/infer.sh
- Official WebUI input and English example configuration: https://github.com/Soul-AILab/SoulX-Singer/blob/main/webui.py
- Official preprocessing model card: https://huggingface.co/Soul-AILab/SoulX-Singer-Preprocess
- Community Apple MLX conversion caveats: https://huggingface.co/mlx-community/SoulX-Singer


### Music Foundry format gap discovered during integration review
- The canonical track timing file currently supplies section boundaries, bar/beat landmarks, layer names, and lyric authority. It does not yet supply per-syllable phoneme sequences, per-phoneme durations, note pitches/types, or an F0 contour.
- SoulX-Singer's official English metadata examples contain per-segment language, time range in milliseconds, duration sequence, text, phoneme sequence, note_pitch sequence, note_type sequence, and F0 sequence. The prompt metadata also references an actual prompt singing recording.
- Therefore the current timing grid cannot be passed directly to SoulX-Singer. A future adapter must consume a proper vocal score/phoneme-alignment artifact and generate the model-specific metadata; it must not guess note pitches or syllable durations from section markers.
- Recommended canonical extension: keep the existing cue sheet and bar/beat timing authoritative, then add a separate, versioned vocal-score artifact with syllable-to-note alignment, phoneme mapping, note durations, and render-layer IDs. Generate SoulX metadata as a derived export, never as the source of truth.
- For a first proof, use one short English hook phrase rather than attempting all 56 bars. The existing chorus starts at zero-based bar 16, but its note-level vocal score still needs authoring and review.
