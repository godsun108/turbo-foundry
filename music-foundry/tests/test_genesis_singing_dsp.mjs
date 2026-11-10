import test from "node:test";
import assert from "node:assert/strict";
import {
  analyzeVoicedRegion, midiToHz, parseSingingScore, psola,
  renderSingingNote, renderSingingScore, SingingRenderError
} from "../voice/genesis-singing-dsp.mjs";

function tone(frequency = 220, seconds = 0.32, sampleRate = 24000) {
  const samples = new Float32Array(Math.round(seconds * sampleRate));
  for (let i = 0; i < samples.length; i++) {
    const t = i / sampleRate;
    const envelope = Math.min(1, i / 180) * Math.min(1, (samples.length - i) / 300);
    samples[i] = envelope * (
      0.48 * Math.sin(2 * Math.PI * frequency * t) +
      0.19 * Math.sin(2 * Math.PI * frequency * 2 * t) +
      0.08 * Math.sin(2 * Math.PI * frequency * 3 * t)
    );
  }
  return samples;
}

test("MIDI conversion uses concert A reference", () => {
  assert.equal(midiToHz(69), 440);
  assert.ok(Math.abs(midiToHz(60) - 261.625565) < 0.001);
  assert.throws(() => midiToHz(12), SingingRenderError);
});

test("voice analysis detects a stable TTS vowel region", () => {
  const analysis = analyzeVoicedRegion(tone(220), 24000);
  assert.ok(analysis.sourceHz > 210 && analysis.sourceHz < 230);
  assert.ok(analysis.end > analysis.start);
});

test("PSOLA changes pitch while preserving requested duration", () => {
  const rendered = psola(tone(220), 24000, 440, 0.5);
  assert.equal(rendered.length, 12000);
  const analysis = analyzeVoicedRegion(rendered, 24000);
  assert.ok(analysis.sourceHz > 415 && analysis.sourceHz < 465, "expected approximately A4, got " + analysis.sourceHz);
});

test("one sung note is rendered to exact beat duration", () => {
  const rendered = renderSingingNote(tone(190), 24000, {
    midi_pitch: 67, duration_beats: 1, vibrato_cents: 0, vibrato_rate_hz: 5
  }, 120);
  assert.equal(rendered.length, 12000);
  assert.ok(rendered.some((sample) => Math.abs(sample) > 0.01));
});

test("Music Foundry score parser reads placed syllables and preserves timeline", () => {
  const parsed = parseSingingScore({
    project_id: "test-song",
    tempo_bpm: 120,
    phrases: [{
      id: "hook", layer: "dry_lead", start_beat: 8,
      syllables: [
        { text: "Sing", phonemes: ["S", "IH1", "NG"], midi_pitch: 67, onset_beats: 0, duration_beats: 0.5 },
        { text: "it", phonemes: ["IH1", "T"], midi_pitch: 69, onset_beats: 0.5, duration_beats: 0.5 }
      ]
    }]
  });
  assert.equal(parsed.events.length, 2);
  assert.equal(parsed.events[0].start_beat, 8);
  assert.equal(parsed.events[1].start_beat, 8.5);
});

test("unplaced scaffold score is rejected instead of inventing melody", () => {
  assert.throws(() => parseSingingScore({
    project_id: "unfinished",
    tempo_bpm: 127,
    phrases: [{
      layer: "dry_lead", start_beat: null,
      syllables: [{ text: "hello", midi_pitch: 60, onset_beats: 0, duration_beats: 1 }]
    }]
  }), /placed start_beat/);
});

test("complete score renderer synthesizes syllables locally and mixes on timeline", async () => {
  const score = {
    project_id: "two-note-test",
    tempo_bpm: 120,
    phrases: [{
      layer: "dry_lead", start_beat: 0,
      syllables: [
        { text: "one", midi_pitch: 60, onset_beats: 0, duration_beats: 0.5 },
        { text: "two", midi_pitch: 64, onset_beats: 0.5, duration_beats: 0.5 }
      ]
    }]
  };
  let calls = 0;
  const result = await renderSingingScore({
    score,
    sampleRate: 24000,
    synthesizeText: async () => { calls++; return { samples: tone(200), sampleRateHz: 24000 }; }
  });
  assert.equal(calls, 2);
  assert.equal(result.syllableCount, 2);
  assert.equal(result.samples.length, 24000);
  assert.equal(result.mode, "sung");
  assert.ok(result.samples.some((sample) => Math.abs(sample) > 0.01));
});
