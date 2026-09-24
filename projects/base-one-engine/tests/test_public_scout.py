import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/"src"))
from public_scout import select
class T(unittest.TestCase):
 def test_public_filters(self):
  rows=[{"ParcelID":"1","SiteCity":"Port St Lucie","TotalAppraisedValue":200000,"Beds":3},
        {"ParcelID":"2","SiteCity":"Fort Pierce","TotalAppraisedValue":100000,"Beds":4},
        {"ParcelID":"3","SiteCity":"Stuart","TotalAppraisedValue":400000,"Beds":3}]
  x=select(rows,max_appraised=300000,min_beds=3)
  self.assertEqual([r["parcel_id"] for r in x],["1"])
if __name__=="__main__":unittest.main()
