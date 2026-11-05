export function validateLyricEventManifest(data) {
  const errors = [];
  if (!data || typeof data !== "object" || Array.isArray(data)) return ["Manifest must be a JSON object."];
  if (data.schema !== "turbo.music-foundry.lyric-events.v1") errors.push("Unsupported lyric event schema.");
  if (data.source_ref !== "music-foundry/projects/somebodys-gotta-do-it/cue-sheet.md") errors.push("Source must be the canonical cue sheet.");
  if (data.lyric_authority !== "source_ref") errors.push("Canonical source reference must remain authoritative.");
  if (data.timing_policy !== "editorial_grid_not_performance_locked") errors.push("Timing policy must remain editorial and unlocked.");
  if (!Array.isArray(data.events) || !data.events.length) return [...errors, "Manifest must contain lyric events."];
  const ids = new Set(); let previousLine = 0;
  for (const [index, event] of data.events.entries()) {
    const prefix = `Event ${index + 1}: `;
    if (!event || typeof event !== "object") { errors.push(prefix + "must be an object."); continue; }
    if (typeof event.event_id !== "string" || !event.event_id || ids.has(event.event_id)) errors.push(prefix + "event ID must be unique and non-empty.");
    ids.add(event.event_id);
    if (!Number.isInteger(event.source_line) || event.source_line <= previousLine) errors.push(prefix + "source lines must be positive and strictly increasing.");
    if (Number.isInteger(event.source_line)) previousLine = event.source_line;
    if (typeof event.text !== "string" || !event.text.trim()) errors.push(prefix + "source text must be non-empty.");
    const t = event.timing;
    if (!t || t.status !== "unplaced" || t.bar !== null || t.beat !== null || t.marker_ref !== null) errors.push(prefix + "timing must remain explicitly unplaced.");
  }
  return errors;
}
const $ = (id) => document.getElementById(id);
const labels = {intro_tag:"Intro tag",verse_1:"Verse 1",pre:"Pre",chorus:"Chorus",verse_2:"Verse 2",bridge_half_time:"Bridge — half-time chaos",final_chorus_outro:"Final chorus / outro"};
let manifest = null;
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
  $("summary").textContent = visible.length + " of " + manifest.events.length + " source-linked lyric events · all timing remains unplaced.";
  if (!visible.length) root.textContent = "No lyric lines match this filter.";
}
$("manifest").addEventListener("change", async event => {
  const file = event.target.files?.[0]; if (!file) return;
  try {
    const data = JSON.parse(await file.text()), errors = validateLyricEventManifest(data);
    if (errors.length) throw new Error(errors.join("\n"));
    manifest = data; $("section").replaceChildren(new Option("All sections",""));
    for (const [id,label] of Object.entries(labels)) if (data.events.some(item=>item.section_id===id)) $("section").add(new Option(label,id));
    $("section").disabled=false; $("search").disabled=false; render();
    $("status").textContent="Verified "+data.events.length+" events against the canonical source reference. Review only; timing is not locked.";
  } catch(error) {
    manifest=null; $("events").replaceChildren(); $("summary").textContent="";
    $("status").textContent="Manifest rejected: "+error.message; $("section").disabled=true; $("search").disabled=true;
  }
});
$("section").addEventListener("change",()=>{if(manifest)render();});
$("search").addEventListener("input",()=>{if(manifest)render();});
