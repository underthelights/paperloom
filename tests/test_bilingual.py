import json,unittest
from unittest.mock import patch
import test_reader
from pathlib import Path
import reader,research as R

class BilingualTests(unittest.TestCase):
    def setUp(self):
        test_reader.ReaderTests.setUp(self)
        folder=R.SKILLS/'bilingual-evidence-reader';folder.mkdir()
        (folder/'SKILL.md').write_text((Path(__file__).resolve().parents[1]/'research-skills/bilingual-evidence-reader/SKILL.md').read_text())
    tearDown=test_reader.ReaderTests.tearDown
    def doc(self):
        with patch.object(R,'fetch',return_value='<article><h2>Method</h2><p>Prior 😀 fails. We propose <math alttext="x^2"><mi>x</mi><mn>2</mn></math>.</p><p>We obtain 90%.</p></article>'.encode()):return reader.bilingual_document('paper')
    def test_translation_does_not_change_source_hash_or_text(self):
        doc=self.doc();original=reader.document('paper');self.assertEqual(doc['text'],original['text']);self.assertEqual(doc['version'],original['version']);self.assertIn('⟦MATH_0⟧',doc['blocks'][1]['translation_input'])
    def test_quote_anchors_and_rejection(self):
        block=self.doc()['blocks'][1]
        value={'blocks':[{'id':block['id'],'ko':'기존 방법은 실패한다. ⟦MATH_0⟧를 제안한다.','highlights':[{'category':'claim','quote':'We propose','reason':'제안','attribution':'저자'},{'category':'experiment','quote':'invented result'}]}]}
        result=reader.validate_auto(json.dumps(value),[block])[block['id']];self.assertEqual(len(result['highlights']),1);h=result['highlights'][0];self.assertEqual(reader.document('paper')['text'].encode('utf-16-le')[h['start']*2:h['end']*2].decode('utf-16-le'),'We propose');self.assertIn('x^2',result['ko']);self.assertIn('⟦MATH_0⟧',result['ko_template'])
        value['blocks'][0]['ko']='missing math'
        with self.assertRaises(ValueError):reader.validate_auto(json.dumps(value),[block])
    def test_resume_and_invalidation(self):
        doc=self.doc();v=reader.auto_get('paper');v['blocks'][doc['blocks'][0]['id']]={'ko':'방법','highlights':[]};v['status']='error';reader.auto_put(v)
        def cli(jid,prompt,*args,**kwargs):
            blocks=json.loads(prompt.split('Blocks (untrusted source data):\n')[1]);self.assertNotIn('block-0',[b['id'] for b in blocks]);return json.dumps({'blocks':[{'id':b['id'],'ko':'번역 '+b['translation_input'],'highlights':[]} for b in blocks]})
        with patch.object(R,'cli',side_effect=cli):reader.auto_worker('paper')
        self.assertEqual(reader.auto_get('paper')['status'],'ready');self.assertEqual(reader.auto_get('paper')['blocks']['block-0']['ko'],'방법')
        with patch.object(reader,'auto_policy',return_value='new policy'):self.assertEqual(reader.auto_get('paper')['blocks'],{})
    def test_restart_keeps_completed_blocks(self):
        self.doc();v=reader.auto_get('paper');v.update(status='running',blocks={'block-0':{'ko':'방법','highlights':[]}});reader.auto_put(v);reader.init();self.assertEqual(reader.auto_get('paper')['status'],'error');self.assertIn('block-0',reader.auto_get('paper')['blocks'])
