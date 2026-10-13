import os
import tempfile
import unittest
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timedelta,timezone
from types import SimpleNamespace
from src.autopilot.recheck_queue import RecheckQueue
from src.autopilot.recheck_leases import RecheckLeases
from src.autopilot.observation_store import ObservationStore
from src.autopilot.recheck_worker import run_recheck
NOW=datetime(2026,10,13,18,0,tzinfo=timezone.utc)
END=NOW-timedelta(minutes=20)
SID="CA"+"a"*32
class Pager:
    def __init__(self,complete=True,reason="sdk_page_exhaustion",ids=(SID,)):
        self.result=SimpleNamespace(complete=complete,reason=reason,child_sids=ids)
    def enumerate_all(self,parent): return self.result
class WorkerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=os.path.join(self.tmp.name,"worker.db")
        self.queue=RecheckQueue(self.path)
        self.leases=RecheckLeases(self.path)
        self.store=ObservationStore(self.path)
        self.queue.schedule("t","p",now=NOW)
    def tearDown(self): self.tmp.cleanup()
    def run_job(self,now=NOW,pager=None):
        return run_recheck(self.path,"t","p",now=now,call_ended_at=END,
                           pager=pager or Pager(),clock=lambda:now)
    def test_first_observation(self):
        result=self.run_job()
        self.assertTrue(result.recorded)
        self.assertFalse(result.settled_for_review)
        self.assertEqual(result.reason,"insufficient_observations")
    def test_second_observation_stable(self):
        self.run_job()
        result=self.run_job(now=NOW+timedelta(minutes=3))
        self.assertTrue(result.settled_for_review)
    def test_provider_failure(self):
        result=self.run_job(pager=Pager(False,"provider_rate_limited"))
        self.assertFalse(result.recorded)
        self.assertEqual(result.reason,"provider_rate_limited")
        self.assertEqual(self.store.load("t","p"),())
    def test_not_due(self):
        self.run_job()
        self.assertEqual(self.run_job().reason,"not_claimed")
    def test_preclaimed(self):
        token=self.leases.claim("t","p",now=NOW)
        self.assertEqual(self.run_job().reason,"not_claimed")
        self.leases.release("t","p",token)
    def test_timeout_retries_then_exhausts(self):
        for attempt in range(4):
            result=self.run_job(now=NOW+timedelta(minutes=3*attempt),
                                pager=Pager(False,"provider_timeout"))
            self.assertFalse(result.recorded)
        self.assertEqual(self.queue.due(now=NOW+timedelta(days=1)),[])
        self.assertEqual(self.store.load("t","p"),())

    def test_delayed_provider_child_appears(self):
        self.run_job()
        result=self.run_job(now=NOW+timedelta(minutes=3),pager=Pager(ids=(SID,"CA"+"b"*32)))
        self.assertFalse(result.settled_for_review)
        self.assertEqual(result.reason,"changing_child_set")

    def test_crash_lease_recovery(self):
        old=self.leases.claim("t","p",now=NOW,lease_seconds=10)
        self.assertTrue(old)
        result=self.run_job(now=NOW+timedelta(seconds=11))
        self.assertTrue(result.recorded)
        self.assertEqual(len(self.store.load("t","p")),1)

    def test_slow_provider_expired_lease_cannot_persist(self):
        result=run_recheck(self.path,"t","p",now=NOW,call_ended_at=END,
                           pager=Pager(),lease_seconds=10,
                           clock=lambda: NOW+timedelta(seconds=11))
        self.assertFalse(result.recorded)
        self.assertEqual(result.reason,"lease_lost")
        self.assertEqual(self.store.load("t","p"),())

    def test_provider_exception_is_counted(self):
        class BrokenPager:
            def enumerate_all(self,parent):
                raise RuntimeError("simulated outage")
        result=self.run_job(pager=BrokenPager())
        self.assertEqual(result.reason,"worker_error")
        self.assertEqual(self.queue.due(now=NOW),[])
        self.assertEqual(self.store.load("t","p"),())

    def test_backwards_clock_does_not_write(self):
        result=run_recheck(self.path,"t","p",now=NOW,call_ended_at=END,
                           pager=Pager(),clock=lambda:NOW-timedelta(seconds=5))
        self.assertEqual(result.reason,"invalid_completion_clock")
        self.assertEqual(self.store.load("t","p"),())

    def test_naive_clock_does_not_write(self):
        result=run_recheck(self.path,"t","p",now=NOW,call_ended_at=END,
                           pager=Pager(),clock=lambda:NOW.replace(tzinfo=None))
        self.assertEqual(result.reason,"invalid_completion_clock")
        self.assertEqual(self.store.load("t","p"),())

    def test_concurrent_workers_only_one_records(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda _:self.run_job(),range(2)))
        self.assertEqual(sum(result.recorded for result in results),1)
        self.assertEqual(len(self.store.load("t","p")),1)

    def test_database_failure_never_reports_success(self):
        class BreakDatabase:
            def enumerate_all(inner,parent):
                with sqlite3.connect(self.path) as db:
                    db.execute("DROP TABLE provider_observations")
                return Pager().result
        result=self.run_job(pager=BreakDatabase())
        self.assertFalse(result.recorded)
        self.assertIn(result.reason,("worker_error","lease_lost_or_storage_error"))

    def test_provider_exception_after_lease_expiry_cannot_advance_job(self):
        class BrokenPager:
            def enumerate_all(self,parent):
                raise TimeoutError("simulated slow provider")
        result=run_recheck(self.path,"t","p",now=NOW,call_ended_at=END,
                           pager=BrokenPager(),lease_seconds=10,
                           clock=lambda:NOW+timedelta(seconds=11))
        self.assertEqual(result.reason,"lease_lost_or_storage_error")
        self.assertEqual(self.queue.due(now=NOW),[("t","p",0,4)])
        self.assertEqual(self.store.load("t","p"),())

    def test_observation_uses_post_request_clock(self):
        finished=NOW+timedelta(seconds=45)
        result=run_recheck(self.path,"t","p",now=NOW,call_ended_at=END,
                           pager=Pager(),clock=lambda:finished)
        self.assertTrue(result.recorded)
        self.assertEqual(self.store.load("t","p")[0].observed_at,finished)

    def test_naive_start_clock_is_rejected(self):
        result=run_recheck(self.path,"t","p",now=NOW.replace(tzinfo=None),
                           call_ended_at=END,pager=Pager(),clock=lambda:NOW)
        self.assertEqual(result.reason,"invalid_start_clock")
        self.assertEqual(self.queue.due(now=NOW),[("t","p",0,4)])

    def test_changing_records(self):
        self.run_job()
        result=self.run_job(now=NOW+timedelta(minutes=3),pager=Pager(ids=()))
        self.assertFalse(result.settled_for_review)
        self.assertEqual(result.reason,"changing_child_set")
if __name__=="__main__":
    unittest.main()
