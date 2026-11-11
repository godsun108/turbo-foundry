const $ = (id) => document.getElementById(id);

// Activate the app-scoped cache before creating the dedicated inference worker.
// The worker's pinned MediaPipe ESM/WASM requests can then be cached by the
// service worker after the first online load and reused on later offline starts.
let offlineCacheReady = false;
if ("serviceWorker" in navigator && window.isSecureContext) {
  try {
    await navigator.serviceWorker.register("./genesis-voice-sw.js");
    await navigator.serviceWorker.ready;
    offlineCacheReady = true;
  } catch {
    // Keep the studio usable when service workers are unavailable or blocked.
  }
}
const worker = new Worker("./genesis-voice-worker.js", { type: "module" });
$("text").maxLength = 4000;
let ready = false;
let busy = false;
let audioUrl = null;
let audioContext = null;
let lastMode = "spoken";
let lastBlob = null;
let bundledScoreText = null;
let oneTapFineChinaPending = false;
async function startFineChinaOneTap(){
  if(busy)return;
  $("oneTapFineChina").disabled=true;
  setStatus("Loading Fine China score and preparing the singer…");
  try{
    const response=await fetch("../fine-china/vocal_score_draft.json",{cache:"no-store"});
    if(!response.ok)throw new Error("Fine China score could not be loaded.");
    const scoreText=await response.text();
    const parsed=JSON.parse(scoreText);
    if(parsed.project_id!=="fine-china"||parsed.tempo_bpm!==126)throw new Error("Fine China score identity check failed.");
    bundledScoreText=scoreText;
    $("score").value="";
    await resumeAudio();
    if(!ready){oneTapFineChinaPending=true;setStatus("First-time setup: loading the on-device singer. Keep this page open while the model downloads…");$("load").click();}
    else{setBusy(true);setStatus("Singer ready. Rendering the Fine China chorus…");worker.postMessage({type:"synthesize-score",scoreText:bundledScoreText,voiceId:$("voice").value});}
  }catch(error){$("oneTapFineChina").disabled=false;setStatus("Could not start Fine China: "+error.message);}
}
$("oneTapFineChina").addEventListener("click",startFineChinaOneTap);

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
  $("delegate").disabled = true;
  $("score").disabled = busy;
  $("sendToMix").disabled = busy || !lastBlob || lastMode !== "sung";
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

$("model").value = navigator.gpu ? "gpu" : "cpu";
$("delegate").value = navigator.gpu ? "GPU" : "CPU";
const browserChecks = [
  "Secure context: " + (window.isSecureContext ? "yes" : "no"),
  "Web Audio: " + (window.AudioContext || window.webkitAudioContext ? "available" : "unavailable"),
  "WebGPU API: " + (navigator.gpu ? "present" : "not present"),
  "Device memory hint: " + (navigator.deviceMemory ? navigator.deviceMemory + " GB" : "not exposed"),
  "Offline app/runtime cache: " + (offlineCacheReady ? "active" : "unavailable")
];
setStatus(browserChecks.join(" · ") + (navigator.gpu ? "" : " · CPU-compatible model selected."));
if (navigator.gpu) {
  navigator.gpu.requestAdapter().then((adapter) => {
    browserChecks.push("WebGPU adapter: " + (adapter ? "available" : "not available"));
    setStatus(browserChecks.join(" · "));
  }).catch((error) => {
    browserChecks.push("WebGPU adapter check failed: " + (error?.message || "unknown error"));
    setStatus(browserChecks.join(" · "));
  });
}

$("model").addEventListener("change", () => {
  const gpu = $("model").value === "gpu";
  $("delegate").value = gpu ? "GPU" : "CPU";
  if (gpu && !navigator.gpu) setStatus("This browser does not expose WebGPU. Choose the CPU model instead.");
});
$("load").addEventListener("click", () => {
  const variant = $("model").value;
  const delegate = variant === "gpu" ? "GPU" : "CPU";
  if (delegate === "GPU" && !navigator.gpu) {
    return setStatus("WebGPU is unavailable in this browser. Choose the CPU-compatible model.");
  }
  const filename = variant === "gpu" ? "kokoro_int8_gpu_fp16.litertlm" : "kokoro_int8_fp16.litertlm";
  const modelUrl = "https://huggingface.co/litert-community/Kokoro-82M/resolve/main/" + filename;
  setBusy(true);
  setStatus("Downloading or opening the 295 MB Kokoro model from its Apache-2.0 release. Keep this page open; the first install may take a while…");
  worker.postMessage({
    type: "init",
    modelUrl,
    delegate,
    speakingRate: Number($("rate").value)
  });
});

function extractTrackLyrics(markdown) {
  const output = [];
  let inLyrics = false;
  let includeAdlibs = false;
  for (const rawLine of markdown.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (line.startsWith("## Mix / edit notes") || line.startsWith("## Current implementation boundary")) break;
    if (line.startsWith("## ")) {
      inLyrics = true;
      includeAdlibs = false;
      continue;
    }
    if (!inLyrics || !line) continue;
    if (line.startsWith("**")) {
      includeAdlibs = line.includes("Optional response ad-libs");
      continue;
    }
    if (line.startsWith("- ")) {
      if (includeAdlibs) {
        const response = line.match(/—\s*[“"]([^”"]+)[”"]/);
        if (response) output.push(response[1]);
      }
      continue;
    }
    if (line.startsWith("Lead:") || line.startsWith("Group:")) {
      output.push(line.slice(line.indexOf(":") + 1).trim());
      continue;
    }
    if (line.startsWith("#") || line.startsWith(">")) continue;
    output.push(line);
  }
  const lyrics = output.join("\n").replace(/\n{3,}/g, "\n\n").trim();
  if (!lyrics) throw new Error("No lyric lines were found in the project cue sheet.");
  if (lyrics.length > 4000) throw new Error("The extracted lyrics exceed the 4,000-character studio limit.");
  return lyrics;
}

$("loadTrackLyrics").addEventListener("click", async () => {
  if (busy) return;
  setStatus("Loading the approved project cue sheet…");
  try {
    const response = await fetch("./cue-sheet.md", { cache: "no-store" });
    if (!response.ok) throw new Error("Cue sheet could not be loaded (" + response.status + ").");
    $("text").value = extractTrackLyrics(await response.text());
    setStatus("Track lyrics loaded from cue-sheet.md. Load the voice model, choose a voice, then generate the spoken-led vocal pass.");
  } catch (error) {
    setStatus("Could not load track lyrics: " + error.message);
  }
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
  if (text.length > 4000) return setStatus("Text exceeds the 4,000-character prototype limit.");
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


$("sendToMix").addEventListener("click", async () => {
  const token = $("apiToken").value.trim();
  const jobId = $("renderJobId").value.trim();
  if (!lastBlob || lastMode !== "sung") return setStatus("Generate a Fine China sung take first.");
  if (!token) return setStatus("Enter the private Music Foundry access token.");
  if (!/^[0-9a-f-]{36}$/i.test(jobId)) return setStatus("Enter the instrumental render job ID.");
  $("sendToMix").disabled = true;
  setStatus("Uploading the sung WAV to your private Fine China render job and creating the mix…");
  try {
    const response = await fetch("/api/v1/jobs/" + jobId + "/vocal", {
      method: "POST",
      headers: { "Authorization": "Bearer " + token, "Content-Type": "audio/wav" },
      body: lastBlob
    });
    const result = await response.json().catch(() => ({ error: "Invalid server response" }));
    if (!response.ok) throw new Error(result.error || "Vocal upload failed (" + response.status + ").");
    const mixResponse = await fetch(result.final_mix_url, {
      headers: { "Authorization": "Bearer " + token }
    });
    if (!mixResponse.ok) throw new Error("The combined mix was created but could not be loaded for preview.");
    const mixBlob = await mixResponse.blob();
    releaseAudioUrl();
    audioUrl = URL.createObjectURL(mixBlob);
    $("preview").src = audioUrl;
    lastBlob = mixBlob;
    lastMode = "mixed";
    $("download").disabled = false;
    $("sendToMix").textContent = "Final mix created";
    $("sendToMix").disabled = true;
    setStatus("Fine China sung vocal and instrumental combined. Listen to the full mix above; download it for review. This is an audition mix, not a mastered release.");
  } catch (error) {
    $("sendToMix").disabled = false;
    setStatus("Could not create the mix: " + error.message);
  }
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
  anchor.download = lastMode === "mixed" ? "fine-china-vocal-instrumental-mix.wav" : (lastMode === "sung" ? "fine-china-sung-vocal.wav" : "genesis-spoken-take.wav");
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
    if(oneTapFineChinaPending){oneTapFineChinaPending=false;setBusy(true);setStatus("Singer ready. Rendering the Fine China chorus…");worker.postMessage({type:"synthesize-score",scoreText:bundledScoreText,voiceId:$("voice").value});}
  } else if (data.type === "progress") {
    setStatus("Generating speech locally… completed " + data.chunkCount + " audio chunk(s).");
  } else if (data.type === "singing-progress") {
    setStatus("Singing syllable " + data.completed + " of " + data.total + ": “" + data.lyric + "”");
  } else if (data.type === "audio") {
    const samples = new Float32Array(data.samples);
    const blob = encodeWav(samples, data.sampleRateHz);
    lastBlob = blob;
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
      $("oneTapFineChina").disabled=false;
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
