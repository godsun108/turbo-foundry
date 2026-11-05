import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "soulx_singer_adapter.py"
spec = importlib.util.spec_from_file_location("soulx_singer_adapter", SCRIPT)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


def metadata():
    return [{
        "index": "test_phrase",
        "language": "English",
        "time": [0, 1000],
        "duration": "0.5 0.5",
        "text": "Hello world",
        "phoneme": "en_HH-AH0 en_W-ER1-L-D",
        "note_pitch": "60 62",
        "note_type": "2 2",
    }]


class SoulXSingerAdapterTests(unittest.TestCase):
    def test_score_metadata_alignment_is_checked(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "target.json"
            path.write_text(json.dumps(metadata()), encoding="utf-8")
            self.assertEqual(len(adapter._load_metadata(path, "target")), 1)
            bad = metadata()
            bad[0]["note_pitch"] = "60"
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "token counts do not align"):
                adapter._load_metadata(path, "target")

    def test_invalid_timing_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "target.json"
            bad = metadata()
            bad[0]["time"] = [1000, 0]
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "time must be"):
                adapter._load_metadata(path, "target")

    def test_command_uses_score_control_and_does_not_execute(self):
        command = adapter.build_command(
            python="python", device="cuda", model=Path("model.pt"),
            config=Path("config.yaml"), prompt_wav=Path("prompt.wav"),
            prompt_metadata=Path("prompt.json"), target_metadata=Path("target.json"),
            phoneset=Path("phones.json"), save_dir=Path("out"),
        )
        self.assertIn("--control", command)
        self.assertIn("score", command)
        self.assertNotIn("--fp16", command)

    def test_fp16_requires_cuda(self):
        with self.assertRaisesRegex(ValueError, "only enabled for CUDA"):
            adapter.build_command(
                python="python", device="cpu", model=Path("model.pt"),
                config=Path("config.yaml"), prompt_wav=Path("prompt.wav"),
                prompt_metadata=Path("prompt.json"), target_metadata=Path("target.json"),
                phoneset=Path("phones.json"), save_dir=Path("out"), fp16=True,
            )


if __name__ == "__main__":
    unittest.main()
