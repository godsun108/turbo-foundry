import createEarthStudioEngine from "./earth_studio_engine_wasm.mjs";

const MAX_EVENTS = 64;
const MAX_PENDING_EVENTS = 512;
const AUTOMATION_PARAMETERS = {cutoff:[80,18000],bend:[-12,12],vibrato:[0,20]};
const EVENT_BYTES = 12;
const MAX_FRAMES = 2048;
const WAVEFORMS = { sine: 0, sawtooth: 1, square: 2, triangle: 3 };

class EarthStudioProcessor extends AudioWorkletProcessor {
  constructor(options) {
    super();
    this.engine = 0; this.outputPtr = 0; this.eventsPtr = 0; this.parametersPtr = 0;
    this.eventCount = 0; this.eventOffsets = new Uint32Array(MAX_EVENTS); this.eventTypes = new Uint8Array(MAX_EVENTS);
    this.eventChannels = new Uint8Array(MAX_EVENTS); this.eventNotes = new Uint8Array(MAX_EVENTS);
    this.eventVelocities = new Float32Array(MAX_EVENTS);
    this.pendingCount = 0; this.pendingAutomation = []; this.settings = {...(options.processorOptions?.settings || {})}; this.pendingFrames = new Float64Array(MAX_PENDING_EVENTS);
    this.pendingTypes = new Uint8Array(MAX_PENDING_EVENTS); this.pendingChannels = new Uint8Array(MAX_PENDING_EVENTS);
    this.pendingNotes = new Uint8Array(MAX_PENDING_EVENTS); this.pendingVelocities = new Float32Array(MAX_PENDING_EVENTS);
    this.memoryView = null;
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
      this.settings={...this.settings,...(options.settings||{})}; this.setInstrument(this.settings);
      this.ready = true; this.port.postMessage({ type: "ready", sampleRate });
    } catch (error) {
      this.failed = true; this.port.postMessage({ type: "error", message: error && error.message ? error.message : String(error) });
    }
  }
  onMessage(message) {
    if (!message || typeof message !== "object") return;
    if (message.type === "cancelScheduled") { this.pendingCount = 0; this.enqueue(2, 0, 0, 255); }
    else if (message.type === "noteOn") this.enqueue(0, message.note, message.velocity ?? 1, message.channel ?? 0, message.when);
    else if (message.type === "noteOff") this.enqueue(1, message.note, 0, message.channel ?? 0, message.when);
    else if (message.type === "allNotesOff") this.enqueue(2, 0, 0, 255, message.when);
    else if (message.type === "settings") { this.settings={...this.settings,...(message.settings||{})}; this.setInstrument(this.settings); }
    else if (message.type === "parameter") {
      const range=AUTOMATION_PARAMETERS[message.parameter];
      if(!range||!Number.isFinite(message.value)||message.value<range[0]||message.value>range[1]||!Number.isFinite(message.when)||this.pendingAutomation.length>=MAX_PENDING_EVENTS)return;
      this.pendingAutomation.push({frame:Math.max(currentFrame,Math.round(message.when*sampleRate)),parameter:message.parameter,value:message.value});
      this.pendingAutomation.sort((a,b)=>a.frame-b.frame);
    }
  }
  enqueue(type, note, velocity, channel = 0, when = undefined) {
    if (this.pendingCount >= MAX_PENDING_EVENTS || !Number.isInteger(note) || note < 0 || note > 127) return false;
    const i = this.pendingCount++;
    this.pendingFrames[i] = Number.isFinite(when) ? Math.max(currentFrame, Math.round(when * sampleRate)) : currentFrame;
    this.pendingTypes[i] = type; this.pendingChannels[i] = channel;
    this.pendingNotes[i] = note; this.pendingVelocities[i] = Math.max(0, Math.min(1, Number(velocity) || 0));
    return true;
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
    const channels=outputs[0];if(!channels||!channels.length)return true;
    const left=channels[0],right=channels.length>1?channels[1]:channels[0],frames=left.length;
    if(!this.ready||this.failed||frames>MAX_FRAMES){left.fill(0);if(right!==left)right.fill(0);return true;}
    const blockStart=currentFrame,blockEnd=blockStart+frames;
    const due=[];let keep=0;
    for(let i=0;i<this.pendingCount;i++){
      const item={frame:this.pendingFrames[i],type:this.pendingTypes[i],channel:this.pendingChannels[i],note:this.pendingNotes[i],velocity:this.pendingVelocities[i]};
      if(item.frame<blockEnd)due.push(item);
      else {this.pendingFrames[keep]=item.frame;this.pendingTypes[keep]=item.type;this.pendingChannels[keep]=item.channel;this.pendingNotes[keep]=item.note;this.pendingVelocities[keep]=item.velocity;keep++;}
    }
    this.pendingCount=keep;
    const automationDue=[],automationKeep=[];
    for(const item of this.pendingAutomation)(item.frame<blockEnd?automationDue:automationKeep).push(item);
    this.pendingAutomation=automationKeep;
    let cursor=0,ai=0;
    while(cursor<frames){
      const absolute=blockStart+cursor;
      while(ai<automationDue.length&&automationDue[ai].frame<=absolute){
        const item=automationDue[ai++];this.settings[item.parameter]=item.value;this.setInstrument(this.settings);
      }
      const next=ai<automationDue.length?Math.max(cursor,automationDue[ai].frame-blockStart):frames;
      const stop=Math.max(cursor+1,Math.min(frames,next)),segmentFrames=stop-cursor;
      this.eventCount=0;
      for(const item of due){
        const offset=item.frame-blockStart;
        if(offset>=cursor&&offset<stop&&this.eventCount<MAX_EVENTS){
          const i=this.eventCount++;this.eventOffsets[i]=offset-cursor;this.eventTypes[i]=item.type;
          this.eventChannels[i]=item.channel;this.eventNotes[i]=item.note;this.eventVelocities[i]=item.velocity;
        }
      }
      const result=this.module._earth_engine_render(this.engine,this.outputPtr,segmentFrames,this.eventsPtr,this.eventCount);
      this.eventCount=0;
      if(result!==0){left.fill(0,cursor,stop);if(right!==left)right.fill(0,cursor,stop);}
      else {const samples=this.module.HEAPF32,base=this.outputPtr>>>2;for(let i=0;i<segmentFrames;i++){left[cursor+i]=samples[base+i*2];if(right!==left)right[cursor+i]=samples[base+i*2+1];}}
      cursor=stop;
    }
    while(ai<automationDue.length){const item=automationDue[ai++];this.settings[item.parameter]=item.value;this.setInstrument(this.settings);}
    return true;
  }
}
registerProcessor("earth-studio-native", EarthStudioProcessor);
