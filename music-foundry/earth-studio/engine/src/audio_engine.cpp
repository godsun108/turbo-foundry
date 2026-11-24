#include "earth_studio/audio_engine.hpp"
#include <algorithm>
#include <cmath>
namespace earth_studio {
namespace {
constexpr double kTwoPi = 6.283185307179586476925286766559;
constexpr double kA4Hz = 440.0;
constexpr float kSilence = 0.00001F;
double midi_frequency(std::uint8_t note) noexcept {
  return kA4Hz * std::pow(2.0, (static_cast<double>(note) - 69.0) / 12.0);
}
}
float AudioEngine::clamp_gain(float value) noexcept {
  if (!std::isfinite(value)) return 0.0F;
  return std::clamp(value, 0.0F, 2.0F);
}
AudioEngine::AudioEngine(EngineConfig config) noexcept : config_(config) {
  if (!std::isfinite(config_.sample_rate) || config_.sample_rate < 8000.0 ||
      config_.sample_rate > 384000.0) config_.sample_rate = 48000.0;
  master_gain_ = clamp_gain(config_.master_gain);
  const double attack = std::clamp(static_cast<double>(config_.attack_seconds), 0.0001, 10.0);
  const double release = std::clamp(static_cast<double>(config_.release_seconds), 0.001, 30.0);
  attack_coefficient_ = 1.0 - std::exp(-1.0 / (attack * config_.sample_rate));
  release_coefficient_ = 1.0 - std::exp(-1.0 / (release * config_.sample_rate));
}
void AudioEngine::set_master_gain(float gain) noexcept { master_gain_ = clamp_gain(gain); }
void AudioEngine::set_tempo(double bpm) noexcept {
  if (std::isfinite(bpm)) tempo_bpm_ = std::clamp(bpm, 20.0, 300.0);
}
void AudioEngine::start_transport() noexcept { transport_running_ = true; }
void AudioEngine::stop_transport() noexcept { transport_running_ = false; }
void AudioEngine::reset_transport() noexcept { transport_frames_ = 0; }
double AudioEngine::beat_position() const noexcept {
  return static_cast<double>(transport_frames_) * tempo_bpm_ / (60.0 * config_.sample_rate);
}
void AudioEngine::note_on(const MidiEvent& event) noexcept {
  if (event.channel > 15 || event.note > 127 || !std::isfinite(event.velocity)) return;
  const float velocity = std::clamp(event.velocity, 0.0F, 1.0F);
  if (velocity <= 0.0F) { note_off(event); return; }
  Voice* selected = nullptr;
  for (auto& voice : voices_) if (!voice.active) { selected = &voice; break; }
  if (selected == nullptr) {
    selected = &voices_[0];
    for (auto& voice : voices_) if (voice.envelope < selected->envelope) selected = &voice;
    ++stolen_voices_;
  }
  selected->phase = 0.0;
  selected->phase_increment = kTwoPi * midi_frequency(event.note) / config_.sample_rate;
  selected->envelope = 0.0F;
  selected->velocity = velocity;
  selected->channel = event.channel;
  selected->note = event.note;
  selected->active = true;
  selected->releasing = false;
}
void AudioEngine::note_off(const MidiEvent& event) noexcept {
  for (auto& voice : voices_)
    if (voice.active && voice.channel == event.channel && voice.note == event.note)
      voice.releasing = true;
}
void AudioEngine::all_notes_off(std::uint8_t channel) noexcept {
  for (auto& voice : voices_)
    if (voice.active && (channel == 0xffU || voice.channel == channel)) voice.releasing = true;
}
void AudioEngine::apply_event(const MidiEvent& event) noexcept {
  switch (event.type) {
    case MidiEventType::note_on: note_on(event); break;
    case MidiEventType::note_off: note_off(event); break;
    case MidiEventType::all_notes_off: all_notes_off(event.channel); break;
  }
}
void AudioEngine::render(float* output, std::uint32_t frames,
                         std::span<const MidiEvent> events) noexcept {
  if (output == nullptr) return;
  if (frames > kMaxBlockFrames) frames = static_cast<std::uint32_t>(kMaxBlockFrames);
  std::size_t event_index = 0;
  for (std::uint32_t frame = 0; frame < frames; ++frame) {
    while (event_index < events.size() && events[event_index].frame_offset == frame) {
      apply_event(events[event_index]);
      ++event_index;
    }
    float left = 0.0F, right = 0.0F;
    for (auto& voice : voices_) {
      if (!voice.active) continue;
      const double coefficient = voice.releasing ? release_coefficient_ : attack_coefficient_;
      const float target = voice.releasing ? 0.0F : voice.velocity;
      voice.envelope += static_cast<float>(coefficient) * (target - voice.envelope);
      if (voice.releasing && voice.envelope < kSilence) { voice = Voice{}; continue; }
      const float sample = static_cast<float>(std::sin(voice.phase)) *
                           voice.envelope * master_gain_ * 0.18F;
      voice.phase += voice.phase_increment;
      if (voice.phase >= kTwoPi) voice.phase -= kTwoPi;
      left += sample * 0.70710678F;
      right += sample * 0.70710678F;
    }
    output[static_cast<std::size_t>(frame) * 2] = std::clamp(left, -1.0F, 1.0F);
    output[static_cast<std::size_t>(frame) * 2 + 1] = std::clamp(right, -1.0F, 1.0F);
  }
  rendered_frames_ += frames;
  if (transport_running_) transport_frames_ += frames;
}
EngineStats AudioEngine::stats() const noexcept {
  std::uint32_t active = 0;
  for (const auto& voice : voices_) if (voice.active) ++active;
  return {rendered_frames_, transport_frames_, active, stolen_voices_};
}
}  // namespace earth_studio
