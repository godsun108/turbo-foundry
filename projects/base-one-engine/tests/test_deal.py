import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/"src"))
from deal import DealInputs, analyze

class DealTests(unittest.TestCase):
    def test_metrics(self):
        x=DealInputs(200000,7000,6000,10000,2200,500,1300,0.05)
        r=analyze(x)
        self.assertAlmostEqual(r["effective_monthly_rent"],2090)
        self.assertAlmostEqual(r["monthly_noi"],1590)
        self.assertAlmostEqual(r["monthly_cash_flow"],290)
        self.assertAlmostEqual(r["cash_required"],23000)
        self.assertAlmostEqual(r["cap_rate"],19080/200000)
        self.assertAlmostEqual(r["cash_on_cash_return"],3480/23000)

    def test_invalid_vacancy(self):
        with self.assertRaises(ValueError):
            analyze(DealInputs(1,0,0,0,0,0,0,1.1))

if __name__=="__main__":
    unittest.main()
