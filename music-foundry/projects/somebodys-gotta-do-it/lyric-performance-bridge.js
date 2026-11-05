import { buildVerifiedPerformanceCueSheet } from "./lyric-performance-bridge-core.mjs";
const $ = id => document.getElementById(id);
const labels = {intro_tag:"Intro tag",verse_1:"Verse 1",pre:"Pre",chorus:"Chorus",verse_2:"Verse 2",bridge_half_time:"Bridge — half-time chaos",final_chorus_outro:"Final chorus / outro"};
let verifiedSheet = null;
function setStatus(message, error = false) {
  $("lyricBridgeStatus").textContent = message;
  $("lyricBridgeStatus").style.color = error ? "#ff9b62" : "";
}
function renderEvents() {
  const root = $("lyricEventList");
  root.replaceChildren();
  if (!verifiedSheet) return;
  const section = $("lyricSectionFilter").value;
  const events = verifiedSheet.events.filter(event => !section || event.section_id === section);
  for (const event of events) {
    const row = document.createElement("div"); row.className = "automation-point";
    const copy = document.createElement("div");
    const title = document.createElement("strong");
    title.textContent = (labels[event.section_id] || event.section_id) + " · source line " + event.source_line;
    const lyric = document.createElement("div"); lyric.textContent = event.text;
    const timing = document.createElement("small"); timing.textContent = "Unplaced · no performance timing inferred";
    copy.append(title, lyric, timing); row.append(copy); root.append(row);
  }
  $("lyricEventCount").textContent = events.length + " shown · " + verifiedSheet.event_count + " verified";
}
async function verifyFiles() {
  verifiedSheet = null;
  $("exportPerformanceCues").disabled = true;
  $("lyricSectionFilter").disabled = true;
  $("lyricEventList").replaceChildren();
  $("lyricEventCount").textContent = "Not verified";
  const sourceFile = $("lyricSourceFile").files?.[0], manifestFile = $("lyricManifestFile").files?.[0];
  if (!sourceFile || !manifestFile) { setStatus("Choose both the canonical cue sheet and generated manifest."); return; }
  try {
    const sourceText = await sourceFile.text();
    const manifest = JSON.parse(await manifestFile.text());
    verifiedSheet = await buildVerifiedPerformanceCueSheet(manifest, sourceText);
    $("lyricSectionFilter").replaceChildren(new Option("All sections", ""));
    for (const [id, label] of Object.entries(labels)) {
      if (verifiedSheet.events.some(event => event.section_id === id)) $("lyricSectionFilter").add(new Option(label, id));
    }
    $("lyricSectionFilter").disabled = false;
    $("exportPerformanceCues").disabled = false;
    renderEvents();
    setStatus("SOURCE VERIFIED · " + verifiedSheet.event_count + " exact lyric events. Original wording preserved; all timing remains unplaced.");
  } catch (error) { setStatus("Cue sheet rejected: " + error.message, true); }
}
$("lyricSourceFile").addEventListener("change", verifyFiles);
$("lyricManifestFile").addEventListener("change", verifyFiles);
$("lyricSectionFilter").addEventListener("change", renderEvents);
$("exportPerformanceCues").addEventListener("click", () => {
  if (!verifiedSheet) return;
  const blob = new Blob([JSON.stringify(verifiedSheet, null, 2)], {type:"application/json"});
  const url = URL.createObjectURL(blob), link = document.createElement("a");
  link.href = url; link.download = "somebodys-gotta-do-it-verified-performance-cues.json"; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 30000);
  setStatus("Exported " + verifiedSheet.event_count + " verified source-linked cues. No vocal timing or audio was generated.");
});
