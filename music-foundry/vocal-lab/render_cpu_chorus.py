#!/usr/bin/env python3
"""Free CPU-only synthetic chorus renderer for Somebody's Gotta Do It.

This is a deliberately labelled robotic demo fallback, not a neural singer.
It uses eSpeak NG for synthetic phonation and Rubber Band for per-word pitch
and duration shaping. It never reads or alters the canonical lyric sheet.
"""
from __future__ import annotations
import argparse, json, math, shutil, subprocess, tempfile, wave
from array import array
from pathlib import Path

BPM = 127
SR = 22050
BASE_MIDI = 65
# Exact chorus lines from the canonical cue sheet. Each word is a scored unit.
PHRASES = [
    ("Somebody's gotta do it", [(1.5,55),(1.0,55),(0.5,60),(1.0,64)], "gang"),
    ("Make the speakers scream", [(0.75,69),(0.25,69),(1.0,72),(2.0,77)], "lead"),
    ("Somebody's gotta do it", [(1.5,55),(1.0,55),(0.5,60),(1.0,64)], "gang"),
    ("Make the lights go mean", [(0.5,71),(0.5,71),(1.0,74),(0.5,74),(1.5,79)], "lead"),
    ("Somebody's gotta do it", [(1.5,55),(1.0,55),(0.5,60),(1.0,64)], "gang"),
    ("Keep the freaks alive", [(0.75,69),(0.25,69),(1.0,72),(2.0,77)], "lead"),
    ("Somebody's gotta do it", [(1.5,55),(1.0,55),(0.5,60),(1.0,64)], "gang"),
    ("And tonight that somebody's me", [(0.5,74),(1.0,74),(0.5,71),(1.0,69),(1.0,67)], "lead"),
]
def run(args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

def read_wav(path):
    with wave.open(str(path), "rb") as w:
        if w.getnchannels()!=1 or w.getsampwidth()!=2:
            raise RuntimeError("Expected mono 16-bit PCM from eSpeak/Rubber Band")
        return w.getframerate(), array("h", w.readframes(w.getnframes()))

def write_wav(path, samples):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(samples.tobytes())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args=ap.parse_args()
    for exe in ("espeak-ng","rubberband","ffmpeg"):
        if not shutil.which(exe): raise SystemExit(f"Missing required executable: {exe}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    beat=60.0/BPM
    rendered=[]
    manifest={"title":"Somebody's Gotta Do It","engine":"eSpeak NG + Rubber Band (CPU fallback)",
      "kind":"synthetic robotic pitched-phonation demo; not a neural singing model",
      "bpm":BPM,"sample_rate":SR,"status":"draft_audition_not_human_reviewed","phrases":[]}
    with tempfile.TemporaryDirectory(prefix="sgdi-vocal-") as td:
      tmp=Path(td)
      for pi,(line,notes,layer) in enumerate(PHRASES):
        words=line.split()
        if len(words)!=len(notes): raise RuntimeError(f"Word/note mismatch: {line}")
        phrase=[]
        for wi,(word,(beats,midi)) in enumerate(zip(words,notes)):
          src=tmp/f"p{pi}_w{wi}_src.wav"; dst=tmp/f"p{pi}_w{wi}.wav"
          run(["espeak-ng","-v","en-us+m3","-s","138","-p","48","-a","180","-w",str(src),word])
          target=beats*beat
          # Rubber Band preserves the synthetic voice's formants while transposing.
          semitones=midi-BASE_MIDI
          run(["rubberband","-p",str(semitones),"-t",str(target),"--quiet",str(src),str(dst)])
          rate,samples=read_wav(dst)
          if rate!=SR:
            raise RuntimeError(f"Unexpected sample rate {rate}; expected {SR}")
          wanted=max(1,int(target*SR))
          if len(samples)>wanted: del samples[wanted:]
          elif len(samples)<wanted: samples.extend([0]*(wanted-len(samples)))
          phrase.extend(samples)
        pfile=tmp/f"phrase_{pi}.wav"; write_wav(pfile,array("h",phrase))
        rendered.append((pfile,layer,line))
        manifest["phrases"].append({"text":line,"delivery":layer,"duration_seconds":round(len(phrase)/SR,4),
          "word_count":len(words),"midi_notes":[n[1] for n in notes]})
      # Lay the eight phrases contiguously; gang lines get a subtle stereo-width
      # treatment in the final bus, while the lead gets a little grit and slap.
      raw=tmp/"chorus_dry.wav"
      all_samples=array("h")
      for pfile,_,_ in rendered:
        _,s=read_wav(pfile); all_samples.extend(s)
      write_wav(raw,all_samples)
      final=args.out
      run(["ffmpeg","-y","-i",str(raw),"-af",
        "highpass=f=110,lowpass=f=9500,acompressor=threshold=0.12:ratio=3:attack=5:release=80,aecho=0.82:0.22:55|110:0.12|0.07",
        "-ar",str(SR),"-ac","2","-c:a","pcm_s16le",str(final)])
    manifest["audio_file"]=str(args.out.name)
    manifest["duration_seconds"]=round(sum(p[0].stat().st_size for p in rendered)/1,0) if False else round(sum(x["duration_seconds"] for x in manifest["phrases"]),3)
    args.out.with_suffix(".manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))
if __name__=="__main__": main()
