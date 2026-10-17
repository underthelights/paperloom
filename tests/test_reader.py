import json,unittest
from unittest.mock import patch
import test_research as base
import research,reader

class ReaderTests(unittest.TestCase):
    tearDown=base.ResearchTests.tearDown
    def setUp(self):
        base.ResearchTests.setUp(self);reader.init();research.save({'id':'paper','identity':'test','title':'Test','arxiv':'2303.04137','notes':'keep'})
    def doc(self):
        with patch.object(research,'fetch',return_value=b'<article><h2 id="s1">Method</h2><p>Selected text and context.</p><script>alert(1)</script><a href="javascript:alert(1)" onclick="bad()">bad</a><img src="https://evil.invalid/a" onerror="bad()"><math alttext="x"><mi>x</mi></math></article>'):
            return reader.document('paper')
    def annotation(self):
        doc=self.doc();start=doc['text'].index('Selected');return reader.save({'paper_id':'paper','version':doc['version'],'start':start,'end':start+13,'exact':'Selected text'})
    def test_original_sanitized_and_cached(self):
        doc=self.doc();self.assertNotIn('script',doc['html']);self.assertNotIn('onclick',doc['html']);self.assertNotIn('evil.invalid',doc['html']);self.assertIn('<math',doc['html']);self.assertEqual(reader.document('paper'),doc)
    def test_anchor_validation_and_note_export(self):
        a=self.annotation();reader.save({'paper_id':'paper','annotation_id':a['id'],'note':'My reasoning','color':'green'});self.assertIn('My reasoning',reader.export('paper'));self.assertEqual(research.get('paper')['notes'],'keep')
        with self.assertRaises(ValueError):reader.save({'paper_id':'paper','version':'wrong','start':0,'end':1,'exact':'M'})
    def test_explanation_persists_on_annotation(self):
        a=self.annotation()
        with patch.object(research,'cli',return_value='Grounded explanation'):reader.worker(a['id'],'explain')
        self.assertEqual(reader.get(a['id'])['answer'],'Grounded explanation');reader.delete(a['id']);self.assertEqual(reader.annotations('paper'),[])
    def test_utf16_selection(self):
        _,path=reader.folder('paper');(path/'document.json').write_text(json.dumps({'text':'a😀bc','version':'v'}))
        a=reader.save({'paper_id':'paper','version':'v','start':3,'end':5,'exact':'bc'});self.assertEqual(a['exact'],'bc')

    def test_followup_preserves_previous_explanation(self):
        a=self.annotation();a.update(answer='First explanation',status='ready');reader.put(a)
        with patch('reader.threading.Thread'):
            reader.explain(a['id'],'explain','Why?')
        self.assertEqual(reader.get(a['id'])['history'][0]['answer'],'First explanation')
        with patch.object(research,'cli',return_value='Follow-up answer'):reader.worker(a['id'],'explain')
        self.assertEqual(reader.get(a['id'])['question'],'Why?')
    def test_interrupted_explanation_recovery(self):
        a=self.annotation();a['status']='running';reader.put(a);reader.init()
        self.assertEqual(reader.get(a['id'])['status'],'error')
