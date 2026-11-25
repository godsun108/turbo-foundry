const app = window.__earthStudio;
if (!app) throw new Error("EARTH STUDIO performance surface could not find the studio host.");
async function waitForGlobal(key,eventName) {
  if (window[key]) return window[key];
  return await new Promise(resolve=>window.addEventListener(eventName,()=>resolve(window[key]),{once:true}));
}
const instrument = await waitForGlobal("__earthInstrument","earthstudio:instrument-ready");
const midi = await waitForGlobal("__earthStudioMidi","earthstudio:midi-ready");
const $ = id => document.getElementById(id);
const targets = [
  {id:"attack",label:"ATTACK",scale:"linear"},
  {id:"decay",label:"DECAY",scale:"linear"},
  {id:"sustain",label:"SUSTAIN",scale:"linear"},
  {id:"release",label:"RELEASE",scale:"linear"},
  {id:"cutoff",label:"FILTER CUTOFF",scale:"log"},
  {id:"vibrato",label:"VIBRATO",scale:"linear"},
  {id:"bend",label:"PITCH BEND",scale:"linear"}
];
let mappings = {};
let learningTarget = null;


const panel=document.createElement("section");
panel.className="panel";
panel.id="performanceSurface";
panel.innerHTML=`
  <div class="track-head"><h2>PERFORMANCE SURFACE</h2><span class="tag">SCENES · MIDI CONTROL</span></div>
  <p class="hint">Launch aligned audio and MIDI scenes. Assign audio tracks to a scene in the timeline; while playing, scene changes wait for the next 4/4 bar. Hardware control mappings are saved with this project.</p>
  <div id="sceneLauncher" class="scene-grid"></div>
  <div class="toolbar" style="margin-top:9px"><span class="hint" id="sceneStatus" role="status" aria-live="polite">No scenes yet. Add an audio track or record a MIDI take to create your first scene.</span><button id="stopMidiScene" class="ghost">STOP MIDI SCENE</button></div>
  <div class="track-head" style="margin-top:18px"><h2>HARDWARE CONTROL LEARN</h2><span class="hint">MIDI CC · 0–127</span></div>
  <div id="ccMappings" class="cc-grid"></div>
  <div class="hint" id="ccStatus" role="status" aria-live="polite" style="margin-top:8px">Connect a MIDI controller, then tap LEARN beside a parameter and move a knob or fader.</div>
`;
const midiPanel=$("midiRecorderPanel");
midiPanel.after(panel);
const style=document.createElement("style");
style.textContent=`
.scene-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin-top:12px}
.scene-launch{min-width:0;min-height:76px;text-align:left;display:flex;flex-direction:column;justify-content:space-between;gap:4px}
.scene-launch.active{border-color:var(--acid);box-shadow:inset 0 0 0 1px var(--acid);background:#27351c}
.scene-launch.pending{border-color:var(--violet);color:#d9ceff}
.scene-launch small{font-size:10px;color:var(--muted);font-weight:500}
.cc-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-top:10px}
.cc-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:8px;align-items:center;padding:9px;background:#10151d;border:1px solid var(--line);border-radius:10px}
.cc-row strong{display:block;font-size:11px}
.cc-row small{display:block;color:var(--muted);font-size:10px;margin-top:2px}
.cc-row button{min-height:34px;padding:6px 9px;font-size:10px}
.cc-row button.learning{border-color:var(--violet);color:#d9ceff}
@media(max-width:600px){.scene-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.cc-grid{grid-template-columns:1fr}}
`;
document.head.append(style);

function persistMappings(){
  window.dispatchEvent(new Event("earthstudio:performancechange"));
  window.dispatchEvent(new Event("earthstudio:change"));
}
function setMappings(value={}){
  const next={};
  if(value&&typeof value==="object"&&!Array.isArray(value)){
    for(const target of targets){
      const mapping=value[target.id];
      if(mapping&&Number.isInteger(mapping.controller)&&mapping.controller>=0&&mapping.controller<=127){
        next[target.id]={controller:mapping.controller};
      }
    }
  }
  mappings=next;
  renderMappings();
}
function renderScenes(){
  const root=$("sceneLauncher");
  root.replaceChildren();
  const info=midi.getSceneInfo();
  if(!info.count){
    const empty=document.createElement("div");
    empty.className="empty";
    empty.textContent="No scenes yet. Record MIDI takes on one or more instrument tracks.";
    root.append(empty);
    $("sceneStatus").textContent="No audio or MIDI scenes available.";
    return;
  }
  for(let index=0;index<info.count;index++){
    const tracks=midi.getTracks();
    const populated=tracks.filter(track=>(track.midiClips||[])[index]).length;
    const audioPopulated=app.state.tracks.filter(track=>(Number.isInteger(track.sceneIndex)?track.sceneIndex:0)===index).length;
    const button=document.createElement("button");
    button.className="scene-launch"+(info.active===index?" active":"")+(info.pending?.index===index?" pending":"");
    const title=document.createElement("strong");
    title.textContent="SCENE "+String(index+1).padStart(2,"0");
    const detail=document.createElement("small");
    detail.textContent=audioPopulated+" audio · "+populated+" MIDI tracks";
    button.append(title,detail);
    button.setAttribute("aria-pressed",String(info.active===index));
    button.addEventListener("click",()=>{
      const snapshot=window.__earthStudioTransport?.snapshot?.()||{absoluteTick:0,playing:false};
      midi.launchScene(index,snapshot.absoluteTick,snapshot.playing);
      renderScenes();
    });
    root.append(button);
  }
  if(info.pending){
    $("sceneStatus").textContent="Scene "+(info.pending.index+1)+" queued · launches at tick "+info.pending.tick+".";
  }else if(info.active===null){
    $("sceneStatus").textContent="No MIDI scene active.";
  }else{
    $("sceneStatus").textContent="Scene "+(info.active+1)+" active.";
  }
}
function renderMappings(){
  const root=$("ccMappings");
  root.replaceChildren();
  for(const target of targets){
    const row=document.createElement("div");
    row.className="cc-row";
    const description=document.createElement("div");
    const name=document.createElement("strong");
    name.textContent=target.label;
    const detail=document.createElement("small");
    detail.textContent=mappings[target.id]?"MIDI CC "+mappings[target.id].controller:"Not assigned";
    description.append(name,detail);
    const button=document.createElement("button");
    button.className=learningTarget===target.id?"learning":"";
    button.textContent=learningTarget===target.id?"MOVE CONTROL":"LEARN";
    button.addEventListener("click",()=>{
      learningTarget=learningTarget===target.id?null:target.id;
      $("ccStatus").textContent=learningTarget?"Move a hardware knob or fader for "+target.label+".":"MIDI learn cancelled.";
      renderMappings();
    });
    row.append(description,button);
    root.append(row);
  }
}
function applyCC(targetId,value){
  const target=targets.find(item=>item.id===targetId);
  const input=$(targetId);
  if(!target||!input)return;
  const min=Number(input.min),max=Number(input.max),normalized=value/127;
  const mapped=target.scale==="log"&&min>0?min*Math.pow(max/min,normalized):min+(max-min)*normalized;
  input.value=String(Math.round(mapped));
  input.dispatchEvent(new Event("input",{bubbles:true}));
}
window.addEventListener("earthstudio:controlchange",event=>{
  const detail=event.detail;
  if(!detail||!Number.isInteger(detail.controller)||!Number.isInteger(detail.value))return;
  if(learningTarget){
    mappings[learningTarget]={controller:detail.controller};
    const label=targets.find(target=>target.id===learningTarget)?.label||learningTarget;
    learningTarget=null;
    persistMappings();
    renderMappings();
    $("ccStatus").textContent=label+" assigned to MIDI CC "+detail.controller+".";
    return;
  }
  for(const target of targets){
    if(mappings[target.id]?.controller===detail.controller)applyCC(target.id,detail.value);
  }
});
$("stopMidiScene").addEventListener("click",()=>{
  midi.stopScene();
  instrument.cancelScheduledMidi?.();
  instrument.allNotesOff();
  renderScenes();
});
window.addEventListener("earthstudio:scenechange",renderScenes);
window.addEventListener("earthstudio:change",renderScenes);
renderScenes();
renderMappings();
window.__earthStudioPerformance={
  getMappings:()=>JSON.parse(JSON.stringify(mappings)),
  setMappings,
  clearMappings:()=>setMappings({})
};
window.dispatchEvent(new Event("earthstudio:performance-ready"));
