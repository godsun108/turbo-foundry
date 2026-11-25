/**
 * EARTH STUDIO v1 browser persistence adapter.
 * Stores project manifests and binary assets locally in IndexedDB.
 * No network access, cloud dependency, or audio callback work.
 */
export const FORMAT = "earthsession";
export const SCHEMA_VERSION = 1;
export const MAX_PROJECT_BYTES = 512 * 1024 * 1024;

export function validateSession(session) {
  const errors = [];
  if (!session || typeof session !== "object" || Array.isArray(session)) return ["session must be an object"];
  if (session.format !== FORMAT) errors.push("format must be earthsession");
  if (session.schemaVersion !== SCHEMA_VERSION) errors.push("unsupported schemaVersion");
  for (const key of ["id", "name", "createdAt", "updatedAt"]) {
    if (typeof session[key] !== "string" || !session[key].trim()) errors.push(key + " must be a non-empty string");
  }
  if (typeof session.tempo !== "number" || !Number.isFinite(session.tempo) || session.tempo < 40 || session.tempo > 240) errors.push("tempo must be between 40 and 240");
  if (!session.meter || !Number.isInteger(session.meter.numerator) || session.meter.numerator < 1 || session.meter.numerator > 32 || ![1,2,4,8,16,32].includes(session.meter.denominator)) errors.push("meter is invalid");
  if (![44100,48000,88200,96000,176400,192000].includes(session.sampleRate)) errors.push("sampleRate is unsupported");
  if (!Array.isArray(session.tracks) || !Array.isArray(session.assets)) errors.push("tracks and assets must be arrays");
  if (session.instrument !== undefined) {
    const p = session.instrument;
    if (!p || typeof p !== "object" || Array.isArray(p)) errors.push("instrument settings must be an object");
    else {
      if (!["sine","sawtooth","square","triangle"].includes(p.oscillator)) errors.push("instrument oscillator is invalid");
      for (const [key,min,max] of [["attack",1,1000],["decay",1,2000],["sustain",0,100],["release",10,4000],["cutoff",80,18000],["vibrato",0,20],["bend",-12,12]]) {
        if (typeof p[key] !== "number" || !Number.isFinite(p[key]) || p[key] < min || p[key] > max) errors.push("instrument " + key + " is outside its supported range");
      }
    }
  }
  if (session.performance !== undefined) {
    const performance = session.performance;
    const allowedTargets = new Set(["attack","decay","sustain","release","cutoff","vibrato","bend"]);
    if (!performance || typeof performance !== "object" || Array.isArray(performance)) {
      errors.push("performance settings must be an object");
    } else {
      for (const key of Object.keys(performance)) {
        if (key !== "midiCCMappings") errors.push("performance contains an unsupported setting");
      }
      const mappings = performance.midiCCMappings;
      if (mappings !== undefined) {
        if (!mappings || typeof mappings !== "object" || Array.isArray(mappings)) {
          errors.push("performance MIDI CC mappings must be an object");
        } else {
          for (const [target, mapping] of Object.entries(mappings)) {
            if (!allowedTargets.has(target)) errors.push("performance MIDI CC mapping target is unsupported");
            if (!mapping || typeof mapping !== "object" || Array.isArray(mapping) ||
                Object.keys(mapping).some(key => key !== "controller") ||
                !Number.isInteger(mapping.controller) || mapping.controller < 0 || mapping.controller > 127) {
              errors.push("performance MIDI CC mapping controller must be an integer from 0 to 127");
            }
          }
        }
      }
    }
  }
  const ids = new Set();
  const storageKeys = new Set();
  for (const asset of session.assets || []) {
    if (!asset || typeof asset.id !== "string" || ids.has(asset.id)) errors.push("asset IDs must be unique strings");
    else ids.add(asset.id);
    if (!asset || typeof asset.storageKey !== "string" || !asset.storageKey || asset.storageKey.split("/").some(part => !part || part === "." || part === "..") || asset.storageKey.startsWith("/") || asset.storageKey.includes(String.fromCharCode(92)) || asset.storageKey.includes(String.fromCharCode(0))) errors.push("asset storageKey must be a safe relative key");
    else if (storageKeys.has(asset.storageKey)) errors.push("asset storageKeys must be unique");
    else storageKeys.add(asset.storageKey);
    if (!asset || !Number.isInteger(asset.sizeBytes) || asset.sizeBytes < 0) errors.push("asset sizeBytes must be a non-negative integer");
    if (!asset || typeof asset.sha256 !== "string" || !/^[a-f0-9]{64}$/.test(asset.sha256)) errors.push("asset sha256 must be a lowercase SHA-256 digest");
  }
  const assetIds = new Set((session.assets || []).map(a => a && a.id));
  const trackIds = new Set();
  for (const track of session.tracks || []) {
    if (!track || typeof track.id !== "string" || trackIds.has(track.id)) errors.push("track IDs must be unique strings");
    else trackIds.add(track.id);
    if (!track || !["audio","midi","instrument"].includes(track.kind)) errors.push("track kind is invalid");
    if (!track || typeof track.gain !== "number" || !Number.isFinite(track.gain) || track.gain < 0 || track.gain > 2) errors.push("track gain is outside 0..2");
    if (!track || typeof track.pan !== "number" || !Number.isFinite(track.pan) || track.pan < -1 || track.pan > 1) errors.push("track pan is outside -1..1");
    if (!track || typeof track.muted !== "boolean" || typeof track.solo !== "boolean") errors.push("track mute and solo flags must be boolean");
    if (!track || !Array.isArray(track.clips)) errors.push("track clips must be an array");
    if (track && track.midiClips !== undefined && !Array.isArray(track.midiClips)) errors.push("track midiClips must be an array when present");
    const midiClipIds = new Set();
    for (const midiClip of (track && track.midiClips) || []) {
      if (!midiClip || typeof midiClip.id !== "string" || !midiClip.id.trim() || midiClipIds.has(midiClip.id)) errors.push("MIDI clip IDs must be unique non-empty strings per track");
      else midiClipIds.add(midiClip.id);
      if (!track || !["midi","instrument"].includes(track.kind)) errors.push("MIDI clips require a midi or instrument track");
      if (!midiClip || !Number.isInteger(midiClip.startTick) || midiClip.startTick < 0 || !Number.isInteger(midiClip.lengthTicks) || midiClip.lengthTicks < 1 || !Array.isArray(midiClip.notes)) errors.push("MIDI clip timing or notes are invalid");
      const noteIds = new Set();
      for (const note of (midiClip && midiClip.notes) || []) {
        if (!note || typeof note.id !== "string" || !note.id.trim() || noteIds.has(note.id)) errors.push("MIDI note IDs must be unique non-empty strings per clip");
        else noteIds.add(note.id);
        if (!note || !Number.isInteger(note.note) || note.note < 0 || note.note > 127) errors.push("MIDI note number must be 0..127");
        if (!note || !Number.isInteger(note.startTick) || note.startTick < 0 || !Number.isInteger(note.durationTicks) || note.durationTicks < 1) errors.push("MIDI note timing is invalid");
        if (!note || !Number.isInteger(note.velocity) || note.velocity < 1 || note.velocity > 127) errors.push("MIDI note velocity must be 1..127");
        if (!note || !Number.isInteger(note.channel) || note.channel < 0 || note.channel > 15) errors.push("MIDI note channel must be 0..15");
        if (midiClip && note && Number.isInteger(note.startTick) && Number.isInteger(note.durationTicks) && Number.isInteger(midiClip.lengthTicks) && note.startTick + note.durationTicks > midiClip.lengthTicks) errors.push("MIDI note extends beyond its clip length");
      }
    }
    for (const clip of (track && track.clips) || []) {
      if (!clip || !assetIds.has(clip.assetId)) errors.push("clip references a missing asset");
      if (!clip || !Number.isFinite(clip.startSeconds) || clip.startSeconds < 0 || !Number.isFinite(clip.sourceStartSeconds) || clip.sourceStartSeconds < 0 || !Number.isFinite(clip.durationSeconds) || clip.durationSeconds <= 0) errors.push("clip timing is invalid");
    }
  }
  return errors;
}

export function encodeSession(session) {
  const errors = validateSession(session);
  if (errors.length) throw new TypeError("Invalid EARTH STUDIO session: " + errors.join("; "));
  return JSON.stringify(session);
}

export function decodeSession(serialized) {
  const parsed = JSON.parse(serialized);
  const errors = validateSession(parsed);
  if (errors.length) throw new TypeError("Invalid EARTH STUDIO session: " + errors.join("; "));
  return parsed;
}

const DB_NAME = "earth-studio-local";
const DB_VERSION = 1;
const PROJECTS = "projects";
const ASSETS = "assets";

function requestResult(request) {
  return new Promise((resolve, reject) => {
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error || new Error("IndexedDB request failed"));
  });
}

export class EarthStudioStore {
  constructor(indexedDBImpl = globalThis.indexedDB) {
    if (!indexedDBImpl) throw new Error("IndexedDB is unavailable in this environment");
    this.indexedDB = indexedDBImpl;
    this.dbPromise = null;
  }
  open() {
    if (this.dbPromise) return this.dbPromise;
    this.dbPromise = new Promise((resolve, reject) => {
      const request = this.indexedDB.open(DB_NAME, DB_VERSION);
      request.onupgradeneeded = () => {
        const db = request.result;
        if (!db.objectStoreNames.contains(PROJECTS)) db.createObjectStore(PROJECTS, {keyPath:"id"});
        if (!db.objectStoreNames.contains(ASSETS)) db.createObjectStore(ASSETS, {keyPath:"key"});
      };
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error || new Error("Could not open local project database"));
      request.onblocked = () => reject(new Error("Project database upgrade is blocked by another open tab"));
    });
    return this.dbPromise;
  }
  async save(session, assets = []) {
    const manifest = JSON.parse(encodeSession(session));
    const totalBytes = assets.reduce((sum, item) => sum + (item && item.blob ? item.blob.size : 0), 0);
    if (totalBytes > MAX_PROJECT_BYTES) throw new RangeError("Project assets exceed the 512 MiB browser-adapter limit");
    const declared = new Map(manifest.assets.map(a => [a.id, a]));
    const supplied = new Set();
    for (const item of assets) {
      const descriptor = item && declared.get(item.id);
      if (!descriptor || supplied.has(item.id) || !item.blob || item.blob.size !== descriptor.sizeBytes) throw new TypeError("Asset payload does not match its manifest descriptor");
      supplied.add(item.id);
    }
    if (supplied.size !== manifest.assets.length) throw new TypeError("Every declared asset must be supplied exactly once for a complete save");
    const db = await this.open();
    await new Promise((resolve, reject) => {
      const tx = db.transaction([PROJECTS, ASSETS], "readwrite");
      const projectStore = tx.objectStore(PROJECTS);
      const assetStore = tx.objectStore(ASSETS);
      projectStore.put({...manifest, savedAt:new Date().toISOString()});
      const keepKeys = new Set(manifest.assets.map(descriptor => manifest.id + ":" + descriptor.storageKey));
      const cursor = assetStore.openCursor();
      cursor.onsuccess = () => {
        const row = cursor.result;
        if (!row) return;
        if (row.value.projectId === manifest.id && !keepKeys.has(row.value.key)) row.delete();
        row.continue();
      };
      cursor.onerror = () => { try { tx.abort(); } catch {} };
      for (const descriptor of manifest.assets) {
        const item = assets.find(candidate => candidate.id === descriptor.id);
        assetStore.put({key:manifest.id + ":" + descriptor.storageKey, projectId:manifest.id, assetId:item.id, blob:item.blob, descriptor});
      }
      tx.oncomplete = resolve;
      tx.onerror = () => reject(tx.error || new Error("Project save failed"));
      tx.onabort = () => reject(tx.error || new Error("Project save was interrupted"));
    });
    return {id:manifest.id, savedAt:new Date().toISOString()};
  }
  async load(projectId) {
    const db = await this.open();
    const project = await requestResult(db.transaction(PROJECTS, "readonly").objectStore(PROJECTS).get(projectId));
    if (!project) return null;
    const assetTx = db.transaction(ASSETS, "readonly");
    const assetRequests = project.assets.map(descriptor => ({
      descriptor,
      request:assetTx.objectStore(ASSETS).get(projectId + ":" + descriptor.storageKey)
    }));
    const storedAssets = await Promise.all(assetRequests.map(async entry => ({
      descriptor:entry.descriptor,
      stored:await requestResult(entry.request)
    })));
    const assets = storedAssets.map(({descriptor,stored}) => {
      if (!stored || stored.assetId !== descriptor.id || !stored.blob || stored.blob.size !== descriptor.sizeBytes) throw new Error("A project asset is missing or has an unexpected size: " + descriptor.id);
      return {id:descriptor.id, blob:stored.blob, descriptor};
    });
    const {savedAt,...session} = project;
    const errors = validateSession(session);
    if (errors.length) throw new TypeError("Stored project is invalid: " + errors.join("; "));
    return {session, assets};
  }
  async list() {
    const db = await this.open();
    const rows = await requestResult(db.transaction(PROJECTS, "readonly").objectStore(PROJECTS).getAll());
    return rows.map(({id,name,updatedAt,savedAt,tempo}) => ({id,name,updatedAt,savedAt,tempo}));
  }
  async remove(projectId) {
    const db = await this.open();
    const tx = db.transaction([PROJECTS, ASSETS], "readwrite");
    tx.objectStore(PROJECTS).delete(projectId);
    const store = tx.objectStore(ASSETS);
    await new Promise((resolve,reject) => {
      const cursor = store.openCursor();
      cursor.onsuccess = () => {
        const item = cursor.result;
        if (!item) return;
        if (item.value.projectId === projectId) item.delete();
        item.continue();
      };
      cursor.onerror = () => reject(cursor.error);
      tx.oncomplete = resolve;
      tx.onerror = () => reject(tx.error || new Error("Project removal failed"));
      tx.onabort = () => reject(tx.error || new Error("Project removal was interrupted"));
    });
  }
}
