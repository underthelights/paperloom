import copy,json,unittest
from pathlib import Path
from unittest.mock import patch
import concept_study as S,knowledge as K,research as R
import test_knowledge

class ConceptStudyTests(unittest.TestCase):
    def setUp(self):
        test_knowledge.KnowledgeTests.setUp(self)
        source=Path(__file__).resolve().parents[1]/'research-skills/concept-guides/latent-action.json'
        self.guide=json.loads(source.read_text());folder=R.SKILLS/'concept-guides';folder.mkdir();(folder/'latent-action.json').write_text(json.dumps(self.guide))
        self.v=K.create('Latent Action');K.edit({'id':self.v['id'],'notes':'Private derivation'})
    tearDown=test_knowledge.KnowledgeTests.tearDown
    def test_reference_and_progress_preserve_personal_notes(self):
        data=S.get(self.v['id']);self.assertEqual(data['status'],'ready');self.assertEqual(len(data['guide']['comparisons']),3)
        q=data['guide']['questions'][0]['id'];result=S.progress({'id':self.v['id'],'question_id':q,'answer':'내 설명','understood':True})
        self.assertTrue(result['progress']['answers'][q]['understood']);self.assertEqual(K.get(self.v['id'])['notes'],'Private derivation')
        result=S.progress({'id':self.v['id'],'question_id':q,'answer':'수정한 설명'});self.assertFalse(result['progress']['answers'][q]['understood'])
        self.assertNotIn('score',result['progress']);self.assertIn('수정한 설명',K.export(self.v['id']).decode());self.assertIn('개념 학습',''.join(json.loads(K.export(self.v['id'],True))['cells'][0]['source']))
    def test_invalid_questions_and_empty_self_confirmation_rejected(self):
        q=self.guide['questions'][0]['id']
        for data in ({'question_id':'invented','answer':'x'},{'question_id':q,'understood':True},{'question_id':q,'answer':'x'*20001},{'question_id':q,'answer':'x','understood':'yes'}):
            with self.assertRaises(ValueError):S.progress({'id':self.v['id'],**data})
        self.assertEqual(S.get(self.v['id'])['progress']['answers'],{})
    def test_unsafe_or_unlinked_guide_rejected(self):
        for mutate in (lambda g:g['sources'][0].update(url='javascript:alert(1)'),lambda g:g['relations'][0].update(target='missing'),lambda g:g['relations'][0].update(type='similarity-guessed'),lambda g:g['sections'][0].update(sources=[]),lambda g:g['questions'].append(copy.deepcopy(g['questions'][0]))):
            guide=copy.deepcopy(self.guide);mutate(guide)
            with self.assertRaises(ValueError):S.validate(guide)
    def test_generation_uses_latest_notes_and_failed_result_keeps_old_guide(self):
        v=K.create('New Concept');K.edit({'id':v['id'],'notes':'old'})
        def result(*args,**kwargs):K.edit({'id':v['id'],'notes':'edited during research'});return json.dumps(self.guide)
        with patch.object(R,'cli',side_effect=result):S.worker(v['id'])
        saved=K.get(v['id']);self.assertEqual(saved['notes'],'edited during research');self.assertEqual(saved['study_status'],'ready')
        with patch.object(R,'cli',return_value='{}'):S.worker(v['id'])
        saved=K.get(v['id']);self.assertEqual(saved['study_status'],'error');self.assertEqual(saved['study_guide'],self.guide);self.assertEqual(saved['notes'],'edited during research')
    def test_recovery_and_duplicate_start(self):
        with patch.object(S.threading,'Thread') as thread:
            S.start({'id':self.v['id']});S.start({'id':self.v['id']});self.assertEqual(thread.call_count,1)
        K.init();self.assertEqual(K.get(self.v['id'])['study_status'],'error');self.assertTrue(S.get(self.v['id'])['error'])
        with patch.object(S.threading,'Thread') as thread:
            thread.return_value.start.side_effect=RuntimeError('start failed')
            with self.assertRaises(RuntimeError):S.start({'id':self.v['id']})
        self.assertEqual(S.get(self.v['id'])['status'],'error')

    def test_changed_question_preserves_answer_without_reusing_confirmation(self):
        key=self.v['id'];q=S.get(key)['guide']['questions'][0]
        S.progress({'id':key,'question_id':q['id'],'question_revision':q['revision'],'answer':'Original explanation','understood':True})
        guide=copy.deepcopy(self.guide);guide['questions'][0]['prompt']='A different question'
        with patch.object(R,'cli',return_value=json.dumps(guide)):S.worker(key)
        answer=S.get(key)['progress']['answers'][q['id']]
        self.assertEqual(answer['answer'],'Original explanation');self.assertEqual(answer['prompt'],q['prompt']);self.assertFalse(answer['understood']);self.assertTrue(answer['stale'])
        self.assertIn(q['prompt'],K.export(key).decode())
        with self.assertRaises(ValueError):S.progress({'id':key,'question_id':q['id'],'question_revision':q['revision'],'answer':'Late save','understood':True})
        self.assertEqual(S.get(key)['progress']['answers'][q['id']]['answer'],'Original explanation')

    def test_cancel_keeps_guide_and_job_cancelled(self):
        key=self.v['id']
        def cancel(jid,*args,**kwargs):
            R.cancel(jid)
            raise InterruptedError()
        with patch.object(R,'cli',side_effect=cancel):S.worker(key)
        self.assertEqual(S.get(key)['guide']['title'],self.guide['title'])
        self.assertEqual(S.get(key)['status'],'draft');self.assertEqual(S.get(key)['error'],'')
        self.assertTrue(any(j['status']=='cancelled' for j in R.JOBS.values()))
