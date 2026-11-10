/**
 * Score-conditioned singing from the existing local Kokoro TTS voice.
 *
 * TTS supplies the voice/timbre; pitch-synchronous overlap-add (PSOLA) retunes
 * voiced syllable regions to MIDI notes while preserving the spectral envelope.
 * No microphone, reference singer, network render, or cloud inference is used.
 */

export class SingingRenderError extends Error {}

const clamp = (value, low, high) => Math.max(low, Math.min(high, value));
const finite = (value) => typeof value === "number" && Number.isFinite(value);

export function midiToHz(midi) {
  if (!Number.isInteger(midi) || midi < 24 || midi > 108) {
    throw new SingingRenderError("MIDI pitch must be an integer from 24 to 108.");
  }
  return 440 * Math.pow(2, (midi - 69) / 12);
}

function autocorrelationPitch(frame, sampleRate) {
  let energy = 0;
  for (let i = 0; i < frame.length; i++) energy += frame[i] * frame[i];
  if (energy / frame.length < 0.000012) return null;

  const minLag = Math.max(2, Math.floor(sampleRate / 500));
  const maxLag = Math.min(Math.floor(sampleRate / 55), Math.floor(frame.length * 0.48));
  let bestLag = 0;
  let best = 0;
  for (let lag = minLag; lag <= maxLag; lag++) {
    let cross = 0, left = 0, right = 0;
    for (let i = 0; i < frame.length - lag; i += 2) {
      const a = frame[i], b = frame[i + lag];
      cross += a * b;
      left += a * a;
      right += b * b;
    }
    const score = cross / Math.sqrt(Math.max(1e-12, left * right));
    if (score > best) { best = score; bestLag = lag; }
  }
  if (best < 0.28 || !bestLag) return null;
  return { hz: sampleRate / bestLag, confidence: best };
}

export function analyzeVoicedRegion(samples, sampleRate) {
  if (!(samples instanceof Float32Array) || samples.length < 512 ||
      !finite(sampleRate) || sampleRate < 8000 || sampleRate > 96000) {
    throw new SingingRenderError("TTS audio must be a Float32Array with a valid sample rate.");
  }
  const frameSize = Math.min(2048, Math.max(1024, 2 ** Math.floor(Math.log2(samples.length))));
  const hop = Math.max(128, Math.floor(frameSize / 4));
  const frames = [];
  for (let start = 0; start + frameSize <= samples.length; start += hop) {
    const frame = samples.subarray(start, start + frameSize);
    const pitch = autocorrelationPitch(frame, sampleRate);
    let rms = 0;
    for (let i = 0; i < frame.length; i++) rms += frame[i] * frame[i];
    rms = Math.sqrt(rms / frame.length);
    if (pitch && rms > 0.003) frames.push({ start, end: start + frameSize, ...pitch });
  }
  if (frames.length < 2) {
    throw new SingingRenderError("The selected TTS voice produced too little voiced audio for a sung note. Try a longer syllable or another voice.");
  }
  const sorted = frames.map((frame) => frame.hz).sort((a, b) => a - b);
  const medianHz = sorted[Math.floor(sorted.length / 2)];
  const coherent = frames.filter((frame) => frame.confidence >= 0.28 && frame.hz >= medianHz * 0.55 && frame.hz <= medianHz * 1.8);
  if (coherent.length < 2) {
    throw new SingingRenderError("Could not reliably track the TTS voice pitch for this syllable.");
  }
  return {
    start: Math.max(0, coherent[0].start - Math.floor(frameSize / 3)),
    end: Math.min(samples.length, coherent[coherent.length - 1].end + Math.floor(frameSize / 3)),
    sourceHz: coherent.map((frame) => frame.hz).sort((a, b) => a - b)[Math.floor(coherent.length / 2)]
  };
}

function resampleSegment(source, outputLength) {
  const output = new Float32Array(Math.max(0, outputLength));
  if (!source.length || !output.length) return output;
  if (output.length === 1) { output[0] = source[0]; return output; }
  const scale = (source.length - 1) / (output.length - 1);
  for (let i = 0; i < output.length; i++) {
    const position = i * scale;
    const left = Math.floor(position);
    const right = Math.min(source.length - 1, left + 1);
    const fraction = position - left;
    output[i] = source[left] * (1 - fraction) + source[right] * fraction;
  }
  return output;
}

function pitchMarks(source, period) {
  const marks = [];
  const half = Math.max(2, Math.round(period * 0.34));
  let expected = 0;
  while (expected < source.length - period) {
    const low = Math.max(0, Math.round(expected - half));
    const high = Math.min(source.length - 1, Math.round(expected + half));
    let best = low;
    for (let i = low + 1; i <= high; i++) {
      if (source[i] > source[best]) best = i;
    }
    if (!marks.length || best - marks[marks.length - 1] > period * 0.55) marks.push(best);
    expected = best + period;
  }
  return marks;
}

/** Pitch-synchronous overlap-add; shifts pulse spacing without resampling formants. */
export function psola(samples, sampleRate, targetHz, outputSeconds, vibrato = {}) {
  if (!(samples instanceof Float32Array) || samples.length < 256 ||
      !finite(sampleRate) || !finite(targetHz) || targetHz < 55 || targetHz > 1000 ||
      !finite(outputSeconds) || outputSeconds < 0.035 || outputSeconds > 12) {
    throw new SingingRenderError("Invalid PSOLA input or target note.");
  }
  const analysis = analyzeVoicedRegion(samples, sampleRate);
  const voiced = samples.subarray(analysis.start, analysis.end);
  const sourcePeriod = sampleRate / analysis.sourceHz;
  const marks = pitchMarks(voiced, sourcePeriod);
  if (marks.length < 3) throw new SingingRenderError("Not enough stable pitch periods to synthesize this note.");

  const outputLength = Math.max(1, Math.round(outputSeconds * sampleRate));
  const output = new Float32Array(outputLength);
  const weights = new Float32Array(outputLength);
  const halfWindow = Math.max(16, Math.round(sourcePeriod * 1.5));
  const vibratoCents = clamp(finite(vibrato.cents) ? vibrato.cents : 18, 0, 60);
  const vibratoRate = clamp(finite(vibrato.rateHz) ? vibrato.rateHz : 5.2, 0, 9);
  let outputMark = 0;
  let pulse = 0;
  while (outputMark < outputLength) {
    const t = outputMark / sampleRate;
    const cents = vibratoCents * Math.sin(2 * Math.PI * vibratoRate * t);
    const frequency = targetHz * Math.pow(2, cents / 1200);
    const sourcePosition = (outputMark / Math.max(1, outputLength - 1)) * (voiced.length - 1);
    let nearest = marks[0];
    let distance = Math.abs(nearest - sourcePosition);
    for (let i = 1; i < marks.length; i++) {
      const candidateDistance = Math.abs(marks[i] - sourcePosition);
      if (candidateDistance < distance) { nearest = marks[i]; distance = candidateDistance; }
      else if (marks[i] > sourcePosition) break;
    }
    for (let offset = -halfWindow; offset <= halfWindow; offset++) {
      const sourceIndex = nearest + offset;
      const outputIndex = outputMark + offset;
      if (sourceIndex < 0 || sourceIndex >= voiced.length || outputIndex < 0 || outputIndex >= outputLength) continue;
      const phase = (offset + halfWindow) / (2 * halfWindow);
      const window = 0.5 - 0.5 * Math.cos(2 * Math.PI * phase);
      output[outputIndex] += voiced[sourceIndex] * window;
      weights[outputIndex] += window;
    }
    const period = sampleRate / frequency;
    outputMark += Math.max(1, Math.round(period));
    pulse++;
    if (pulse > outputLength) break;
  }
  for (let i = 0; i < output.length; i++) {
    output[i] = weights[i] > 0.0001 ? output[i] / weights[i] : 0;
  }
  return output;
}

export function renderSingingNote(samples, sampleRate, note, tempoBpm) {
  if (!note || !Number.isInteger(note.midi_pitch) ||
      !finite(note.duration_beats) || note.duration_beats <= 0 ||
      !finite(tempoBpm) || tempoBpm < 40 || tempoBpm > 240) {
    throw new SingingRenderError("Each sung syllable needs a MIDI pitch, positive beat duration, and valid tempo.");
  }
  const targetSeconds = note.duration_beats * 60 / tempoBpm;
  if (targetSeconds < 0.045 || targetSeconds > 12) {
    throw new SingingRenderError("Syllable duration must be between 45 ms and 12 seconds.");
  }
  const voiced = analyzeVoicedRegion(samples, sampleRate);
  const onsetSource = samples.subarray(0, voiced.start);
  const vowelSource = samples.subarray(voiced.start, voiced.end);
  const codaSource = samples.subarray(voiced.end);
  const onsetSeconds = Math.min(onsetSource.length / sampleRate, targetSeconds * 0.18);
  const codaSeconds = Math.min(codaSource.length / sampleRate, targetSeconds * 0.12);
  const vowelSeconds = Math.max(0.035, targetSeconds - onsetSeconds - codaSeconds);
  const onset = resampleSegment(onsetSource, Math.round(onsetSeconds * sampleRate));
  const vowel = psola(vowelSource, sampleRate, midiToHz(note.midi_pitch), vowelSeconds, {
    cents: note.vibrato_cents ?? 18,
    rateHz: note.vibrato_rate_hz ?? 5.2
  });
  const coda = resampleSegment(codaSource, Math.max(0, Math.round((targetSeconds - onsetSeconds - vowelSeconds) * sampleRate)));
  const output = new Float32Array(Math.round(targetSeconds * sampleRate));
  output.set(onset.subarray(0, output.length), 0);
  output.set(vowel.subarray(0, output.length - onset.length), onset.length);
  const codaStart = Math.min(output.length, onset.length + vowel.length);
  output.set(coda.subarray(0, output.length - codaStart), codaStart);
  return output;
}

export function parseSingingScore(root) {
  if (!root || typeof root !== "object" || !Array.isArray(root.phrases) ||
      !finite(root.tempo_bpm) || root.tempo_bpm < 40 || root.tempo_bpm > 240) {
    throw new SingingRenderError("Import a Music Foundry vocal score with phrases and tempo_bpm.");
  }
  const events = [];
  for (const phrase of root.phrases) {
    if (!phrase || phrase.layer === "rest" || phrase.delivery === "rest") continue;
    const syllables = Array.isArray(phrase.syllables) ? phrase.syllables : [];
    if (!syllables.length) continue;
    if (!finite(phrase.start_beat) || phrase.start_beat < 0) {
      throw new SingingRenderError("Every phrase with sung syllables needs a placed start_beat.");
    }
    for (const syllable of syllables) {
      const text = typeof syllable.text === "string" ? syllable.text.trim() : "";
      if (!text || text === "<SP>") continue;
      const onset = syllable.onset_beats;
      const duration = syllable.duration_beats;
      const pitch = syllable.midi_pitch;
      if (!finite(onset) || onset < 0 || !finite(duration) || duration <= 0 ||
          !Number.isInteger(pitch) || pitch < 24 || pitch > 108) {
        throw new SingingRenderError("Every sung syllable needs text, onset_beats, duration_beats, and midi_pitch. Unplaced scaffold scores cannot be sung.");
      }
      if (text.length > 80) throw new SingingRenderError("Each score event must be a syllable-sized lyric unit (80 characters maximum).");
      events.push({
        text, phonemes: Array.isArray(syllable.phonemes) ? syllable.phonemes : [],
        midi_pitch: pitch, onset_beats: onset, duration_beats: duration,
        start_beat: phrase.start_beat + onset,
        vibrato_cents: syllable.vibrato_cents,
        vibrato_rate_hz: syllable.vibrato_rate_hz
      });
      if (events.length > 512) throw new SingingRenderError("A score may contain at most 512 sung syllables per render.");
    }
  }
  events.sort((a, b) => a.start_beat - b.start_beat);
  if (!events.length) throw new SingingRenderError("The score contains no placed, pitched syllables.");
  return {
    title: root.project_id || root.title || "Sovereign sung take",
    tempoBpm: root.tempo_bpm,
    events
  };
}

export async function renderSingingScore({ score, sampleRate, synthesizeText, onProgress, isCancelled }) {
  const parsed = parseSingingScore(score);
  if (typeof synthesizeText !== "function") throw new SingingRenderError("A local TTS voice is required.");
  const finalBeat = Math.max(...parsed.events.map((event) => event.start_beat + event.duration_beats));
  const totalFrames = Math.ceil(finalBeat * 60 / parsed.tempoBpm * sampleRate);
  if (totalFrames > sampleRate * 180) throw new SingingRenderError("Sung score exceeds the 180-second render limit.");
  const mix = new Float32Array(totalFrames);
  for (let index = 0; index < parsed.events.length; index++) {
    if (isCancelled?.()) throw new SingingRenderError("Singing render cancelled.");
    const event = parsed.events[index];
    const source = await synthesizeText(event.text);
    if (isCancelled?.()) throw new SingingRenderError("Singing render cancelled.");
    const noteAudio = renderSingingNote(source.samples, source.sampleRateHz || sampleRate, event, parsed.tempoBpm);
    const start = Math.round(event.start_beat * 60 / parsed.tempoBpm * sampleRate);
    for (let i = 0; i < noteAudio.length && start + i < mix.length; i++) {
      mix[start + i] += noteAudio[i] * 0.78;
    }
    onProgress?.({ completed: index + 1, total: parsed.events.length, lyric: event.text });
  }
  let peak = 0;
  for (let i = 0; i < mix.length; i++) peak = Math.max(peak, Math.abs(mix[i]));
  const gain = peak > 0.89 ? 0.89 / peak : 1;
  if (gain !== 1) for (let i = 0; i < mix.length; i++) mix[i] *= gain;
  return {
    samples: mix,
    sampleRateHz: sampleRate,
    mode: "sung",
    title: parsed.title,
    syllableCount: parsed.events.length,
    tempoBpm: parsed.tempoBpm,
    durationSeconds: mix.length / sampleRate,
    peakBeforeNormalization: peak,
    normalizationGain: gain
  };
}
