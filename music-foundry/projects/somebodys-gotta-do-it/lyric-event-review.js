import { validateLyricEventManifest } from "./lyric-event-review-core.mjs";
const $ = (id) => document.getElementById(id);
const labels = {intro_tag:"Intro tag",verse_1:"Verse 1",pre:"Pre",chorus:"Chorus",verse_2:"Verse 2",bridge_half_time:"Bridge — half-time chaos",final_chorus_outro:"Final chorus / outro"};
let manifest = null;
let sourceText = null;
function reset(message) {
  manifest = null; $("events").replaceChildren(); $("summary").textContent = "";
  $("section").disabled = true; $("search").disabled = true; $("status").textContent = message;
}
function render() {
  const root = $("events"); root.replaceChildren();
  const section = $("section").value, query = $("search").value.toLocaleLowerCase();
  const visible = manifest.events.filter(event => (!section || event.section_id === section) && (!query || event.text.toLocaleLowerCase().includes(query)));
  for (const event of visible) {
    const article = document.createElement("article"); article.className = "event";
    const meta = document.createElement("div"); meta.className = "meta";
    const name = document.createElement("strong"); name.textContent = labels[event.section_id] || event.section_id;
    const line = document.createElement("span"); line.className = "tag"; line.textContent = "Cue sheet line " + event.source_line;
    const timing = document.createElement("span"); timing.className = "tag"; timing.textContent = "Timing unplaced";
    const text = document.createElement("p"); text.textContent = event.text;
    meta.append(name,line,timing); article.append(meta,text); root.append(article);
  }
  $("summary").textContent = visible.length + " of " + manifest.events.length + " source-verified lyric events · all timing remains unplaced.";
  if (!visible.length) root.textContent = "No lyric lines match this filter.";
}
async function verify() {
  if (sourceText === null || !$("manifest").files?.[0]) { reset("Choose both the canonical cue sheet and generated manifest to verify the lyrics."); return; }
  try {
    const data = JSON.parse(await $("manifest").files[0].text());
    const errors = await validateLyricEventManifest(data, sourceText);
    if (errors.length) throw new Error(errors.join("\n"));
    manifest = data;
    $("section").replaceChildren(new Option("All sections",""));
    for (const [id,label] of Object.entries(labels)) if (data.events.some(item=>item.section_id===id)) $("section").add(new Option(label,id));
    $("section").disabled = false; $("search").disabled = false; render();
    $("status").textContent = "SOURCE VERIFIED: " + data.events.length + " lyric events exactly match the canonical cue sheet and SHA-256. Review only; timing is not locked.";
  } catch(error) { reset("Manifest rejected: " + error.message); }
}
$("source").addEventListener("change", async event => {
  const file = event.target.files?.[0]; sourceText = file ? await file.text() : null; await verify();
});
$("manifest").addEventListener("change", verify);
$("section").addEventListener("change",()=>{if(manifest)render();});
$("search").addEventListener("input",()=>{if(manifest)render();});
