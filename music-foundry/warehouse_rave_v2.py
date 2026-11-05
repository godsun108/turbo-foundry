"""Original warehouse-rave rework: 132 BPM, four-on-the-floor, rolling bass and rave stabs.

Standard-library renderer. Produces separate drums, bass, synth and FX stems plus a
mono-compatible instrumental preview. No vocals are synthesized.
"""
import argparse
import array
import json
import math
import random
import wave
from pathlib import Path

RATE = 22050
PPQ = 480
BEAT = PPQ
BAR = 4 * BEAT
BPM = 132
SECTIONS = [
    ("intro", 8), ("build_1", 8), ("drop_1", 16),
    ("breakdown", 8), ("build_2", 8), ("final_drop", 12), ("outro", 4),
]
ROOTS = [45, 41, 48, 43]  # A, F, C, G; minor-leaning rave loop


def hz(note):
    return 440.0 * 2 ** ((note - 69) / 12)


def build_events():
    events = {name: [] for name in ("drums", "bass", "synth", "fx")}
    section_map = {}
    bar_no = 0
    for section, bars in SECTIONS:
        section_map[section] = bar_no
        for local in range(bars):
            bar = bar_no + local
            base = bar * BAR
            root = ROOTS[bar % 4]
            intro = section == "intro"
            build = section in ("build_1", "build_2")
            breakdown = section == "breakdown"
            drop = section in ("drop_1", "final_drop")
            outro = section == "outro"

            # Four-on-the-floor kick, with a controlled halftime breakdown.
            if not intro and not outro:
                for beat in ((0, 2) if breakdown else range(4)):
                    events["drums"].append(("kick", base + beat * BEAT, 0.42, 112 if drop else 98))
                if not breakdown:
                    for beat in (1, 3):
                        events["drums"].append(("clap", base + beat * BEAT, 0.20, 92 if drop else 78))
                    for eighth in range(8):
                        vel = 70 if eighth % 2 else 42
                        events["drums"].append(("hat", base + eighth * BEAT // 2, 0.055, vel))
                    if drop:
                        for sixteenth in (3, 7, 11, 15):
                            events["drums"].append(("openhat", base + sixteenth * BEAT // 4, 0.12, 78))
                if build:
                    # Snare roll accelerates through the last four bars.
                    if local >= bars - 4:
                        step = max(1, 4 - (local - (bars - 4)))
                        for n in range(16 // step):
                            events["drums"].append(("clap", base + n * step * BEAT // 4, 0.08, 48 + 10 * (local - (bars - 4))))
                if drop and local % 4 == 3:
                    for n in range(8):
                        events["drums"].append(("clap", base + 3 * BEAT + n * BEAT // 8, 0.055, 55 + n * 5))

            # Rolling, octave-layered offbeat bass. Keep the breakdown spacious.
            if drop:
                for eighth in range(8):
                    if eighth in (0, 4):
                        continue
                    pitch = root - 12 + (12 if eighth in (3, 7) and section == "final_drop" else 0)
                    events["bass"].append(("bass", base + eighth * BEAT // 2, 0.31, 105 if eighth % 2 else 90, pitch))
            elif build and local >= 4:
                for eighth in (2, 6):
                    events["bass"].append(("bass", base + eighth * BEAT // 2, 0.24, 70, root - 12))
            elif breakdown and local in (4, 6):
                events["bass"].append(("sub", base, 1.7, 66, root - 24))

            # Dark minor chord stabs and a hypnotic eighth-note rave sequence.
            if breakdown:
                for pitch in (root + 12, root + 15, root + 19):
                    events["synth"].append(("pad", base, 3.8, 54, pitch))
            elif not intro and not outro:
                chord = (root + 12, root + 15, root + 19)
                for beat in (0, 2):
                    for pitch in chord:
                        events["synth"].append(("stab", base + beat * BEAT, 0.34, 88 if drop else 64, pitch))
                if drop:
                    scale = (0, 3, 7, 10, 12, 10, 7, 3)
                    for eighth, degree in enumerate(scale):
                        events["synth"].append(("arp", base + eighth * BEAT // 2, 0.19, 82, root + 24 + degree))
            if build and local >= 4:
                for sixteenth in range(16):
                    events["fx"].append(("riser", base + sixteenth * BEAT // 4, 0.18, 30 + sixteenth * 3, 0))
            if drop and local == 0:
                events["fx"].append(("impact", base, 1.1, 118, 0))
        bar_no += bars
    return events, section_map, bar_no


def add_voice(buf, start_tick, duration_beats, velocity, kind, pitch, rng):
    start = round(start_tick * RATE * 60 / (PPQ * BPM))
    length = max(1, round(duration_beats * RATE * 60 / BPM))
    end = min(len(buf), start + length)
    if start >= end:
        return
    freq = hz(pitch) if pitch else 55.0
    for i in range(start, end):
        t = i - start
        sec = t / RATE
        progress = t / max(1, length)
        amp = velocity / 127 * 0.27
        if kind == "kick":
            phase = 2 * math.pi * (48 * sec + 42 * (1 - math.exp(-sec * 35)) / 35)
            sample = math.sin(phase) * math.exp(-sec * 8.5)
            sample += (rng.random() * 2 - 1) * math.exp(-sec * 100) * .16
        elif kind == "clap":
            env = math.exp(-sec * 30)
            sample = ((rng.random() * 2 - 1) * .7 + math.sin(2 * math.pi * 190 * sec) * .2) * env
        elif kind in ("hat", "openhat"):
            decay = 20 if kind == "hat" else 8
            sample = (rng.random() * 2 - 1) * math.exp(-sec * decay) * .42
        elif kind == "bass":
            env = min(1, sec * 180) * math.exp(-progress * 2.8)
            phase = (sec * freq) % 1
            saw = 2 * phase - 1
            sample = math.tanh(saw * 2.7) * env
            sample += math.sin(2 * math.pi * freq * sec) * .35 * env
        elif kind == "sub":
            sample = math.sin(2 * math.pi * freq * sec) * math.exp(-progress * 1.1)
        elif kind in ("stab", "arp", "pad"):
            env = min(1, sec * (35 if kind == "pad" else 180))
            env *= (1 if kind == "pad" else math.exp(-progress * 2.0))
            detune = math.sin(2 * math.pi * freq * 1.006 * sec)
            saw = 2 * ((sec * freq) % 1) - 1
            sample = (math.sin(2 * math.pi * freq * sec) * .55 + detune * .2 + saw * .25)
            if kind == "pad":
                env *= min(1, max(0, (length - t) / max(1, RATE * .3)))
            sample *= env
        elif kind == "riser":
            noise = rng.random() * 2 - 1
            sample = noise * (progress ** 1.7) * .55
        elif kind == "impact":
            sample = math.sin(2 * math.pi * (42 - 22 * progress) * sec) * math.exp(-progress * 5)
        else:
            sample = 0
        buf[i] += int(sample * amp * 32767)


def render(output, bpm=BPM, sample_rate=RATE):
    global BPM, RATE
    if not 100 <= bpm <= 150:
        raise ValueError("warehouse rave tempo must be 100–150 BPM")
    if not 8000 <= sample_rate <= 48000:
        raise ValueError("sample rate must be 8000–48000 Hz")
    BPM, RATE = bpm, sample_rate
    events, section_map, bars = build_events()
    seconds = bars * 4 * 60 / bpm
    frames = math.ceil(seconds * sample_rate)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    stems = {}
    for name, notes in events.items():
        buf = array.array("i", [0]) * frames
        rng = random.Random(900 + len(name))
        for note in notes:
            kind, tick, duration, velocity, *rest = note
            pitch = rest[0] if rest else 0
            add_voice(buf, tick, duration, velocity, kind, pitch, rng)
        stems[name] = buf
    mix = array.array("i", [0]) * frames
    for name, buf in stems.items():
        for i, value in enumerate(buf):
            mix[i] += value
        path = output / f"{name}.wav"
        with wave.open(str(path), "wb") as wav:
            wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(sample_rate)
            wav.writeframes(array.array("h", (max(-32768, min(32767, x)) for x in buf)).tobytes())
    peak = max((abs(x) for x in mix), default=1)
    gain = min(1.0, 30000 / peak)
    with wave.open(str(output / "instrumental_mix.wav"), "wb") as wav:
        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(sample_rate)
        wav.writeframes(array.array("h", (max(-32768, min(32767, round(x * gain))) for x in mix)).tobytes())
    manifest = {
        "title": "Somebody's Gotta Do It — Warehouse Rave V2",
        "render_type": "procedural_warehouse_rave_instrumental",
        "bpm": bpm, "meter": "4/4", "bars": bars,
        "duration_seconds": round(seconds, 3), "sample_rate": sample_rate,
        "channels": 1, "bit_depth": 16, "section_starts": section_map,
        "stems": [f"{name}.wav" for name in stems],
        "mix": "instrumental_mix.wav", "vocals_rendered": False,
        "note": "Original procedural warehouse-rave sound-design sketch; no vocals. Creative audition, not a mastered commercial release."
    }
    (output / "audio_manifest.json").write_text(json.dumps(manifest, indent=2))
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="music-foundry/output/warehouse-rave-v2")
    parser.add_argument("--bpm", type=int, default=BPM)
    parser.add_argument("--sample-rate", type=int, default=RATE)
    args = parser.parse_args()
    print(render(args.output, args.bpm, args.sample_rate))
