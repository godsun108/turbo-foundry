import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/"src"))
from scenario import FinancingScenario, compare_scenarios, stress_test

P={"purchase_price":200000,"monthly_rent":2200,
   "monthly_operating_expenses":500,"vacancy_rate":0.05}

class ScenarioTests(unittest.TestCase):
    def test_compare_preserves_identity(self):
        a=FinancingScenario("cash",200000,5000,10000,0)
        b=FinancingScenario("financed",7000,6000,10000,1300)
        out=compare_scenarios(P,[a,b])
        self.assertEqual([x["financing"]["name"] for x in out],["cash","financed"])
        self.assertGreater(out[0]["monthly_cash_flow"],out[1]["monthly_cash_flow"])

    def test_stress_grid(self):
        s=FinancingScenario("example",7000,6000,10000,1300)
        out=stress_test(P,s,rent_multipliers=(0.9,1.0),vacancy_rates=(.05,.15),
                        expense_multipliers=(1.0,1.3))
        self.assertEqual(len(out),8)
        worst=min(out,key=lambda x:x["monthly_cash_flow"])
        best=max(out,key=lambda x:x["monthly_cash_flow"])
        self.assertLess(worst["monthly_cash_flow"],best["monthly_cash_flow"])

    def test_no_scenarios_rejected(self):
        with self.assertRaises(ValueError):
            compare_scenarios(P,[])

if __name__=="__main__":
    unittest.main()
