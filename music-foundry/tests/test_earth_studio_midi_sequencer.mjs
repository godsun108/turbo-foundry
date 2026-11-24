import test from "node:test";
import assert from "node:assert/strict";
import {
  MIDI_PPQ, ticksToSeconds, secondsToTicks, quantizeTick, createMidiClip,
  validateMidiClip, MidiRecorder, MidiSequencer, collectMidiEvents, createAudioWorkletMidiSink,
  dispatchMidiEvents
} from "../earth-studio/midi-sequencer.mjs";

test("musical clock converts ticks and seconds at the configured tempo",()=>{
  assert.equal(MIDI_PPQ,960);
  assert.equal(ticksToSeconds(960,120),.5);
  assert.equal(secondsToTicks(.5,120),960);
  assert.equal(secondsToTicks(1,60),960);
});
test("quantization supports grid snapping and partial strength",()=>{
  assert.equal(quantizeTick(470,120),480);
  assert.equal(quantizeTick(470,120,.5),475);
  assert.equal(quantizeTick(470,120,0),470);
});
test("MIDI clip model preserves note timing, velocity, channel and ordering",()=>{
  const clip=createMidiClip({id:"clip-1",startTick:960,lengthTicks:1920,notes:[
    {id:"b",note:64,startTick:480,durationTicks:240,velocity:88,channel:1},
    {id:"a",note:60,startTick:0,durationTicks:480,velocity:110,channel:0}
  ]});
  assert.deepEqual(clip.notes.map(n=>n.id),["a","b"]);
  assert.deepEqual(validateMidiClip(clip),[]);
});
test("MIDI clip validation rejects invalid note range and duration",()=>{
  const errors=validateMidiClip({id:"bad",startTick:0,lengthTicks:100,notes:[
    {id:"x",note:128,startTick:0,durationTicks:101,velocity:0,channel:16}
  ]});
  assert.ok(errors.some(e=>e.includes("0..127")));
  assert.ok(errors.some(e=>e.includes("extends beyond")));
  assert.ok(errors.some(e=>e.includes("velocity")));
  assert.ok(errors.some(e=>e.includes("channel")));
});
test("recorder captures polyphonic notes and closes held notes on stop",()=>{
  const recorder=new MidiRecorder().start({tempo:120,startTick:1920});
  recorder.noteOn({note:60,velocity:96,timeSeconds:0});
  recorder.noteOn({note:64,velocity:72,timeSeconds:.25});
  recorder.noteOff({note:60,timeSeconds:.5});
  recorder.stop({timeSeconds:.75});
  const clip=recorder.toClip({id:"take-1"});
  assert.equal(clip.startTick,1920);
  assert.deepEqual(clip.notes.map(n=>[n.note,n.startTick,n.durationTicks,n.velocity]),[
    [60,0,960,96],[64,480,960,72]
  ]);
});
test("recorder quantizes note boundaries and ignores unmatched note-offs",()=>{
  const recorder=new MidiRecorder().start({tempo:120,quantizeTicks:240});
  assert.equal(recorder.noteOff({note:50,timeSeconds:.1}),false);
  recorder.noteOn({note:50,velocity:100,timeSeconds:.13});
  recorder.noteOff({note:50,timeSeconds:.38});
  recorder.stop({timeSeconds:.5});
  assert.deepEqual(recorder.toClip({id:"q",lengthTicks:960}).notes[0],{
    id:"note-1",note:50,startTick:240,durationTicks:480,velocity:100,channel:0
  });
});
test("sequencer emits ordered AudioContext-time events with note-off before note-on",()=>{
  const clip=createMidiClip({id:"c",startTick:0,lengthTicks:1920,notes:[
    {id:"a",note:60,startTick:0,durationTicks:480,velocity:100,channel:0},
    {id:"b",note:60,startTick:480,durationTicks:480,velocity:90,channel:0}
  ]});
  const events=collectMidiEvents([clip],{tempo:120,fromTick:0,toTick:961,originTime:10});
  assert.deepEqual(events.map(e=>[e.type,e.tick,e.when]),[
    ["noteOn",0,10],["noteOff",480,10.25],["noteOn",480,10.25],["noteOff",960,10.5]
  ]);
});
test("sequencer repeats notes inside a bounded loop window",()=>{
  const clip=createMidiClip({id:"loop",startTick:0,lengthTicks:1920,notes:[
    {id:"a",note:60,startTick:0,durationTicks:240,velocity:100,channel:0}
  ]});
  const events=collectMidiEvents([clip],{tempo:120,fromTick:0,toTick:1920,loop:{startTick:0,endTick:960}});
  assert.deepEqual(events.filter(e=>e.type==="noteOn").map(e=>e.tick),[0,960]);
});
test("native AudioWorklet sink sends timestamped note events and velocity scaling",()=>{
  const messages=[];
  const sink=createAudioWorkletMidiSink({postMessage:m=>messages.push(m)});
  const events=[
    {type:"noteOn",note:64,velocity:127,channel:2,when:3.5},
    {type:"noteOff",note:64,velocity:0,channel:2,when:4}
  ];
  assert.equal(dispatchMidiEvents(events,sink),2);
  assert.deepEqual(messages,[
    {type:"noteOn",note:64,velocity:1,channel:2,when:3.5},
    {type:"noteOff",note:64,channel:2,when:4}
  ]);
});

test("sequencer dispatches its scheduled events through the native sink",()=>{
  const messages=[];
  const sequencer=new MidiSequencer({sink:createAudioWorkletMidiSink({postMessage:m=>messages.push(m)})});
  const clip=createMidiClip({id:"native",startTick:0,lengthTicks:960,notes:[
    {id:"n",note:67,startTick:0,durationTicks:480,velocity:64,channel:1}
  ]});
  const events=sequencer.playWindow([clip],{tempo:120,fromTick:0,toTick:960,originTime:2});
  assert.equal(events.length,2);
  assert.deepEqual(messages.map(m=>m.type),["noteOn","noteOff"]);
  assert.equal(messages[0].velocity,64/127);
  assert.equal(messages[0].when,2);
  assert.equal(messages[1].when,2.25);
});

test("sequencer window slicing does not retrigger notes already in progress",()=>{
  const clip=createMidiClip({id:"slice",startTick:0,lengthTicks:1440,notes:[
    {id:"long",note:60,startTick:0,durationTicks:960,velocity:100,channel:0},
    {id:"next",note:62,startTick:960,durationTicks:240,velocity:90,channel:0}
  ]});
  const events=collectMidiEvents([clip],{tempo:120,fromTick:480,toTick:1201,originTime:5});
  assert.deepEqual(events.map(e=>[e.type,e.tick]),[
    ["noteOff",960],["noteOn",960],["noteOff",1200]
  ]);
  assert.equal(events[0].when,5.25);
});

import {MusicalTransport} from "../earth-studio/midi-sequencer.mjs";

test("standalone transport clock plays, pauses, seeks, and resumes without browser APIs", () => {
  let now = 0;
  const transport = new MusicalTransport({tempo:120,now:()=>now});
  transport.play(now);
  now = 1;
  assert.equal(transport.snapshot(now).tick, 1920);
  transport.pause(now);
  now = 5;
  assert.equal(transport.snapshot(now).tick, 1920);
  transport.play(now);
  now = 5.5;
  assert.equal(transport.snapshot(now).tick, 2880);
  transport.seek(960,now);
  assert.equal(transport.snapshot(now).tick, 960);
  now = 6;
  assert.equal(transport.snapshot(now).tick, 1920);
  transport.setTempo(60,now);
  now = 7;
  assert.equal(transport.snapshot(now).tick, 2880);
  transport.stop();
  assert.equal(transport.snapshot(now).tick, 0);
  assert.equal(transport.snapshot(now).playing, false);
});

test("standalone transport wraps loop position and reports absolute loop count", () => {
  let now = 0;
  const transport = new MusicalTransport({tempo:120,now:()=>now,loop:{startTick:960,endTick:2880}});
  transport.play(now);
  now = 2;
  const state = transport.snapshot(now);
  assert.equal(state.absoluteTick, 3840);
  assert.equal(state.tick, 1920);
  assert.equal(state.loopCount, 1);
});

test("standalone transport schedules look-ahead events against a host audio clock", () => {
  let now = 0;
  const transport = new MusicalTransport({tempo:120,now:()=>now});
  const clips = [{id:"clip-1",startTick:0,lengthTicks:1920,notes:[
    {id:"n1",note:60,startTick:0,durationTicks:480,velocity:100,channel:0}
  ]}];
  transport.play(now);
  const events = transport.scheduleAhead(clips,{clockTimeSeconds:0,audioTimeSeconds:12,lookAheadSeconds:.3});
  assert.equal(events.length,2);
  assert.equal(events[0].when,12);
  assert.equal(events[1].when,12.25);
});

test("standalone transport repeats scheduled notes inside a loop window", () => {
  let now = 0;
  const transport = new MusicalTransport({tempo:120,now:()=>now,loop:{startTick:0,endTick:960}});
  transport.play(now);
  const clips = [{id:"clip-1",startTick:0,lengthTicks:960,notes:[
    {id:"n1",note:60,startTick:0,durationTicks:240,velocity:100,channel:0}
  ]}];
  const events = transport.scheduleAhead(clips,{clockTimeSeconds:0,audioTimeSeconds:4,lookAheadSeconds:1.1});
  assert.deepEqual(events.map(event=>event.type),["noteOn","noteOff","noteOn","noteOff","noteOn"]);
  assert.equal(events[2].when,4.5);
});

test("standalone look-ahead scheduler never emits duplicate events across overlapping polls", () => {
  let now = 0;
  const transport = new MusicalTransport({tempo:120,now:()=>now});
  const clips = [{id:"clip-1",startTick:0,lengthTicks:1920,notes:[
    {id:"n1",note:60,startTick:480,durationTicks:480,velocity:100,channel:0},
    {id:"n2",note:62,startTick:960,durationTicks:240,velocity:100,channel:0}
  ]}];
  transport.play(now);
  const first = transport.scheduleAhead(clips,{clockTimeSeconds:0,audioTimeSeconds:20,lookAheadSeconds:.3});
  now = .1;
  const second = transport.scheduleAhead(clips,{clockTimeSeconds:now,audioTimeSeconds:20.1,lookAheadSeconds:.3});
  const combined = [...first,...second];
  assert.deepEqual(combined.map(event=>[event.type,event.tick]),[
    ["noteOn",480],["noteOff",960],["noteOn",960]
  ]);
  assert.equal(new Set(combined.map(event=>event.type+":"+event.tick+":"+event.note)).size,combined.length);
});
