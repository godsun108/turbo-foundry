import {MidiRecorder, collectMidiEvents, createAudioWorkletMidiSink, dispatchMidiEvents, MIDI_PPQ} from "./midi-sequencer.mjs";

const app = window.__earthStudio;
const instrument = window.__earthInstrument;
if (!app || !instrument) throw new Error("EARTH STUDIO MIDI controls could not find the studio or performance instrument.");
app.state.midiTracks ||= [];

const panel = document.createElement("section");
panel.className = "panel";
panel.id = "midiRecorderPanel";
panel.innerHTML = `
  <div class="track-head"><h2>MIDI RECORDING & PIANO ROLL</h2><span class="tag">960 PPQ · LOCAL</span></div>
  <div class="toolbar" id="midiToolbar">
    <button class="primary" id="midiRecord">● RECORD</button>
    <button id="midiStop" disabled>■ STOP TAKE</button>
    <button id="midiOverdub">OVERDUB: OFF</button>
    <label class="hint" for="midiQuantize">QUANTIZE</label>
    <select id="midiQuantize" style="min-height:40px;background:#0b1017;color:white;border:1px solid var(--line);border-radius:8px;padding:7px">
      <option value="0">OFF</option><option value="240">1/16</option><option value="480">1/8</option><option value="960">1/4</option>
    </select>
  </div>
  <div class="toolbar" style="margin-top:9px">
    <input id="midiTrackName" type="text" maxlength="64" value="Instrument 1" aria-label="MIDI track name" style="flex:1;min-width:140px;min-height:40px;background:#0b1017;color:white;border:1px solid var(--line);border-radius:8px;padding:8px">
    <span class="hint" id="midiRecordStatus" role="status" aria-live="polite">Ready to record the performance keyboard.</span>
  </div>
  <div id="midiTrackList" style="margin-top:12px"></div>
  <div class="hint" style="margin-top:8px">Recorded notes are saved inside the .earthsession project. Quantization is applied on capture; overdub preserves the selected take's existing notes.</div>
`;
const instrumentPanel = document.getElementById("instrumentPanel");
instrumentPanel.after(panel);

const $ = id => document.getElementById(id);
let recorder = null;
let recording = false;
let overdub = false;
let recordStartTime = 0;
let activeTrackId = null;
let unsubscribe = null;
let playbackGeneration = 0;

const id = prefix => prefix + "-" + crypto.randomUUID();
const status = message => { $("midiRecordStatus").textContent = message; };
const selectedTrack = () => app.state.midiTracks.find(track => track.id === activeTrackId) || app.state.midiTracks[0] || null;
const currentTempo = () => Math.max(40, Math.min(240, Number($("bpm").value) || 120));
const currentDurationTicks = () => Math.max(1, Math.ceil(app.state.duration * currentTempo() * MIDI_PPQ / 60));

function render() {
  const root = $("midiTrackList");
  root.replaceChildren();
  if (!app.state.midiTracks.length) {
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = "No MIDI takes yet. Tap RECORD, play the keyboard, then STOP TAKE.";
    root.append(empty);
    return;
  }
  for (const track of app.state.midiTracks) {
    const card = document.createElement("div");
    card.className = "control";
    card.style.marginTop = "8px";
    card.style.borderColor = track.id === activeTrackId ? "var(--acid)" : "var(--line)";
    const header = document.createElement("div");
    header.className = "track-head";
    const title = document.createElement("strong");
    title.textContent = track.name;
    const select = document.createElement("button");
    select.textContent = track.id === activeTrackId ? "SELECTED" : "SELECT";
    select.onclick = () => { activeTrackId = track.id; $("midiTrackName").value = track.name; render(); };
    header.append(title, select);
    card.append(header);
    for (const clip of track.midiClips || []) {
      const row = document.createElement("div");
      row.className = "hint";
      row.style.margin = "7px 0";
      row.textContent = clip.notes.length + " notes · " + Math.round(clip.lengthTicks / MIDI_PPQ * 100) / 100 + " beats · " + clip.id;
      card.append(row);
      const roll = document.createElement("div");
      roll.style.cssText = "position:relative;height:116px;overflow:hidden;border:1px solid var(--line);border-radius:8px;background:repeating-linear-gradient(90deg,#111923 0,#111923 39px,#25303d 40px),repeating-linear-gradient(0deg,transparent 0,transparent 13px,#283442 14px);";
      const maxTick = Math.max(1, clip.lengthTicks);
      for (const note of clip.notes) {
        const block = document.createElement("div");
        block.title = "MIDI " + note.note + " · velocity " + note.velocity + " · " + note.durationTicks + " ticks";
        const left = Math.min(99, note.startTick / maxTick * 100);
        const width = Math.max(.7, note.durationTicks / maxTick * 100);
        block.style.cssText = "position:absolute;height:9px;min-width:3px;border-radius:3px;background:var(--acid);border:1px solid #efffc2;top:" + (106 - (note.note % 12) * 8) + "px;left:" + left + "%;width:" + width + "%;opacity:" + (.45 + note.velocity / 230) + ";";
        roll.append(block);
      }
      card.append(roll);
    }
    root.append(card);
  }
}
function ensureTrack() {
  let track = selectedTrack();
  if (!track) {
    track = {id:id("midi-track"),name:$("midiTrackName").value.trim() || "Instrument 1",kind:"instrument",gain:1,pan:0,muted:false,solo:false,clips:[],midiClips:[]};
    app.state.midiTracks.push(track);
    activeTrackId = track.id;
  }
  track.name = $("midiTrackName").value.trim().slice(0,64) || track.name;
  return track;
}
async function startRecording() {
  if (recording) return;
  try {
    const start = await instrument.prepare();
    const track = ensureTrack();
    recorder = new MidiRecorder({idPrefix:"note"});
    recorder.start({tempo:currentTempo(),quantizeTicks:Number($("midiQuantize").value)||0});
    recordStartTime = start;
    recording = true;
    $("midiRecord").disabled = true;
    $("midiStop").disabled = false;
    status(overdub ? "Overdubbing · play the keyboard." : "Recording · play the keyboard.");
    render();
  } catch (error) {
    status("Could not start recording: " + (error?.message || String(error)));
  }
}
function stopRecording() {
  if (!recording || !recorder) return;
  const endTime = instrument.getAudioContextTime();
  recorder.stop({timeSeconds:Math.max(0,endTime-recordStartTime)});
  const track = ensureTrack();
  const take = recorder.toClip({id:id("midi-clip"),lengthTicks:Math.max(currentDurationTicks(),...recorder.notes.map(note=>note.startTick+note.durationTicks),1)});
  if (overdub && track.midiClips.length) {
    const previous = track.midiClips[track.midiClips.length-1];
    const notes = [...previous.notes,...take.notes.map(note=>({...note,id:id("note")}))];
    const lengthTicks = Math.max(previous.lengthTicks,take.lengthTicks,...notes.map(note=>note.startTick+note.durationTicks));
    track.midiClips[track.midiClips.length-1] = {...previous,notes,lengthTicks};
  } else {
    track.midiClips.push(take);
  }
  recording = false;
  recorder = null;
  $("midiRecord").disabled = false;
  $("midiStop").disabled = true;
  window.dispatchEvent(new Event("earthstudio:change"));
  render();
  status("Take saved in the project · " + (overdub ? "overdub complete." : "recording complete."));
}
function receive(event) {
  if (!recording || !recorder) return;
  const timeSeconds = Math.max(0,event.audioTime-recordStartTime);
  try {
    if (event.type === "noteOn") recorder.noteOn({note:event.note,velocity:event.velocity||100,channel:event.channel||0,timeSeconds,key:String(event.channel||0)+":"+event.note});
    else if (event.type === "noteOff") recorder.noteOff({note:event.note,channel:event.channel||0,timeSeconds,key:String(event.channel||0)+":"+event.note});
  } catch (error) { status("MIDI capture error: " + error.message); }
}
function stopPlayback() {
  playbackGeneration++;
  try { instrument.allNotesOff(); } catch {}
}
async function schedulePlayback() {
  const generation = ++playbackGeneration;
  if (!app.state.playing || !app.state.midiTracks.length) return;
  try {
    const originTime = await instrument.prepare();
    if (generation !== playbackGeneration || !app.state.playing) return;
    const clips = app.state.midiTracks.flatMap(track => (track.muted || (app.state.midiTracks.some(item=>item.solo) && !track.solo)) ? [] : (track.midiClips||[]).map(clip=>({...clip,trackId:track.id})));
    if (!clips.length) return;
    const toTick = Math.max(currentDurationTicks(),...clips.map(clip=>clip.startTick+clip.lengthTicks));
    const events = collectMidiEvents(clips,{tempo:currentTempo(),fromTick:0,toTick,originTime:originTime+.08});
    if (events.length > 512) { status("Playback event limit reached (512 scheduled events). Split the arrangement into shorter sections."); return; }
    dispatchMidiEvents(events,createAudioWorkletMidiSink(instrument.port));
    status("MIDI playback scheduled · " + events.length + " events.");
  } catch (error) {
    status("MIDI playback unavailable: " + (error?.message || String(error)));
  }
}
$("midiRecord").addEventListener("click",startRecording);
$("midiStop").addEventListener("click",stopRecording);
$("midiOverdub").addEventListener("click",()=>{overdub=!overdub;$("midiOverdub").textContent="OVERDUB: "+(overdub?"ON":"OFF");});
if (typeof instrument.onMidiEvent === "function") unsubscribe = instrument.onMidiEvent(receive);
$("play").addEventListener("click",()=>{if(app.state.playing) schedulePlayback();else stopPlayback();});
$("stop").addEventListener("click",stopPlayback);
$("clearSession").addEventListener("click",()=>{app.state.midiTracks=[];activeTrackId=null;render();stopPlayback();});
$("newProject").addEventListener("click",()=>{app.state.midiTracks=[];activeTrackId=null;render();stopPlayback();});
window.addEventListener("earthstudio:change",render);
window.__earthStudioMidi = {render,stopRecording,getTracks:()=>app.state.midiTracks,dispose:()=>unsubscribe?.()};
render();
