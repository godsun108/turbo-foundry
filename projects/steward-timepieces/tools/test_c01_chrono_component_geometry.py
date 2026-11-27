import unittest
from c01_chrono_component_geometry import (
    validate_component, validate_package, generate_component_scad,
)

class ChronographComponentGeometryTests(unittest.TestCase):
    def part(self, ident="synthetic_wheel", kind="annulus"):
        params={"outer_radius_mm":3,"inner_radius_mm":1,"height_mm":0.5}
        if kind=="cylinder": params={"radius_mm":2,"height_mm":0.5}
        if kind=="extruded_polygon":
            params={"outline_xy_mm":[[0,0],[2,0],[1,2]],"height_mm":0.5}
        return {"id":ident,"role":"SYNTHETIC FIXTURE ONLY","geometry_type":kind,
            "parameters":params,"pose":{"x_mm":0,"y_mm":0,"z_mm":0,
            "rx_deg":0,"ry_deg":0,"rz_deg":0},
            "evidence_id":"TEST-FIXTURE","source_revision":"TEST"}
    def package(self):
        a=self.part("part_a"); b=self.part("part_b","cylinder")
        return {"candidate_id":"SYNTHETIC-ONLY","evidence_id":"TEST",
            "source_revision":"FIXTURE","components":[a,b],
            "interfaces":[{"id":"interface_1","component_a":"part_a",
                "component_b":"part_b","interface_type":"synthetic-only",
                "evidence_id":"TEST","source_revision":"FIXTURE"}]}
    def test_accepts_supported_geometry_types(self):
        for kind in ("cylinder","annulus","extruded_polygon"):
            self.assertTrue(validate_component(self.part(kind=kind))["geometry_complete"])
    def test_rejects_invalid_annulus(self):
        p=self.part(); p["parameters"]["inner_radius_mm"]=3
        with self.assertRaises(ValueError): validate_component(p)
    def test_rejects_duplicate_ids(self):
        p=self.package(); p["components"][1]["id"]="part_a"
        with self.assertRaises(ValueError): validate_package(p)
    def test_rejects_unknown_interface_endpoint(self):
        p=self.package(); p["interfaces"][0]["component_b"]="missing"
        with self.assertRaises(ValueError): validate_package(p)
    def test_requires_provenance(self):
        p=self.package(); p["components"][0]["evidence_id"]=""
        with self.assertRaises(ValueError): validate_package(p)
    def test_generates_reviewable_source_without_assembly(self):
        source=generate_component_scad(self.package())
        self.assertIn("module part_part_a()",source)
        self.assertIn("// part_part_a();",source)
    def test_never_authorizes_manufacture(self):
        self.assertFalse(validate_package(self.package())["manufacturing_release"])

if __name__=="__main__": unittest.main()
