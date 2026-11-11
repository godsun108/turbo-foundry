import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
try:
    import torch
    import soundfile as sf
    from genesis_singer.model import GenesisSinger
    from genesis_singer.audio import wav_to_mel,mel_to_wav,SAMPLE_RATE,HOP
    from genesis_singer.data import SingingDataset
except ImportError:
    torch=None

@unittest.skipIf(torch is None,"install music-foundry/genesis_singer/requirements.txt to run neural singer tests")
class GenesisSingerTests(unittest.TestCase):
    def test_score_conditioned_model_expands_durations_to_mel_frames(self):
        model=GenesisSinger(vocab_size=12,speakers=2,hidden=32,layers=1,heads=4)
        output=model(torch.tensor([[1,2,3]]),torch.tensor([[60,62,64]]),torch.tensor([[2,2,3]]),torch.tensor([[4,5,6]]),torch.tensor([1]))
        self.assertEqual(tuple(output.shape),(1,15,80)); self.assertTrue(torch.isfinite(output).all())
    def test_model_rejects_misaligned_score_arrays(self):
        model=GenesisSinger(vocab_size=8,hidden=32,layers=1,heads=4)
        with self.assertRaises(ValueError): model(torch.tensor([[1,2]]),torch.tensor([[60]]),torch.tensor([[2,2]]),torch.tensor([[4,4]]),torch.tensor([0]))
    def test_audio_features_and_baseline_decoder_round_trip_shape(self):
        mel=wav_to_mel(torch.randn(SAMPLE_RATE//4)*0.01)
        self.assertEqual(mel.ndim,2); self.assertEqual(mel.shape[1],80)
        decoded=mel_to_wav(mel,iterations=2)
        self.assertEqual(decoded.numel(),(mel.shape[0]-1)*HOP); self.assertTrue(torch.isfinite(decoded).all())
    def test_dataset_checks_consent_and_frame_alignment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); wav=torch.zeros(SAMPLE_RATE//4); sf.write(str(root/'take.wav'),wav.numpy(),SAMPLE_RATE,subtype='PCM_16')
            frames=wav_to_mel(wav).shape[0]
            row={'audio':'take.wav','phoneme_ids':[1,2],'pitches':[60,62],'note_types':[2,2],
                 'durations_frames':[frames//2,frames-frames//2],'speaker_id':0,'consent_id':'signed-consent-001'}
            manifest=root/'train.jsonl'; manifest.write_text(json.dumps(row)+chr(10),encoding='utf-8')
            sample=SingingDataset(manifest,vocab_size=4,speakers=1)[0]
            self.assertEqual(sample['mel'].shape[0],frames); self.assertEqual(sample['phoneme_ids'].tolist(),[1,2])

if __name__=='__main__': unittest.main()
