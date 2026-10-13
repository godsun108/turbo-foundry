import unittest
from types import SimpleNamespace
from src.autopilot.child_enumeration import enumerate_child_calls

PARENT="CA"+"a"*32
CHILD="CA"+"b"*32
CHILD2="CA"+"c"*32
class Calls:
    def __init__(self,items): self.items=items
    def list(self,*,parent_call_sid,limit): return self.items[:limit]
class Provider:
    def __init__(self,items): self.calls=Calls(items)
def leg(sid,parent=PARENT): return SimpleNamespace(sid=sid,parent_call_sid=parent)

class TestEnumeration(unittest.TestCase):
    def test_single_child(self):
        result=enumerate_child_calls(Provider([leg(CHILD)]),PARENT)
        self.assertTrue(result.complete)
        self.assertEqual(result.child_sids,(CHILD,))

    def test_limit_exceeded(self):
        self.assertEqual(enumerate_child_calls(Provider([leg(CHILD),leg(CHILD2)]),
                                              PARENT,max_legs=1).reason,"limit_exceeded")

    def test_parent_mismatch(self):
        self.assertEqual(enumerate_child_calls(Provider([leg(CHILD,"CA"+"d"*32)]),
                                              PARENT).reason,"child_parent_mismatch")

    def test_duplicate_child(self):
        self.assertEqual(enumerate_child_calls(Provider([leg(CHILD),leg(CHILD)]),
                                              PARENT).reason,"duplicate_child")

    def test_invalid_parent(self):
        self.assertEqual(enumerate_child_calls(Provider([]),"bad").reason,"invalid_parent_sid")

    def test_invalid_limit(self):
        self.assertEqual(enumerate_child_calls(Provider([]),PARENT,max_legs=0).reason,"invalid_limit")

    def test_provider_error(self):
        class Broken:
            class Calls:
                def list(self,**kwargs): raise RuntimeError("offline")
            calls=Calls()
        self.assertEqual(enumerate_child_calls(Broken(),PARENT).reason,"provider_list_failed")

if __name__=="__main__":
    unittest.main()
