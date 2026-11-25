/**
 * Non-destructive audio clip editing primitives for EARTH STUDIO.
 * A clip is an instance of a shared source asset; edits never rewrite audio.
 */
const finite = (value, name) => {
  if (typeof value !== "number" || !Number.isFinite(value)) throw new TypeError(name + " must be finite");
  return value;
};
const positive = (value, name) => {
  finite(value, name);
  if (value <= 0) throw new RangeError(name + " must be greater than zero");
  return value;
};
export function validateAudioClip(clip) {
  const errors = [];
  if (!clip || typeof clip !== "object" || Array.isArray(clip)) return ["clip must be an object"];
  if (typeof clip.id !== "string" || !clip.id.trim()) errors.push("clip id must be a non-empty string");
  if (typeof clip.assetId !== "string" || !clip.assetId.trim()) errors.push("clip assetId must be a non-empty string");
  for (const [key,min] of [["startSeconds",0],["sourceStartSeconds",0]]) {
    if (typeof clip[key] !== "number" || !Number.isFinite(clip[key]) || clip[key] < min) errors.push(key + " must be a non-negative finite number");
  }
  if (typeof clip.durationSeconds !== "number" || !Number.isFinite(clip.durationSeconds) || clip.durationSeconds <= 0) errors.push("durationSeconds must be positive and finite");
  if (clip.loop !== undefined && typeof clip.loop !== "boolean") errors.push("loop must be boolean when present");
  return errors;
}
function assertClip(clip) {
  const errors = validateAudioClip(clip);
  if (errors.length) throw new TypeError("Invalid audio clip: " + errors.join("; "));
}
function makeId(idFactory) {
  if (typeof idFactory !== "function") throw new TypeError("idFactory must be a function");
  const id = idFactory();
  if (typeof id !== "string" || !id.trim()) throw new TypeError("idFactory must return a non-empty string");
  return id;
}
export function splitAudioClip(clip, splitAtSeconds, idFactory) {
  assertClip(clip);
  finite(splitAtSeconds, "splitAtSeconds");
  const relative = splitAtSeconds - clip.startSeconds;
  if (relative <= 0 || relative >= clip.durationSeconds) throw new RangeError("split point must be inside the clip");
  const left = {...clip, durationSeconds:relative};
  const right = {
    ...clip,
    id:makeId(idFactory),
    startSeconds:splitAtSeconds,
    sourceStartSeconds:clip.sourceStartSeconds + relative,
    durationSeconds:clip.durationSeconds - relative
  };
  return [left,right];
}
export function trimAudioClip(clip, {leftSeconds = 0, rightSeconds = 0} = {}) {
  assertClip(clip);
  finite(leftSeconds, "leftSeconds"); finite(rightSeconds, "rightSeconds");
  if (leftSeconds < 0 || rightSeconds < 0 || leftSeconds + rightSeconds >= clip.durationSeconds) {
    throw new RangeError("trim must leave a positive clip duration");
  }
  return {
    ...clip,
    startSeconds:clip.startSeconds + leftSeconds,
    sourceStartSeconds:clip.sourceStartSeconds + leftSeconds,
    durationSeconds:clip.durationSeconds - leftSeconds - rightSeconds
  };
}
export function moveAudioClip(clip, startSeconds) {
  assertClip(clip);
  finite(startSeconds, "startSeconds");
  if (startSeconds < 0) throw new RangeError("clip cannot be moved before the timeline start");
  return {...clip,startSeconds};
}
export function duplicateAudioClip(clip, {idFactory, offsetSeconds = 0} = {}) {
  assertClip(clip);
  finite(offsetSeconds, "offsetSeconds");
  const startSeconds = clip.startSeconds + offsetSeconds;
  if (startSeconds < 0) throw new RangeError("duplicate cannot start before the timeline start");
  return {...clip,id:makeId(idFactory),startSeconds};
}
export function setAudioClipLoop(clip, loop) {
  assertClip(clip);
  if (typeof loop !== "boolean") throw new TypeError("loop must be boolean");
  return {...clip,loop};
}
export function validateAudioClipList(clips) {
  if (!Array.isArray(clips)) return ["clips must be an array"];
  const errors = [], ids = new Set();
  for (const clip of clips) {
    errors.push(...validateAudioClip(clip));
    if (clip && typeof clip.id === "string") {
      if (ids.has(clip.id)) errors.push("audio clip IDs must be unique per track");
      ids.add(clip.id);
    }
  }
  return errors;
}

/** Snap seconds to a musical grid. divisionsPerBeat: 1=quarter, 2=eighth, 4=sixteenth, 8=thirty-second. */
export function snapAudioTime(seconds, {tempo = 120, divisionsPerBeat = 4, enabled = true} = {}) {
  finite(seconds, "seconds"); positive(tempo, "tempo");
  if (!Number.isInteger(divisionsPerBeat) || divisionsPerBeat < 1 || divisionsPerBeat > 64) {
    throw new RangeError("divisionsPerBeat must be an integer from 1 to 64");
  }
  if (!enabled) return Math.max(0, seconds);
  const gridSeconds = 60 / tempo / divisionsPerBeat;
  return Math.max(0, Math.round(seconds / gridSeconds) * gridSeconds);
}
