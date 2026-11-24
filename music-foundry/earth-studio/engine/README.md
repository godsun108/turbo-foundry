# EARTH STUDIO Native Audio Engine V1

A dependency-free, portable C++20 DSP core. This is not yet a device driver, DAW host, plugin host, or finished standalone application.

## V1 capabilities
- Fixed 32-voice polyphonic sine instrument with MIDI note-on, note-off, and all-notes-off.
- Sample-offset event dispatch inside each render block.
- Preallocated voice storage and bounded render blocks (maximum 2048 frames).
- Interleaved stereo float output, master-gain clamp, smoothed attack/release envelope.
- Sample-clock transport with tempo and beat-position reporting.
- No allocation, mutex, file/network I/O, or exceptions in the render function.

## Build and test
    cmake -S music-foundry/earth-studio/engine -B build/earth-studio-engine
    cmake --build build/earth-studio-engine --config Release
    ctest --test-dir build/earth-studio-engine --output-on-failure

## Real-time boundary
Construct and configure the engine before starting the device, then pass caller-owned output memory and an already ordered event span. Do not call setters or inspect mutable engine state concurrently with rendering; V1 uses a single audio-thread ownership model. The caller must split device callbacks into blocks no larger than 2048 frames and keep events sorted by frame offset. Events outside the current block are not consumed.

This is a DSP core only. A platform adapter must still provide audio I/O, device lifecycle, MIDI input, thread handoff, and callback-size adaptation. No iOS Audio Unit, CoreAudio, WASAPI, ALSA, browser WASM, hardware controller, recording, effects rack, or plugin support is claimed yet.

## Next instrument steps
Add oscillator waveforms/wavetables, pitch bend and modulation, per-voice envelopes, filters, parameter automation, and a stable C ABI before platform adapters are attached.
