import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/"src"))
from adapters.st_lucie_parcels import normalize

class AdapterTests(unittest.TestCase):
    def test_normalize_public_record(self):
        r={"ParcelID":"123","SiteAddress":"1 Main St","SiteCity":"Port St Lucie",
           "SiteZIP":"34953","TotalAppraisedValue":210000,
           "LandUseCodeDescription":"Single Family","Beds":"3","Baths":2}
        c=normalize(r,"2026-09-24T00:00:00+00:00")
        self.assertEqual(c.asking_price,210000)
        self.assertIn("Port St Lucie",c.address)
        self.assertIn("reference",c.source_kind)

    def test_no_value_rejected(self):
        with self.assertRaises(ValueError): normalize({"ParcelID":"x","TotalAppraisedValue":0})

if __name__=="__main__": unittest.main()
