import { validateLyricEventManifest } from "./lyric-event-review-core.mjs";

export async function buildVerifiedPerformanceCueSheet(manifest, sourceText) {
  const errors = await validateLyricEventManifest(manifest, sourceText);
  if (errors.length) throw new Error(errors.join("\n"));
  return {
    schema: "turbo.music-foundry.verified-performance-cues.v1",
    source_ref: manifest.source_ref,
    source_sha256: manifest.source_sha256,
    lyric_authority: "canonical_source_only",
    timing_status: "unplaced",
    timing_policy: "editorial_grid_not_performance_locked",
    event_count: manifest.events.length,
    events: manifest.events.map(event => ({
      event_id: event.event_id,
      section_id: event.section_id,
      source_line: event.source_line,
      text: event.text,
      timing: { status: "unplaced", bar: null, beat: null, marker_ref: null }
    }))
  };
}
