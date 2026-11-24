# EARTH STUDIO Native Instrument Engine V2

Portable dependency-free C++20 DSP core. This remains a DSP library plus browser audio adapter, not a platform device driver, plugin host, or standalone hardware product.

## Instrument features
- Four oscillator shapes: sine, saw, square, triangle.
- 32-voice polyphony and sample-offset MIDI note-on/note-off/all-notes-off.
- Per-voice ADSR amplitude envelope.
- One-pole low-pass filter, pitch bend, vibrato, stereo float output and sample-clock transport.
- Fixed voice storage and bounded render blocks (2048 frames maximum); native render performs no heap allocation, locking, I/O, or exception throwing.

## Native build and tests
    cmake -S music-foundry/earth-studio/engine -B build/earth-studio-engine
    cmake --build build/earth-studio-engine --config Release
    ctest --test-dir build/earth-studio-engine --output-on-failure

## Browser WASM + AudioWorklet
The browser adapter attempts the native C++/WASM engine first. If the generated module or AudioWorklet is unavailable, it falls back to the Web Audio oscillator implementation.

Build with Emscripten:
    emcmake cmake -S music-foundry/earth-studio/engine -B build/earth-studio-wasm
    cmake --build build/earth-studio-wasm --target earth_studio_engine_wasm

Copy the generated files into music-foundry/earth-studio/:
    cp build/earth-studio-wasm/web/earth_studio_engine_wasm.mjs music-foundry/earth-studio/
    cp build/earth-studio-wasm/web/earth_studio_engine_wasm.wasm music-foundry/earth-studio/

Serve EARTH STUDIO from HTTPS or localhost so AudioWorklet and WebAssembly are available. The worklet imports the generated Emscripten ES module, creates the engine outside process(), preallocates bounded output/event/parameter memory, and renders interleaved stereo float32 blocks. It converts those samples into browser output channels without allocating buffers in the audio callback. MIDI note messages are bounded to 64 events per block; UI note events enter at the next render quantum.

The generated WASM files are build artifacts and are intentionally not committed. If either generated file is absent, unsupported, or fails initialization, the UI reports the reason and uses the Web Audio fallback. This target still requires a real Emscripten build and real-device/browser audio verification before describing the WASM path as tested.

## Threading contract
Create/destroy and parameter changes are processor-message operations. The AudioWorklet owns the engine and all calls to it; UI messages are serialized through its port. Native callers must provide sorted events whose frame offsets are inside the current block.

## Known DSP limitations
The current oscillator shapes are not anti-aliased; the filter is a one-pole low-pass without resonance. The next DSP quality milestone is band-limited oscillators, a resonant filter, parameter automation and a modulation matrix.
