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
double time_coefficient(float seconds, double sample_rate, float minimum) noexcept {
  const double safe = std::clamp(static_cast<double>(seconds), static_cast<double>(minimum), 30.0);
  return 1.0 - std::exp(-1.0 / (safe * sample_rate));
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
  parameters_.attack_seconds = config_.attack_seconds;
  parameters_.release_seconds = config_.release_seconds;
  set_instrument_parameters(parameters_);
}
void AudioEngine::set_master_gain(float gain) noexcept { master_gain_ = clamp_gain(gain); }
void AudioEngine::set_instrument_parameters(const InstrumentParameters& p) noexcept {
  parameters_.waveform = p.waveform;
  parameters_.attack_seconds = std::isfinite(p.attack_seconds) ? std::clamp(p.attack_seconds, 0.0001F, 10.0F) : 0.008F;
  parameters_.decay_seconds = std::isfinite(p.decay_seconds) ? std::clamp(p.decay_seconds, 0.001F, 30.0F) : 0.18F;
  parameters_.sustain_level = std::isfinite(p.sustain_level) ? std::clamp(p.sustain_level, 0.0F, 1.0F) : 0.7F;
  parameters_.release_seconds = std::isfinite(p.release_seconds) ? std::clamp(p.release_seconds, 0.001F, 30.0F) : 0.16F;
  parameters_.filter_cutoff_hz = std::isfinite(p.filter_cutoff_hz) ? std::clamp(p.filter_cutoff_hz, 20.0F, static_cast<float>(config_.sample_rate * 0.45)) : 12000.0F;
  parameters_.pitch_bend_semitones = std::isfinite(p.pitch_bend_semitones) ? std::clamp(p.pitch_bend_semitones, -24.0F, 24.0F) : 0.0F;
  parameters_.vibrato_rate_hz = std::isfinite(p.vibrato_rate_hz) ? std::clamp(p.vibrato_rate_hz, 0.1F, 20.0F) : 5.0F;
  parameters_.vibrato_depth_semitones = std::isfinite(p.vibrato_depth_semitones) ? std::clamp(p.vibrato_depth_semitones, 0.0F, 2.0F) : 0.0F;
  attack_coefficient_ = time_coefficient(parameters_.attack_seconds, config_.sample_rate, 0.0001F);
  decay_coefficient_ = time_coefficient(parameters_.decay_seconds, config_.sample_rate, 0.001F);
  release_coefficient_ = time_coefficient(parameters_.release_seconds, config_.sample_rate, 0.001F);
  const double cutoff = static_cast<double>(parameters_.filter_cutoff_hz);
  filter_coefficient_ = 1.0 - std::exp(-kTwoPi * cutoff / config_.sample_rate);
  vibrato_increment_ = kTwoPi * static_cast<double>(parameters_.vibrato_rate_hz) / config_.sample_rate;
}
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
  *selected = Voice{};
  selected->base_phase_increment = kTwoPi * midi_frequency(event.note) / config_.sample_rate;
  selected->velocity = velocity;
  selected->channel = event.channel;
  selected->note = event.note;
  selected->stage = EnvelopeStage::attack;
  selected->active = true;
}
void AudioEngine::note_off(const MidiEvent& event) noexcept {
  for (auto& voice : voices_)
    if (voice.active && voice.channel == event.channel && voice.note == event.note)
      voice.stage = EnvelopeStage::release;
}
void AudioEngine::all_notes_off(std::uint8_t channel) noexcept {
  for (auto& voice : voices_)
    if (voice.active && (channel == 0xffU || voice.channel == channel))
      voice.stage = EnvelopeStage::release;
}
void AudioEngine::apply_event(const MidiEvent& event) noexcept {
  switch (event.type) {
    case MidiEventType::note_on: note_on(event); break;
    case MidiEventType::note_off: note_off(event); break;
    case MidiEventType::all_notes_off: all_notes_off(event.channel); break;
  }
}
float AudioEngine::oscillator_sample(double phase) const noexcept {
  const double normalized = phase / kTwoPi;
  switch (parameters_.waveform) {
    case OscillatorWaveform::sine: return static_cast<float>(std::sin(phase));
    case OscillatorWaveform::saw: return static_cast<float>(2.0 * normalized - 1.0);
    case OscillatorWaveform::square: return normalized < 0.5 ? 1.0F : -1.0F;
    case OscillatorWaveform::triangle:
      return static_cast<float>(1.0 - 4.0 * std::abs(normalized - 0.5));
  }
  return 0.0F;
}
void AudioEngine::render(float* output, std::uint32_t frames,
                         std::span<const MidiEvent> events) noexcept {
  if (output == nullptr) return;
  frames = std::min(frames, static_cast<std::uint32_t>(kMaxBlockFrames));
  std::size_t event_index = 0;
  for (std::uint32_t frame = 0; frame < frames; ++frame) {
    while (event_index < events.size() && events[event_index].frame_offset == frame) {
      apply_event(events[event_index]); ++event_index;
    }
    float left = 0.0F, right = 0.0F;
    for (auto& voice : voices_) {
      if (!voice.active) continue;
      switch (voice.stage) {
        case EnvelopeStage::attack:
          voice.envelope += static_cast<float>(attack_coefficient_) * (1.0F - voice.envelope);
          if (voice.envelope >= 0.999F) { voice.envelope = 1.0F; voice.stage = EnvelopeStage::decay; }
          break;
        case EnvelopeStage::decay:
          voice.envelope += static_cast<float>(decay_coefficient_) * (parameters_.sustain_level - voice.envelope);
          if (std::abs(voice.envelope - parameters_.sustain_level) < 0.0005F) {
            voice.envelope = parameters_.sustain_level; voice.stage = EnvelopeStage::sustain;
          }
          break;
        case EnvelopeStage::sustain: voice.envelope = parameters_.sustain_level; break;
        case EnvelopeStage::release:
          voice.envelope += static_cast<float>(release_coefficient_) * (0.0F - voice.envelope);
          if (voice.envelope < kSilence) { voice = Voice{}; continue; }
          break;
      }
      const double vibrato = std::pow(2.0, (static_cast<double>(parameters_.pitch_bend_semitones) +
        std::sin(voice.vibrato_phase) * static_cast<double>(parameters_.vibrato_depth_semitones)) / 12.0);
      const double increment = voice.base_phase_increment * vibrato;
      float sample = oscillator_sample(voice.phase) * voice.envelope * voice.velocity;
      voice.filter_state += static_cast<float>(filter_coefficient_) * (sample - voice.filter_state);
      sample = voice.filter_state * master_gain_ * 0.16F;
      voice.phase += increment;
      if (voice.phase >= kTwoPi) voice.phase -= kTwoPi * std::floor(voice.phase / kTwoPi);
      voice.vibrato_phase += vibrato_increment_;
      if (voice.vibrato_phase >= kTwoPi) voice.vibrato_phase -= kTwoPi;
      left += sample * 0.70710678F; right += sample * 0.70710678F;
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
