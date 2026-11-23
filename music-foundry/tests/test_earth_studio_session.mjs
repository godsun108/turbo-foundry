import test from "node:test";
import assert from "node:assert/strict";
import { encodeSession, decodeSession, validateSession } from "../earth-studio/session-store.mjs";

const valid = () => ({
  format:"earthsession", schemaVersion:1, id:"project-1", name:"Test Session",
  createdAt:"2026-11-23T12:00:00.000Z", updatedAt:"2026-11-23T12:00:00.000Z",
  tempo:124, meter:{numerator:4,denominator:4}, sampleRate:48000,
  tracks:[{id:"track-1",name:"Drums",kind:"audio",gain:1,pan:0,muted:false,solo:false,
    clips:[{id:"clip-1",assetId:"asset-1",startSeconds:2,sourceStartSeconds:0,durationSeconds:4}]}],
  assets:[{id:"asset-1",storageKey:"audio/asset-1.wav",mediaType:"audio/wav",sizeBytes:128,sha256:"a".repeat(64)}]
});

test("valid v1 session round-trips without losing project data", () => {
  const session = valid();
  assert.deepEqual(decodeSession(encodeSession(session)), session);
});

test("rejects an unknown format or schema version", () => {
  const session = valid();
  session.schemaVersion = 99;
  assert.ok(validateSession(session).some(error => error.includes("schemaVersion")));
});

test("rejects invalid tempo, pan, and unsafe asset paths", () => {
  const session = valid();
  session.tempo = 500;
  session.tracks[0].pan = 2;
  session.assets[0].storageKey = "../outside.wav";
  const errors = validateSession(session);
  assert.ok(errors.some(error => error.includes("tempo")));
  assert.ok(errors.some(error => error.includes("pan")));
  assert.ok(errors.some(error => error.includes("safe relative")));
});

test("rejects clips that reference missing assets", () => {
  const session = valid();
  session.tracks[0].clips[0].assetId = "missing";
  assert.ok(validateSession(session).some(error => error.includes("missing asset")));
});

test("rejects duplicate track and asset IDs", () => {
  const session = valid();
  session.tracks.push({...session.tracks[0]});
  session.assets.push({...session.assets[0]});
  const errors = validateSession(session);
  assert.ok(errors.some(error => error.includes("track IDs")));
  assert.ok(errors.some(error => error.includes("asset IDs")));
});

test("decode rejects malformed JSON and structurally invalid sessions", () => {
  assert.throws(() => decodeSession("{"), SyntaxError);
  assert.throws(() => decodeSession(JSON.stringify({...valid(),tempo:0})), TypeError);
});

test("rejects missing mute and solo flags", () => {
  const session = valid();
  delete session.tracks[0].muted;
  delete session.tracks[0].solo;
  const errors = validateSession(session);
  assert.ok(errors.some(error => error.includes("mute and solo")));
});
