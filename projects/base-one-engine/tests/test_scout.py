import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/"src"))
from scout import Candidate, ScoutCriteria, discover, detect_changes

def c(ref,price,address="1 Main St, Port St. Lucie, FL"):
    return Candidate("test",ref,"2026-09-24T12:00:00+00:00",address,price,"single_family",3,2,1400)

class ScoutTests(unittest.TestCase):
    def test_filters(self):
        q=ScoutCriteria(("Port St. Lucie",),250000,("single_family",),3,1200)
        self.assertEqual([x.source_reference for x in discover([c("a",240000),c("b",260000)],q)],["a"])

    def test_change_detection(self):
        r=detect_changes([c("a",250000)],[c("a",240000),c("b",200000)])
        self.assertEqual(len(r["changed"]),1)
        self.assertEqual(len(r["added"]),1)
        self.assertEqual(len(r["removed"]),0)

if __name__=="__main__":
    unittest.main()
