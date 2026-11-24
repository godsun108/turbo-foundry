#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
namespace earth_studio {
inline constexpr std::size_t kMaxVoices = 32;
inline constexpr std::size_t kMaxBlockFrames = 2048;
enum class MidiEventType : std::uint8_t { note_on, note_off, all_notes_off };
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
struct EngineStats {
  std::uint64_t rendered_frames{0};
  std::uint64_t transport_frames{0};
  std::uint32_t active_voices{0};
  std::uint64_t stolen_voices{0};
};
class AudioEngine final {
 public:
  explicit AudioEngine(EngineConfig config = {}) noexcept;
  // Interleaved stereo float output. Caller owns memory; output is overwritten.
  // Events must be sorted by frame_offset and lie inside this block.
  // No allocation, locking, I/O, or exceptions occur in render().
  void render(float* output_interleaved, std::uint32_t frames,
              std::span<const MidiEvent> events = {}) noexcept;
  void set_master_gain(float gain) noexcept;
  void set_tempo(double beats_per_minute) noexcept;
  void start_transport() noexcept;
  void stop_transport() noexcept;
  void reset_transport() noexcept;
  [[nodiscard]] double tempo() const noexcept { return tempo_bpm_; }
  [[nodiscard]] bool transport_running() const noexcept { return transport_running_; }
  [[nodiscard]] double beat_position() const noexcept;
  [[nodiscard]] EngineStats stats() const noexcept;
 private:
  struct Voice {
    double phase{0.0};
    double phase_increment{0.0};
    float envelope{0.0F};
    float velocity{0.0F};
    std::uint8_t channel{0};
    std::uint8_t note{0};
    bool active{false};
    bool releasing{false};
  };
  void apply_event(const MidiEvent& event) noexcept;
  void note_on(const MidiEvent& event) noexcept;
  void note_off(const MidiEvent& event) noexcept;
  void all_notes_off(std::uint8_t channel) noexcept;
  [[nodiscard]] static float clamp_gain(float value) noexcept;
  EngineConfig config_{};
  std::array<Voice, kMaxVoices> voices_{};
  double tempo_bpm_{120.0};
  double attack_coefficient_{0.0};
  double release_coefficient_{0.0};
  float master_gain_{0.8F};
  bool transport_running_{false};
  std::uint64_t rendered_frames_{0};
  std::uint64_t transport_frames_{0};
  std::uint64_t stolen_voices_{0};
};
}  // namespace earth_studio
