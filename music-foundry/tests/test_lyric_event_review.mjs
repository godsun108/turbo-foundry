import test from "node:test";
import assert from "node:assert/strict";
import { webcrypto } from "node:crypto";
import { validateLyricEventManifest } from "../projects/somebodys-gotta-do-it/lyric-event-review-core.mjs";
globalThis.crypto ??= webcrypto;
const source = "## Intro tag\n(Fuck it, I'll do it)\n";
async function fixture() {
  const digest = await webcrypto.subtle.digest("SHA-256", new TextEncoder().encode(source));
  const source_sha256 = Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2,"0")).join("");
  return { schema:"turbo.music-foundry.lyric-events.v1", project_id:"somebodys-gotta-do-it",
    source_ref:"music-foundry/projects/somebodys-gotta-do-it/cue-sheet.md", source_sha256,
    lyric_authority:"source_ref", timing_policy:"editorial_grid_not_performance_locked",
    events:[{event_id:"intro_tag:L002",section_id:"intro_tag",source_line:2,text:"(Fuck it, I'll do it)",timing:{status:"unplaced",bar:null,beat:null,marker_ref:null}}] };
}
test("accepts exact source-linked lyric events with matching SHA-256", async () => {
  assert.deepEqual(await validateLyricEventManifest(await fixture(), source), []);
});
test("rejects lyric text changed while source reference remains unchanged", async () => {
  const data = await fixture(); data.events[0].text = "Altered lyric";
  const errors = await validateLyricEventManifest(data, source);
  assert.ok(errors.some(error => error.includes("text does not exactly match")));
});
test("rejects a changed canonical source file by SHA-256", async () => {
  const errors = await validateLyricEventManifest(await fixture(), source.replace("Fuck it", "Fine"));
  assert.ok(errors.some(error => error.includes("SHA-256 does not match")));
});
test("rejects missing or additional lyric events", async () => {
  const data = await fixture(); data.events.push(structuredClone(data.events[0]));
  const errors = await validateLyricEventManifest(data, source);
  assert.ok(errors.some(error => error.includes("Event count mismatch")));
});
test("rejects a changed source reference and falsely placed timing", async () => {
  const data = await fixture(); data.source_ref = "different.md"; data.events[0].timing.status = "placed";
  const errors = await validateLyricEventManifest(data, source);
  assert.ok(errors.some(error => error.includes("canonical cue sheet")));
  assert.ok(errors.some(error => error.includes("unplaced")));
});
test("rejects forged event IDs, section IDs, and source line numbers", async () => {
  const data = await fixture(); data.events[0].event_id = "forged"; data.events[0].section_id = "verse_1"; data.events[0].source_line = 3;
  const errors = await validateLyricEventManifest(data, source);
  assert.ok(errors.some(error => error.includes("event_id does not exactly match")));
  assert.ok(errors.some(error => error.includes("section_id does not exactly match")));
  assert.ok(errors.some(error => error.includes("source_line does not exactly match")));
});
