const $ = (id) => document.getElementById(id);
const worker = new Worker("./genesis-voice-worker.js", { type: "module" });
$("text").maxLength = 1200;
let ready = false;
let busy = false;
let audioUrl = null;
let audioContext = null;
let lastMode = "spoken";
let bundledScoreText = null;

function setStatus(message) {
  $("status").textContent = message;
}

function setBusy(value) {
  busy = value;
  $("load").disabled = busy || ready;
  $("synthesize").disabled = busy || !ready;
  $("sing").disabled = busy || !ready || (!bundledScoreText && !$("score").files?.length);
  $("stop").disabled = !busy;
  $("model").disabled = busy || ready;
  $("delegate").disabled = busy || ready;
  $("score").disabled = busy;
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

async function resumeAudio() {
  const AudioContextClass = window.AudioContext || window.webkitAudioContext;
  if (!AudioContextClass) throw new Error("Web Audio is unavailable.");
  audioContext ??= new AudioContextClass();
  await audioContext.resume();
}

$("delegate").value = navigator.gpu ? "GPU" : "CPU";
const browserChecks = [
  "Secure context: " + (window.isSecureContext ? "yes" : "no"),
  "Web Audio: " + (window.AudioContext || window.webkitAudioContext ? "available" : "unavailable"),
  "WebGPU API: " + (navigator.gpu ? "present" : "not present"),
  "Device memory hint: " + (navigator.deviceMemory ? navigator.deviceMemory + " GB" : "not exposed")
];
setStatus(browserChecks.join(" · ") + (navigator.gpu ? "" : " · CPU mode selected; choose a CPU-compatible model."));
if (navigator.gpu) {
  navigator.gpu.requestAdapter().then((adapter) => {
    browserChecks.push("WebGPU adapter: " + (adapter ? "available" : "not available"));
    setStatus(browserChecks.join(" · "));
  }).catch((error) => {
    browserChecks.push("WebGPU adapter check failed: " + (error?.message || "unknown error"));
    setStatus(browserChecks.join(" · "));
  });
}

$("load").addEventListener("click", () => {
  const file = $("model").files?.[0];
  if (!file) return setStatus("Choose a .litertlm model file first.");
  if (!file.name.toLowerCase().endsWith(".litertlm") || file.size < 1024 * 1024) return setStatus("Choose a complete .litertlm model bundle.");
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

$("score").addEventListener("change", () => {
  bundledScoreText = null;
  setBusy(false);
  const file = $("score").files?.[0];
  if (file) setStatus("Score selected: " + file.name + ". Load the voice model, then generate the sung take.");
});

$("fineChina").addEventListener("click", async () => {
  if (busy) return;
  setStatus("Loading the bundled Fine China composition-draft score…");
  try {
    const response = await fetch("../fine-china/vocal_score_draft.json", { cache: "no-store" });
    if (!response.ok) throw new Error("Fine China score could not be loaded (" + response.status + ").");
    const text = await response.text();
    const parsed = JSON.parse(text);
    if (parsed.project_id !== "fine-china" || parsed.tempo_bpm !== 126) {
      throw new Error("The bundled Fine China score did not match the expected project.");
    }
    bundledScoreText = text;
    $("score").value = "";
    setBusy(false);
    setStatus("Fine China draft loaded: 73 placed syllables at 126 BPM. This is a composition draft—audition and approve the melody before release.");
  } catch (error) {
    bundledScoreText = null;
    setBusy(false);
    setStatus("Could not load Fine China score: " + error.message);
  }
});

$("synthesize").addEventListener("click", async () => {
  const text = $("text").value.trim();
  if (!text) return setStatus("Enter text to synthesize.");
  if (text.length > 1200) return setStatus("Text exceeds the 1,200-character prototype limit.");
  try { await resumeAudio(); }
  catch (error) { return setStatus("Audio playback could not start: " + error.message); }
  setBusy(true);
  setStatus("Synthesizing speech locally…");
  worker.postMessage({ type: "synthesize", text, voiceId: $("voice").value });
});

$("sing").addEventListener("click", async () => {
  const file = $("score").files?.[0];
  if (!bundledScoreText && !file) return setStatus("Choose a Music Foundry vocal-score JSON file or load the Fine China draft.");
  if (file && file.size > 2_000_000) return setStatus("Score file exceeds the 2 MB safety limit.");
  let scoreText = bundledScoreText;
  try {
    if (!scoreText) scoreText = await file.text();
    JSON.parse(scoreText);
    await resumeAudio();
  } catch (error) {
    return setStatus("Score or audio setup error: " + error.message);
  }
  setBusy(true);
  setStatus("Preparing score. The local voice will sing each placed syllable on its MIDI pitch…");
  worker.postMessage({
    type: "synthesize-score",
    scoreText,
    voiceId: $("voice").value
  });
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
  anchor.download = lastMode === "sung" ? "genesis-sung-take.wav" : "genesis-spoken-take.wav";
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
  if (data.type === "status") {
    setStatus(data.message);
  } else if (data.type === "ready") {
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
    setStatus("Model ready. " + data.voices.length + " voices available. Speech and singing inference stay in this browser.");
  } else if (data.type === "progress") {
    setStatus("Generating speech locally… completed " + data.chunkCount + " audio chunk(s).");
  } else if (data.type === "singing-progress") {
    setStatus("Singing syllable " + data.completed + " of " + data.total + ": “" + data.lyric + "”");
  } else if (data.type === "audio") {
    const samples = new Float32Array(data.samples);
    const blob = encodeWav(samples, data.sampleRateHz);
    releaseAudioUrl();
    audioUrl = URL.createObjectURL(blob);
    $("preview").src = audioUrl;
    $("preview").hidden = false;
    $("download").disabled = false;
    lastMode = data.mode || "spoken";
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
    if (lastMode === "sung") {
      const meta = data.metadata || {};
      setStatus("Sung take rendered: " + (meta.syllableCount || "—") + " syllables · " +
        (meta.tempoBpm || "—") + " BPM · " + samples.length + " samples at " +
        data.sampleRateHz + " Hz. This is a prototype render; audition it before using it in a release.");
    } else {
      setStatus("Spoken take rendered. " + samples.length + " samples at " + data.sampleRateHz +
        " Hz. Download the WAV and import it into the vocal timeline.");
    }
  } else if (data.type === "cancelled") {
    setBusy(false);
    setStatus("Synthesis cancelled.");
  } else if (data.type === "error") {
    setBusy(false);
    setStatus("Voice engine error: " + data.message);
  }
});

window.addEventListener("beforeunload", () => { releaseAudioUrl(); worker.terminate(); });

worker.addEventListener("error", (event) => {
  setBusy(false);
  setStatus("Voice worker failed: " + (event.message || "unknown worker error"));
});
