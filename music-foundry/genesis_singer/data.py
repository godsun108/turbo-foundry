"""Validated JSONL dataset for licensed, aligned singing recordings."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
import torch
from torch.utils.data import Dataset
import soundfile as sf
from .audio import SAMPLE_RATE, wav_to_mel

class SingingDataset(Dataset):
    """Rows require audio, phoneme_ids, pitches, note_types, durations_frames, speaker_id, consent_id."""
    def __init__(self, manifest: Path, vocab_size: int, speakers: int):
        self.manifest=Path(manifest).resolve(); self.root=self.manifest.parent; self.rows: list[dict[str,Any]]=[]
        for line_no,line in enumerate(self.manifest.read_text(encoding="utf-8").splitlines(),1):
            if not line.strip(): continue
            row=json.loads(line); required=("audio","phoneme_ids","pitches","note_types","durations_frames","speaker_id","consent_id")
            missing=[k for k in required if k not in row]
            if missing: raise ValueError(f"line {line_no}: missing {missing}")
            arrays=[row[k] for k in ("phoneme_ids","pitches","note_types","durations_frames")]
            if not all(isinstance(a,list) and a for a in arrays) or len({len(a) for a in arrays})!=1: raise ValueError(f"line {line_no}: aligned non-empty score arrays required")
            if not str(row["consent_id"]).strip(): raise ValueError(f"line {line_no}: consent_id required")
            if any(not 1<=int(x)<vocab_size for x in row["phoneme_ids"]): raise ValueError(f"line {line_no}: invalid phoneme id")
            if any(not 0<=int(x)<=127 for x in row["pitches"]): raise ValueError(f"line {line_no}: invalid MIDI pitch")
            if any(not 0<=int(x)<=3 for x in row["note_types"]): raise ValueError(f"line {line_no}: invalid note type")
            if any(int(x)<1 for x in row["durations_frames"]): raise ValueError(f"line {line_no}: durations must be positive")
            if not 0<=int(row["speaker_id"])<speakers: raise ValueError(f"line {line_no}: speaker_id out of range")
            audio=(self.root/row["audio"]).resolve()
            if not audio.is_file(): raise ValueError(f"line {line_no}: audio not found: {audio}")
            row["_audio"]=audio; self.rows.append(row)
        if not self.rows: raise ValueError("training manifest is empty")
    def __len__(self): return len(self.rows)
    def __getitem__(self,index):
        row=self.rows[index]; wav,rate=sf.read(str(row["_audio"]),dtype="float32",always_2d=False)
        if rate!=SAMPLE_RATE or wav.ndim!=1: raise ValueError(f"{row['_audio']}: expected mono {SAMPLE_RATE} Hz WAV")
        target=wav_to_mel(torch.from_numpy(wav.copy())); durations=torch.tensor(row["durations_frames"],dtype=torch.long)
        if int(durations.sum())!=target.shape[0]: raise ValueError(f"{row['_audio']}: duration sum {int(durations.sum())} != mel frames {target.shape[0]}")
        return {"phoneme_ids":torch.tensor(row["phoneme_ids"],dtype=torch.long),"pitches":torch.tensor(row["pitches"],dtype=torch.long),"note_types":torch.tensor(row["note_types"],dtype=torch.long),"durations":durations,"speaker_id":torch.tensor(int(row["speaker_id"]),dtype=torch.long),"mel":target}
