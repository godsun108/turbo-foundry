#include "earth_studio/audio_engine.hpp"
#include <array>
#include <cmath>
#include <cstdlib>
#include <iostream>
namespace {
void require(bool ok, const char* message) {
  if (!ok) { std::cerr << "FAIL: " << message << '\n'; std::exit(1); }
}
float render_energy(earth_studio::OscillatorWaveform waveform) {
  earth_studio::AudioEngine engine;
  auto p = engine.instrument_parameters(); p.waveform = waveform;
  p.attack_seconds = 0.001F; p.decay_seconds = 0.001F; p.sustain_level = 1.0F;
  engine.set_instrument_parameters(p);
  std::array<float, 1024> out{};
  const std::array on{earth_studio::MidiEvent{0, earth_studio::MidiEventType::note_on, 0, 69, 1.0F}};
  engine.render(out.data(), 512, on);
  float energy = 0.0F;
  for (std::size_t i = 0; i < 1024; ++i) energy += std::abs(out[i]);
  return energy;
}
void silence_and_clock() {
  earth_studio::AudioEngine engine;
  std::array<float, 256> out{};
  engine.render(out.data(), 128);
  for (float x : out) require(x == 0.0F, "fresh engine renders silence");
  require(engine.stats().rendered_frames == 128, "render frame count");
}
void oscillator_shapes() {
  const float sine = render_energy(earth_studio::OscillatorWaveform::sine);
  const float saw = render_energy(earth_studio::OscillatorWaveform::saw);
  const float square = render_energy(earth_studio::OscillatorWaveform::square);
  const float triangle = render_energy(earth_studio::OscillatorWaveform::triangle);
  require(sine > 1.0F && saw > 1.0F && square > 1.0F && triangle > 1.0F, "all oscillator shapes render audible output");
  require(std::abs(sine - square) > 0.1F, "waveforms have distinct output");
}
void sample_offset_midi() {
  earth_studio::AudioEngine engine;
  std::array<float, 128> out{};
  const std::array events{earth_studio::MidiEvent{8, earth_studio::MidiEventType::note_on, 0, 69, 1.0F}};
  engine.render(out.data(), 64, events);
  for (std::size_t i = 0; i < 8; ++i)
    require(out[i*2] == 0.0F && out[i*2+1] == 0.0F, "event is sample-offset accurate");
  bool audible = false;
  for (std::size_t i = 9; i < 64; ++i) audible = audible || std::abs(out[i*2]) > 0.0001F;
  require(audible, "note becomes audible");
}
void envelope_filter_and_modulation() {
  earth_studio::AudioEngine engine;
  auto p = engine.instrument_parameters();
  p.attack_seconds = 0.001F; p.decay_seconds = 0.001F; p.sustain_level = 0.25F;
  p.release_seconds = 0.01F; p.filter_cutoff_hz = 700.0F;
  p.pitch_bend_semitones = 2.0F; p.vibrato_rate_hz = 6.0F; p.vibrato_depth_semitones = 0.4F;
  engine.set_instrument_parameters(p);
  std::array<float, 8192> out{};
  const std::array on{earth_studio::MidiEvent{0, earth_studio::MidiEventType::note_on, 0, 57, 0.8F}};
  engine.render(out.data(), 2048, on);
  bool audible = false;
  for (float x : out) audible = audible || std::abs(x) > 0.0001F;
  require(audible, "ADSR/filter/modulated voice renders");
  const std::array off{earth_studio::MidiEvent{0, earth_studio::MidiEventType::note_off, 0, 57, 0.0F}};
  engine.render(out.data(), 2048, off);
  engine.render(out.data(), 2048);
  engine.render(out.data(), 2048);
  require(engine.stats().active_voices == 0, "release completes and frees voice");
}
void transport_clock() {
  earth_studio::AudioEngine engine;
  engine.set_tempo(120.0); engine.start_transport();
  std::array<float, 4096> out{};
  engine.render(out.data(), 2048);
  require(engine.stats().transport_frames == 2048, "transport frame counter");
  require(engine.beat_position() > 0.08 && engine.beat_position() < 0.09, "tempo-derived beat position");
  engine.stop_transport(); engine.render(out.data(), 1024);
  require(engine.stats().transport_frames == 2048, "stopped transport holds position");
}
void voice_pool_and_block_limit() {
  earth_studio::AudioEngine engine;
  std::array<float, 4096> out{};
  std::array<earth_studio::MidiEvent, earth_studio::kMaxVoices + 1> chord{};
  for (std::size_t i = 0; i < chord.size(); ++i)
    chord[i] = {0, earth_studio::MidiEventType::note_on, 0, static_cast<std::uint8_t>(36+i), 0.5F};
  engine.render(out.data(), 8, chord);
  require(engine.stats().active_voices == earth_studio::kMaxVoices, "voice count is bounded");
  require(engine.stats().stolen_voices == 1, "voice stealing is observable");
  engine.render(out.data(), static_cast<std::uint32_t>(earth_studio::kMaxBlockFrames + 4));
  require(engine.stats().rendered_frames == 8 + earth_studio::kMaxBlockFrames, "oversized blocks clamp");
}
}
int main() {
  silence_and_clock(); oscillator_shapes(); sample_offset_midi(); envelope_filter_and_modulation();
  transport_clock(); voice_pool_and_block_limit();
  std::cout << "EARTH STUDIO instrument tests passed\n";
}
