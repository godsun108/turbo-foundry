import {MidiRecorder, MIDI_PPQ, nextQuantizedTick, recordMidiAutomationPoint} from "./midi-sequencer.mjs";

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
    <label class="hint" for="midiAutomationParameter">MODULATION TARGET</label>
    <select id="midiAutomationParameter" style="min-height:40px;background:#0b1017;color:white;border:1px solid var(--line);border-radius:8px;padding:7px"><option value="cutoff">FILTER CUTOFF</option><option value="bend">PITCH BEND</option><option value="vibrato">VIBRATO</option></select>
    <button id="midiLearnCC">LEARN KNOB</button>
    <button id="midiArmAutomation">ARM MODULATION: OFF</button>
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
let selectedNoteRef = null;
let loopEnabled = false;
let activeScene = 0;
let sceneStartAbsoluteTick = 0;
let pendingScene = null;
let midiAccess = null;
const midiInputs = new Set();

const id = prefix => prefix + "-" + crypto.randomUUID();
const status = message => { $("midiRecordStatus").textContent = message; };
const selectedTrack = () => app.state.midiTracks.find(track => track.id === activeTrackId) || app.state.midiTracks[0] || null;
const currentTempo = () => Math.max(40, Math.min(240, Number($("bpm").value) || 120));
const currentDurationTicks = () => Math.max(1, Math.ceil(app.state.duration * currentTempo() * MIDI_PPQ / 60));

function render() {
  reconcileScenes();
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
      const tools=document.createElement("div");tools.className="toolbar";tools.style.marginTop="8px";
      const parameter=document.createElement("select");parameter.setAttribute("aria-label","MIDI automation parameter");
      for(const pair of [["cutoff","FILTER CUTOFF"],["bend","PITCH BEND"],["vibrato","VIBRATO"]])parameter.add(new Option(pair[1],pair[0]));
      const hint=document.createElement("span");hint.className="hint";hint.textContent="PARAMETER LANE · TAP TO ADD / DRAG TO EDIT";
      tools.append(parameter,hint);card.append(tools);
      const lane=document.createElement("div");lane.style.cssText="height:72px;position:relative;border:1px solid var(--line);border-radius:8px;background:#101820;touch-action:none;margin-bottom:12px";
      const svg=document.createElementNS("http://www.w3.org/2000/svg","svg");svg.setAttribute("viewBox","0 0 1000 72");svg.setAttribute("preserveAspectRatio","none");svg.style.cssText="width:100%;height:100%;overflow:visible";
      const path=document.createElementNS("http://www.w3.org/2000/svg","path");path.setAttribute("fill","none");path.setAttribute("stroke","#54e7d1");path.setAttribute("stroke-width","2.5");path.setAttribute("vector-effect","non-scaling-stroke");svg.append(path);lane.append(svg);card.append(lane);
      const lanes=clip.parameterAutomation||(clip.parameterAutomation=[]);
      const ranges={cutoff:[80,18000],bend:[-12,12],vibrato:[0,20]};
      const activeLane=()=>lanes.find(item=>item.parameter===parameter.value);
      const coordinates=point=>{const range=ranges[parameter.value];return {x:point.tick/Math.max(1,clip.lengthTicks)*1000,y:66-(point.value-range[0])/(range[1]-range[0])*58}};
      const drawLane=()=>{const active=activeLane(),points=active?.points||[];path.setAttribute("d",points.length?"M "+points.map(point=>{const pos=coordinates(point);return pos.x+" "+pos.y}).join(" L "):"");svg.querySelectorAll("circle").forEach(node=>node.remove());points.forEach(point=>{const pos=coordinates(point),dot=document.createElementNS("http://www.w3.org/2000/svg","circle");dot.setAttribute("cx",pos.x);dot.setAttribute("cy",pos.y);dot.setAttribute("r","5");dot.setAttribute("fill","#f8ffb0");dot.setAttribute("stroke","#10201e");dot.setAttribute("stroke-width","1.5");dot.addEventListener("pointerdown",event=>{event.preventDefault();event.stopPropagation();const move=ev=>{const rect=lane.getBoundingClientRect(),range=ranges[parameter.value];point.tick=Math.max(0,Math.min(clip.lengthTicks,Math.round((ev.clientX-rect.left)/rect.width*clip.lengthTicks)));point.value=Math.max(range[0],Math.min(range[1],range[0]+(range[1]-range[0])*(rect.bottom-ev.clientY)/rect.height));active.points.sort((a,b)=>a.tick-b.tick);drawLane()};const finish=()=>{window.removeEventListener("pointermove",move);window.removeEventListener("pointerup",finish);window.dispatchEvent(new Event("earthstudio:change"));app.recalc();render()};window.addEventListener("pointermove",move);window.addEventListener("pointerup",finish,{once:true})});svg.append(dot)})};
      parameter.addEventListener("change",drawLane);
      lane.addEventListener("pointerdown",event=>{if(event.target.closest("circle"))return;const rect=lane.getBoundingClientRect(),range=ranges[parameter.value],tick=Math.max(0,Math.min(clip.lengthTicks,Math.round((event.clientX-rect.left)/rect.width*clip.lengthTicks))),value=Math.max(range[0],Math.min(range[1],range[0]+(range[1]-range[0])*(rect.bottom-event.clientY)/rect.height));let active=activeLane();if(!active){active={parameter:parameter.value,points:[]};lanes.push(active)}const found=active.points.findIndex(point=>Math.abs(point.tick-tick)<30);if(found>=0)active.points.splice(found,1);else active.points.push({tick,value});active.points.sort((a,b)=>a.tick-b.tick);drawLane();window.dispatchEvent(new Event("earthstudio:change"))});
      drawLane();
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
    const transportPosition = window.__earthStudioTransport?.snapshot?.();
    recorder.start({tempo:currentTempo(),startTick:transportPosition?.tick||0,quantizeTicks:Number($("midiQuantize").value)||0});
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
  const take = recorder.toClip({id:id("midi-clip")});
  if (overdub && track.midiClips.length) {
    const previous = track.midiClips[track.midiClips.length-1];
    const takeOffset = Math.max(0,take.startTick-previous.startTick);
    const notes = [...previous.notes,...take.notes.map(note=>({...note,id:id("note"),startTick:takeOffset+note.startTick}))];
    const lengthTicks = Math.max(previous.lengthTicks,takeOffset+take.lengthTicks,...notes.map(note=>note.startTick+note.durationTicks));
    track.midiClips[track.midiClips.length-1] = {...previous,notes,lengthTicks};
  } else {
    const sceneIndex=track.midiClips.length;
    track.midiClips.push(take);
    const snapshot=window.__earthStudioTransport?.snapshot?.()||{absoluteTick:0,playing:false};
    launchScene(sceneIndex,snapshot.absoluteTick,snapshot.playing);
  }
  recording = false;
  recorder = null;
  $("midiRecord").disabled = false;
  $("midiStop").disabled = true;
  window.dispatchEvent(new Event("earthstudio:change"));
  window.dispatchEvent(new Event("earthstudio:scenechange"));
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
function captureModulation(controller,value,channel){
  if(learningController){
    learnedController=controller;
    learningController=false;
    $("midiLearnCC").textContent="LEARN KNOB · CC "+controller;
    status("MIDI CC "+controller+" learned. Arm modulation and play to record it.");
    return;
  }
  if(!modulationArmed||learnedController===null||controller!==learnedController)return;
  const track=selectedTrack();
  const clip=track?.midiClips?.[activeScene];
  const snapshot=window.__earthStudioTransport?.snapshot?.();
  if(!clip||!snapshot?.playing){
    status("Start playback in the target scene to record modulation.");
    return;
  }
  const parameter=$("midiAutomationParameter").value;
  const ranges={cutoff:[80,18000],bend:[-12,12],vibrato:[0,20]};
  const range=ranges[parameter];
  const normalized=parameter==="cutoff"
    ? range[0]*Math.pow(range[1]/range[0],value/127)
    : range[0]+(range[1]-range[0])*(value/127);
  const relativeTick=Math.max(0,(snapshot.tick??snapshot.absoluteTick)-sceneStartAbsoluteTick);
  try{
    recordMidiAutomationPoint(clip,parameter,relativeTick,normalized,{quantizeTicks});
    modulationDirty=true;
    status("Recording "+parameter+" · MIDI CC "+controller+" · "+Math.round(relativeTick)+" ticks");
  }catch(error){status("Modulation capture error: "+(error?.message||String(error)));}
}
$("midiLearnCC").addEventListener("click",()=>{
  learningController=true;
  $("midiLearnCC").textContent="MOVE A KNOB…";
  status("Move the hardware knob or fader you want to assign.");
});
$("midiArmAutomation").addEventListener("click",()=>{
  modulationArmed=!modulationArmed;
  $("midiArmAutomation").textContent="ARM MODULATION: "+(modulationArmed?"ON":"OFF");
  if(!modulationArmed&&modulationDirty){
    modulationDirty=false;
    window.dispatchEvent(new Event("earthstudio:change"));
    app.recalc();
    status("Modulation take saved to the selected MIDI clip.");
  }else status(modulationArmed?"Modulation armed · start playback and move the learned control.":"Modulation capture disarmed.");
});
function stopPlayback() {
  try { instrument.allNotesOff(); } catch {}
}
$("midiRecord").addEventListener("click",startRecording);
$("midiStop").addEventListener("click",stopRecording);
$("midiOverdub").addEventListener("click",()=>{overdub=!overdub;$("midiOverdub").textContent="OVERDUB: "+(overdub?"ON":"OFF");});
$("midiLoop").addEventListener("click",()=>{
  loopEnabled=!loopEnabled;
  app.state.midiLoopRepeats=loopEnabled?4:1;
  app.state.midiLoopEnabled=loopEnabled;
  $("midiLoop").textContent="MIDI LOOP ×4: "+(loopEnabled?"ON":"OFF");
  window.dispatchEvent(new Event("earthstudio:transport-config"));
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
    midiInputs.clear();
    for(const input of midiAccess.inputs.values()){
      input.onmidimessage=event=>{
        const [statusByte,data1,data2]=event.data;
        const command=statusByte&0xf0,channel=statusByte&0x0f;
        if(command===0xb0){captureModulation(data1,data2,channel);window.dispatchEvent(new CustomEvent("earthstudio:controlchange",{detail:{controller:data1,value:data2,channel}}));return;}
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
window.addEventListener("earthstudio:change",()=>{reconcileScenes();render();updateSelectionControls();});
function sceneCount(){
  const midiCount=Math.max(0,...app.state.midiTracks.map(track=>(track.midiClips||[]).length));
  const audioCount=Math.max(0,...app.state.tracks.map(track=>(Number.isInteger(track.sceneIndex)?track.sceneIndex:0)+1));
  return Math.max(midiCount,audioCount);
}
function reconcileScenes(){
  const count=sceneCount();
  let changed=false;
  if(!count&&activeScene!==null){activeScene=null;pendingScene=null;sceneStartAbsoluteTick=0;changed=true;}
  else if(count&&activeScene===null){activeScene=0;pendingScene=null;sceneStartAbsoluteTick=0;changed=true;}
  else if(count&&activeScene!==null&&activeScene>=count){activeScene=0;pendingScene=null;sceneStartAbsoluteTick=0;changed=true;}
  if(pendingScene&&pendingScene.index>=count){pendingScene=null;changed=true;}
  if(changed)window.dispatchEvent(new Event("earthstudio:scenechange"));
}
function launchScene(index,absoluteTick=window.__earthStudioTransport?.snapshot?.().absoluteTick||0,playing=!!window.__earthStudioTransport?.snapshot?.().playing){
  if(!Number.isInteger(index)||index<0||index>=sceneCount())return false;
  pendingScene=playing?{index,tick:nextQuantizedTick(absoluteTick,4*MIDI_PPQ)}:null;
  if(!playing){activeScene=index;sceneStartAbsoluteTick=absoluteTick;window.dispatchEvent(new Event("earthstudio:scenechange"));}
  else status("Scene "+(index+1)+" queued for the next bar.");
  return true;
}
function advanceScene(absoluteTick){
  if(!pendingScene||absoluteTick<pendingScene.tick)return false;
  activeScene=pendingScene.index;sceneStartAbsoluteTick=pendingScene.tick;pendingScene=null;
  window.dispatchEvent(new Event("earthstudio:scenechange"));
  status("Scene "+(activeScene+1)+" launched.");
  return true;
}
function stopScene(){pendingScene=null;activeScene=null;sceneStartAbsoluteTick=0;stopPlayback();window.dispatchEvent(new Event("earthstudio:scenechange"));}
function resetSceneSelection(){activeScene=sceneCount()?0:null;pendingScene=null;sceneStartAbsoluteTick=0;window.dispatchEvent(new Event("earthstudio:scenechange"));}
window.__earthStudioMidi = {
  render,stopRecording,getTracks:()=>app.state.midiTracks,
  getClips:()=>{const tracks=app.state.midiTracks;const anySolo=tracks.some(track=>track.solo);return activeScene===null?[]:tracks.flatMap(track=>(track.muted||(anySolo&&!track.solo))?[]:((track.midiClips||[])[activeScene]?[{...(track.midiClips||[])[activeScene],startTick:sceneStartAbsoluteTick,trackId:track.id}]:[]));},
  getSceneInfo:()=>({count:sceneCount(),active:activeScene,startTick:sceneStartAbsoluteTick,pending:pendingScene?{index:pendingScene.index,tick:pendingScene.tick}:null,audioTrackCount:app.state.tracks.filter(track=>(Number.isInteger(track.sceneIndex)?track.sceneIndex:0)===activeScene).length}),
  getAudioTracks:()=>{const tracks=app.state.tracks;const anySolo=tracks.some(track=>track.solo);return activeScene===null?[]:tracks.filter(track=>(Number.isInteger(track.sceneIndex)?track.sceneIndex:0)===activeScene&&!track.muted&&(!anySolo||track.solo));},
  launchScene,advanceScene,stopScene,resetSceneSelection,isLoopEnabled:()=>loopEnabled,
  onTransportStart:()=>{},onTransportStop:stopPlayback,
  dispose:()=>{unsubscribe?.();for(const input of midiAccess?.inputs.values()||[])input.onmidimessage=null;}
};
render();
window.dispatchEvent(new Event("earthstudio:midi-ready"));
