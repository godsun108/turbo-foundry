import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/"src"))
from scout import Candidate
from enrich import join_public_records
from shortlist import shortlist

def c(kind,ref,address,price,beds=3,size=1400):
    return Candidate(kind,ref,"2026-09-24T00:00:00Z",address,price,"Residential",beds,2,size)

class Tests(unittest.TestCase):
    def test_address_join_alias(self):
        l=c("listing","l","1 Main St, Port Saint Lucie, FL",250000)
        p=c("parcel","p","1 Main St, Port St Lucie, FL",200000)
        self.assertEqual(join_public_records([l],[p])[0]["match_status"],"exact_unique")
    def test_shortlist_orders_score(self):
        a=c("x","a","A",200000); b=c("x","b","B",280000)
        self.assertEqual(shortlist([b,a],300000)[0]["candidate"].source_reference","a")
if __name__=="__main__": unittest.main()
