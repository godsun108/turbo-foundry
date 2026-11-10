import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const root = new URL("../projects/somebodys-gotta-do-it/", import.meta.url);
const [html, studio, worker] = await Promise.all([
  readFile(new URL("genesis-voice-studio.html", root), "utf8"),
  readFile(new URL("genesis-voice-studio.js", root), "utf8"),
  readFile(new URL("genesis-voice-worker.js", root), "utf8")
]);

test("studio offers pinned Kokoro GPU and CPU bundles without a manual model picker", () => {
  assert.match(html, /value="gpu"/);
  assert.match(html, /value="cpu"/);
  assert.doesNotMatch(html, /type="file"[^>]*\.litertlm/i);
  assert.match(studio, /kokoro_int8_gpu_fp16\.litertlm/);
  assert.match(studio, /kokoro_int8_fp16\.litertlm/);
});

test("MediaPipe receives the documented modelAssetPath URL", () => {
  assert.match(worker, /modelAssetPath:\s*data\.modelUrl/);
  assert.doesNotMatch(worker, /modelAssetBuffer/);
  assert.match(worker, /https:\\\/\\\/huggingface\\\.co\\\/litert-community/);
});

test("full-track spoken vocal button loads the canonical cue sheet", () => {
  assert.match(html, /id="loadTrackLyrics"/);
  assert.match(studio, /fetch\("\.\/cue-sheet\.md"/);
  assert.match(studio, /extractTrackLyrics/);
  assert.match(studio, /maxLength = 4000/);
});
