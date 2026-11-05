import test from "node:test";
import assert from "node:assert/strict";
import { validateLyricEventManifest } from "../projects/somebodys-gotta-do-it/lyric-event-review-core.mjs";
const sample = {
  schema: "turbo.music-foundry.lyric-events.v1",
  source_ref: "music-foundry/projects/somebodys-gotta-do-it/cue-sheet.md",
  lyric_authority: "source_ref",
  timing_policy: "editorial_grid_not_performance_locked",
  events: [{
    event_id: "intro_tag:L010", section_id: "intro_tag", source_line: 10,
    text: "(Fuck it, I'll do it)",
    timing: { status: "unplaced", bar: null, beat: null, marker_ref: null }
  }]
};
test("accepts canonical source-linked lyric events with unplaced timing", () => {
  assert.deepEqual(validateLyricEventManifest(sample), []);
});
test("rejects a changed source reference and falsely placed timing", () => {
  const changed = structuredClone(sample);
  changed.source_ref = "different.md"; changed.events[0].timing.status = "placed";
  const errors = validateLyricEventManifest(changed);
  assert.ok(errors.some(error => error.includes("canonical cue sheet")));
  assert.ok(errors.some(error => error.includes("unplaced")));
});
test("rejects duplicate IDs and out-of-order source lines", () => {
  const changed = structuredClone(sample);
  changed.events.push({ ...structuredClone(sample.events[0]), source_line: 9 });
  const errors = validateLyricEventManifest(changed);
  assert.ok(errors.some(error => error.includes("unique")));
  assert.ok(errors.some(error => error.includes("strictly increasing")));
});
