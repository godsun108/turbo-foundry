import unittest
from types import SimpleNamespace
from src.autopilot.paged_child_calls import enumerate_pages

PARENT="CA"+"a"*32
A="CA"+"b"*32
B="CA"+"c"*32
def leg(sid,parent=PARENT): return SimpleNamespace(sid=sid,parent_call_sid=parent)

class TestPagedEnumeration(unittest.TestCase):
    def test_two_pages_complete(self):
        def fetch(parent,cursor,size):
            return ([leg(A)],"next") if cursor is None else ([leg(B)],None)
        result=enumerate_pages(fetch,PARENT)
        self.assertTrue(result.complete)
        self.assertEqual(result.pages_checked,2)
        self.assertEqual(result.child_sids,(A,B))

    def test_empty_page_complete(self):
        self.assertTrue(enumerate_pages(lambda *args:([],None),PARENT).complete)

    def test_page_limit(self):
        result=enumerate_pages(lambda *args:([leg(A)],"next"),PARENT,max_pages=1)
        self.assertEqual(result.reason,"page_limit_exceeded")

    def test_repeated_cursor(self):
        def fetch(parent,cursor,size):
            return ([leg(A)],"next") if cursor is None else ([leg(B)],"next")
        self.assertEqual(enumerate_pages(fetch,PARENT).reason,"invalid_or_repeated_cursor")

    def test_timeout(self):
        def fetch(*args): raise TimeoutError()
        self.assertEqual(enumerate_pages(fetch,PARENT).reason,"provider_timeout")

    def test_bad_parent_link(self):
        self.assertEqual(enumerate_pages(lambda *args:([leg(A,"CA"+"d"*32)],None),
                                         PARENT).reason,"child_parent_mismatch")

    def test_duplicate_across_pages(self):
        def fetch(parent,cursor,size):
            return ([leg(A)],"next") if cursor is None else ([leg(A)],None)
        self.assertEqual(enumerate_pages(fetch,PARENT).reason,"duplicate_child")

    def test_leg_limit(self):
        self.assertEqual(enumerate_pages(lambda *args:([leg(A),leg(B)],None),
                                         PARENT,max_legs=1).reason,"leg_limit_exceeded")

    def test_malformed_response(self):
        self.assertEqual(enumerate_pages(lambda *args:[],PARENT).reason,"malformed_page")

    def test_invalid_bounds(self):
        self.assertEqual(enumerate_pages(lambda *args:([],None),PARENT,page_size=0).reason,
                         "invalid_bounds")

if __name__=="__main__":
    unittest.main()
