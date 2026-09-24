import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/"src"))
from scout_runner import run

class RunnerTests(unittest.TestCase):
    def test_persists_and_detects_price_change(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d); src=d/"src.json"; cfg=d/"cfg.json"; state=d/"state.json"; out=d/"out"
            cfg.write_text(json.dumps({"locations":["Port St. Lucie"]}))
            base={"source_kind":"test","source_reference":"x","retrieved_at":"2026-09-24T00:00:00+00:00",
                  "address":"1 Main, Port St. Lucie, FL","asking_price":250000,
                  "property_type":"single_family","bedrooms":3,"bathrooms":2,"square_feet":1400}
            src.write_text(json.dumps([base]))
            a=run(src,cfg,state,out); self.assertEqual(len(a["changes"]["added"]),1)
            base["asking_price"]=240000; src.write_text(json.dumps([base]))
            b=run(src,cfg,state,out); self.assertEqual(len(b["changes"]["changed"]),1)
            self.assertTrue(state.exists()); self.assertTrue((out/"scout-latest.json").exists())

if __name__=="__main__": unittest.main()
