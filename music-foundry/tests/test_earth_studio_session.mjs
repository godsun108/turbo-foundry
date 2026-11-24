import test from "node:test";
import assert from "node:assert/strict";
import { encodeSession, decodeSession, validateSession } from "../earth-studio/session-store.mjs";

const valid = () => ({
  format:"earthsession", schemaVersion:1, id:"project-1", name:"Test Session",
  createdAt:"2026-11-23T12:00:00.000Z", updatedAt:"2026-11-23T12:00:00.000Z",
  tempo:124, meter:{numerator:4,denominator:4}, sampleRate:48000,
  tracks:[{id:"track-1",name:"Drums",kind:"audio",gain:1,pan:0,muted:false,solo:false,
    clips:[{id:"clip-1",assetId:"asset-1",startSeconds:2,sourceStartSeconds:0,durationSeconds:4}]}],
  assets:[{id:"asset-1",storageKey:"audio/asset-1.wav",mediaType:"audio/wav",sizeBytes:128,sha256:"a".repeat(64)}],
  instrument:{oscillator:"sine",attack:20,decay:180,sustain:70,release:300,cutoff:8000,vibrato:0,bend:0}
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

test("rejects duplicate asset storage keys", () => {
  const session = valid();
  session.assets.push({...session.assets[0],id:"asset-2"});
  assert.ok(validateSession(session).some(error => error.includes("storageKeys must be unique")));
});

test("validates and round-trips portable instrument settings", () => {
  const session = valid();
  assert.deepEqual(decodeSession(encodeSession(session)).instrument, session.instrument);
  session.instrument.cutoff = 50000;
  assert.ok(validateSession(session).some(error => error.includes("instrument cutoff")));
});

test("MIDI clips round-trip in earthsession without breaking legacy tracks",()=>{
  const session=valid();
  session.tracks.push({id:"midi-1",name:"Keys",kind:"midi",gain:1,pan:0,muted:false,solo:false,clips:[],midiClips:[
    {id:"clip-1",startTick:1920,lengthTicks:960,notes:[
      {id:"note-1",note:60,startTick:0,durationTicks:480,velocity:100,channel:0},
      {id:"note-2",note:64,startTick:480,durationTicks:480,velocity:82,channel:1}
    ]}
  ]});
  assert.deepEqual(decodeSession(encodeSession(session)).tracks[1].midiClips,session.tracks[1].midiClips);
  const legacy=valid();
  assert.equal(decodeSession(encodeSession(legacy)).tracks[0].midiClips,undefined);
});
test("rejects MIDI clips on audio tracks and notes outside clip bounds",()=>{
  const session=valid();
  session.tracks[0].midiClips=[{id:"bad",startTick:0,lengthTicks:120,notes:[
    {id:"n",note:60,startTick:0,durationTicks:240,velocity:100,channel:0}
  ]}];
  const errors=validateSession(session);
  assert.ok(errors.some(error=>error.includes("MIDI clips require")));
  assert.ok(errors.some(error=>error.includes("extends beyond")));
});
