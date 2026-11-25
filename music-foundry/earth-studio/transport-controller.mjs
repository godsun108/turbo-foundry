import {
  MusicalTransport, MIDI_PPQ, secondsToTicks, ticksToSeconds,
  createAudioWorkletMidiSink, dispatchMidiEvents
} from "./midi-sequencer.mjs";

const app = window.__earthStudio;
if (!app) throw new Error("EARTH STUDIO shared transport could not find the studio host.");
async function waitForGlobal(key,eventName) {
  if (window[key]) return window[key];
  return await new Promise(resolve=>window.addEventListener(eventName,()=>resolve(window[key]),{once:true}));
}
const instrument = await waitForGlobal("__earthInstrument","earthstudio:instrument-ready");
const midi = await waitForGlobal("__earthStudioMidi","earthstudio:midi-ready");

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
  return midi.isLoopEnabled() && items.length ? {startTick:items[0].startTick,endTick:loopEndTick(items)} : null;
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
  const scene = midi.getSceneInfo();
  const tracks = midi.getAudioTracks?.() || [];
  if (scene.active === null || !tracks.length) return;
  const absoluteTick = secondsToTicks(Math.max(0,positionSeconds),transport.tempo,transport.ppq);
  const elapsed = ticksToSeconds(Math.max(0,absoluteTick-scene.startTick),transport.tempo,transport.ppq);
  const startAt = audioContext.currentTime + 0.05;
  for (const track of tracks) {
    const clipList = track.clips?.length ? track.clips : [{
      startSeconds:Math.max(0,Number(track.offset)||0),sourceStartSeconds:0,durationSeconds:track.buffer.duration
    }];
    for (const clip of clipList) {
      const clipStart = Math.max(0,Number(clip.startSeconds)||0);
      const sourceStart = Math.max(0,Number(clip.sourceStartSeconds)||0);
      const clipDuration = Math.max(0,Number(clip.durationSeconds)||0);
      if (!clipDuration) continue;
      const relative = elapsed - clipStart;
      if (relative >= clipDuration && !clip.loop) continue;
      const source = audioContext.createBufferSource();
      const gain = audioContext.createGain();
      const pan = audioContext.createStereoPanner ? audioContext.createStereoPanner() : null;
      source.buffer = track.buffer;
      source.loop = !!clip.loop;
      if (source.loop) {
        source.loopStart = sourceStart;
        source.loopEnd = Math.min(track.buffer.duration,sourceStart+clipDuration);
      }
      const clipGain = Number.isFinite(clip.gain) ? clip.gain : 1;
      const fadeIn = Math.max(0,Number(clip.fadeInSeconds)||0);
      const fadeOut = Math.max(0,Number(clip.fadeOutSeconds)||0);
      const clipStartOffset = Math.max(0,relative);
      const remaining = Math.max(0,clipDuration-clipStartOffset);
      const clipWhen = startAt + Math.max(0,clipStart-elapsed);
      const effectiveGain = Math.max(0,Math.min(2,track.gain*clipGain));
      gain.gain.setValueAtTime(0,clipWhen);
      const fadeInRemaining = Math.max(0,fadeIn-clipStartOffset);
      if (fadeInRemaining > 0) {
        const startLevel = fadeIn ? effectiveGain*Math.min(1,clipStartOffset/fadeIn) : effectiveGain;
        gain.gain.setValueAtTime(startLevel,clipWhen);
        gain.gain.linearRampToValueAtTime(effectiveGain,clipWhen+fadeInRemaining);
      } else {
        gain.gain.setValueAtTime(effectiveGain,clipWhen);
      }
      if (!clip.loop && fadeOut > 0) {
        const fadeOutAt = clipWhen + Math.max(0,remaining-fadeOut);
        gain.gain.setValueAtTime(effectiveGain,fadeOutAt);
        gain.gain.linearRampToValueAtTime(0,clipWhen+remaining);
      }
      source.connect(gain);
      if (pan) {
        pan.pan.value = track.pan;
        gain.connect(pan);
        pan.connect(audioContext.destination);
      } else {
        gain.connect(audioContext.destination);
      }
      const skip = Math.max(0,relative);
      const when = startAt + Math.max(0,clipStart-elapsed);
      if (source.loop) {
        const loopLength = Math.max(0.001,source.loopEnd-source.loopStart);
        source.start(when,sourceStart+(skip%loopLength));
      } else {
        source.start(when,sourceStart+skip,clipDuration-skip);
      }
      source.onended = () => {
        try { source.disconnect(); gain.disconnect(); pan?.disconnect(); } catch {}
        audioSources = audioSources.filter(item=>item!==source);
      };
      audioSources.push(source);
    }
  }
}
function updateClock(snapshot = transport.snapshot()) {
  const items=clips();
  const sceneEnd=Math.max(0,...items.map(clip=>clip.startTick+clip.lengthTicks));
  const duration=Math.max(app.state.duration,ticksToSeconds(sceneEnd,transport.tempo,transport.ppq));
  app.state.duration=duration;
  const seconds = ticksToSeconds(snapshot.absoluteTick,transport.tempo,transport.ppq);
  app.state.playhead = Math.min(duration,seconds);
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
    return true;
  }
  return false;
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
      const finalTick = loop ? loop.startTick+(loop.endTick-loop.startTick)*4 : Number.POSITIVE_INFINITY;
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
  midi.advanceScene(snapshot.absoluteTick);
  const activeClips=clips();
  const scene=midi.getSceneInfo();
  const audioEndTick=Math.max(0,...(midi.getAudioTracks?.()||[]).flatMap(track=>(track.clips?.length?track.clips:[{startSeconds:Number(track.offset)||0,durationSeconds:track.buffer.duration}]).map(clip=>scene.startTick+secondsToTicks(clip.startSeconds+clip.durationSeconds,transport.tempo,transport.ppq))));
  const endTick=transport.loop
    ? transport.loop.startTick+(transport.loop.endTick-transport.loop.startTick)*4
    : Math.max(scene.startTick,audioEndTick,...activeClips.map(clip=>clip.startTick+clip.lengthTicks));
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
    const position = transport.snapshot(now()).absoluteTick;
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
  app.state.playhead = ticksToSeconds(snapshot.absoluteTick,transport.tempo,transport.ppq);
  $("play").textContent = "▶ PLAY";
  updateClock(snapshot);
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
window.addEventListener("earthstudio:scenechange",()=>{
  refreshLoop();
  if (transport.playing) {
    cancelMidi();
    stopAudioSources();
    const snapshot=transport.snapshot(now());
    playAudioFrom(ticksToSeconds(snapshot.absoluteTick,transport.tempo,transport.ppq));
  } else {
    stopAudioSources();
  }
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

/* Compact clip-envelope inspector: all edits update portable clip metadata. */
function mountClipEnvelopeInspector() {
  if (document.getElementById("earthClipEnvelope")) return;
  const panel=document.createElement("section");
  panel.id="earthClipEnvelope";
  panel.style.cssText="position:fixed;z-index:30;right:12px;bottom:12px;width:min(300px,calc(100vw - 24px));padding:12px;border:1px solid #64748b;border-radius:12px;background:#101820;color:#f8fafc;font:13px system-ui;box-shadow:0 8px 28px #0008";
  panel.innerHTML='<strong>CLIP ENVELOPE</strong><div id="earthClipEnvelopeName" style="opacity:.7;margin:4px 0 8px">Select an audio clip</div><label>Clip gain <output id="earthClipGainValue">1.00×</output><input id="earthClipGain" type="range" min="0" max="2" step=".01" value="1" style="width:100%"></label><label>Fade in <output id="earthClipFadeInValue">0.0s</output><input id="earthClipFadeIn" type="range" min="0" max="10" step=".05" value="0" style="width:100%"></label><label>Fade out <output id="earthClipFadeOutValue">0.0s</output><input id="earthClipFadeOut" type="range" min="0" max="10" step=".05" value="0" style="width:100%"></label>';
  document.body.append(panel);
  const fields=[["earthClipGain","gain",1],["earthClipFadeIn","fadeInSeconds",0],["earthClipFadeOut","fadeOutSeconds",0]];
  function selected() {
    const track=app.state.tracks.find(t=>t.id===app.state.selected);
    return track?.clips?.find(c=>c.id===app.state.selectedClip) || null;
  }
  function sync() {
    const clip=selected(),name=document.getElementById("earthClipEnvelopeName");
    name.textContent=clip ? "Selected audio clip · "+clip.id : "Select an audio clip";
    for(const [id,key,fallback] of fields) {
      const input=document.getElementById(id),value=clip?.[key]??fallback;
      input.value=String(value);input.disabled=!clip;
      document.getElementById(id+"Value").textContent=key==="gain"?Number(value).toFixed(2)+"×":Number(value).toFixed(1)+"s";
      if(key!=="gain")input.max=clip?String(Math.min(10,clip.durationSeconds)): "10";
    }
  }
  for(const [id,key] of fields.map(([id,key])=>[id,key])) {
    document.getElementById(id).addEventListener("input",event=>{
      const clip=selected();if(!clip)return;
      const next={...clip,[key]:Number(event.target.value)};
      if((next.fadeInSeconds||0)+(next.fadeOutSeconds||0)>next.durationSeconds) {
        if(key==="fadeInSeconds")next.fadeOutSeconds=Math.max(0,next.durationSeconds-next.fadeInSeconds);
        else if(key==="fadeOutSeconds")next.fadeInSeconds=Math.max(0,next.durationSeconds-next.fadeOutSeconds);
      }
      Object.assign(clip,next);
      sync();
      window.dispatchEvent(new Event("earthstudio:change"));
    });
  }
  window.addEventListener("earthstudio:change",sync);
  const observer=new MutationObserver(sync);
  observer.observe(document.body,{subtree:true,childList:true});
  sync();
}
mountClipEnvelopeInspector();

window.__earthStudioTransport = {
  transport,
  play:start,
  pause,
  stop,
  seekSeconds(seconds){transport.seek(secondsToTicks(Math.max(0,seconds),tempo(),MIDI_PPQ),now());cancelMidi();},
  snapshot:()=>transport.snapshot(now())
};
