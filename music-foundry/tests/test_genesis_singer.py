import json
import sys
import tempfile
import unittest
from pathlib import Path

import torch
import soundfile as sf

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from genesis_singer.model import GenesisSinger
from genesis_singer.audio import wav_to_mel,mel_to_wav,SAMPLE_RATE,HOP
from genesis_singer.data import SingingDataset

class GenesisSingerTests(unittest.TestCase):
    def test_score_conditioned_model_expands_durations_to_mel_frames(self):
        model=GenesisSinger(vocab_size=12,speakers=2,hidden=32,layers=1,heads=4)
        ids=torch.tensor([[1,2,3]])
        pitches=torch.tensor([[60,62,64]])
        kinds=torch.tensor([[2,2,3]])
        durations=torch.tensor([[4,5,6]])
        speakers=torch.tensor([1])
        output=model(ids,pitches,kinds,durations,speakers)
        self.assertEqual(tuple(output.shape),(1,15,80))
        self.assertTrue(torch.isfinite(output).all())

    def test_model_rejects_misaligned_score_arrays(self):
        model=GenesisSinger(vocab_size=8,hidden=32,layers=1,heads=4)
        with self.assertRaises(ValueError):
            model(torch.tensor([[1,2]]),torch.tensor([[60]]),torch.tensor([[2,2]]),torch.tensor([[4,4]]),torch.tensor([0]))

    def test_audio_features_and_baseline_decoder_round_trip_shape(self):
        wav=torch.randn(SAMPLE_RATE//4)*0.01
        mel=wav_to_mel(wav)
        self.assertEqual(mel.ndim,2)
        self.assertEqual(mel.shape[1],80)
        decoded=mel_to_wav(mel,iterations=2)
        self.assertEqual(decoded.numel(),(mel.shape[0]-1)*HOP)
        self.assertTrue(torch.isfinite(decoded).all())

    def test_dataset_checks_consent_and_frame_alignment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); audio=torch.zeros(SAMPLE_RATE//4)
            wav_path=root/'take.wav'; sf.write(wav_path,audio.numpy(),SAMPLE_RATE,subtype='PCM_16')
            frame_count=wav_to_mel(audio).shape[0]
            row={'audio':'take.wav','phoneme_ids':[1,2],'pitches':[60,62],
                 'note_types':[2,2],'durations_frames':[frame_count//2,frame_count-frame_count//2],
                 'speaker_id':0,'consent_id':'signed-consent-001'}
            manifest=root/'train.jsonl'; manifest.write_text(json.dumps(row)+'\\n',encoding='utf-8')
            dataset=SingingDataset(manifest,vocab_size=4,speakers=1)
            sample=dataset[0]
            self.assertEqual(sample['mel'].shape[0],frame_count)
            self.assertEqual(sample['phoneme_ids'].tolist(),[1,2])

if __name__=='__main__': unittest.main()
