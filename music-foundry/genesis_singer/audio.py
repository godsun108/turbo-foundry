"""Mel features and baseline Griffin-Lim decoder."""
from __future__ import annotations
import math
import torch
SAMPLE_RATE, N_FFT, HOP, MEL_BINS = 24000, 1024, 256, 80

def mel_filter(sample_rate=SAMPLE_RATE, n_fft=N_FFT, n_mels=MEL_BINS, device=None):
    def hz_to_mel(hz): return 2595.0 * math.log10(1.0 + hz / 700.0)
    def mel_to_hz(mel): return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)
    points = torch.linspace(hz_to_mel(0), hz_to_mel(sample_rate/2), n_mels+2, device=device)
    hz = torch.tensor([mel_to_hz(float(x)) for x in points], device=device)
    bins = torch.floor((n_fft+1)*hz/sample_rate).long()
    bank = torch.zeros(n_mels, n_fft//2+1, device=device)
    for m in range(1, n_mels+1):
        left, center, right = bins[m-1:m+2].tolist(); center=max(center,left+1); right=max(right,center+1)
        for k in range(max(0,left), min(center,bank.shape[1])): bank[m-1,k]=(k-left)/max(1,center-left)
        for k in range(max(0,center), min(right,bank.shape[1])): bank[m-1,k]=(right-k)/max(1,right-center)
    return bank

def wav_to_mel(wav):
    if wav.ndim != 1: raise ValueError("audio must be mono")
    window=torch.hann_window(N_FFT,device=wav.device)
    spec=torch.stft(wav,n_fft=N_FFT,hop_length=HOP,window=window,center=True,return_complex=True).abs()
    return torch.log(torch.clamp(mel_filter(device=wav.device) @ spec,min=1e-5)).transpose(0,1)

def mel_to_wav(log_mel, iterations=48):
    """Approximate inverse-mel Griffin-Lim; not a production neural vocoder."""
    if log_mel.ndim != 2 or log_mel.shape[1] != MEL_BINS: raise ValueError("expected [frames,80] log-mel")
    mel=torch.exp(log_mel).transpose(0,1); bank=mel_filter(device=log_mel.device)
    magnitude=torch.clamp(torch.linalg.pinv(bank) @ mel,min=1e-7).sqrt()
    phase=torch.rand(magnitude.shape,device=log_mel.device)* (2*math.pi)
    window=torch.hann_window(N_FFT,device=log_mel.device); spec=torch.polar(magnitude,phase)
    length=(log_mel.shape[0]-1)*HOP
    for _ in range(max(1,iterations)):
        wav=torch.istft(spec,n_fft=N_FFT,hop_length=HOP,window=window,center=True,length=length)
        rebuilt=torch.stft(wav,n_fft=N_FFT,hop_length=HOP,window=window,center=True,return_complex=True)
        spec=magnitude*torch.exp(1j*torch.angle(rebuilt))
    return torch.istft(spec,n_fft=N_FFT,hop_length=HOP,window=window,center=True,length=length).clamp(-1,1)
