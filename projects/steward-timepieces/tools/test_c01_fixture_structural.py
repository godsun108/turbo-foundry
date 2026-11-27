import unittest
from c01_fixture_structural import (
    FixtureEngineeringError, beam_screen, compliance_correction,
    uncertainty_budget, guardband_result, datum_transfer_repeatability,
    validate_qualification_packet,
)

class TestFixtureStructural(unittest.TestCase):
    def test_cantilever_beam_screen(self):
        r=beam_screen(10,100,200000,1000,5,"cantilever_end","SYN","SYN-R1")
        self.assertAlmostEqual(r["deflection_mm"],10000/(3*200000*1000))
        self.assertAlmostEqual(r["nominal_bending_stress_mpa"],5.0)
    def test_simply_supported_beam_screen(self):
        r=beam_screen(10,100,200000,1000,5,"simply_supported_center","SYN","SYN-R1")
        self.assertAlmostEqual(r["deflection_mm"],10000000/(48*200000*1000))
        self.assertAlmostEqual(r["nominal_bending_stress_mpa"],0.125)
    def test_rejects_unsupported_boundary_condition(self):
        with self.assertRaises(FixtureEngineeringError):
            beam_screen(10,100,200000,1000,5,"fixed_fixed","SYN","SYN-R1")
    def test_compliance_correction(self):
        r=compliance_correction(.20,10,.005,"SYN","SYN-R1")
        self.assertAlmostEqual(r["estimated_fixture_deflection_mm"],.05)
        self.assertAlmostEqual(r["corrected_mechanism_travel_mm"],.15)
    def test_rejects_overcorrection(self):
        with self.assertRaises(FixtureEngineeringError):
            compliance_correction(.01,10,.005,"SYN","SYN-R1")
    def test_uncertainty_rss(self):
        items=[{"component_id":"A","standard_uncertainty":3,"evidence_id":"S1","source_revision":"R1"},
               {"component_id":"B","standard_uncertainty":4,"evidence_id":"S2","source_revision":"R1"}]
        r=uncertainty_budget(items,2,"SYN","SYN-R1")
        self.assertAlmostEqual(r["combined_standard_uncertainty"],5)
        self.assertAlmostEqual(r["expanded_uncertainty"],10)
    def test_uncertainty_requires_unique_ids(self):
        items=[{"component_id":"A","standard_uncertainty":1,"evidence_id":"S1","source_revision":"R1"},
               {"component_id":"A","standard_uncertainty":2,"evidence_id":"S2","source_revision":"R1"}]
        with self.assertRaises(FixtureEngineeringError): uncertainty_budget(items,2,"SYN","SYN-R1")
    def test_guardband_three_outcomes(self):
        self.assertEqual(guardband_result(5,1,0,10,"S","R")["status"],"pass")
        self.assertEqual(guardband_result(12,1,0,10,"S","R")["status"],"fail")
        self.assertEqual(guardband_result(10,1,0,10,"S","R")["status"],"indeterminate")
    def test_datum_transfer_repeatability(self):
        r=datum_transfer_repeatability([1,2,3],"SYN","SYN-R1")
        self.assertAlmostEqual(r["mean"],2); self.assertAlmostEqual(r["range"],2)
        self.assertAlmostEqual(r["sample_standard_deviation"],1)
    def test_qualification_packet_fails_closed(self):
        r=validate_qualification_packet({"fixture_id":"SYN"})
        self.assertFalse(r["complete_for_review"])
        self.assertFalse(r["fixture_physically_qualified"])
        self.assertFalse(r["test_release_authorized"])

if __name__=="__main__": unittest.main()
