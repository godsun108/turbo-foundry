import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/"src"))
from adapters.reso_web_api import normalize

class ResoTests(unittest.TestCase):
    def test_normalize(self):
        x=normalize({"ListingKey":"abc","ListPrice":299000,"StandardStatus":"Active",
          "PropertyType":"Residential","BedroomsTotal":3,"BathroomsTotalInteger":2,
          "LivingArea":1450,"UnparsedAddress":"1 Main St","City":"Stuart",
          "StateOrProvince":"FL","PostalCode":"34994"},"2026-09-24T00:00:00+00:00")
        self.assertEqual(x.asking_price,299000)
        self.assertEqual(x.source_kind,"reso_active_listing")
        self.assertIn("Stuart",x.address)

    def test_requires_price(self):
        with self.assertRaises(ValueError): normalize({"ListingKey":"x","ListPrice":None})

if __name__=="__main__": unittest.main()
