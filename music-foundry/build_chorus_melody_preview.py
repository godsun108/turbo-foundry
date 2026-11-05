"""Build a separate, provisional MIDI audition of chorus melody concept A.

This does not edit the canonical song arrangement or vocal score. The output is
an 8-bar MIDI clip: bars 1, 3, 5 and 7 are intentionally left open for the
gang-shouted title hook; the candidate sung responses enter on bars 2, 4, 6, 8.
"""
import argparse
import importlib.util
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("music_foundry_generator", HERE / "generate.py")
GEN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GEN)

PPQ = GEN.PPQ
BAR = PPQ * 4
BPM = 127  # provisional audition tempo; not the project's locked tempo

# Each tuple: MIDI pitch, phrase-relative onset in beats, duration in beats.
PHRASES = (
    ((69, 0, .75), (69, .75, .25), (72, 1, 1), (77, 2, 2)),
    ((71, 0, .5), (71, .5, .5), (74, 1, 1), (74, 2, .5), (79, 2.5, 1.5)),
    ((69, 0, .75), (69, .75, .25), (72, 1, 1), (77, 2, 2)),
    ((74, 0, .5), (74, .5, 1), (71, 1.5, .5), (69, 2, 1), (67, 3, 1)),
)


def build_notes():
    notes = []
    for phrase_index, phrase in enumerate(PHRASES):
        bar_start = (phrase_index * 2 + 1) * BAR
        for pitch, onset, duration in phrase:
            notes.append((pitch, bar_start + round(onset * PPQ),
                          round(duration * PPQ), 88))
    return notes


def make(output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    tempo = round(60000000 / BPM)
    meta = GEN.chunk(b"MTrk", b"\x00\xff\x51\x03" + tempo.to_bytes(3, "big") + b"\x00\xff\x2f\x00")
    header = GEN.chunk(b"MThd", struct.pack(">HHH", 1, 2, PPQ))
    melody = GEN.track(build_notes(), channel=2, program=80)
    output.write_bytes(header + meta + melody)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="music-foundry/output/chorus_melody_concept_a.mid")
    args = parser.parse_args()
    print(make(args.output))
