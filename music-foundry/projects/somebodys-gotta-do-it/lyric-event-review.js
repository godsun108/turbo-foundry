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
