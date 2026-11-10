#!/usr/bin/env node
/**
 * Sovereign internal runner entry point.
 * Invoke this file through Sovereign-Offline POST /v1/execute with command=node.
 * All child processes use spawn(..., shell:false); no hosted CI, shell, CDN or network.
 */
import { spawn } from "node:child_process";
import path from "node:path";
import process from "node:process";

const root = process.cwd();
const checks = [
  ["syntax: Voice Studio", ["--check", "--input-type=module", "<", "music-foundry/projects/somebodys-gotta-do-it/genesis-voice-studio.js"]],
  ["syntax: singing worker", ["--check", "--input-type=module", "<", "music-foundry/projects/somebodys-gotta-do-it/genesis-voice-worker.js"]],
  ["syntax: singing DSP", ["--check", "music-foundry/voice/genesis-singing-dsp.mjs"]],
  ["tests: singing DSP", ["--test", "music-foundry/tests/test_genesis_singing_dsp.mjs"]]
];

function execute(label, args) {
  return new Promise((resolve) => {
    const normalized = args.includes("<")
      ? ["--input-type=module", "-e", `import fs from 'node:fs'; import vm from 'node:vm'; const source=fs.readFileSync(${JSON.stringify(path.join(root,args.at(-1)))},'utf8'); new vm.SourceTextModule(source); `]
      : args;
    const child = spawn(process.execPath, normalized, {
      cwd: root,
      env: { PATH: process.env.PATH || "", HOME: process.env.HOME || "" },
      shell: false,
      stdio: ["ignore", "pipe", "pipe"]
    });
    let stdout = "", stderr = "", settled = false;
    const cap = (current, chunk) => (current + chunk.toString()).slice(-24000);
    child.stdout.on("data", chunk => { stdout = cap(stdout, chunk); });
    child.stderr.on("data", chunk => { stderr = cap(stderr, chunk); });
    const timer = setTimeout(() => {
      if (!settled) { settled = true; child.kill("SIGKILL"); resolve({ label, ok: false, timeout: true, stdout, stderr }); }
    }, 60000);
    child.on("error", error => {
      if (settled) return;
      settled = true; clearTimeout(timer);
      resolve({ label, ok: false, error: error.message, stdout, stderr });
    });
    child.on("close", (code, signal) => {
      if (settled) return;
      settled = true; clearTimeout(timer);
      resolve({ label, ok: code === 0, code, signal, stdout, stderr });
    });
  });
}

const results = [];
for (const [label, args] of checks) {
  const result = await execute(label, args);
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
