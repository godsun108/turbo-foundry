import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/"src"))
from adapters.rentcast import normalize

class RentCastTests(unittest.TestCase):
    def test_active_listing(self):
        c=normalize({"id":"p1","formattedAddress":"1 Main St, Stuart, FL 34994",
          "price":275000,"status":"Active","propertyType":"Single Family",
          "bedrooms":3,"bathrooms":2,"squareFootage":1450},"2026-09-24T00:00:00Z")
        self.assertEqual(c.asking_price,275000)
        self.assertEqual(c.source_kind,"rentcast_active_listing")
    def test_inactive_rejected(self):
        with self.assertRaises(ValueError):
            normalize({"id":"x","price":1,"status":"Inactive"})
if __name__=="__main__": unittest.main()
