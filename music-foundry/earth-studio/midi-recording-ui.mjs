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
    <button id="midiLoop">MIDI LOOP ×4: OFF</button>
    <button id="midiConnect">CONNECT MIDI DEVICE</button>
    <label class="hint" for="midiQuantize">QUANTIZE</label>
    <select id="midiQuantize" style="min-height:40px;background:#0b1017;color:white;border:1px solid var(--line);border-radius:8px;padding:7px">
      <option value="0">OFF</option><option value="240">1/16</option><option value="480">1/8</option><option value="960">1/4</option>
    </select>
  </div>
  <div class="toolbar" style="margin-top:9px">
    <input id="midiTrackName" type="text" maxlength="64" value="Instrument 1" aria-label="MIDI track name" style="flex:1;min-width:140px;min-height:40px;background:#0b1017;color:white;border:1px solid var(--line);border-radius:8px;padding:8px">
    <span class="hint" id="midiRecordStatus" role="status" aria-live="polite">Ready to record the performance keyboard.</span>
  </div>
  <div class="toolbar" style="margin-top:10px"><label class="hint" for="midiVelocity">SELECTED NOTE VELOCITY</label><input id="midiVelocity" type="range" min="1" max="127" value="100" disabled style="flex:1;min-width:120px"><output id="midiVelocityValue" class="tag">—</output><button id="midiDeleteNote" disabled>DELETE NOTE</button></div>
  <div class="hint" id="midiDeviceStatus" style="margin-top:6px">Hardware MIDI: not connected.</div>
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
let selectedNoteRef = null;
let loopEnabled = false;
let midiAccess = null;
const midiInputs = new Set();

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
      roll.style.cssText = "position:relative;height:256px;overflow:hidden;touch-action:none;border:1px solid var(--line);border-radius:8px;background:repeating-linear-gradient(90deg,#111923 0,#111923 39px,#25303d 40px),repeating-linear-gradient(0deg,transparent 0,transparent 1px,#283442 2px);";
      const maxTick = Math.max(1, clip.lengthTicks);
      for (const note of clip.notes) {
        const block = document.createElement("button");
        block.type = "button";
        block.title = "Drag to move pitch/time; drag the right edge to resize. MIDI " + note.note + " · velocity " + note.velocity;
        block.setAttribute("aria-label", block.title);
        const left = Math.min(99, note.startTick / maxTick * 100);
        const width = Math.max(.7, note.durationTicks / maxTick * 100);
        const paintNote = () => {
          const x = Math.min(99, note.startTick / Math.max(1,clip.lengthTicks) * 100);
          const w = Math.max(.7, note.durationTicks / Math.max(1,clip.lengthTicks) * 100);
          block.style.left = x + "%";
          block.style.width = w + "%";
          block.style.top = Math.max(0,Math.min(246,246-note.note*2)) + "px";
          block.title = "MIDI " + note.note + " · velocity " + note.velocity + " · " + note.durationTicks + " ticks";
        };
        block.style.cssText = "position:absolute;height:9px;min-width:3px;padding:0;border-radius:3px;background:var(--acid);border:" + (selectedNoteRef?.noteId===note.id ? "2px solid #ffffff" : "1px solid #efffc2") + ";opacity:" + (.45 + note.velocity / 230) + ";touch-action:none;";
        block.style.left = left + "%";
        block.style.width = width + "%";
        block.style.top = Math.max(0,Math.min(246,246-note.note*2)) + "px";
        block.addEventListener("pointerdown",event=>{
          event.preventDefault();
          selectedNoteRef={trackId:track.id,clipId:clip.id,noteId:note.id};
          updateSelectionControls();
          block.setPointerCapture(event.pointerId);
          const rect=roll.getBoundingClientRect();
          const originX=event.clientX,originY=event.clientY;
          const originalStart=note.startTick,originalDuration=note.durationTicks,originalPitch=note.note;
          const resizing=event.offsetX>=block.clientWidth-12;
          const move=moveEvent=>{
            const delta=Math.round(((moveEvent.clientX-originX)/Math.max(1,rect.width)*maxTick)/60)*60;
            if(resizing) note.durationTicks=Math.max(60,originalDuration+delta);
            else note.startTick=Math.max(0,originalStart+delta);
            note.note=Math.max(0,Math.min(127,originalPitch-Math.round((moveEvent.clientY-originY)/2)));
            clip.lengthTicks=Math.max(clip.lengthTicks,note.startTick+note.durationTicks);
            paintNote();
          };
          const finish=()=>{
            block.removeEventListener("pointermove",move);
            block.removeEventListener("pointerup",finish);
            block.removeEventListener("pointercancel",finish);
            window.dispatchEvent(new Event("earthstudio:change"));
            app.recalc();
            render();
          };
          block.addEventListener("pointermove",move);
          block.addEventListener("pointerup",finish,{once:true});
          block.addEventListener("pointercancel",finish,{once:true});
        });
        roll.append(block);
      }
      card.append(roll);
    }
    root.append(card);
  }
}
function selectedNote() {
  if (!selectedNoteRef) return null;
  const track=app.state.midiTracks.find(item=>item.id===selectedNoteRef.trackId);
  const clip=track?.midiClips?.find(item=>item.id===selectedNoteRef.clipId);
  const note=clip?.notes?.find(item=>item.id===selectedNoteRef.noteId);
  return note ? {track,clip,note} : null;
}
function updateSelectionControls() {
  const selected=selectedNote();
  $("midiVelocity").disabled=!selected;
  $("midiDeleteNote").disabled=!selected;
  $("midiVelocity").value=selected?.note.velocity||100;
  $("midiVelocityValue").textContent=selected?String(selected.note.velocity):"—";
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
  app.recalc();
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
    const loopEnd = Math.max(1,...clips.map(clip=>clip.startTick+clip.lengthTicks));
    const repeats = loopEnabled ? 4 : 1;
    const toTick = loopEnd*repeats+1;
    const events = collectMidiEvents(clips,{tempo:currentTempo(),fromTick:0,toTick,originTime:originTime+.08,loop:loopEnabled?{startTick:0,endTick:loopEnd}:null});
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
$("midiLoop").addEventListener("click",()=>{
  loopEnabled=!loopEnabled;
  app.state.midiLoopRepeats=loopEnabled?4:1;
  $("midiLoop").textContent="MIDI LOOP ×4: "+(loopEnabled?"ON":"OFF");
  app.recalc();
  status(loopEnabled?"MIDI clips will repeat for four cycles on playback.":"MIDI loop playback disabled.");
});
$("midiVelocity").addEventListener("input",event=>{
  const selected=selectedNote();
  if(!selected)return;
  selected.note.velocity=Number(event.target.value);
  $("midiVelocityValue").textContent=String(selected.note.velocity);
  window.dispatchEvent(new Event("earthstudio:change"));
  render();
});
$("midiDeleteNote").addEventListener("click",()=>{
  const selected=selectedNote();
  if(!selected)return;
  selected.clip.notes=selected.clip.notes.filter(note=>note.id!==selected.note.id);
  selectedNoteRef=null;
  updateSelectionControls();
  window.dispatchEvent(new Event("earthstudio:change"));
  render();
  app.recalc();
});
async function connectHardwareMidi(){
  if(!navigator.requestMIDIAccess){
    $("midiDeviceStatus").textContent="Web MIDI is unavailable in this browser. Use a supported desktop browser or the on-screen keyboard.";
    return;
  }
  try{
    midiAccess=await navigator.requestMIDIAccess({sysex:false});
    for(const input of midiAccess.inputs.values()){
      if(midiInputs.has(input.id))continue;
      input.onmidimessage=event=>{
        const [statusByte,data1,data2]=event.data;
        const command=statusByte&0xf0,channel=statusByte&0x0f;
        const audioTime=instrument.getAudioContextTime()+((event.timeStamp-performance.now())/1000);
        if(command===0x90&&data2>0)receive({type:"noteOn",note:data1,velocity:data2,channel,audioTime});
        else if(command===0x80||(command===0x90&&data2===0))receive({type:"noteOff",note:data1,channel,audioTime});
      };
      midiInputs.add(input.id);
    }
    const names=[...midiAccess.inputs.values()].map(input=>input.name||input.id);
    $("midiDeviceStatus").textContent=names.length?"Connected MIDI input(s): "+names.join(", "):"MIDI permission granted. Connect a device and refresh the connection.";
    status("Hardware MIDI access ready.");
  }catch(error){
    $("midiDeviceStatus").textContent="MIDI connection failed: "+(error?.message||String(error));
  }
}
$("midiConnect").addEventListener("click",connectHardwareMidi);
if (typeof instrument.onMidiEvent === "function") unsubscribe = instrument.onMidiEvent(receive);

$("stop").addEventListener("click",stopPlayback);
$("clearSession").addEventListener("click",()=>{app.state.midiTracks=[];activeTrackId=null;render();stopPlayback();});
$("newProject").addEventListener("click",()=>{app.state.midiTracks=[];activeTrackId=null;render();stopPlayback();});
window.addEventListener("earthstudio:change",()=>{render();updateSelectionControls();});
window.__earthStudioMidi = {render,stopRecording,getTracks:()=>app.state.midiTracks,onTransportStart:schedulePlayback,onTransportStop:stopPlayback,dispose:()=>{unsubscribe?.();for(const input of midiAccess?.inputs.values()||[])input.onmidimessage=null;}};
render();
