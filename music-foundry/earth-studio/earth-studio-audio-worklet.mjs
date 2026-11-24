import createEarthStudioEngine from "./earth_studio_engine_wasm.mjs";

const MAX_EVENTS = 64;
const EVENT_BYTES = 12;
const MAX_FRAMES = 2048;
const WAVEFORMS = { sine: 0, sawtooth: 1, square: 2, triangle: 3 };

class EarthStudioProcessor extends AudioWorkletProcessor {
  constructor(options) {
    super();
    this.engine = 0; this.outputPtr = 0; this.eventsPtr = 0; this.parametersPtr = 0;
    this.eventCount = 0; this.eventTypes = new Uint8Array(MAX_EVENTS);
    this.eventChannels = new Uint8Array(MAX_EVENTS); this.eventNotes = new Uint8Array(MAX_EVENTS);
    this.eventVelocities = new Float32Array(MAX_EVENTS); this.memoryView = null;
    this.ready = false; this.failed = false;
    this.port.onmessage = event => this.onMessage(event.data);
    this.initialize(options.processorOptions || {});
  }
  async initialize(options) {
    try {
      const module = await createEarthStudioEngine({ locateFile: path => new URL(path, import.meta.url).href });
      this.module = module; this.engine = module._earth_engine_create(sampleRate);
      if (!this.engine) throw new Error("Native engine creation failed");
      this.outputPtr = module._malloc(MAX_FRAMES * 2 * 4);
      this.eventsPtr = module._malloc(MAX_EVENTS * EVENT_BYTES);
      this.parametersPtr = module._malloc(36);
      if (!this.outputPtr || !this.eventsPtr || !this.parametersPtr) throw new Error("Could not allocate bounded audio buffers");
      this.memoryView = new DataView(module.HEAPU8.buffer);
      this.setInstrument(options.settings || {});
      this.ready = true; this.port.postMessage({ type: "ready", sampleRate });
    } catch (error) {
      this.failed = true; this.port.postMessage({ type: "error", message: error && error.message ? error.message : String(error) });
    }
  }
  onMessage(message) {
    if (!message || typeof message !== "object") return;
    if (message.type === "noteOn") this.enqueue(0, message.note, message.velocity ?? 1);
    else if (message.type === "noteOff") this.enqueue(1, message.note, 0);
    else if (message.type === "allNotesOff") this.enqueue(2, 0, 0, 255);
    else if (message.type === "settings") this.setInstrument(message.settings || {});
  }
  enqueue(type, note, velocity, channel = 0) {
    if (this.eventCount >= MAX_EVENTS || !Number.isInteger(note) || note < 0 || note > 127) return;
    const i = this.eventCount++; this.eventTypes[i] = type; this.eventChannels[i] = channel;
    this.eventNotes[i] = note; this.eventVelocities[i] = Math.max(0, Math.min(1, Number(velocity) || 0));
  }
  setInstrument(settings) {
    if (!this.module || !this.engine || !this.parametersPtr) return;
    const m = this.module, view = new DataView(m.HEAPU8.buffer), p = this.parametersPtr;
    const waveform = WAVEFORMS[settings.oscillator] ?? 0;
    const attack = Math.max(.001, Math.min(10, (Number(settings.attack) || 20) / 1000));
    const decay = Math.max(.001, Math.min(30, (Number(settings.decay) || 180) / 1000));
    const sustain = Math.max(0, Math.min(1, (Number(settings.sustain) ?? 70) / 100));
    const release = Math.max(.001, Math.min(30, (Number(settings.release) || 300) / 1000));
    const cutoff = Math.max(20, Math.min(sampleRate * .45, Number(settings.cutoff) || 8000));
    const bend = Math.max(-24, Math.min(24, Number(settings.bend) || 0));
    const depth = Math.max(0, Math.min(2, (Number(settings.vibrato) || 0) / 10));
    view.setUint32(p, waveform, true); view.setFloat32(p + 4, attack, true);
    view.setFloat32(p + 8, decay, true); view.setFloat32(p + 12, sustain, true);
    view.setFloat32(p + 16, release, true); view.setFloat32(p + 20, cutoff, true);
    view.setFloat32(p + 24, bend, true); view.setFloat32(p + 28, 5, true);
    view.setFloat32(p + 32, depth, true); m._earth_engine_set_instrument(this.engine, p);
  }
  process(_inputs, outputs) {
    const channels = outputs[0]; if (!channels || !channels.length) return true;
    const left = channels[0], right = channels.length > 1 ? channels[1] : channels[0], frames = left.length;
    if (!this.ready || this.failed || frames > MAX_FRAMES) { left.fill(0); if (right !== left) right.fill(0); return true; }
    const view = this.memoryView, eventBase = this.eventsPtr;
    for (let i = 0; i < this.eventCount; i++) {
      const offset = eventBase + i * EVENT_BYTES; view.setUint32(offset, 0, true);
      view.setUint8(offset + 4, this.eventTypes[i]); view.setUint8(offset + 5, this.eventChannels[i]);
      view.setUint8(offset + 6, this.eventNotes[i]); view.setUint8(offset + 7, 0);
      view.setFloat32(offset + 8, this.eventVelocities[i], true);
    }
    const result = this.module._earth_engine_render(this.engine, this.outputPtr, frames, this.eventsPtr, this.eventCount);
    this.eventCount = 0;
    if (result !== 0) { left.fill(0); if (right !== left) right.fill(0); return true; }
    const samples = this.module.HEAPF32, start = this.outputPtr >>> 2;
    for (let i = 0; i < frames; i++) { left[i] = samples[start + i * 2]; if (right !== left) right[i] = samples[start + i * 2 + 1]; }
    return true;
  }
}
registerProcessor("earth-studio-native", EarthStudioProcessor);
