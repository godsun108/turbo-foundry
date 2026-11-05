import test from "node:test";
import assert from "node:assert/strict";
import { webcrypto } from "node:crypto";
import { buildVerifiedPerformanceCueSheet } from "../projects/somebodys-gotta-do-it/lyric-performance-bridge-core.mjs";
globalThis.crypto = webcrypto;
const source = "## Intro tag\nFirst exact line\nSecond exact line\n";
async function digest(text) {
  const hash = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return Array.from(new Uint8Array(hash), b => b.toString(16).padStart(2,"0")).join("");
}
async function fixture() {
  return {
    schema:"turbo.music-foundry.lyric-events.v1",
    source_ref:"music-foundry/projects/somebodys-gotta-do-it/cue-sheet.md",
    source_sha256:await digest(source),
    lyric_authority:"source_ref",
    timing_policy:"editorial_grid_not_performance_locked",
    events:[1,2].map((line,index)=>({
      event_id:"intro_tag:L00"+(line+0),section_id:"intro_tag",source_line:line+0,
      text:index===0?"First exact line":"Second exact line",
      timing:{status:"unplaced",bar:null,beat:null,marker_ref:null}
    }))
  };
}
test("exports exact source-linked performance cues without inventing timing",async()=>{
  const cues=await buildVerifiedPerformanceCueSheet(await fixture(),source);
  assert.equal(cues.event_count,2);
  assert.deepEqual(cues.events.map(event=>event.text),["First exact line","Second exact line"]);
  assert.ok(cues.events.every(event=>event.timing.status==="unplaced"&&event.timing.bar===null&&event.timing.beat===null));
});
test("rejects changed source text before exporting cues",async()=>{
  await assert.rejects(()=>buildVerifiedPerformanceCueSheet(await fixture(),source.replace("First","Changed")),/SHA-256/);
});
test("rejects altered lyric event text",async()=>{
  const manifest=await fixture();manifest.events[0].text="rewritten lyric";
  await assert.rejects(()=>buildVerifiedPerformanceCueSheet(manifest,source),/text does not exactly match/);
});
