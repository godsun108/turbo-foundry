"""Fine China — 120-bar soulful bass-house arrangement.

126 BPM, A minor, Am–F–C–G. A warm, human groove grows from intimate
spoken-word space into a bright, communal "EAT ON IT" drop.
"""
PPQ = 480
BEAT = PPQ
BAR = 4 * BEAT
BPM = 126
SECTIONS = [
    ("intro", 8), ("verse_1", 16), ("pre_chorus_1", 8),
    ("chorus_1", 16), ("verse_2", 16), ("pre_chorus_2", 8),
    ("chorus_2", 16), ("bridge", 8), ("final_chorus", 16), ("outro", 8),
]
CHORDS = {
    "Am": (45, 48, 52), "F": (41, 45, 48),
    "C": (48, 52, 55), "G": (43, 47, 50),
}
HOOK = [69, 72, 76, 74, 72, 69, 67, 69]
BASS_PATTERN = [(0, .52), (.75, .22), (1.5, .34), (2.25, .22), (3, .58), (3.75, .16)]


def build_notes():
    tracks = {name: [] for name in ("chords", "bass", "lead", "drums", "texture")}
    arrangement = []
    cursor = 0
    for section, bars in SECTIONS:
        arrangement.append({"name": section, "start_bar": cursor, "bars": bars})
        for local in range(bars):
            bar = cursor + local
            base = bar * BAR
            chord_name = ("Am", "F", "C", "G")[(bar // 2) % 4]
            root, third, fifth = CHORDS[chord_name]
            intro = section == "intro"
            verse = section.startswith("verse")
            build = section.startswith("pre_chorus")
            bridge = section == "bridge"
            drop = section.startswith("chorus")
            final = section == "final_chorus"
            outro = section == "outro"

            # Soulful organ/piano-like offbeat chord stabs, opening into sustained bridge voicings.
            chord_pitches = (root + 12, third + 12, fifth + 12)
            if bridge:
                chord_pitches = (root + 12, fifth + 12, third + 24)
                for pitch in chord_pitches:
                    tracks["chords"].append((pitch, base, int(BAR * .9), 68))
            elif intro or outro:
                for pitch in chord_pitches:
                    tracks["chords"].append((pitch, base, int(BAR * .88), 44 if intro else 38))
            else:
                for beat_pos in ((1, 3) if verse else (0, 1.5, 2.5, 3.5)):
                    for pitch in chord_pitches:
                        tracks["chords"].append((pitch, base + int(beat_pos * BEAT),
                                                 int(BEAT * (.42 if drop else .55)),
                                                 78 if drop else (58 if verse else 67)))

            # Rounded, syncopated bassline. The drops get a stronger octave answer.
            if drop:
                for i, (pos, length) in enumerate(BASS_PATTERN):
                    if local % 4 == 3 and i == 0:
                        continue
                    pitch = root - 12 + (12 if i in (2, 5) else 0)
                    if final and local >= 8 and i in (1, 4):
                        pitch += 7
                    tracks["bass"].append((pitch, base + int(pos * BEAT),
                                           max(54, int(length * BEAT)), 108 if i in (0, 4) else 90))
            elif build:
                for pos in (0, 1, 2, 3):
                    tracks["bass"].append((root - 12, base + int(pos * BEAT),
                                           int(BEAT * .22), 72 + local * 2))
            elif verse:
                for pos in (0, 1.75, 3):
                    tracks["bass"].append((root - 12, base + int(pos * BEAT),
                                           int(BEAT * .34), 76))
            elif bridge and local in (0, 2, 4, 6):
                tracks["bass"].append((root - 24, base, int(BAR * .68), 76))
            elif intro and local in (4, 6):
                tracks["bass"].append((root - 12, base + 2 * BEAT, int(BEAT * .5), 52))
            elif outro and local in (0, 4):
                tracks["bass"].append((root - 12, base, int(BEAT * 1.5), 48))

            # A rising, singable hook; fragments foreshadow the chorus and final drop.
            if intro and local in (6, 7):
                for i, pitch in enumerate(HOOK[:4]):
                    tracks["lead"].append((pitch, base + int((2 + i * .5) * BEAT),
                                           int(BEAT * .28), 52))
            elif verse and local in (7, 15):
                for i, pitch in enumerate(HOOK[:2]):
                    tracks["lead"].append((pitch, base + int((3 + i * .5) * BEAT),
                                           int(BEAT * .22), 48))
            elif build:
                for i, pitch in enumerate(HOOK[:4]):
                    tracks["lead"].append((pitch, base + int((2 + i * .5) * BEAT),
                                           int(BEAT * .22), 58 + i * 4))
            elif drop and local % 2 == 0:
                phrase = HOOK if local % 4 == 0 else HOOK[4:]
                for i, pitch in enumerate(phrase):
                    tracks["lead"].append((pitch + (12 if final and local >= 8 else 0),
                                           base + int(i * .5 * BEAT),
                                           int(BEAT * .28), 78 if final else 70))
            elif bridge and local in (2, 6):
                for i, pitch in enumerate((64, 67, 69, 72)):
                    tracks["lead"].append((pitch, base + int((1.5 + i * .5) * BEAT),
                                           int(BEAT * .34), 56))

            # Four-on-the-floor kick, clap on 2/4, shuffled-feel eighth hats.
            if not intro and not outro:
                if bridge:
                    tracks["drums"].append((36, base, int(BEAT * .22), 86))
                    tracks["drums"].append((38, base + 2 * BEAT, int(BEAT * .18), 74))
                    for pos in (1, 3):
                        tracks["drums"].append((42, base + pos * BEAT, 42, 42))
                else:
                    for beat in range(4):
                        tracks["drums"].append((36, base + beat * BEAT, int(BEAT * .2),
                                                112 if drop else (96 if build else 88)))
                    for beat in (1, 3):
                        tracks["drums"].append((38, base + beat * BEAT, int(BEAT * .18),
                                                104 if drop else 82))
                    for eighth in range(8):
                        if drop or eighth % 2:
                            tracks["drums"].append((42, base + eighth * BEAT // 2, 44,
                                                    72 if drop else 46))
                    if drop and local % 4 == 3:
                        for n, pitch in enumerate((38, 42, 46, 42)):
                            tracks["drums"].append((pitch, base + 3 * BEAT + n * BEAT // 4,
                                                    52, 62 + n * 8))
                    if build:
                        for sixteenth in range(8, 16):
                            tracks["drums"].append((38, base + sixteenth * BEAT // 4,
                                                    42, 48 + (sixteenth - 8) * 5))

            if build:
                tracks["texture"].append((96, base + 3 * BEAT, int(BEAT * .3), 72))
            if drop and local in (0, 8):
                tracks["texture"].append((76, base, int(BEAT * .65), 84))
        cursor += bars
    return tracks, arrangement
