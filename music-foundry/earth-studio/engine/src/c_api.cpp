#include "earth_studio/c_api.h"
#include "earth_studio/audio_engine.hpp"

#include <array>
#include <cmath>
#include <new>
#include <span>

namespace {
bool valid_parameters(const earth_instrument_parameters& p, double sample_rate) noexcept {
  return p.waveform <= 3U &&
    std::isfinite(p.attack_seconds) && p.attack_seconds >= 0.0001F && p.attack_seconds <= 10.0F &&
    std::isfinite(p.decay_seconds) && p.decay_seconds >= 0.001F && p.decay_seconds <= 30.0F &&
    std::isfinite(p.sustain_level) && p.sustain_level >= 0.0F && p.sustain_level <= 1.0F &&
    std::isfinite(p.release_seconds) && p.release_seconds >= 0.001F && p.release_seconds <= 30.0F &&
    std::isfinite(p.filter_cutoff_hz) && p.filter_cutoff_hz >= 20.0F &&
      static_cast<double>(p.filter_cutoff_hz) <= sample_rate * 0.45 &&
    std::isfinite(p.pitch_bend_semitones) && p.pitch_bend_semitones >= -24.0F && p.pitch_bend_semitones <= 24.0F &&
    std::isfinite(p.vibrato_rate_hz) && p.vibrato_rate_hz >= 0.1F && p.vibrato_rate_hz <= 20.0F &&
    std::isfinite(p.vibrato_depth_semitones) && p.vibrato_depth_semitones >= 0.0F &&
      p.vibrato_depth_semitones <= 2.0F;
}
}

struct earth_engine_handle {
  explicit earth_engine_handle(double rate) noexcept : sample_rate(rate), engine(earth_studio::EngineConfig{rate}) {}
  double sample_rate;
  earth_studio::AudioEngine engine;
};

extern "C" {
earth_engine_handle* earth_engine_create(double rate) {
  if (!std::isfinite(rate) || rate < 8000.0 || rate > 384000.0) return nullptr;
  return new(std::nothrow) earth_engine_handle(rate);
}

void earth_engine_destroy(earth_engine_handle* h) { delete h; }

int32_t earth_engine_render(earth_engine_handle* h, float* out, uint32_t frames,
                            const earth_midi_event* events, uint32_t count) {
  if (!h || !out || frames == 0U || frames > earth_studio::kMaxBlockFrames ||
      (count != 0U && !events) || count > 64U) return -1;

  std::array<earth_studio::MidiEvent, 64> converted{};
  uint32_t previous = 0;
  for (uint32_t i = 0; i < count; ++i) {
    const auto& e = events[i];
    const bool all_channels = e.type == 2U && e.channel == 0xffU;
    if (e.frame_offset >= frames || (i != 0U && e.frame_offset < previous) ||
        e.type > 2U || (e.channel > 15U && !all_channels) || e.note > 127U ||
        !std::isfinite(e.velocity) || e.velocity < 0.0F || e.velocity > 1.0F) return -2;
    previous = e.frame_offset;
    const auto type = e.type == 0U ? earth_studio::MidiEventType::note_on :
      e.type == 1U ? earth_studio::MidiEventType::note_off : earth_studio::MidiEventType::all_notes_off;
    converted[i] = {e.frame_offset, type, e.channel, e.note, e.velocity};
  }

  h->engine.render(out, frames, std::span<const earth_studio::MidiEvent>(converted.data(), count));
  return 0;
}

int32_t earth_engine_set_instrument(earth_engine_handle* h, const earth_instrument_parameters* p) {
  if (!h || !p || !valid_parameters(*p, h->sample_rate)) return -1;
  auto v = h->engine.instrument_parameters();
  v.waveform = static_cast<earth_studio::OscillatorWaveform>(p->waveform);
  v.attack_seconds = p->attack_seconds;
  v.decay_seconds = p->decay_seconds;
  v.sustain_level = p->sustain_level;
  v.release_seconds = p->release_seconds;
  v.filter_cutoff_hz = p->filter_cutoff_hz;
  v.pitch_bend_semitones = p->pitch_bend_semitones;
  v.vibrato_rate_hz = p->vibrato_rate_hz;
  v.vibrato_depth_semitones = p->vibrato_depth_semitones;
  h->engine.set_instrument_parameters(v);
  return 0;
}

int32_t earth_engine_set_master_gain(earth_engine_handle* h, float gain) {
  if (!h || !std::isfinite(gain) || gain < 0.0F || gain > 2.0F) return -1;
  h->engine.set_master_gain(gain);
  return 0;
}

uint32_t earth_engine_active_voices(const earth_engine_handle* h) {
  return h ? h->engine.stats().active_voices : 0U;
}
}
