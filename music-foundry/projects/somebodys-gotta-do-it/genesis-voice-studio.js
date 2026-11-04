const $ = (id) => document.getElementById(id);
const worker = new Worker("./genesis-voice-worker.js", { type: "module" });
let ready = false;
let audioUrl = null;
let audioContext = null;

function setStatus(message) {
  $("status").textContent = message;
}

function setBusy(busy) {
  $("load").disabled = busy || ready;
  $("synthesize").disabled = busy || !ready;
  $("stop").disabled = !busy;
}

function releaseAudioUrl() {
  if (audioUrl) URL.revokeObjectURL(audioUrl);
  audioUrl = null;
}

function encodeWav(samples, sampleRate) {
  const bytes = new ArrayBuffer(44 + samples.length * 2);
  const view = new DataView(bytes);
  const writeText = (offset, value) => {
    for (let i = 0; i < value.length; i++) view.setUint8(offset + i, value.charCodeAt(i));
  };
  writeText(0, "RIFF");
  view.setUint32(4, 36 + samples.length * 2, true);
  writeText(8, "WAVE");
  writeText(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeText(36, "data");
  view.setUint32(40, samples.length * 2, true);
  for (let i = 0; i < samples.length; i++) {
    const value = Number.isFinite(samples[i]) ? Math.max(-1, Math.min(1, samples[i])) : 0;
    view.setInt16(44 + i * 2, Math.round(value * 32767), true);
  }
  return new Blob([bytes], { type: "audio/wav" });
}

$("delegate").value = navigator.gpu ? "GPU" : "CPU";
if (!navigator.gpu) setStatus("WebGPU is not detected. CPU mode selected; use a CPU-compatible model bundle.");

$("load").addEventListener("click", () => {
  const file = $("model").files?.[0];
  if (!file) return setStatus("Choose a .litertlm model file first.");
  const delegate = $("delegate").value;
  if (delegate === "GPU" && !navigator.gpu) {
    return setStatus("WebGPU is unavailable in this browser. Select CPU and a CPU-compatible model.");
  }
  setBusy(true);
  setStatus("Loading model into the local worker. Large model files can take time and memory…");
  worker.postMessage({
    type: "init",
    file,
    delegate,
    speakingRate: Number($("rate").value)
  });
});

$("synthesize").addEventListener("click", async () => {
  const text = $("text").value.trim();
  if (!text) return setStatus("Enter text to synthesize.");
  if (text.length > 4000) return setStatus("Text exceeds the 4,000-character limit.");
  try {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) throw new Error("Web Audio is unavailable.");
    audioContext ??= new AudioContextClass();
    await audioContext.resume();
  } catch (error) {
    return setStatus("Audio playback could not start: " + error.message);
  }
  setBusy(true);
  setStatus("Synthesizing locally…");
  worker.postMessage({ type: "synthesize", text, voiceId: $("voice").value });
});

$("stop").addEventListener("click", () => {
  worker.postMessage({ type: "cancel" });
  setBusy(false);
  setStatus("Cancellation requested.");
});

$("download").addEventListener("click", () => {
  const player = $("preview");
  if (!player.src) return;
  const anchor = document.createElement("a");
  anchor.href = player.src;
  anchor.download = "genesis-spoken-take.wav";
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
});

$("voice").addEventListener("change", () => {
  const option = $("voice").selectedOptions[0];
  $("locale").value = option?.dataset.locale || "—";
});

worker.addEventListener("message", async (event) => {
  const data = event.data || {};
  if (data.type === "ready") {
    ready = true;
    $("voice").replaceChildren();
    for (const voice of data.voices) {
      const option = document.createElement("option");
      option.value = voice.voiceId;
      option.textContent = voice.displayName + " (" + voice.voiceId + ")";
      option.dataset.locale = voice.locale || "";
      $("voice").append(option);
    }
    const preferred = [...$("voice").options].find((option) => option.value === "af_heart");
    if (preferred) $("voice").value = preferred.value;
    $("voice").disabled = false;
    $("locale").value = $("voice").selectedOptions[0]?.dataset.locale || "—";
    setBusy(false);
    $("load").disabled = true;
    setStatus("Model ready. " + data.voices.length + " voices available. No audio has been uploaded.");
  } else if (data.type === "audio") {
    const samples = new Float32Array(data.samples);
    const blob = encodeWav(samples, data.sampleRateHz);
    releaseAudioUrl();
    audioUrl = URL.createObjectURL(blob);
    $("preview").src = audioUrl;
    $("preview").hidden = false;
    $("download").disabled = false;
    try {
      const buffer = audioContext.createBuffer(1, samples.length, data.sampleRateHz);
      buffer.copyToChannel(samples, 0);
      const source = audioContext.createBufferSource();
      source.buffer = buffer;
      source.connect(audioContext.destination);
      source.start();
    } catch (error) {
      setStatus("WAV ready; automatic preview failed: " + error.message);
    }
    setBusy(false);
    setStatus("Spoken take rendered. " + samples.length + " samples at " + data.sampleRateHz + " Hz. Download the WAV and import it into the vocal timeline.");
  } else if (data.type === "cancelled") {
    setBusy(false);
    setStatus("Synthesis cancelled.");
  } else if (data.type === "error") {
    setBusy(false);
    setStatus("Voice engine error: " + data.message);
  }
});

window.addEventListener("beforeunload", releaseAudioUrl);
