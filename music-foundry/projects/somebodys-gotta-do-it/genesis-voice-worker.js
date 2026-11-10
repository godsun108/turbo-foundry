import { FilesetResolver, TextToSpeech } from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-audio@1.2.2/+esm";
import { renderSingingScore } from "../../voice/genesis-singing-dsp.mjs";

const WASM_ROOT = "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-audio@1.2.2/wasm";
const MAX_OUTPUT_SECONDS = 180;
const MAX_SCORE_BYTES = 2_000_000;
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
      if (typeof data.modelUrl !== "string" ||
          !/^https:\/\/huggingface\.co\/litert-community\/Kokoro-82M\/resolve\/main\/kokoro_int8_(gpu_fp16|fp16)\.litertlm$/.test(data.modelUrl)) {
        throw new Error("Choose one of the two pinned Kokoro model bundles.");
      }
      self.postMessage({ type: "status", message: "Downloading or opening the pinned Kokoro model. The first download is about 295 MB…" });
      engine = await TextToSpeech.createFromOptions(audioFileset, {
        baseOptions: { modelAssetPath: data.modelUrl, delegate: data.delegate },
        defaultVoiceId: "af_heart",
        speakingRate: data.speakingRate,
        cacheDirectory: ""
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

  if (data.type === "synthesize" || data.type === "synthesize-score") {
    if (!engine) {
      self.postMessage({ type: "error", message: "Load a local voice model before synthesis." });
      return;
    }
    const job = ++activeJob;
    try {
      const synthesizeText = async (text) => {
        const chunks = [];
        let totalSamples = 0;
        let sampleRateHz = 24000;
        const stream = await engine.synthesizeStream(text, { voiceId: data.voiceId });
        for await (const chunk of stream) {
          if (job !== activeJob) throw new Error("Synthesis cancelled.");
          const samples = chunk.samples instanceof Float32Array
            ? new Float32Array(chunk.samples)
            : Float32Array.from(chunk.samples);
          const chunkRate = chunk.sampleRateHz || sampleRateHz;
          if (totalSamples && chunkRate !== sampleRateHz) {
            throw new Error("The voice engine changed sample rate during one syllable.");
          }
          sampleRateHz = chunkRate;
          totalSamples += samples.length;
          if (totalSamples > sampleRateHz * 20) {
            try { engine.cancel(); } catch {}
            throw new Error("One syllable exceeded the 20-second safety limit.");
          }
          chunks.push(samples);
        }
        if (job !== activeJob) throw new Error("Synthesis cancelled.");
        if (!totalSamples) throw new Error("The voice engine returned no audio samples.");
        const combined = new Float32Array(totalSamples);
        let offset = 0;
        for (const chunk of chunks) { combined.set(chunk, offset); offset += chunk.length; }
        return { samples: combined, sampleRateHz };
      };

      if (data.type === "synthesize") {
        const audio = await synthesizeText(data.text);
        if (job !== activeJob) return;
        if (audio.samples.length > audio.sampleRateHz * MAX_OUTPUT_SECONDS) {
          throw new Error("Take exceeded the 3-minute prototype limit. Shorten the text and try again.");
        }
        self.postMessage({
          type: "audio", mode: "spoken", samples: audio.samples.buffer,
          sampleRateHz: audio.sampleRateHz, chunkCount: 1
        }, [audio.samples.buffer]);
        return;
      }

      if (typeof data.scoreText !== "string" || data.scoreText.length > MAX_SCORE_BYTES) {
        throw new Error("Choose a valid Music Foundry score file smaller than 2 MB.");
      }
      let score;
      try { score = JSON.parse(data.scoreText); }
      catch { throw new Error("The selected score is not valid JSON."); }

      self.postMessage({ type: "status", message: "Reading score and checking every placed syllable…" });
      const rendered = await renderSingingScore({
        score,
        sampleRate: 48000,
        synthesizeText,
        isCancelled: () => job !== activeJob,
        onProgress: ({ completed, total, lyric }) => {
          self.postMessage({
            type: "singing-progress",
            completed, total, lyric
          });
        }
      });
      if (job !== activeJob) return;
      const samples = rendered.samples;
      self.postMessage({
        type: "audio",
        mode: "sung",
        samples: samples.buffer,
        sampleRateHz: rendered.sampleRateHz,
        metadata: {
          title: rendered.title,
          syllableCount: rendered.syllableCount,
          tempoBpm: rendered.tempoBpm,
          durationSeconds: rendered.durationSeconds,
          algorithm: "kokoro-tts+psola-v1",
          source: "local-selected-litertlm-model",
          requiresUserVoice: false,
          requiresReferenceAudio: false,
          inferenceNetworkAccess: false,
          status: "prototype_render_pending_audition"
        }
      }, [samples.buffer]);
    } catch (error) {
      if (job === activeJob) self.postMessage({ type: "error", message: error?.message || String(error) });
    }
  }
});
