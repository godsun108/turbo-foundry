/**
 * EARTH STUDIO MIDI clock, recording, and deterministic event scheduling.
 * This module is browser-independent so the same musical model can run
 * in the browser, Node tests, and the future standalone host.
 */
export const MIDI_PPQ = 960;

function finite(value, name) {
  if (typeof value !== "number" || !Number.isFinite(value)) throw new TypeError(name + " must be a finite number");
  return value;
}
function integer(value, name, min = 0, max = Number.MAX_SAFE_INTEGER) {
  if (!Number.isInteger(value) || value < min || value > max) throw new RangeError(name + " is outside its supported integer range");
  return value;
}
function validateTempo(tempo) {
  finite(tempo, "tempo");
  if (tempo < 40 || tempo > 240) throw new RangeError("tempo must be between 40 and 240 BPM");
  return tempo;
}

export function ticksToSeconds(ticks, tempo, ppq = MIDI_PPQ) {
  finite(ticks, "ticks"); validateTempo(tempo); integer(ppq, "ppq", 1);
  return ticks * 60 / (tempo * ppq);
}
export function secondsToTicks(seconds, tempo, ppq = MIDI_PPQ) {
  finite(seconds, "seconds"); validateTempo(tempo); integer(ppq, "ppq", 1);
  return Math.round(seconds * tempo * ppq / 60);
}
export function quantizeTick(tick, gridTicks, strength = 1) {
  finite(tick, "tick"); integer(gridTicks, "gridTicks", 1);
  finite(strength, "strength");
  if (strength < 0 || strength > 1) throw new RangeError("strength must be between 0 and 1");
  const snapped = Math.round(tick / gridTicks) * gridTicks;
  return Math.max(0, Math.round(tick + (snapped - tick) * strength));
}

export function validateMidiClip(clip) {
  const errors = [];
  if (!clip || typeof clip !== "object" || Array.isArray(clip)) return ["MIDI clip must be an object"];
  if (typeof clip.id !== "string" || !clip.id.trim()) errors.push("MIDI clip id must be a non-empty string");
  if (!Number.isInteger(clip.startTick) || clip.startTick < 0) errors.push("MIDI clip startTick must be a non-negative integer");
  if (!Number.isInteger(clip.lengthTicks) || clip.lengthTicks < 1) errors.push("MIDI clip lengthTicks must be a positive integer");
  if (!Array.isArray(clip.notes)) errors.push("MIDI clip notes must be an array");
  const ids = new Set();
  for (const note of clip.notes || []) {
    if (!note || typeof note !== "object") { errors.push("MIDI notes must be objects"); continue; }
    if (typeof note.id !== "string" || !note.id.trim() || ids.has(note.id)) errors.push("MIDI note IDs must be unique non-empty strings");
    else ids.add(note.id);
    if (!Number.isInteger(note.note) || note.note < 0 || note.note > 127) errors.push("MIDI note number must be 0..127");
    if (!Number.isInteger(note.startTick) || note.startTick < 0) errors.push("MIDI note startTick must be a non-negative integer");
    if (!Number.isInteger(note.durationTicks) || note.durationTicks < 1) errors.push("MIDI note durationTicks must be a positive integer");
    if (!Number.isInteger(note.velocity) || note.velocity < 1 || note.velocity > 127) errors.push("MIDI note velocity must be 1..127");
    if (!Number.isInteger(note.channel) || note.channel < 0 || note.channel > 15) errors.push("MIDI channel must be 0..15");
    if (Number.isInteger(note.startTick) && Number.isInteger(note.durationTicks) && Number.isInteger(clip.lengthTicks) && note.startTick + note.durationTicks > clip.lengthTicks) errors.push("MIDI note extends beyond its clip length");
  }
  return errors;
}

export function createMidiClip({id, startTick = 0, lengthTicks, notes = []}) {
  const clip = {
    id, startTick, lengthTicks,
    notes: notes.map(note => ({id:note.id, note:note.note, startTick:note.startTick, durationTicks:note.durationTicks, velocity:note.velocity, channel:note.channel ?? 0}))
  };
  const errors = validateMidiClip(clip);
  if (errors.length) throw new TypeError("Invalid EARTH STUDIO MIDI clip: " + errors.join("; "));
  clip.notes.sort((a,b) => a.startTick - b.startTick || a.note - b.note || a.id.localeCompare(b.id));
  return clip;
}

/**
 * Captures keyboard/MIDI input in musical ticks. timeSeconds is measured
 * relative to the transport start, not wall-clock time.
 */
export class MidiRecorder {
  constructor({ppq = MIDI_PPQ, idPrefix = "note"} = {}) {
    integer(ppq, "ppq", 1);
    this.ppq = ppq; this.idPrefix = idPrefix; this.sequence = 0;
    this.recording = false; this.pending = new Map(); this.notes = [];
  }
  start({startTick = 0, tempo = 120, quantizeTicks = 0} = {}) {
    integer(startTick, "startTick", 0); validateTempo(tempo);
    integer(quantizeTicks, "quantizeTicks", 0);
    this.startTick = startTick; this.tempo = tempo; this.quantizeTicks = quantizeTicks;
    this.pending.clear(); this.notes = []; this.recording = true;
    return this;
  }
  toTick(timeSeconds) {
    finite(timeSeconds, "timeSeconds");
    if (timeSeconds < 0) throw new RangeError("timeSeconds cannot be negative");
    return secondsToTicks(timeSeconds, this.tempo, this.ppq);
  }
  keyFor(note, channel, key) {
    integer(note, "note", 0, 127); integer(channel, "channel", 0, 15);
    return key === undefined ? channel + ":" + note : String(key);
  }
  noteOn({note, velocity = 100, channel = 0, timeSeconds, key} = {}) {
    if (!this.recording) return false;
    integer(velocity, "velocity", 1, 127);
    const id = this.keyFor(note, channel, key);
    if (this.pending.has(id)) this.close(id, this.toTick(timeSeconds));
    this.pending.set(id, {note, velocity, channel, startTick:this.toTick(timeSeconds)});
    return true;
  }
  noteOff({note, channel = 0, timeSeconds, key} = {}) {
    if (!this.recording) return false;
    const id = this.keyFor(note, channel, key);
    return this.close(id, this.toTick(timeSeconds));
  }
  close(id, endTick) {
    const active = this.pending.get(id);
    if (!active) return false;
    this.pending.delete(id);
    let startTick = active.startTick, finishTick = Math.max(startTick + 1, endTick);
    if (this.quantizeTicks > 0) {
      startTick = quantizeTick(startTick, this.quantizeTicks);
      finishTick = quantizeTick(finishTick, this.quantizeTicks);
    }
    finishTick = Math.max(startTick + 1, finishTick);
    this.notes.push({
      id:this.idPrefix + "-" + (++this.sequence), note:active.note,
      startTick, durationTicks:finishTick - startTick,
      velocity:active.velocity, channel:active.channel
    });
    return true;
  }
  stop({timeSeconds} = {}) {
    if (!this.recording) return this.notes.length;
    const endTick = this.toTick(timeSeconds);
    for (const id of [...this.pending.keys()]) this.close(id, endTick);
    this.recording = false;
    return this.notes.length;
  }
  toClip({id = "midi-take", startTick = this.startTick || 0, lengthTicks} = {}) {
    if (this.recording) throw new Error("Stop MIDI recording before creating a clip");
    const requiredLength = Math.max(1, ...this.notes.map(note => note.startTick + note.durationTicks));
    return createMidiClip({id, startTick, lengthTicks: lengthTicks ?? requiredLength, notes:this.notes});
  }
}

/**
 * Converts clip notes into absolute AudioContext-time events. The caller
 * supplies a scheduling window; no timers or audio work occur in this module.
 */
export function collectMidiEvents(clips, {
  tempo, fromTick = 0, toTick, originTime = 0, ppq = MIDI_PPQ, loop = null
} = {}) {
  validateTempo(tempo); finite(fromTick, "fromTick"); finite(toTick, "toTick"); finite(originTime, "originTime");
  integer(ppq, "ppq", 1);
  if (fromTick < 0 || toTick <= fromTick) throw new RangeError("playback window must have increasing non-negative ticks");
  if (!Array.isArray(clips)) throw new TypeError("clips must be an array");
  if (loop && (!Number.isInteger(loop.startTick) || !Number.isInteger(loop.endTick) || loop.startTick < 0 || loop.endTick <= loop.startTick)) throw new RangeError("loop range is invalid");
  const events = [];
  const addNote = (clip, note, start, end) => {
    const onTick = Math.max(start, fromTick), offTick = Math.min(end, toTick);
    if (onTick < toTick && onTick < offTick) {
      if (start >= fromTick) events.push({type:"noteOn",tick:start,note:note.note,velocity:note.velocity,channel:note.channel,trackId:clip.trackId,clipId:clip.id});
      else events.push({type:"noteOn",tick:fromTick,note:note.note,velocity:note.velocity,channel:note.channel,trackId:clip.trackId,clipId:clip.id});
      if (end < toTick) events.push({type:"noteOff",tick:end,note:note.note,velocity:0,channel:note.channel,trackId:clip.trackId,clipId:clip.id});
    }
  };
  for (const clip of clips) {
    const errors = validateMidiClip(clip);
    if (errors.length) throw new TypeError("Invalid MIDI clip " + clip.id + ": " + errors.join("; "));
    for (const note of clip.notes) {
      const absoluteStart = clip.startTick + note.startTick;
      const absoluteEnd = absoluteStart + note.durationTicks;
      if (!loop) addNote(clip, note, absoluteStart, absoluteEnd);
      else {
        const loopStart = loop.startTick, loopEnd = loop.endTick, loopLength = loopEnd - loopStart;
        if (absoluteStart < loopStart || absoluteStart >= loopEnd) continue;
        const firstCycle = Math.floor((fromTick - absoluteStart) / loopLength);
        const lastCycle = Math.ceil((toTick - absoluteStart) / loopLength);
        for (let cycle = firstCycle; cycle <= lastCycle; cycle++) {
          const start = absoluteStart + cycle * loopLength;
          const end = Math.min(absoluteEnd, loopEnd) + cycle * loopLength;
          addNote(clip, note, start, end);
        }
      }
    }
  }
  events.sort((a,b) => a.tick - b.tick || (a.type === b.type ? 0 : a.type === "noteOff" ? -1 : 1) || a.channel - b.channel || a.note - b.note);
  return events.map(event => ({...event, when:originTime + ticksToSeconds(event.tick - fromTick, tempo, ppq)}));
}

export function createAudioWorkletMidiSink(port) {
  if (!port || typeof port.postMessage !== "function") throw new TypeError("AudioWorklet port must expose postMessage");
  return {
    noteOn(note, velocity, when, channel = 0) { port.postMessage({type:"noteOn",note,velocity:velocity / 127,channel,when}); },
    noteOff(note, when, channel = 0) { port.postMessage({type:"noteOff",note,channel,when}); },
    allNotesOff(when) { port.postMessage({type:"allNotesOff",when}); }
  };
}

export class MidiSequencer {
  constructor({sink, ppq = MIDI_PPQ} = {}) {
    integer(ppq, "ppq", 1);
    if (!sink) throw new TypeError("A MIDI event sink is required");
    this.sink = sink; this.ppq = ppq;
  }
  collect(clips, options) { return collectMidiEvents(clips, {...options, ppq:this.ppq}); }
  playWindow(clips, options) {
    const events = this.collect(clips, options);
    dispatchMidiEvents(events, this.sink);
    return events;
  }
  allNotesOff(when) { if (typeof this.sink.allNotesOff === "function") this.sink.allNotesOff(when); }
}

export function dispatchMidiEvents(events, sink) {
  if (!Array.isArray(events) || !sink) throw new TypeError("events and a MIDI sink are required");
  for (const event of events) {
    if (event.type === "noteOn") sink.noteOn(event.note,event.velocity,event.when,event.channel);
    else if (event.type === "noteOff") sink.noteOff(event.note,event.when,event.channel);
  }
  return events.length;
}
