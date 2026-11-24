# EARTH STUDIO Native Instrument Engine V2

Portable dependency-free C++20 DSP core, still a DSP library rather than a device driver, DAW host, plugin host, or standalone product.

## Instrument features
- Four oscillator shapes: sine, saw, square, triangle.
- 32-voice polyphony and sample-offset MIDI note-on/note-off/all-notes-off.
- Per-voice ADSR amplitude envelope.
- Resonance-free one-pole low-pass filter with adjustable cutoff.
- Global pitch bend and LFO vibrato controls.
- Smoothed parameters, bounded gain, stereo float output and sample-clock transport.
- Fixed voice storage and bounded render blocks (2048 frames maximum); render performs no heap allocation, locking, I/O, or exception throwing.

## Build and test
    cmake -S music-foundry/earth-studio/engine -B build/earth-studio-engine
    cmake --build build/earth-studio-engine --config Release
    ctest --test-dir build/earth-studio-engine --output-on-failure

Configure parameters before rendering and do not mutate/read engine state concurrently with the audio thread. Callers must supply sorted events whose frame offsets are inside the current block. Platform audio I/O, MIDI hardware, browser WASM, iOS Audio Unit/CoreAudio, recording, effects, plugin support and standalone device integration remain future adapter work.

## DSP note
The first filter is intentionally a stable one-pole low-pass without resonance. Oscillator shapes are naive band-limitedness-wise (no anti-aliasing); V2 establishes the instrument parameter contract, not a final high-quality synth. Next priorities: band-limited wavetable/PolyBLEP oscillators, resonant filter, modulation matrix, parameter automation and C ABI.

## Shared C ABI and WebAssembly target

`include/earth_studio/c_api.h` is the stable boundary for browser/WASM and future platform audio hosts. It exposes opaque engine ownership, bounded stereo rendering, MIDI event batches and instrument parameters without exposing C++ object layout.

- Create/destroy and parameter changes are control-thread operations.
- Render accepts up to 2048 frames and at most 64 sorted sample-offset events per call; invalid blocks/events are rejected.
- Output is interleaved stereo float32.
- Regular CMake builds include a C ABI test executable.
- With Emscripten installed: `emcmake cmake -S music-foundry/earth-studio/engine -B build/earth-studio-wasm`, then `cmake --build build/earth-studio-wasm --target earth_studio_engine_wasm`.

The WASM target is a build artifact, not a committed binary. The browser still uses its Web Audio prototype until an AudioWorklet adapter is wired and verified against the generated module. Never create/destroy the engine or mutate its parameters inside a real-time render callback.
