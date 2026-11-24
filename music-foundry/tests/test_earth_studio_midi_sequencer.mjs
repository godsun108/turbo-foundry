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
    id:"note-1",note:50,startTick:240,durationTicks:240,velocity:100,channel:0
  });
});
test("sequencer emits ordered AudioContext-time events with note-off before note-on",()=>{
  const clip=createMidiClip({id:"c",startTick:0,lengthTicks:1920,notes:[
    {id:"a",note:60,startTick:0,durationTicks:480,velocity:100,channel:0},
    {id:"b",note:60,startTick:480,durationTicks:480,velocity:90,channel:0}
  ]});
  const events=collectMidiEvents([clip],{tempo:120,fromTick:0,toTick:960,originTime:10});
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
  const events=collectMidiEvents([clip],{tempo:120,fromTick:480,toTick:1200,originTime:5});
  assert.deepEqual(events.map(e=>[e.type,e.tick]),[
    ["noteOff",960],["noteOn",960],["noteOff",1200]
  ]);
  assert.equal(events[0].when,5.25);
});
