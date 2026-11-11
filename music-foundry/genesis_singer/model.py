"""Compact score-conditioned singing acoustic model; experimental, not pretrained."""
from __future__ import annotations
import torch
from torch import nn

class GenesisSinger(nn.Module):
    def __init__(self, vocab_size: int, speakers: int = 1, mel_bins: int = 80, hidden: int = 256, layers: int = 4, heads: int = 4, max_pitch: int = 128, dropout: float = 0.1):
        super().__init__()
        if vocab_size < 2 or speakers < 1 or hidden % heads: raise ValueError("invalid model dimensions")
        self.vocab_size, self.speakers, self.mel_bins = vocab_size, speakers, mel_bins
        self.phoneme = nn.Embedding(vocab_size, hidden, padding_idx=0)
        self.pitch = nn.Embedding(max_pitch, hidden, padding_idx=0)
        self.note_type = nn.Embedding(4, hidden, padding_idx=0)
        self.speaker = nn.Embedding(speakers, hidden)
        self.position = nn.Embedding(8192, hidden)
        layer = nn.TransformerEncoderLayer(d_model=hidden, nhead=heads, dim_feedforward=hidden*4, dropout=dropout, batch_first=True, norm_first=True, activation="gelu")
        self.encoder = nn.TransformerEncoder(layer, num_layers=layers, enable_nested_tensor=False)
        self.refine = nn.Sequential(nn.Conv1d(hidden, hidden, 5, padding=2), nn.GELU(), nn.Conv1d(hidden, hidden, 5, padding=2), nn.GELU())
        self.output = nn.Linear(hidden, mel_bins)

    def forward(self, phoneme_ids, pitches, note_types, durations, speaker_ids):
        if not (phoneme_ids.shape == pitches.shape == note_types.shape == durations.shape): raise ValueError("score tensors must share [B,N] shape")
        if torch.any(durations < 0): raise ValueError("durations cannot be negative")
        bsz, count = phoneme_ids.shape
        speaker_vec = self.speaker(speaker_ids.reshape(bsz, 1, 1)).expand(-1, count, -1)
        encoded = self.phoneme(phoneme_ids) + self.pitch(pitches) + self.note_type(note_types) + speaker_vec
        expanded = torch.repeat_interleave(encoded, durations.long(), dim=1)
        if expanded.shape[1] == 0: raise ValueError("score expands to zero frames")
        if expanded.shape[1] > self.position.num_embeddings: raise ValueError("score exceeds 8192-frame context; split into phrases")
        pos = torch.arange(expanded.shape[1], device=expanded.device).unsqueeze(0)
        hidden = self.encoder(expanded + self.position(pos))
        hidden = self.refine(hidden.transpose(1, 2)).transpose(1, 2)
        return self.output(hidden)
