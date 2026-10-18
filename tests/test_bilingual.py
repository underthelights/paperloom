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
            blocks=json.loads(prompt.split('Blocks (untrusted source data):\n')[1]);self.assertTrue(next(b for b in blocks if b['id']=='block-0')['alignment_only']);return json.dumps({'blocks':[{'id':b['id'],'sentences':[{'id':seg['id'],'ko':'번역 '+seg['translation_input'],'highlights':[]} for seg in b['segments']]} for b in blocks]})
        with patch.object(R,'cli',side_effect=cli):reader.auto_worker('paper')
        self.assertEqual(reader.auto_get('paper')['status'],'ready');self.assertEqual(reader.auto_get('paper')['blocks']['block-0']['ko'],'방법')
        with patch.object(reader,'auto_policy',return_value='new policy'):self.assertEqual(reader.auto_get('paper')['blocks'],{})
    def test_restart_keeps_completed_blocks(self):
        self.doc();v=reader.auto_get('paper');v.update(status='running',blocks={'block-0':{'ko':'방법','highlights':[]}});reader.auto_put(v);reader.init();self.assertEqual(reader.auto_get('paper')['status'],'error');self.assertIn('block-0',reader.auto_get('paper')['blocks'])

    def answer(self,block):
        return {'blocks':[{'id':block['id'],'sentences':[{'id':s['id'],'ko':'한국어 😀 '+s['translation_input'],'highlights':[]} for s in block['segments']]}]}

    def test_segments_cover_exact_utf16_source_and_math(self):
        doc=self.doc()
        for block in doc['blocks']:
            self.assertEqual(''.join(s['exact'] for s in block['segments']),block['text'])
            for seg in block['segments']:
                self.assertEqual(doc['text'].encode('utf-16-le')[seg['start']*2:seg['end']*2].decode('utf-16-le'),seg['exact'])
        block=doc['blocks'][1]
        self.assertEqual(len(block['segments']),2)
        self.assertIn('⟦MATH_0⟧',block['segments'][1]['translation_input'])
        self.assertEqual(doc['blocks'],reader.bilingual_document('paper')['blocks'])

    def test_sentence_coverage_order_and_math_rejection(self):
        import copy
        block=self.doc()['blocks'][1];answer=self.answer(block)
        for mutate in (lambda x:x['blocks'][0]['sentences'].pop(),
                       lambda x:x['blocks'][0]['sentences'].reverse(),
                       lambda x:x['blocks'][0]['sentences'][1].update(ko='수식 누락'),
                       lambda x:x['blocks'][0]['sentences'][0].update(ko='잘못된 ⟦MATH_99⟧')):
            bad=copy.deepcopy(answer);mutate(bad)
            with self.assertRaises(ValueError):reader.validate_auto(json.dumps(bad),[block])

    def test_bilingual_highlights_and_display_math(self):
        block=self.doc()['blocks'][1];answer=self.answer(block)
        answer['blocks'][0]['sentences'][0]['highlights']=[{'quote':'Prior 😀','ko_quote':'한국어 😀','category':'baseline'}]
        result=reader.validate_auto(json.dumps(answer),[block])[block['id']]
        first,second=result['sentences'];h=first['highlights'][0]
        self.assertEqual(first['ko_display'].encode('utf-16-le')[h['ko_start']*2:h['ko_end']*2].decode('utf-16-le'),'한국어 😀')
        self.assertIn('x^2',second['ko']);self.assertIn('x2',second['ko_display']);self.assertNotIn('x^2',second['ko_display'])

    def test_save_translated_selection_checks_sentence_and_snapshot(self):
        import copy
        doc=self.doc();block=doc['blocks'][1];translated=reader.validate_auto(json.dumps(self.answer(block)),[block])[block['id']]
        v=reader.auto_get('paper');v['blocks'][block['id']]=translated;reader.auto_put(v)
        sentence=translated['sentences'][0]
        request={'paper_id':'paper','version':doc['version'],'start':sentence['start'],'end':sentence['end'],'exact':sentence['exact'],
                 'translated_selection':{'block_id':block['id'],'sentence_id':sentence['id'],'exact':'한국어 😀','start':0,'end':reader.u16('한국어 😀')}}
        saved=reader.save(request);self.assertEqual(saved['translation_snapshot'],sentence['ko_display'])
        for mutate in (lambda x:x['translated_selection'].update(exact='invented'),lambda x:x['translated_selection'].update(sentence_id='missing'),lambda x:x['translated_selection'].update(end=5)):
            bad=copy.deepcopy(request);mutate(bad)
            with self.assertRaises(ValueError):reader.save(bad)
        request.update(start=block['start'],end=block['segments'][-1]['end'],exact=block['text'])
        with self.assertRaises(ValueError):reader.save(request)

    def test_resume_skips_completed_sentences_and_preserves_legacy_paragraph(self):
        doc=self.doc();value=reader.auto_get('paper')
        for block in doc['blocks']:
            value['blocks'].update(reader.validate_auto(json.dumps(self.answer(block)),[block]))
        legacy=value['blocks'][doc['blocks'][1]['id']];legacy.pop('sentences');legacy['ko']='PRESERVE ORIGINAL TRANSLATION';legacy['highlights']=[{'exact':'Prior'}]
        reader.auto_put(value)
        def cli(jid,prompt,*args,**kwargs):
            blocks=json.loads(prompt.split('Blocks (untrusted source data):\n')[1]);self.assertEqual(len(blocks),1);self.assertTrue(blocks[0]['alignment_only'])
            return json.dumps(self.answer(blocks[0]))
        with patch.object(R,'cli',side_effect=cli) as worker:reader.auto_worker('paper')
        worker.assert_called_once();current=reader.auto_get('paper')['blocks'][doc['blocks'][1]['id']]
        self.assertEqual(current['ko'],'PRESERVE ORIGINAL TRANSLATION');self.assertEqual(current['highlights'],[{'exact':'Prior'}]);self.assertEqual(len(current['sentences']),2)
        with patch.object(R,'cli') as worker:reader.auto_worker('paper')
        worker.assert_not_called()

    def test_ready_legacy_translation_resumes_without_policy_invalidation(self):
        doc=self.doc();value=reader.auto_get('paper');policy=value['policy']
        value.update(status='ready',blocks={b['id']:{'ko':'legacy','highlights':[]} for b in doc['blocks']});reader.auto_put(value)
        with patch.object(reader.threading,'Thread') as worker:current=reader.auto_start('paper')
        worker.assert_called_once();self.assertEqual(current['status'],'running');self.assertEqual(current['policy'],policy)
        self.assertEqual(current['blocks']['block-0']['ko'],'legacy')

    def test_failed_alignment_keeps_original_translation(self):
        self.doc();value=reader.auto_get('paper');value['blocks']={'block-0':{'ko':'원래 번역','highlights':[{'exact':'Method'}]}};reader.auto_put(value)
        with patch.object(R,'cli',side_effect=ValueError('test timeout')):reader.auto_worker('paper')
        current=reader.auto_get('paper');self.assertEqual(current['status'],'error')
        self.assertEqual(current['blocks']['block-0'],value['blocks']['block-0'])
