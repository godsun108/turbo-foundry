import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/"src"))
from intake import PropertyRecord, Source
from scenario import FinancingScenario
from report import build_deal_report, render_markdown

S=[Source("listing","example://1","2026-09-24T12:00:00+00:00")]
F=[FinancingScenario("example",10000,5000,15000,1400)]

class ReportTests(unittest.TestCase):
    def test_missing_data_blocks_analysis(self):
        p=PropertyRecord("123 Example St",250000,"single_family")
        r=build_deal_report(p,S,F)
        self.assertEqual(r["analysis_status"],"incomplete")
        self.assertEqual(r["scenario_results"],[])
        self.assertIn("monthly_rent_estimate",r["missing_fields"])

    def test_complete_report(self):
        p=PropertyRecord("123 Example St",250000,"single_family",3,2,1500,3000,2400,2200,15000)
        r=build_deal_report(p,S,F)
        self.assertEqual(r["analysis_status"],"complete")
        self.assertEqual(len(r["scenario_results"]),1)
        self.assertEqual(len(r["stress_results"]["example"]),27)
        md=render_markdown(r)
        self.assertIn("Scenario comparison",md)
        self.assertIn("Provenance",md)

if __name__=="__main__":
    unittest.main()
