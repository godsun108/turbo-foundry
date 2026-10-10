"""Deterministic original MIDI sketch generator. Python 3, no dependencies."""
import argparse
import json
import struct
from pathlib import Path

PPQ = 480

def varlen(n):
    if n < 0:
        raise ValueError("negative delta")
    parts = [n & 127]
    n >>= 7
    while n:
        parts.insert(0, 128 | (n & 127))
        n >>= 7
    return bytes(parts)

def chunk(name, data):
    return name + struct.pack(">I", len(data)) + data

def track(notes, channel=0, program=0):
    events = [(0, bytes([0xC0 | channel, program]))]
    for pitch, start, duration, velocity in notes:
        if not (0 <= pitch <= 127 and 1 <= velocity <= 127 and duration > 0):
            raise ValueError("invalid note")
        events.append((start, bytes([0x90 | channel, pitch, velocity])))
        events.append((start + duration, bytes([0x80 | channel, pitch, 0])))
    events.sort(key=lambda e: (e[0], e[1][0] & 0xF0 == 0x90))
    out, previous = bytearray(), 0
    for at, data in events:
        out.extend(varlen(at - previous))
        out.extend(data)
        previous = at
    out.extend(b"\x00\xff\x2f\x00")
    return chunk(b"MTrk", bytes(out))

def make(output, bpm=122, bars=8):
    if not 40 <= bpm <= 240 or not 1 <= bars <= 128:
        raise ValueError("bpm or bars out of range")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    beat = PPQ
    # Original procedural A-minor groove, four independently editable tracks.
    chords, bass, lead, drums = [], [], [], []
    progression = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]
    melody = [69, 72, 76, 72, 67, 69, 64, 67]
    for bar in range(bars):
        base = bar * 4 * beat
        chord = progression[bar % 4]
        for pitch in chord:
            chords.append((pitch, base, 4 * beat - 12, 72))
        for b in range(4):
            bass.append((chord[0] - 12, base + b * beat, int(beat * .72), 90))
            drums.append((36, base + b * beat, int(beat * .2), 100))
            drums.append((42, base + b * beat + beat // 2, int(beat * .15), 60))
        for b in (1, 3):
            drums.append((38, base + b * beat, int(beat * .2), 88))
        for step in range(8):
            lead.append((melody[(bar * 8 + step) % len(melody)], base + step * (beat // 2), int(beat * .38), 76))
    parts = {"chords": (chords, 0, 88), "bass": (bass, 1, 38), "lead": (lead, 2, 80), "drums": (drums, 9, 0)}
    tempo = round(60000000 / bpm)
    meta = chunk(b"MTrk", b"\x00\xff\x51\x03" + tempo.to_bytes(3, "big") + b"\x00\xff\x2f\x00")
    header = chunk(b"MThd", struct.pack(">HHH", 1, 2, PPQ))
    for name, (notes, channel, program) in parts.items():
        (output / f"{name}.mid").write_bytes(header + meta + track(notes, channel, program))
    (output / "manifest.json").write_text(json.dumps({"bpm": bpm, "bars": bars, "key": "A minor", "tracks": list(parts), "note": "Procedural MIDI sketch; no sampled audio included."}, indent=2))
    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="music-foundry/output")
    parser.add_argument("--bpm", type=int, default=122)
    parser.add_argument("--bars", type=int, default=8)
    args = parser.parse_args()
    print(make(args.output, args.bpm, args.bars))
