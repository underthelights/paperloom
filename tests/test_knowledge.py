import json,unittest
from unittest.mock import patch
import test_research as base
import research as R,reader,intake,knowledge as K
import paperloom_workflow as workflow

class KnowledgeTests(unittest.TestCase):
    tearDown=base.ResearchTests.tearDown
    def setUp(self):
        base.ResearchTests.setUp(self);reader.init();intake.init();workflow.init();K.init()
        for i in range(65):R.save({'id':str(i),'identity':'test:'+str(i),'title':'Paper '+str(i).zfill(2),'authors':['Ada'],'year':'2025','status':'ready','category':'Robotics','reports':[]})
    def test_catalog_paginates_and_filters_concept(self):
        result=K.catalog({'sort':'title','offset':30});self.assertEqual(result['total'],65);self.assertEqual(result['items'][0]['title'],'Paper 30');self.assertEqual(len(result['items']),30)
        K.create('Temporal ensemble','4');result=K.catalog({'concept':'Temporal ensemble'});self.assertEqual([x['id'] for x in result['items']],['4'])
    def test_shared_notebook_preserves_notes_and_rejects_cross_paper_quote(self):
        v=K.create('Temporal ensemble','1');K.edit({'id':v['id'],'notes':'proof'});v=K.create('temporal ensemble','2');self.assertEqual(v['papers'],['1','2']);self.assertEqual(v['notes'],'proof')
        reader.put({'id':'a','paper_id':'1','exact':'quote'})
        with self.assertRaises(ValueError):K.create('Temporal ensemble','2','a')
        v=K.create('Temporal ensemble','1','a');self.assertEqual(v['annotations'],['a']);self.assertIn('quote',K.export(v['id']).decode())
    def test_recovery_and_export(self):
        v=K.create('Async','1');v.update(status='running',video_status='running');K.put(v);K.init();self.assertEqual(K.get(v['id'])['status'],'error');self.assertEqual(json.loads(K.export(v['id'],True))['nbformat'],4)
    def test_large_author_list_keeps_identity_per_paper(self):
        p=R.get('1');p['authors']=['Author '+str(i) for i in range(200)];R.save(p);people=K.people('1')['items'];self.assertEqual(len(people),200);self.assertEqual(len({a['id'] for a in people}),200);self.assertTrue(all(a['paper_affiliation']=='확인 불가' for a in people))
    def test_worker_preserves_notes_and_unverified_person_is_not_promoted(self):
        v=K.create('Async','1')
        with patch.object(R,'cli',return_value='## Definition\nEvidence insufficient.'):
            K.worker(v['id'])
        self.assertEqual(K.get(v['id'])['status'],'ready')
        a=K.people('1')['items'][0];a['kind']='person';K.put(a)
        with patch.object(R,'cli',return_value=json.dumps({'identity_status':'unverified','education':[{'degree':'PhD','evidence_url':'https://example.com'}],'current_affiliation':'Invented'})):K.worker(a['id'])
        profile=K.get(a['id'])['profile'];self.assertEqual(profile['education'],[]);self.assertEqual(profile['current_affiliation'],'확인 불가')
    def test_video_rejects_code_and_path_escape(self):
        v=K.create('Async')
        with self.assertRaises(ValueError):K.video({'id':v['id'],'template':'exec(x)'})
        v['video']='../library.sqlite3';K.put(v)
        with self.assertRaises(ValueError):K.video_file(v['id'])

    def test_author_name_order_and_ambiguous_matching(self):
        p=R.get('1');p['authors']=['Lovelace, Ada'];p['reports']=[{'discovery':{'affiliations':[{'author':'Ada Lovelace','paper_affiliation':'Verified institution'}]}}];R.save(p)
        self.assertEqual(K.people('1')['items'][0]['paper_affiliation'],'Verified institution')
        p['reports'][0]['discovery']['affiliations'].append({'author':'Ada Lovelace','paper_affiliation':'Other institution'});R.save(p)
        self.assertEqual(K.people('1')['items'][0]['paper_affiliation'],'확인 불가')

    def test_deleting_highlight_detaches_all_notebooks_preserving_notes(self):
        reader.put({'id':'linked','paper_id':'1','exact':'source quote'})
        a=K.create('Ensemble','1','linked');b=K.create('Control','1','linked')
        K.edit({'id':a['id'],'notes':'Keep the derivation'})
        reader.delete('linked')
        self.assertEqual(K.get(a['id'])['annotations'],[])
        self.assertEqual(K.get(b['id'])['annotations'],[])
        self.assertEqual(K.get(a['id'])['notes'],'Keep the derivation')
        self.assertEqual(K.get(a['id'])['papers'],['1'])
        with self.assertRaises(ValueError):K.create('Ensemble','1','linked')
