import unittest
from datetime import datetime,timedelta,timezone
from src.autopilot.settlement import Observation,assess_settlement
NOW=datetime(2026,10,13,18,0,tzinfo=timezone.utc)
END=NOW-timedelta(minutes=10)
SID="CA"+"a"*32
def obs(minutes,ids=(SID,),complete=True):
    return Observation(NOW-timedelta(minutes=minutes),ids,complete)
class SettlementTests(unittest.TestCase):
    def assess(self,observations,**kwargs):
        return assess_settlement(END,tuple(observations),now=NOW,**kwargs)
    def test_stable(self):
        result=self.assess([obs(5),obs(2)])
        self.assertTrue(result.settled_for_review)
    def test_too_recent(self):
        result=assess_settlement(NOW-timedelta(seconds=10),(obs(5),obs(2)),now=NOW)
        self.assertEqual(result.reason,"call_too_recent")
    def test_single_observation(self):
        self.assertEqual(self.assess([obs(2)]).reason,"insufficient_observations")
    def test_too_close(self):
        self.assertEqual(self.assess([obs(3),obs(2)]).reason,"observations_too_close")
    def test_changed_children(self):
        self.assertEqual(self.assess([obs(5),obs(2,())]).reason,"changing_child_set")
    def test_incomplete_page(self):
        self.assertEqual(self.assess([obs(5,complete=False),obs(2)]).reason,"incomplete_pagination")
    def test_future_observation(self):
        self.assertEqual(self.assess([obs(5),obs(-1)]).reason,"observation_outside_window")
    def test_naive_timestamp(self):
        self.assertEqual(assess_settlement(END.replace(tzinfo=None),(obs(5),obs(2)),now=NOW).reason,
                         "invalid_timestamp")
    def test_duplicate_sid(self):
        self.assertEqual(self.assess([obs(5,(SID,SID)),obs(2)]).reason,"duplicate_child_sid")
if __name__=="__main__":
    unittest.main()
