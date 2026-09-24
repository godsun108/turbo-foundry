import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/"src"))
from intake import PropertyRecord, Source, make_deal_record

class IntakeTests(unittest.TestCase):
    def test_record_is_deterministic(self):
        p=PropertyRecord("123 Example St",250000,"single_family",3,2,1500,3000,2400,2200,15000)
        s=[Source("listing","example://listing","2026-09-24T12:00:00+00:00")]
        a=make_deal_record(p,s,{"vacancy_rate":.05})
        b=make_deal_record(p,s,{"vacancy_rate":.05})
        self.assertEqual(a["record_sha256"],b["record_sha256"])

    def test_provenance_required(self):
        p=PropertyRecord("123 Example St",250000,"single_family")
        with self.assertRaises(ValueError): make_deal_record(p,[])

    def test_bad_price_rejected(self):
        p=PropertyRecord("123 Example St",0,"single_family")
        with self.assertRaises(ValueError):
            make_deal_record(p,[Source("manual","user","2026-09-24T12:00:00+00:00")])

if __name__=="__main__":
    unittest.main()
