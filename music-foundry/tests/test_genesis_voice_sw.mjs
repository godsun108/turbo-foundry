import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import vm from "node:vm";

const source = await readFile(
  new URL("../projects/somebodys-gotta-do-it/genesis-voice-sw.js", import.meta.url),
  "utf8"
);

function harness() {
  const listeners = new Map();
  const cacheStore = new Map();
  const cacheCalls = [];
  const cache = {
    async addAll(urls) {
      cacheCalls.push({ type: "addAll", urls });
      for (const url of urls) cacheStore.set(url, { cached: true, url });
    },
    async match(request) {
      const key = typeof request === "string" ? request : request.url;
      return cacheStore.get(key);
    },
    async put(request, response) {
      const key = typeof request === "string" ? request : request.url;
      cacheStore.set(key, response);
      cacheCalls.push({ type: "put", key });
    }
  };
  const self = {
    location: { href: "https://example.test/music-foundry/projects/somebodys-gotta-do-it/genesis-voice-sw.js",
      origin: "https://example.test" },
    registration: { scope: "https://example.test/music-foundry/projects/somebodys-gotta-do-it/" },
    clients: { claim: async () => {} },
    skipWaiting: async () => {},
    addEventListener(type, fn) { listeners.set(type, fn); }
  };
  const context = {
    self,
    URL,
    caches: {
      async open(name) { return cache; },
      async keys() { return ["genesis-voice-studio-old"]; },
      async delete() { return true; }
    },
    fetch: async (request) => new Response("network:" + (request.url || request), {
      status: 200, headers: { "content-length": "12" }
    }),
    Response,
    Promise,
    Number
  };
  vm.runInNewContext(source, context, { filename: "genesis-voice-sw.js" });
  return { listeners, cacheStore, cacheCalls };
}

test("install pre-caches the app shell, DSP module, and score fixture", async () => {
  const h = harness();
  let installPromise;
  h.listeners.get("install")({ waitUntil(p) { installPromise = p; } });
  await installPromise;
  const call = h.cacheCalls.find(x => x.type === "addAll");
  assert.ok(call);
  assert.ok(call.urls.some(url => url.endsWith("/genesis-voice-studio.html")));
  assert.ok(call.urls.some(url => url.endsWith("/genesis-singing-dsp.mjs")));
  assert.ok(call.urls.some(url => url.endsWith("/vocal_score_draft.json")));
});

test("pinned MediaPipe runtime requests are cacheable", async () => {
  const h = harness();
  let responsePromise;
  const request = { method: "GET", url: "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-audio@1.2.2/wasm/audio_wasm_internal.wasm" };
  h.listeners.get("fetch")({ request, respondWith(p) { responsePromise = p; } });
  const response = await responsePromise;
  assert.equal(response.status, 200);
  assert.ok(h.cacheCalls.some(x => x.type === "put" && x.key === request.url));
});

test("unrelated third-party URLs and model file inputs are not intercepted", () => {
  const h = harness();
  let intercepted = false;
  const unrelated = { method: "GET", url: "https://untrusted.example/model.litertlm" };
  h.listeners.get("fetch")({ request: unrelated, respondWith() { intercepted = true; } });
  assert.equal(intercepted, false);
});

test("non-GET requests are not intercepted", () => {
  const h = harness();
  let intercepted = false;
  const request = { method: "POST", url: "https://example.test/execute" };
  h.listeners.get("fetch")({ request, respondWith() { intercepted = true; } });
  assert.equal(intercepted, false);
});
