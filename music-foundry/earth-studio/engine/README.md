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
