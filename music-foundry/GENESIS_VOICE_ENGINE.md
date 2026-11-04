# Genesis Voice Engine — local spoken synthesis adapter

Status: **adapter implemented; runtime/model not yet installed or verified**.

## What this adds

The new genesis_voice_adapter.py connects Music Foundry's provider-neutral vocal request contract to a local Piper CLI installation. It is a real audio-rendering integration point, not a scripted reply or browser speech playback.

- Spoken text only. Singing is deliberately rejected by this adapter.
- Requires a Piper executable and a local .onnx voice model supplied by the operator.
- Does not download models, contact a provider, require credentials, or call a remote endpoint.
- Uses an argument array with shell=False; text is sent on stdin.
- Dispatch is denied unless the caller explicitly passes authorized=True.
- Accepts 44.1 or 48 kHz output requests, normalizes mono Piper PCM to the requested channel count, and currently exports 16-bit PCM WAV.
- Refuses to overwrite an existing output unless overwrite=True is explicitly supplied.

## Example

~~~python
from vocal_render_contract import make_render_request
from genesis_voice_adapter import render_spoken

engine = {
    "schema": "turbo.music-foundry.local-voice-engine.v1",
    "engine": "piper-cli",
    "execution": "local",
    "modes": ["spoken"],
    "executable": "/path/to/piper",
    "model_path": "/path/to/voice.onnx",
    "timeout_seconds": 60,
    "credential_handling": "none",
}

request = make_render_request(
    project_id="somebodys-gotta-do-it",
    source_ref="projects/somebodys-gotta-do-it/cue-sheet.md",
    mode="spoken",
    layers=["dry_lead"],
    sample_rate=48000,
    bit_depth=16,
    channels=1,
)

result = render_spoken(
    text="Somebody's gotta do it.",
    request=request,
    descriptor=engine,
    output_path="/path/to/output/spoken-lead.wav",
    authorized=True,
)
~~~

The output directory must already exist. Use a voice model whose license and usage terms permit the intended project. This adapter does not clone a person's voice and does not establish rights to any model or voice.

## Verification boundary

The automated tests use a deterministic fake Piper process that writes a small WAV fixture. They verify dispatch authorization, local-only configuration, rejection of sung mode, model-path checks, no-overwrite behavior, and WAV normalization. They do **not** prove that Piper is installed, that a particular voice model works, or that the resulting voice is suitable for commercial music.

Next gates:
1. Install or locate a trusted local Piper executable and voice model without bypassing the $0 approval boundary.
2. Run a real spoken test using original project text and inspect the WAV.
3. Compare voice quality, pronunciation, timing, and CPU performance.
4. Integrate rendered takes with the existing vocal timeline and effects chain.
5. Evaluate a separate singing-synthesis engine; do not route sung requests through Piper.


## Browser-first neural voice studio (Kokoro)

The track project also includes a browser studio at projects/somebodys-gotta-do-it/genesis-voice-studio.html. It uses Google's MediaPipe Tasks Audio Text-to-Speech web API with a Kokoro-compatible LiteRT-LM model bundle.

- The operator selects a local .litertlm file; the page does not automatically download model weights.
- Synthesis runs in a Web Worker, with GPU/WebGPU or CPU selection.
- The worker enumerates available voices and streams synthesis chunks; the studio accumulates the resulting audio and exports 24 kHz mono 16-bit PCM WAV.
- The WAV can be imported into the existing vocal timeline for arrangement, effects, and stem export.
- The MediaPipe JavaScript package and WASM runtime are currently loaded from jsDelivr at pinned version 1.2.2. This is a runtime CDN dependency; this first browser prototype is not fully offline until those assets are vendored.
- The Kokoro GPU bundle documented by Google is approximately 295 MB and is Apache 2.0 licensed. The operator must obtain the model from the linked official model source and review the applicable license before use.

The browser studio is an integration prototype, not yet a verified iPhone/Safari runtime. WebGPU support, CPU fallback, peak memory, audio quality, WAV export, and local-file loading require real-device testing. It does not sing, clone voices, or upload the selected model, text, or generated audio to a project server.

Reference implementation documentation:
- MediaPipe web TTS: https://developers.google.com/edge/mediapipe/solutions/audio/text_to_speech/web_js
- MediaPipe model overview and model sizes/licenses: https://developers.google.com/edge/mediapipe/solutions/audio/text_to_speech
- Kokoro model bundles: https://huggingface.co/litert-community/Kokoro-82M

Piper remains a local command-line fallback for desktop environments with an installed Piper binary and separately supplied ONNX voice model. The browser Kokoro path is the preferred quality and iPhone-oriented candidate.
