import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from pathlib import Path
import research as R
from cli_scheduler import Scheduler


class SchedulerTests(unittest.TestCase):
    def test_shared_cli_limit_queue_visibility_and_reuse(self):
        scheduler=Scheduler(2,10);release=threading.Event();two=threading.Event();queued=threading.Event()
        guard=threading.Lock();active=0;maximum=0;calls=0
        jobs={str(i):{'id':str(i),'status':'running','stage':'test','cancel':False} for i in range(4)}
        def body(*args,**kwargs):
            nonlocal active,maximum,calls
            with guard:
                active+=1;calls+=1;maximum=max(maximum,active)
                if calls==2:two.set()
            release.wait(3)
            with guard:active-=1
            return 'ok'
        original=scheduler.slot
        from contextlib import contextmanager
        @contextmanager
        def observed(cancelled,changed):
            def update(state,position):
                changed(state,position)
                if state=='queued':queued.set()
            with original(cancelled,update):yield
        with patch.object(R,'CLI_SCHEDULER',scheduler),patch.object(R,'JOBS',jobs),patch.object(R,'_cli',side_effect=body),patch.object(scheduler,'slot',observed),ThreadPoolExecutor(4) as pool:
            futures=[pool.submit(R.cli,str(i),'prompt',Path('.'),'test') for i in range(4)]
            try:
                self.assertTrue(two.wait(2));self.assertTrue(queued.wait(2))
                self.assertTrue(any(j.get('cli_status')=='queued' for j in jobs.values()))
                self.assertEqual(maximum,2)
            finally:release.set()
            self.assertEqual([f.result(3) for f in futures],['ok']*4)
        self.assertEqual(len(scheduler.active),0);self.assertEqual(len(scheduler.waiting),0)

    def test_bounded_wait_and_cancel_do_not_leak_slots(self):
        scheduler=Scheduler(1,1);cancel=threading.Event();queued=threading.Event()
        def waiting():
            with scheduler.slot(cancel.is_set,lambda state,pos:queued.set() if state=='queued' else None):
                self.fail('cancelled request acquired slot')
        with scheduler.slot(),ThreadPoolExecutor(1) as pool:
            future=pool.submit(waiting)
            self.assertTrue(queued.wait(2))
            try:
                with self.assertRaises(ValueError):
                    with scheduler.slot():pass
            finally:cancel.set()
            with self.assertRaises(InterruptedError):future.result(2)
        with scheduler.slot():pass
        self.assertFalse(scheduler.active);self.assertFalse(scheduler.waiting)

    def test_failed_body_releases_capacity(self):
        scheduler=Scheduler(1,1)
        with self.assertRaises(RuntimeError):
            with scheduler.slot():raise RuntimeError('failed process')
        with scheduler.slot():self.assertEqual(len(scheduler.active),1)

    def test_live_queue_merges_persisted_jobs_without_process_objects(self):
        import json,sqlite3,tempfile
        with tempfile.TemporaryDirectory() as tmp:
            dbpath=Path(tmp)/'jobs.sqlite3'
            with sqlite3.connect(dbpath) as db:
                db.execute('CREATE TABLE jobs(id TEXT PRIMARY KEY, body TEXT)')
                db.execute('INSERT INTO jobs VALUES(?,?)',('same',json.dumps({'id':'same','status':'queued','created':'1'})))
            jobs={'same':{'id':'same','status':'done','created':'1','process':object(),'cancel':False}}
            jobs.update({str(i):{'id':str(i),'status':'queued','kind':'bilingual','created':'2'} for i in range(35)})
            with patch.object(R,'db',side_effect=lambda:sqlite3.connect(dbpath)),patch.object(R,'JOBS',jobs):
                result=R.saved_jobs()
            self.assertEqual(sum(j['status']=='queued' for j in result),35)
            self.assertEqual(len([j for j in result if j['id']=='same']),1)
            self.assertNotIn('process',result[-1]);self.assertNotIn('cancel',result[-1]);json.dumps(result)

    def test_reader_job_does_not_block_research_but_same_kind_does(self):
        jobs={'reader':{'id':'reader','paper_id':'paper','kind':'bilingual','stage':'bilingual-reader','status':'running'}}
        with patch.object(R,'get',return_value={'arxiv':'1234.56789'}),patch.object(R,'JOBS',jobs),patch.object(R,'persist_job'),patch.object(R.threading,'Thread'):
            started=R.start('paper')
            self.assertEqual(started['kind'],'research')
            with self.assertRaises(ValueError):R.start('paper')
