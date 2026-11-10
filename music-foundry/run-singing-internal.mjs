#!/usr/bin/env node
/**
 * Sovereign internal runner entry point.
 * Invoke through Sovereign-Offline POST /v1/execute with command=node.
 * Uses shell-free Node child processes and no hosted CI or network.
 */
import { spawn } from "node:child_process";
import { readFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";

const root = process.cwd();
const checks = [
  { label: "syntax: Voice Studio", args: ["--check", "--input-type=module"], stdin: "music-foundry/projects/somebodys-gotta-do-it/genesis-voice-studio.js" },
  { label: "syntax: singing worker", args: ["--check", "--input-type=module"], stdin: "music-foundry/projects/somebodys-gotta-do-it/genesis-voice-worker.js" },
  { label: "syntax: singing DSP", args: ["--check", "music-foundry/voice/genesis-singing-dsp.mjs"] },
  { label: "syntax: offline service worker", args: ["--check", "music-foundry/projects/somebodys-gotta-do-it/genesis-voice-sw.js"] },
  { label: "tests: singing DSP", args: ["--test", "music-foundry/tests/test_genesis_singing_dsp.mjs"] }
];

function execute(check) {
  return new Promise(async (resolve) => {
    const child = spawn(process.execPath, check.args, {
      cwd: root,
      env: { PATH: process.env.PATH || "", HOME: process.env.HOME || "" },
      shell: false,
      stdio: ["pipe", "pipe", "pipe"]
    });
    let stdout = "", stderr = "", settled = false;
    const cap = (current, chunk) => (current + chunk.toString()).slice(-24000);
    child.stdout.on("data", chunk => { stdout = cap(stdout, chunk); });
    child.stderr.on("data", chunk => { stderr = cap(stderr, chunk); });
    const timer = setTimeout(() => {
      if (!settled) {
        settled = true;
        child.kill("SIGKILL");
        resolve({ label: check.label, ok: false, timeout: true, stdout, stderr });
      }
    }, 60000);
    child.on("error", error => {
      if (settled) return;
      settled = true; clearTimeout(timer);
      resolve({ label: check.label, ok: false, error: error.message, stdout, stderr });
    });
    child.on("close", (code, signal) => {
      if (settled) return;
      settled = true; clearTimeout(timer);
      resolve({ label: check.label, ok: code === 0, code, signal, stdout, stderr });
    });
    try {
      if (check.stdin) child.stdin.end(await readFile(path.join(root, check.stdin)));
      else child.stdin.end();
    } catch (error) {
      child.kill("SIGKILL");
      if (!settled) {
        settled = true; clearTimeout(timer);
        resolve({ label: check.label, ok: false, error: error.message, stdout, stderr });
      }
    }
  });
}

const results = [];
for (const check of checks) {
  const result = await execute(check);
  results.push(result);
  process.stdout.write(JSON.stringify(result) + "\n");
  if (!result.ok) break;
}
const passed = results.filter(result => result.ok).length;
process.stdout.write(JSON.stringify({
  schema: "sovereign.music-foundry.internal-run.v1",
  runner: "sovereign-offline-controlled-executor",
  network: "not-used",
  hostedRunner: false,
  passed,
  total: checks.length,
  ok: passed === checks.length
}) + "\n");
if (passed !== checks.length) process.exitCode = 1;
