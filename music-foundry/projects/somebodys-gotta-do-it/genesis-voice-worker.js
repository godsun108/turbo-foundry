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
      const result = await engine.synthesize(data.text, { voiceId: data.voiceId });
      if (job !== activeJob) return;
      const samples = result.samples instanceof Float32Array
        ? result.samples
        : Float32Array.from(result.samples);
      const transferable = samples.buffer.slice(
        samples.byteOffset,
        samples.byteOffset + samples.byteLength
      );
      self.postMessage({
        type: "audio",
        samples: transferable,
        sampleRateHz: result.sampleRateHz
      }, [transferable]);
    } catch (error) {
      if (job === activeJob) {
        self.postMessage({ type: "error", message: error?.message || String(error) });
      }
    }
  }
});
