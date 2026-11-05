const SOURCE = "music-foundry/projects/somebodys-gotta-do-it/cue-sheet.md";
const SECTIONS = {"Intro tag":"intro_tag","Verse 1":"verse_1","Pre":"pre","Chorus":"chorus","Verse 2":"verse_2","Bridge — half-time chaos":"bridge_half_time","Final chorus / outro":"final_chorus_outro"};
function expectedEvents(text) {
  let section = null;
  const result = [];
  const lines = text.replace(/\r\n?/g, "\n").split("\n");
  for (let i = 0; i < lines.length; i++) {
    const raw = lines[i];
    if (raw.startsWith("## ")) { section = SECTIONS[raw.slice(3).trim()] || null; continue; }
    if (!section || !raw.trim()) continue;
    const trimmed = raw.trim();
    if (["#", "**", "- ", "|", "```"].some(prefix => trimmed.startsWith(prefix))) continue;
    const line = i + 1;
    result.push({event_id: section + ":L" + String(line).padStart(3,"0"), section_id:section, source_line:line, text:raw});
  }
  return result;
}
async function hash(text) {
  if (!globalThis.crypto?.subtle || typeof TextEncoder === "undefined") throw new Error("SHA-256 verification unavailable.");
  const bytes = new TextEncoder().encode(text);
  const digest = await globalThis.crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest), b => b.toString(16).padStart(2,"0")).join("");
}
export async function validateLyricEventManifest(data, sourceText) {
  const errors = [];
  if (!data || typeof data !== "object" || Array.isArray(data)) return ["Manifest must be a JSON object."];
  if (typeof sourceText !== "string") return ["Load the canonical cue-sheet.md file to verify lyric integrity."];
  if (data.schema !== "turbo.music-foundry.lyric-events.v1") errors.push("Unsupported lyric event schema.");
  if (data.source_ref !== SOURCE) errors.push("Source must be the canonical cue sheet.");
  if (data.lyric_authority !== "source_ref") errors.push("Canonical source reference must remain authoritative.");
  if (data.timing_policy !== "editorial_grid_not_performance_locked") errors.push("Timing policy must remain editorial and unlocked.");
  const normalized = sourceText.replace(/\r\n?/g, "\n");
  const actualHash = await hash(normalized);
  if (typeof data.source_sha256 !== "string" || !/^[a-f0-9]{64}$/.test(data.source_sha256)) errors.push("Manifest must contain a valid SHA-256 source hash.");
  else if (data.source_sha256 !== actualHash) errors.push("Canonical cue-sheet SHA-256 does not match the manifest.");
  const expected = expectedEvents(normalized);
  if (!Array.isArray(data.events)) return [...errors, "Manifest events must be an array."];
  if (data.events.length !== expected.length) errors.push("Event count mismatch: expected " + expected.length + " canonical lyric lines, received " + data.events.length + ".");
  for (let i = 0; i < Math.min(data.events.length, expected.length); i++) {
    const event = data.events[i], source = expected[i], prefix = "Event " + (i + 1) + ": ";
    if (!event || typeof event !== "object" || Array.isArray(event)) { errors.push(prefix + "must be an object."); continue; }
    for (const key of ["event_id","section_id","source_line","text"]) if (event[key] !== source[key]) errors.push(prefix + key + " does not exactly match canonical cue-sheet line " + source.source_line + ".");
    const t = event.timing;
    if (!t || t.status !== "unplaced" || t.bar !== null || t.beat !== null || t.marker_ref !== null) errors.push(prefix + "timing must remain explicitly unplaced.");
  }
  return errors;
}
