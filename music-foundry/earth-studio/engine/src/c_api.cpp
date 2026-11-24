#include "earth_studio/c_api.h"
#include "earth_studio/audio_engine.hpp"
#include <array>
#include <new>
struct earth_engine_handle { explicit earth_engine_handle(double rate) noexcept : engine(earth_studio::EngineConfig{rate}) {} earth_studio::AudioEngine engine; };
extern "C" {
earth_engine_handle* earth_engine_create(double rate){return new(std::nothrow) earth_engine_handle(rate);}
void earth_engine_destroy(earth_engine_handle* h){delete h;}
int32_t earth_engine_render(earth_engine_handle* h,float* out,uint32_t frames,const earth_midi_event* events,uint32_t count){
 if(!h||!out||frames==0U||frames>earth_studio::kMaxBlockFrames||(count&& !events)||count>64U)return -1;
 std::array<earth_studio::MidiEvent,64> converted{};uint32_t previous=0;
 for(uint32_t i=0;i<count;++i){const auto&e=events[i];if(e.frame_offset>=frames||(i&&e.frame_offset<previous)||e.type>2U||e.channel>15U||e.note>127U)return -2;previous=e.frame_offset;
 const auto type=e.type==0U?earth_studio::MidiEventType::note_on:e.type==1U?earth_studio::MidiEventType::note_off:earth_studio::MidiEventType::all_notes_off;
 converted[i]={e.frame_offset,type,e.channel,e.note,e.velocity};}
 h->engine.render(out,frames,std::span<const earth_studio::MidiEvent>(converted.data(),count));return 0;
}
int32_t earth_engine_set_instrument(earth_engine_handle*h,const earth_instrument_parameters*p){
 if(!h||!p||p->waveform>3U)return -1;auto v=h->engine.instrument_parameters();v.waveform=static_cast<earth_studio::OscillatorWaveform>(p->waveform);
 v.attack_seconds=p->attack_seconds;v.decay_seconds=p->decay_seconds;v.sustain_level=p->sustain_level;v.release_seconds=p->release_seconds;
 v.filter_cutoff_hz=p->filter_cutoff_hz;v.pitch_bend_semitones=p->pitch_bend_semitones;v.vibrato_rate_hz=p->vibrato_rate_hz;v.vibrato_depth_semitones=p->vibrato_depth_semitones;h->engine.set_instrument_parameters(v);return 0;
}
int32_t earth_engine_set_master_gain(earth_engine_handle*h,float gain){if(!h)return -1;h->engine.set_master_gain(gain);return 0;}
uint32_t earth_engine_active_voices(const earth_engine_handle*h){return h?h->engine.stats().active_voices:0U;}
}
