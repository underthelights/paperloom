import json
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch
import app
import desktop_ai

class DesktopAITests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.old=(app.DATA,app.DB)
        app.DATA=Path(self.tmp.name);app.DB=app.DATA/'library.sqlite3';app.init()
        with app.connect() as c:c.execute('INSERT INTO settings VALUES(?,?)',('chat_provider',json.dumps('ollama')))
    def tearDown(self):
        desktop_ai.shutdown()
        app.DATA,app.DB=self.old
        self.tmp.cleanup()
    def wait_job(self,job):
        for _ in range(100):
            value=desktop_ai.snapshot(job['id'])
            if value['status'] not in ('queued','running'):return value
            time.sleep(.01)
        self.fail('Job did not complete')
    def test_no_source_requires_general_mode(self):
        p=app.upsert({'title':'Only title'})
        with self.assertRaises(ValueError):desktop_ai.start({'id':p['id'],'question':'Explain'},app)
        with patch.object(app,'ollama',return_value='General idea'):
            job=desktop_ai.start({'id':p['id'],'question':'Brainstorm','mode':'general'},app)
            self.assertEqual(self.wait_job(job)['status'],'done')
        self.assertEqual(len(app.get_paper(p['id'])['chat']),2)
    def test_quotes_history_and_concurrent_notes_preserved(self):
        p=app.upsert({'title':'Source','text':'Measured accuracy 91%.'})
        def reply(messages):
            self.assertIn('Measured accuracy 91%',messages[1]['content'])
            self.assertIn('Quoted selection',messages[-1]['content'])
            latest=app.get_paper(p['id']);latest['notes']='Concurrent user edit';app.save(latest)
            return '91%'
        with patch.object(app,'ollama',side_effect=reply):
            job=desktop_ai.start({'id':p['id'],'question':'Accuracy?','quote':'91%'},app)
            self.assertEqual(self.wait_job(job)['status'],'done')
        saved=app.get_paper(p['id']);self.assertEqual(saved['notes'],'Concurrent user edit');self.assertEqual(saved['chat'][0]['quote'],'91%')
    def test_cancel_discards_response_and_keeps_history(self):
        p=app.upsert({'title':'Source','text':'Data'})
        entered=threading.Event();release=threading.Event();finished=threading.Event()
        def reply(_):
            entered.set();release.wait(3);finished.set();return 'Do not store'
        with patch.object(app,'ollama',side_effect=reply):
            job=desktop_ai.start({'id':p['id'],'question':'Explain'},app)
            self.assertTrue(entered.wait(2))
            desktop_ai.cancel(job['id']);release.set();self.assertTrue(finished.wait(2));time.sleep(.03)
        self.assertEqual(desktop_ai.snapshot(job['id'])['status'],'cancelled')
        self.assertEqual(app.get_paper(p['id'])['chat'],[])
