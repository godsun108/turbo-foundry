import {
  MusicalTransport, MIDI_PPQ, secondsToTicks, ticksToSeconds,
  createAudioWorkletMidiSink, dispatchMidiEvents
} from "./midi-sequencer.mjs";

const app = window.__earthStudio;
const instrument = window.__earthInstrument;
const midi = window.__earthStudioMidi;
if (!app || !instrument || !midi) throw new Error("EARTH STUDIO shared transport could not find its host modules.");

const $ = id => document.getElementById(id);
const now = () => performance.now() / 1000;
const transport = new MusicalTransport({tempo:Number($("bpm").value) || 120,now});
let audioContext = null;
let audioSources = [];
let animationFrame = 0;
let lastMidiWarning = false;

function tempo() {
  return Math.max(40,Math.min(240,Number($("bpm").value) || 120));
}
function clips() {
  return midi.getClips();
}
function loopEndTick(items = clips()) {
  return Math.max(1,...items.map(clip=>clip.startTick+clip.lengthTicks));
}
function loopConfig(items = clips()) {
  return midi.isLoopEnabled() && items.length ? {startTick:0,endTick:loopEndTick(items)} : null;
}
function cancelMidi() {
  instrument.cancelScheduledMidi?.();
  midi.onTransportStop?.();
  const snapshot = transport.snapshot(now());
  transport.seek(snapshot.absoluteTick,now());
}
function stopAudioSources() {
  for (const source of audioSources) {
    try { source.stop(); } catch {}
    try { source.disconnect(); } catch {}
  }
  audioSources = [];
}
function playAudioFrom(positionSeconds) {
  if (!audioContext || audioContext.state === "closed") return;
  const startAt = audioContext.currentTime + 0.05;
  const anySolo = app.state.tracks.some(track=>track.solo);
  for (const track of app.state.tracks) {
    if (track.muted || (anySolo && !track.solo)) continue;
    const offset = Math.max(0,Number(track.offset)||0);
    const skip = Math.max(0,positionSeconds-offset);
    if (skip >= track.buffer.duration) continue;
    const source = audioContext.createBufferSource();
    const gain = audioContext.createGain();
    source.buffer = track.buffer;
    gain.gain.value = track.gain;
    const pan = audioContext.createStereoPanner ? audioContext.createStereoPanner() : null;
    source.connect(gain);
    if (pan) {
      pan.pan.value = track.pan;
      gain.connect(pan);
      pan.connect(audioContext.destination);
    } else {
      gain.connect(audioContext.destination);
    }
    source.start(startAt + Math.max(0,offset-positionSeconds),skip);
    source.onended = () => {
      try { source.disconnect(); gain.disconnect(); pan?.disconnect(); } catch {}
      audioSources = audioSources.filter(item=>item!==source);
    };
    audioSources.push(source);
  }
}
function updateClock(snapshot = transport.snapshot()) {
  const seconds = ticksToSeconds(snapshot.absoluteTick,transport.tempo,transport.ppq);
  app.state.playhead = Math.min(app.state.duration,seconds);
  $("clock").textContent = app.formatTime ? app.formatTime(app.state.playhead)+" / "+app.formatTime(app.state.duration) : formatTime(app.state.playhead)+" / "+formatTime(app.state.duration);
  $("seek").value = app.state.duration ? Math.round(app.state.playhead/app.state.duration*1000) : 0;
}
function formatTime(value) {
  const seconds=Math.max(0,value||0);
  return String(Math.floor(seconds/60)).padStart(2,"0")+":"+String(Math.floor(seconds%60)).padStart(2,"0")+"."+Math.floor((seconds%1)*10);
}
function refreshLoop() {
  const next = loopConfig();
  const current = transport.snapshot().loop;
  if (JSON.stringify(next) !== JSON.stringify(current)) {
    transport.setLoop(next,now());
    cancelMidi();
  }
}
function scheduleMidi() {
  if (!transport.playing) return;
  const items = clips();
  if (!items.length) return;
  if (!instrument.isNativeReady?.()) {
    if (!lastMidiWarning) {
      app.say("MIDI playback requires the native AudioWorklet engine; the keyboard remains available in Web Audio fallback mode.");
      lastMidiWarning = true;
    }
    return;
  }
  try {
    const clockTimeSeconds = now();
    const audioTimeSeconds = audioContext.currentTime + 0.05;
    const events = transport.scheduleAhead(items,{
      clockTimeSeconds,audioTimeSeconds,lookAheadSeconds:0.14
    });
    if (events.length) {
      const loop = transport.loop;
      const finalTick = loop ? loop.endTick*4 : Number.POSITIVE_INFINITY;
      const bounded = events.filter(event=>event.tick<finalTick || (event.tick===finalTick && event.type==="noteOff"));
      dispatchMidiEvents(bounded,createAudioWorkletMidiSink(instrument.port));
    }
  } catch (error) {
    app.say("MIDI scheduler error: "+(error?.message||String(error)));
  }
}
function frame() {
  if (!transport.playing) return;
  const snapshot = transport.snapshot(now());
  updateClock(snapshot);
  const endTick = transport.loop ? transport.loop.endTick*4 : secondsToTicks(app.state.duration,transport.tempo,transport.ppq);
  if (snapshot.absoluteTick >= endTick) {
    stop();
    return;
  }
  scheduleMidi();
  animationFrame = requestAnimationFrame(frame);
}
async function start() {
  if (transport.playing) return;
  if (!app.state.tracks.length && !clips().length) {
    app.say("Add audio or record a MIDI take first.");
    return;
  }
  try {
    await instrument.prepare();
    audioContext = instrument.getAudioContext();
    if (!audioContext) throw new Error("AudioContext is unavailable.");
    await audioContext.resume();
    transport.setTempo(tempo(),now());
    transport.setLoop(loopConfig(),now());
    const position = transport.snapshot(now()).tick;
    transport.play(now());
    app.state.playing = true;
    playAudioFrom(ticksToSeconds(position,transport.tempo,transport.ppq));
    $("play").textContent = "Ⅱ PAUSE";
    app.say("Shared musical transport running.");
    lastMidiWarning = false;
    cancelAnimationFrame(animationFrame);
    animationFrame = requestAnimationFrame(frame);
  } catch (error) {
    app.say("Could not start transport: "+(error?.message||String(error)));
  }
}
function pause() {
  if (!transport.playing) return;
  const snapshot = transport.pause(now());
  cancelAnimationFrame(animationFrame);
  animationFrame = 0;
  stopAudioSources();
  cancelMidi();
  app.state.playing = false;
  app.state.playhead = ticksToSeconds(snapshot.tick,transport.tempo,transport.ppq);
  $("play").textContent = "▶ PLAY";
  updateClock({absoluteTick:snapshot.tick});
  app.say("Paused.");
}
function stop() {
  cancelAnimationFrame(animationFrame);
  animationFrame = 0;
  transport.stop();
  stopAudioSources();
  cancelMidi();
  app.state.playing = false;
  app.state.playhead = 0;
  $("play").textContent = "▶ PLAY";
  updateClock({absoluteTick:0});
  app.recalc();
  app.say("Stopped.");
}
function seekFromControl() {
  const seconds = app.state.duration * Number($("seek").value) / 1000;
  const tick = secondsToTicks(seconds,tempo(),MIDI_PPQ);
  const wasPlaying = transport.playing;
  transport.seek(tick,now());
  cancelMidi();
  stopAudioSources();
  app.state.playhead = seconds;
  updateClock({absoluteTick:tick});
  if (wasPlaying) playAudioFrom(seconds);
}
$("play").onclick = () => transport.playing ? pause() : start();
$("stop").onclick = stop;
$("seek").addEventListener("input",seekFromControl);
$("bpm").addEventListener("change",()=>{
  const snapshot = transport.setTempo(tempo(),now());
  cancelMidi();
  app.recalc();
  if (transport.playing) app.state.playhead=ticksToSeconds(snapshot.absoluteTick,transport.tempo,transport.ppq);
});
window.addEventListener("earthstudio:transport-config",()=>{
  refreshLoop();
  if (transport.playing) cancelMidi();
});
window.addEventListener("earthstudio:change",()=>{
  if (transport.playing) {
    refreshLoop();
    cancelMidi();
  }
});
document.addEventListener("visibilitychange",()=>{
  if (document.hidden && transport.playing) pause();
});
document.addEventListener("click",event=>{
  if (event.target.closest("#newProject,#clearSession")) stop();
});
window.__earthStudioTransport = {
  transport,
  play:start,
  pause,
  stop,
  seekSeconds(seconds){transport.seek(secondsToTicks(Math.max(0,seconds),tempo(),MIDI_PPQ),now());cancelMidi();},
  snapshot:()=>transport.snapshot(now())
};
