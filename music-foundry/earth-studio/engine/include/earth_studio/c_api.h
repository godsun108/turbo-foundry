#pragma once
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
typedef struct earth_engine_handle earth_engine_handle;
typedef struct earth_midi_event { uint32_t frame_offset; uint8_t type; uint8_t channel; uint8_t note; uint8_t reserved; float velocity; } earth_midi_event;
typedef struct earth_instrument_parameters { uint32_t waveform; float attack_seconds; float decay_seconds; float sustain_level; float release_seconds; float filter_cutoff_hz; float pitch_bend_semitones; float vibrato_rate_hz; float vibrato_depth_semitones; } earth_instrument_parameters;
earth_engine_handle* earth_engine_create(double sample_rate);
void earth_engine_destroy(earth_engine_handle* engine);
int32_t earth_engine_render(earth_engine_handle* engine,float* output,uint32_t frames,const earth_midi_event* events,uint32_t event_count);
int32_t earth_engine_set_instrument(earth_engine_handle* engine,const earth_instrument_parameters* parameters);
int32_t earth_engine_set_master_gain(earth_engine_handle* engine,float gain);
uint32_t earth_engine_active_voices(const earth_engine_handle* engine);
#ifdef __cplusplus
}
#endif
