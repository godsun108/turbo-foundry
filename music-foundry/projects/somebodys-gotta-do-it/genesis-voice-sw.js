const CACHE_NAME = "genesis-voice-studio-v2";
const MAX_CDN_RESPONSE_BYTES = 64 * 1024 * 1024;
const MAX_MODEL_RESPONSE_BYTES = 350 * 1024 * 1024;
const SHELL_FILES = [
  "genesis-voice-studio.html",
  "genesis-voice-studio.js",
  "genesis-voice-worker.js",
  "../../voice/genesis-singing-dsp.mjs",
  "../fine-china/vocal_score_draft.json"
];

self.addEventListener("install", (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    const urls = SHELL_FILES.map((file) => new URL(file, self.registration.scope).href);
    await cache.addAll(urls);
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter((key) => key.startsWith("genesis-voice-studio-") && key !== CACHE_NAME)
      .map((key) => caches.delete(key)));
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;
  const url = new URL(request.url);

  if (url.origin === self.location.origin) {
    event.respondWith((async () => {
      const cache = await caches.open(CACHE_NAME);
      const cached = await cache.match(request);
      if (cached) return cached;
      try {
        const response = await fetch(request);
        if (response.ok) await cache.put(request, response.clone());
        return response;
      } catch (error) {
        if (request.mode === "navigate") {
          const fallback = await cache.match(new URL("genesis-voice-studio.html", self.registration.scope).href);
          if (fallback) return fallback;
        }
        throw error;
      }
    })());
    return;
  }

  // Only persist the exact pinned MediaPipe Tasks Audio package. The selected
  // .litertlm model is user-owned local input and is never fetched or cached here.
  const isPinnedRuntime = url.origin === "https://cdn.jsdelivr.net" &&
    url.pathname.startsWith("/npm/@mediapipe/tasks-audio@1.2.2/");
  const isPinnedModel = url.origin === "https://huggingface.co" &&
    url.pathname.startsWith("/litert-community/Kokoro-82M/resolve/main/") &&
    (url.pathname.endsWith("/kokoro_int8_gpu_fp16.litertlm") ||
     url.pathname.endsWith("/kokoro_int8_fp16.litertlm"));
  if (isPinnedRuntime || isPinnedModel) {
    event.respondWith((async () => {
      const cache = await caches.open(CACHE_NAME);
      const cached = await cache.match(request);
      if (cached) return cached;
      const response = await fetch(request);
      const declaredLength = Number(response.headers.get("content-length") || 0);
      const limit = isPinnedModel ? MAX_MODEL_RESPONSE_BYTES : MAX_CDN_RESPONSE_BYTES;
      if (response.ok && response.type !== "opaque" &&
          (!declaredLength || declaredLength <= limit)) {
        try { await cache.put(request, response.clone()); } catch {}
      }
      return response;
    })());
  }
});
