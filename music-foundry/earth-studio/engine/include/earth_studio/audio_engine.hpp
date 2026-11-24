#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
namespace earth_studio {
inline constexpr std::size_t kMaxVoices = 32;
inline constexpr std::size_t kMaxBlockFrames = 2048;
enum class MidiEventType : std::uint8_t { note_on, note_off, all_notes_off };
enum class OscillatorWaveform : std::uint8_t { sine, saw, square, triangle };
struct MidiEvent {
  std::uint32_t frame_offset{0};
  MidiEventType type{MidiEventType::note_on};
  std::uint8_t channel{0};
  std::uint8_t note{60};
  float velocity{1.0F};
};
struct EngineConfig {
  double sample_rate{48000.0};
  float master_gain{0.8F};
  float attack_seconds{0.008F};
  float release_seconds{0.12F};
};
struct InstrumentParameters {
  OscillatorWaveform waveform{OscillatorWaveform::saw};
  float attack_seconds{0.008F};
  float decay_seconds{0.18F};
  float sustain_level{0.72F};
  float release_seconds{0.16F};
  float filter_cutoff_hz{12000.0F};
  float pitch_bend_semitones{0.0F};
  float vibrato_rate_hz{5.0F};
  float vibrato_depth_semitones{0.0F};
};
struct EngineStats {
  std::uint64_t rendered_frames{0};
  std::uint64_t transport_frames{0};
  std::uint32_t active_voices{0};
  std::uint64_t stolen_voices{0};
};
class AudioEngine final {
 public:
  explicit AudioEngine(EngineConfig config = {}) noexcept;
  void render(float* output_interleaved, std::uint32_t frames,
              std::span<const MidiEvent> events = {}) noexcept;
  void set_master_gain(float gain) noexcept;
  void set_instrument_parameters(const InstrumentParameters& parameters) noexcept;
  [[nodiscard]] InstrumentParameters instrument_parameters() const noexcept { return parameters_; }
  void set_tempo(double beats_per_minute) noexcept;
  void start_transport() noexcept;
  void stop_transport() noexcept;
  void reset_transport() noexcept;
  [[nodiscard]] double tempo() const noexcept { return tempo_bpm_; }
  [[nodiscard]] bool transport_running() const noexcept { return transport_running_; }
  [[nodiscard]] double beat_position() const noexcept;
  [[nodiscard]] EngineStats stats() const noexcept;
 private:
  enum class EnvelopeStage : std::uint8_t { attack, decay, sustain, release };
  struct Voice {
    double phase{0.0};
    double base_phase_increment{0.0};
    double vibrato_phase{0.0};
    float envelope{0.0F};
    float velocity{0.0F};
    float filter_state{0.0F};
    std::uint8_t channel{0};
    std::uint8_t note{0};
    EnvelopeStage stage{EnvelopeStage::attack};
    bool active{false};
  };
  void apply_event(const MidiEvent& event) noexcept;
  void note_on(const MidiEvent& event) noexcept;
  void note_off(const MidiEvent& event) noexcept;
  void all_notes_off(std::uint8_t channel) noexcept;
  [[nodiscard]] float oscillator_sample(double phase) const noexcept;
  [[nodiscard]] static float clamp_gain(float value) noexcept;
  EngineConfig config_{};
  InstrumentParameters parameters_{};
  std::array<Voice, kMaxVoices> voices_{};
  double tempo_bpm_{120.0};
  double attack_coefficient_{0.0};
  double decay_coefficient_{0.0};
  double release_coefficient_{0.0};
  double filter_coefficient_{0.0};
  double vibrato_increment_{0.0};
  float master_gain_{0.8F};
  bool transport_running_{false};
  std::uint64_t rendered_frames_{0};
  std::uint64_t transport_frames_{0};
  std::uint64_t stolen_voices_{0};
};
}  // namespace earth_studio
