import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

const [modulePath, wasmPath] = process.argv.slice(2);
if (!modulePath || !wasmPath) throw new Error("Usage: node wasm_smoke_test.mjs <module.mjs> <module.wasm>");
const { default: createEarthStudioEngine } = await import(pathToFileURL(modulePath).href);
const module = await createEarthStudioEngine({
  wasmBinary: readFileSync(wasmPath),
  locateFile: path => new URL(path, pathToFileURL(modulePath)).href
});
const engine = module._earth_engine_create(48000);
if (!engine) throw new Error("WASM engine creation failed");
const parameters = module._malloc(36);
const output = module._malloc(128 * 2 * 4);
const events = module._malloc(12);
if (!parameters || !output || !events) throw new Error("WASM smoke-test allocation failed");
const view = new DataView(module.HEAPU8.buffer);
view.setUint32(parameters, 0, true);
view.setFloat32(parameters + 4, .02, true);
view.setFloat32(parameters + 8, .18, true);
view.setFloat32(parameters + 12, .7, true);
view.setFloat32(parameters + 16, .3, true);
view.setFloat32(parameters + 20, 8000, true);
view.setFloat32(parameters + 24, 0, true);
view.setFloat32(parameters + 28, 5, true);
view.setFloat32(parameters + 32, 0, true);
if (module._earth_engine_set_instrument(engine, parameters) !== 0) throw new Error("WASM instrument parameter setup failed");
view.setFloat32(parameters + 12, 2, true);
if (module._earth_engine_set_instrument(engine, parameters) !== -1) throw new Error("WASM C ABI did not reject invalid sustain");
view.setFloat32(parameters + 12, .7, true);
view.setUint32(events, 0, true);
view.setUint8(events + 4, 0);
view.setUint8(events + 5, 0);
view.setUint8(events + 6, 69);
view.setUint8(events + 7, 0);
view.setFloat32(events + 8, 1, true);
if (module._earth_engine_render(engine, output, 128, events, 1) !== 0) throw new Error("WASM render call failed");
const samples = module.HEAPF32.subarray(output >>> 2, (output >>> 2) + 256);
let peak = 0;
for (let i = 0; i < samples.length; i++) peak = Math.max(peak, Math.abs(samples[i]));
if (!(peak > .0001)) throw new Error("WASM engine rendered silence");
if (module._earth_engine_active_voices(engine) !== 1) throw new Error("WASM voice count did not update");
module._earth_engine_destroy(engine);
module._free(events); module._free(output); module._free(parameters);
process.stdout.write("EARTH STUDIO WASM smoke test passed; peak=" + peak.toFixed(6) + "\n");
