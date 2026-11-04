import { FilesetResolver, TextToSpeech } from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-audio@1.2.2/+esm";

const WASM_ROOT = "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-audio@1.2.2/wasm";
const MAX_OUTPUT_SECONDS = 180;
let engine = null;
let activeJob = 0;
let loading = false;

self.addEventListener("message", async (event) => {
  const data = event.data || {};
  if (data.type === "cancel") {
    activeJob++;
    try { engine?.cancel(); } catch {}
    self.postMessage({ type: "cancelled" });
    return;
  }

  if (data.type === "init") {
    if (loading || engine) {
      self.postMessage({ type: "error", message: "A model is already loading or loaded. Reload this page to change models." });
      return;
    }
    loading = true;
    try {
      self.postMessage({ type: "status", message: "Loading MediaPipe audio runtime…" });
      const audioFileset = await FilesetResolver.forAudioTasks(WASM_ROOT);
      self.postMessage({ type: "status", message: "Opening the selected model file locally…" });
      const modelReader = data.file.stream().getReader();
      engine = await TextToSpeech.createFromOptions(audioFileset, {
        baseOptions: { modelAssetBuffer: modelReader, delegate: data.delegate },
        speakingRate: data.speakingRate,
        cacheDirectory: ":nocache"
      });
      self.postMessage({ type: "status", message: "Model loaded. Enumerating available voices…" });
      const voices = await engine.listVoices();
      if (!Array.isArray(voices) || !voices.length) {
        throw new Error("The model loaded but did not expose any selectable voices.");
      }
      self.postMessage({ type: "ready", voices });
    } catch (error) {
      engine = null;
      self.postMessage({ type: "error", message: error?.message || String(error) });
    } finally {
      loading = false;
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
      const stream = await engine.synthesizeStream(data.text, { voiceId: data.voiceId });
      for await (const chunk of stream) {
        if (job !== activeJob) return;
        const samples = chunk.samples instanceof Float32Array
          ? new Float32Array(chunk.samples)
          : Float32Array.from(chunk.samples);
        const chunkRate = chunk.sampleRateHz || sampleRateHz;
        if (chunkCount && chunkRate !== sampleRateHz) {
          throw new Error("The voice engine changed sample rate during one take.");
        }
        sampleRateHz = chunkRate;
        totalSamples += samples.length;
        if (totalSamples > sampleRateHz * MAX_OUTPUT_SECONDS) {
          try { engine.cancel(); } catch {}
          throw new Error("Take exceeded the 3-minute prototype limit. Shorten the text and try again.");
        }
        chunks.push(samples);
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
      self.postMessage({ type: "audio", samples: combined.buffer, sampleRateHz, chunkCount }, [combined.buffer]);
    } catch (error) {
      if (job === activeJob) self.postMessage({ type: "error", message: error?.message || String(error) });
    }
  }
});
