import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/"src"))
from scout import Candidate
from scout_rank import score

class RankTests(unittest.TestCase):
    def c(self,price,beds=3,size=1400):
        return Candidate("test","x","2026-09-24T00:00:00Z","1 Main",price,"Residential",beds,2,size)
    def test_lower_price_scores_higher_all_else_equal(self):
        self.assertGreater(score(self.c(200000),300000)["priority_score"],
                           score(self.c(275000),300000)["priority_score"])
    def test_missing_data_not_rewarded(self):
        self.assertGreater(score(self.c(200000),300000)["priority_score"],
                           score(self.c(200000,None,None),300000)["priority_score"])
if __name__=="__main__": unittest.main()
