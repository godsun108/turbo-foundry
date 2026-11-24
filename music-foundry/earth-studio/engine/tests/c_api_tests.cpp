#include "earth_studio/c_api.h"

#include <array>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <limits>

void require(bool ok, const char* message) {
  if (!ok) {
    std::cerr << "FAIL: " << message << '\n';
    std::exit(1);
  }
}

int main() {
  require(earth_engine_create(0.0) == nullptr, "invalid sample rate rejected");
  require(earth_engine_create(std::numeric_limits<double>::quiet_NaN()) == nullptr,
          "non-finite sample rate rejected");

  auto* h = earth_engine_create(48000.0);
  require(h != nullptr, "create");
  earth_instrument_parameters p{0U, .001F, .001F, 1.0F, .05F, 12000.0F, 0.0F, 5.0F, 0.0F};
  require(earth_engine_set_instrument(h, &p) == 0, "set valid params");

  auto invalid = p;
  invalid.attack_seconds = std::numeric_limits<float>::quiet_NaN();
  require(earth_engine_set_instrument(h, &invalid) == -1, "non-finite parameter rejected");
  invalid = p;
  invalid.sustain_level = 1.5F;
  require(earth_engine_set_instrument(h, &invalid) == -1, "out-of-range parameter rejected");
  require(earth_engine_set_master_gain(h, std::numeric_limits<float>::infinity()) == -1,
          "non-finite gain rejected");

  std::array<float, 256> out{};
  earth_midi_event on{0U, 0U, 0U, 69U, 0U, 1.0F};
  require(earth_engine_render(h, out.data(), 128U, &on, 1U) == 0, "render");
  bool audible = false;
  for (float x : out) audible = audible || std::abs(x) > .0001F;
  require(audible, "audio crosses C ABI");
  require(earth_engine_active_voices(h) == 1U, "voice stats");

  earth_midi_event bad_offset{128U, 0U, 0U, 60U, 0U, 1.0F};
  require(earth_engine_render(h, out.data(), 128U, &bad_offset, 1U) == -2,
          "invalid event offset rejected");
  earth_midi_event bad_velocity{0U, 0U, 0U, 60U, 0U, 2.0F};
  require(earth_engine_render(h, out.data(), 128U, &bad_velocity, 1U) == -2,
          "invalid velocity rejected");
  earth_midi_event all_off{0U, 2U, 0xffU, 0U, 0U, 0.0F};
  require(earth_engine_render(h, out.data(), 128U, &all_off, 1U) == 0,
          "all-channels note-off accepted");
  require(earth_engine_render(nullptr, out.data(), 128U, nullptr, 0U) == -1,
          "null handle rejected");
  require(earth_engine_render(h, out.data(), 2049U, nullptr, 0U) == -1,
          "oversized block rejected");

  earth_engine_destroy(h);
  std::cout << "EARTH STUDIO C ABI tests passed\n";
}
