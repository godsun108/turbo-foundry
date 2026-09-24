import tempfile
import unittest
from pathlib import Path
from foundry import scaffold, slugify

class FoundryTests(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(slugify("Base One Engine"),"Base-One-Engine")

    def test_scaffold(self):
        with tempfile.TemporaryDirectory() as d:
            root=scaffold("Base One Engine","Analyze property deals.",Path(d))
            self.assertTrue((root/"README.md").exists())
            self.assertTrue((root/".github/workflows/ci.yml").exists())
            self.assertTrue((root/"tests/test_smoke.py").exists())
            self.assertIn("Analyze property deals.",(root/"README.md").read_text())

    def test_business_scaffold(self):
        with tempfile.TemporaryDirectory() as d:
            root=scaffold("Base One Engine","Analyze property deals.",Path(d),"business")
            self.assertTrue((root/"operations").is_dir())
            self.assertTrue((root/"models").is_dir())
            self.assertIn("Project type: business",(root/"README.md").read_text())

    def test_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"x"; root.mkdir(); (root/"keep").write_text("x")
            with self.assertRaises(FileExistsError):
                scaffold("x","x",Path(d))

if __name__=="__main__":
    unittest.main()
