import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { buildVerifiedPerformanceCueSheet } from "../projects/somebodys-gotta-do-it/lyric-performance-bridge-core.mjs";

const sourceUrl = new URL("../projects/somebodys-gotta-do-it/cue-sheet.md", import.meta.url);
const manifestUrl = new URL("../output/somebodys-gotta-do-it/lyric-events.json", import.meta.url);

test("canonical song manifest becomes 65 exact unplaced recording cues", async () => {
  const [source, rawManifest] = await Promise.all([
    readFile(sourceUrl, "utf8"),
    readFile(manifestUrl, "utf8")
  ]);
  const manifest = JSON.parse(rawManifest);
  const cues = await buildVerifiedPerformanceCueSheet(manifest, source);
  assert.equal(cues.event_count, 65);
  assert.equal(cues.events.length, 65);
  assert.equal(cues.source_sha256, manifest.source_sha256);
  assert.deepEqual(cues.events.map(event => event.text), manifest.events.map(event => event.text));
  assert.deepEqual(cues.events.map(event => event.event_id), manifest.events.map(event => event.event_id));
  assert.ok(cues.events.every(event =>
    event.timing.status === "unplaced" &&
    event.timing.bar === null &&
    event.timing.beat === null &&
    event.timing.marker_ref === null
  ));
});
