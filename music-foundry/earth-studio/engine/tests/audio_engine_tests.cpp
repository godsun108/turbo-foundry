#include "earth_studio/audio_engine.hpp"
#include <array>
#include <cmath>
#include <cstdlib>
#include <iostream>
namespace {
void require(bool ok, const char* message) {
  if (!ok) { std::cerr << "FAIL: " << message << '\n'; std::exit(1); }
}
void silence_and_clock() {
  earth_studio::AudioEngine engine;
  std::array<float, 256> out{};
  engine.render(out.data(), 128);
  for (float x : out) require(x == 0.0F, "fresh engine renders silence");
  require(engine.stats().rendered_frames == 128, "render frame count");
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
void transport_clock() {
  earth_studio::AudioEngine engine;
  engine.set_tempo(120.0);
  engine.start_transport();
  std::array<float, 4096> out{};
  engine.render(out.data(), 2048);
  require(engine.stats().transport_frames == 2048, "transport frame counter");
  require(engine.beat_position() > 0.08 && engine.beat_position() < 0.09, "tempo-derived beat position");
  engine.stop_transport();
  engine.render(out.data(), 1024);
  require(engine.stats().transport_frames == 2048, "stopped transport holds position");
}
void voice_pool_and_release() {
  earth_studio::AudioEngine engine({48000.0, 0.8F, 0.001F, 0.01F});
  std::array<float, 4096> out{};
  const std::array on{earth_studio::MidiEvent{0, earth_studio::MidiEventType::note_on, 0, 60, 1.0F}};
  engine.render(out.data(), 64, on);
  require(engine.stats().active_voices == 1, "note-on allocates a voice");
  const std::array off{earth_studio::MidiEvent{0, earth_studio::MidiEventType::note_off, 0, 60, 0.0F}};
  engine.render(out.data(), 2048, off);\n  engine.render(out.data(), 2048);\n  engine.render(out.data(), 2048);
  require(engine.stats().active_voices == 0, "release returns voice to pool");
  std::array<earth_studio::MidiEvent, earth_studio::kMaxVoices + 1> chord{};
  for (std::size_t i = 0; i < chord.size(); ++i)
    chord[i] = {0, earth_studio::MidiEventType::note_on, 0, static_cast<std::uint8_t>(36+i), 0.5F};
  engine.render(out.data(), 8, chord);
  require(engine.stats().active_voices == earth_studio::kMaxVoices, "voice count is bounded");
  require(engine.stats().stolen_voices == 1, "voice stealing is observable");
}
void block_limit() {
  earth_studio::AudioEngine engine;
  std::array<float, (earth_studio::kMaxBlockFrames + 4) * 2> out{};
  engine.render(out.data(), static_cast<std::uint32_t>(earth_studio::kMaxBlockFrames + 4));
  require(engine.stats().rendered_frames == earth_studio::kMaxBlockFrames, "oversized blocks clamp");
}
}
int main() {
  silence_and_clock(); sample_offset_midi(); transport_clock(); voice_pool_and_release(); block_limit();
  std::cout << "EARTH STUDIO engine tests passed\n";
}
