import unittest
from types import SimpleNamespace
from src.autopilot.twilio_paging import TwilioCallPager

ACCOUNT="AC"+"a"*32
PARENT="CA"+"b"*32
CHILD="CA"+"c"*32
def call(**overrides):
    values=dict(sid=CHILD,account_sid=ACCOUNT,parent_call_sid=PARENT)
    values.update(overrides)
    return SimpleNamespace(**values)
class Page:
    def __init__(self,items,next_page_url=None):
        self.items=items
        self.next_page_url=next_page_url
    def __iter__(self): return iter(self.items)
class Calls:
    def __init__(self,page): self.result=page
    def page(self,**kwargs): return self.result
class Client:
    def __init__(self,page): self.calls=Calls(page)

class TestTwilioPaging(unittest.TestCase):
    def pager(self,page): return TwilioCallPager(Client(page),ACCOUNT)
    def test_sdk_multi_page(self):
        first=Page([call()],next_page_url="/next")
        second=Page([call(sid="CA"+"d"*32)])
        first.next_page=lambda:second
        result=self.pager(first).enumerate_all(PARENT)
        self.assertTrue(result.complete)
        self.assertEqual(result.pages_checked,2)

    def test_sdk_page_limit(self):
        first=Page([call()],next_page_url="/next")
        first.next_page=lambda:Page([call(sid="CA"+"d"*32)])
        self.assertEqual(self.pager(first).enumerate_all(PARENT,max_pages=1).reason,
                         "page_limit_exceeded")

    def test_sdk_missing_next_method(self):
        first=Page([call()],next_page_url="/next")
        self.assertEqual(self.pager(first).enumerate_all(PARENT).reason,
                         "missing_sdk_next_page")

    def test_sdk_account_mismatch(self):
        result=self.pager(Page([call(account_sid="AC"+"d"*32)])).enumerate_all(PARENT)
        self.assertEqual(result.reason,"account_mismatch")

    def test_rate_limit(self):
        class RateLimited(Exception):
            status=429
        class Calls:
            def page(self,**kwargs): raise RateLimited()
        class Client:
            calls=Calls()
        result=TwilioCallPager(Client(),ACCOUNT).enumerate_all(PARENT)
        self.assertEqual(result.reason,"provider_rate_limited")
        self.assertFalse(result.complete)

    def test_provider_unavailable(self):
        class Unavailable(Exception):
            status=503
        class Calls:
            def page(self,**kwargs): raise Unavailable()
        class Client:
            calls=Calls()
        result=TwilioCallPager(Client(),ACCOUNT).enumerate_all(PARENT)
        self.assertEqual(result.reason,"provider_temporarily_unavailable")

    def test_auth_failure(self):
        class Forbidden(Exception):
            status=403
        class Calls:
            def page(self,**kwargs): raise Forbidden()
        class Client:
            calls=Calls()
        result=TwilioCallPager(Client(),ACCOUNT).enumerate_all(PARENT)
        self.assertEqual(result.reason,"provider_auth_failed")

    def test_single_page(self):
        items,next_cursor=self.pager(Page([call()])).fetch_page(PARENT,None,50)
        self.assertEqual(len(items),1)
        self.assertIsNone(next_cursor)
    def test_continuation_fails_closed(self):
        with self.assertRaises(ValueError):
            self.pager(Page([call()],"https://api.twilio.com/next")).fetch_page(PARENT,None,50)
    def test_wrong_account(self):
        with self.assertRaises(ValueError):
            self.pager(Page([call(account_sid="AC"+"d"*32)])).fetch_page(PARENT,None,50)
    def test_wrong_parent(self):
        with self.assertRaises(ValueError):
            self.pager(Page([call(parent_call_sid="CA"+"d"*32)])).fetch_page(PARENT,None,50)
    def test_external_cursor_rejected(self):
        with self.assertRaises(ValueError):
            self.pager(Page([])).fetch_page(PARENT,"https://example.test",50)
    def test_invalid_account(self):
        with self.assertRaises(ValueError): TwilioCallPager(Client(Page([])),"bad")

if __name__=="__main__":
    unittest.main()
