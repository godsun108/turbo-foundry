import { FilesetResolver, TextToSpeech } from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-audio@1.2.2/+esm";

const WASM_ROOT = "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-audio@1.2.2/wasm";
let engine = null;
let activeJob = 0;

self.addEventListener("message", async (event) => {
  const data = event.data || {};
  if (data.type === "cancel") {
    activeJob++;
    try { engine?.cancel(); } catch {}
    self.postMessage({ type: "cancelled" });
    return;
  }

  if (data.type === "init") {
    try {
      const audioFileset = await FilesetResolver.forAudioTasks(WASM_ROOT);
      const modelReader = data.file.stream().getReader();
      engine = await TextToSpeech.createFromOptions(audioFileset, {
        baseOptions: {
          modelAssetBuffer: modelReader,
          delegate: data.delegate
        },
        speakingRate: data.speakingRate,
        cacheDirectory: ":nocache"
      });
      const voices = await engine.listVoices();
      self.postMessage({ type: "ready", voices });
    } catch (error) {
      self.postMessage({ type: "error", message: error?.message || String(error) });
    }
    return;
  }

  if (data.type === "synthesize") {
    if (!engine) {
      self.postMessage({ type: "error", message: "Load a voice model before synthesis." });
      return;
    }
    const job = ++activeJob;
    try {
      const chunks = [];
      let totalSamples = 0;
      let sampleRateHz = 24000;
      let chunkCount = 0;
      for await (const chunk of engine.synthesizeStream(data.text, { voiceId: data.voiceId })) {
        if (job !== activeJob) return;
        const samples = chunk.samples instanceof Float32Array
          ? new Float32Array(chunk.samples)
          : Float32Array.from(chunk.samples);
        chunks.push(samples);
        totalSamples += samples.length;
        sampleRateHz = chunk.sampleRateHz || sampleRateHz;
        chunkCount++;
        self.postMessage({ type: "progress", chunkCount });
      }
      if (job !== activeJob) return;
      if (!totalSamples) throw new Error("The voice engine returned no audio samples.");
      const combined = new Float32Array(totalSamples);
      let offset = 0;
      for (const chunk of chunks) {
        combined.set(chunk, offset);
        offset += chunk.length;
      }
      self.postMessage({
        type: "audio",
        samples: combined.buffer,
        sampleRateHz,
        chunkCount
      }, [combined.buffer]);
    } catch (error) {
      if (job === activeJob) {
        self.postMessage({ type: "error", message: error?.message || String(error) });
      }
    }
  }
});
