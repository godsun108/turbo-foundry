import { validateSoulXPhones } from "./soulx-phone-inventory.js";
const $ = (id) => document.getElementById(id);
let score = null;
let drafts = {};
let controls = {};
let reviewFlags = {};
const phrasesRoot = $("phrases");

function setStatus(message) { $("status").textContent = message; }
function safeNumber(value) { if(value===null || value===undefined || String(value).trim()==="") return null; const n = Number(value); return Number.isFinite(n) ? n : null; }
function download(name, data) {
  const blob = new Blob([JSON.stringify(data, null, 2) + "\n"], {type:"application/json"});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a"); a.href=url; a.download=name;
  document.body.append(a); a.click(); a.remove(); URL.revokeObjectURL(url);
}
function isWorkbench(data) {
  return data && data.format === "turbo.music-foundry.vocal-score-workbench.v1" &&
    data.score && Array.isArray(data.score.phrases) && data.drafts && typeof data.drafts === "object";
}
function phraseDraft(phrase) {
  const existing = Array.isArray(phrase.lyric_units) ? phrase.lyric_units : [];
  const words = phrase.text.trim().split(/\s+/);
  return words.map((word, index) => {
    const unit = existing[index] || {};
    return {
      text: word,
      phonemes: Array.isArray(unit.phonemes) ? unit.phonemes.join(" ") : "",
      onset: unit.onset_beats ?? "",
      duration: unit.duration_beats ?? "",
      pitch: unit.midi_pitch ?? "",
      noteType: unit.note_type || "normal"
    };
  });
}
function render() {
  phrasesRoot.replaceChildren();
  controls = {};
  if (!score) return;
  $("tempo").value = score.tempo_bpm ?? 127;
  $("tempoLock").value = score.tempo_status || "provisional";
  for (const phrase of score.phrases.filter(p => p.delivery === "sung" || p.delivery === "chant")) {
    const card = document.createElement("section"); card.className="phrase";
    const heading=document.createElement("h2"); heading.textContent=phrase.id+" · "+phrase.text; card.append(heading);
    const meta=document.createElement("p"); meta.className="small muted";
    meta.textContent="Phrase status: "+(phrase.alignment_status || "unaligned")+" · Phrase start/duration are required.";
    card.append(meta);
    const timing=document.createElement("div"); timing.className="row";
    const start=makeField("Phrase start beat", phrase.start_beat ?? "", "number", "phrase-start");
    const duration=makeField("Phrase duration (beats)", phrase.duration_beats ?? "", "number", "phrase-duration");
    timing.append(start.wrap,duration.wrap); card.append(timing);
    const rows=drafts[phrase.id] || phraseDraft(phrase); drafts[phrase.id]=rows;
    rows.forEach((unit,index) => {
      const box=document.createElement("div"); box.className="word";
      const h=document.createElement("h3"); h.textContent=(index+1)+". "+unit.text; box.append(h);
      const fields=document.createElement("div"); fields.className="row";
      const phones=makeField("ARPABET phones","", "text","phones");
      phones.input.value=unit.phonemes;
      const onset=makeField("Onset (beats)",unit.onset,"number","onset");
      const dur=makeField("Duration (beats)",unit.duration,"number","duration");
      const pitch=makeField("MIDI pitch",unit.pitch,"number","pitch");
      const type=makeField("Note type",unit.noteType,"select","noteType");
      type.input.replaceChildren(...["normal","tie"].map(v=>{const o=document.createElement("option");o.value=v;o.textContent=v;return o;}));
      type.input.value=unit.noteType;
      fields.append(phones.wrap,onset.wrap,dur.wrap,pitch.wrap,type.wrap);
      box.append(fields);
      [phones.input,onset.input,dur.input,pitch.input,type.input].forEach(input=>{
        input.addEventListener("input",()=>{unit.phonemes=phones.input.value;unit.onset=onset.input.value;unit.duration=dur.input.value;unit.pitch=pitch.input.value;unit.noteType=type.input.value;});
        input.addEventListener("change",()=>{unit.phonemes=phones.input.value;unit.onset=onset.input.value;unit.duration=dur.input.value;unit.pitch=pitch.input.value;unit.noteType=type.input.value;});
      });
      card.append(box);
    });
    const reviewLabel=document.createElement("label");
    const review=document.createElement("input"); review.type="checkbox"; review.checked=reviewFlags[phrase.id] ?? (phrase.alignment_status==="reviewed");
    review.style.width="auto"; review.style.marginRight="8px";
    review.addEventListener("change",()=>{reviewFlags[phrase.id]=review.checked;});
    reviewLabel.append(review,document.createTextNode(" I have reviewed every pronunciation, note, and timing value in this phrase."));
    card.append(reviewLabel);
    const anchor=document.createElement("input"); anchor.type="hidden"; anchor.value=phrase.id;
    controls[phrase.id]={startInput:start.input,durationInput:duration.input,reviewInput:review};
    phrasesRoot.append(card);
  }
  $("saveWork").disabled=false;
  $("exportScore").disabled=false;
  setStatus("Loaded "+score.phrases.filter(p=>p.delivery==="sung"||p.delivery==="chant").length+" sung/chant phrases. No score values have been inferred.");
}
function makeField(label,value,type,kind) {
  const wrap=document.createElement("div"); const l=document.createElement("label"); l.textContent=label; wrap.append(l);
  let input;
  if(type==="select"){input=document.createElement("select");}
  else {input=document.createElement("input");input.type=type; if(type==="number"){input.step="0.001";}}
  input.value=value; input.dataset.kind=kind; wrap.append(input); return {wrap,input};
}
function collectPhrase(phrase) {
  const rows=drafts[phrase.id] || [];
  const control=controls[phrase.id] || {};
  const start=safeNumber(control.startInput?.value ?? phrase.start_beat);
  const phraseDuration=safeNumber(control.durationInput?.value ?? phrase.duration_beats);
  const errors=[];
  if(start===null || start<0) errors.push(phrase.id+": invalid phrase start beat");
  if(phraseDuration===null || phraseDuration<=0) errors.push(phrase.id+": invalid phrase duration");
  const expected=phrase.text.trim().split(/\s+/);
  if(rows.length!==expected.length || rows.some((u,i)=>u.text!==expected[i])) errors.push(phrase.id+": word tokens do not exactly match source lyric");
  let cursor=0;
  const units=rows.map((u,index)=>{
    const onset=safeNumber(u.onset), duration=safeNumber(u.duration), pitch=safeNumber(u.pitch);
    const phones=u.phonemes.trim().split(/\s+/).filter(Boolean);
    if(!phones.length) errors.push(phrase.id+" word "+(index+1)+": reviewed phonemes required");
    for(const phoneError of validateSoulXPhones(phones)) errors.push(phrase.id+" word "+(index+1)+": "+phoneError);
    if(onset===null || Math.abs(onset-cursor)>1e-6) errors.push(phrase.id+" word "+(index+1)+": onset must continue exactly from prior unit (starting at 0)");
    if(duration===null || duration<=0) errors.push(phrase.id+" word "+(index+1)+": positive duration required");
    if(pitch===null || !Number.isInteger(pitch) || pitch<1 || pitch>127) errors.push(phrase.id+" word "+(index+1)+": MIDI pitch must be an integer from 1 to 127");
    if(u.noteType!=="normal" && u.noteType!=="tie") errors.push(phrase.id+" word "+(index+1)+": unsupported note type");
    if(duration!==null && duration>0) cursor=(onset??cursor)+duration;
    return {text:u.text,phonemes:phones,onset_beats:onset,duration_beats:duration,midi_pitch:pitch,note_type:u.noteType};
  });
  if(phraseDuration!==null && Math.abs(cursor-phraseDuration)>1e-6) errors.push(phrase.id+": note units must fill the phrase duration exactly");
  if(!(control.reviewInput?.checked ?? reviewFlags[phrase.id] ?? (phrase.alignment_status==="reviewed")) ) errors.push(phrase.id+": human review checkbox required");
  return {errors,units,start,phraseDuration};
}
function collectAll() {
  const output=JSON.parse(JSON.stringify(score));
  const errors=[];
  output.tempo_bpm=safeNumber($("tempo").value);
  output.tempo_status=$("tempoLock").value;
  if(output.tempo_bpm===null || output.tempo_bpm<=0) errors.push("Tempo must be a positive number.");
  if(output.tempo_status!=="locked") errors.push("Lock the performance tempo before canonical singing export.");
  const sung=output.phrases.filter(p=>p.delivery==="sung"||p.delivery==="chant");
  for(const phrase of sung){
    const source=score.phrases.find(p=>p.id===phrase.id);
    const result=collectPhrase(source);
    errors.push(...result.errors);
    phrase.start_beat=result.start;
    phrase.duration_beats=result.phraseDuration;
    phrase.lyric_units=result.units;
    phrase.alignment_status="reviewed";
  }
  if(errors.length) return {errors};
  output.score_status="reviewed";
  return {output,errors:[]};
}
$("scoreFile").addEventListener("change",async event=>{
  const file=event.target.files?.[0]; if(!file)return;
  try{
    const data=JSON.parse(await file.text());
    if(isWorkbench(data)){score=data.score;drafts=data.drafts;reviewFlags=data.reviewFlags||{};}
    else if(data && Array.isArray(data.phrases)){score=data;drafts={};}
    else throw new Error("This file is not a supported vocal score or workbench file.");
    for(const p of score.phrases){if((p.delivery==="sung"||p.delivery==="chant")&&!drafts[p.id]) drafts[p.id]=phraseDraft(p);}
    render();
  }catch(error){setStatus("Could not open file: "+error.message);}
});
$("saveWork").addEventListener("click",()=>{
  if(!score)return;
  for(const phrase of score.phrases.filter(p=>p.delivery==="sung"||p.delivery==="chant")){
    const control=controls[phrase.id] || {};
    phrase.start_beat=safeNumber(control.startInput?.value ?? phrase.start_beat);
    phrase.duration_beats=safeNumber(control.durationInput?.value ?? phrase.duration_beats);
  }
  download("vocal-score-workbench.json",{format:"turbo.music-foundry.vocal-score-workbench.v1",score,drafts,reviewFlags});
  setStatus("Saved workbench file. This preserves incomplete draft fields without marking the score reviewed.");
});
$("exportScore").addEventListener("click",()=>{
  if(!score)return;
  const result=collectAll();
  if(result.errors.length){setStatus("Export blocked:\n• "+result.errors.join("\n• "));return;}
  download("vocal_score.reviewed.json",result.output);
  setStatus("Reviewed vocal score exported. The original imported file was not modified.");
});
