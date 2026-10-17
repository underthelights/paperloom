import unittest,json
from unittest.mock import patch
import test_research as base
import research as R,intake,reader
import paperloom_workflow as workflow

class WorkflowTests(unittest.TestCase):
    tearDown=base.ResearchTests.tearDown
    def setUp(self):
        base.ResearchTests.setUp(self);intake.init();reader.init();workflow.ACTIVE.clear();workflow.init()
        self.item={'id':'inbox','title':'Discovery','input':'https://arxiv.org/abs/2303.04137','messages':[{'role':'user','content':'https://arxiv.org/abs/2303.04137'}],'result':{'collection':'Robotics','concepts':['Diffusion'],'papers':[]},'status':'ready','organized':True,'sources':[],'history':[]}
        intake.save(self.item)
        self.paper={'id':'paper','identity':'arxiv:2303.04137','title':'Paper','arxiv':'2303.04137','reports':[{'tldr':'Known report'}],'status':'analyzed','last_run':'a'*32,'notes':'Personal note','references':[]};R.save(self.paper)
    def test_stages_link_and_reuse_without_reanalysis(self):
        candidate=workflow.evidence_papers(self.item)
        with patch.object(R,'add',return_value=self.paper),patch.object(R,'start') as start,patch.object(reader,'document',return_value={}),patch.object(workflow,'graph_for',return_value={'status':'ready','id':'W1','nodes':12,'edges':20,'error':''}):
            workflow.run('inbox',candidate);workflow.run('inbox',candidate);start.assert_not_called()
        item=intake.get('inbox');self.assertEqual(item['pipeline']['status'],'done');summary=workflow.paper_summary('paper');self.assertEqual(len(summary['links']),1);self.assertTrue(summary['has_note'])
    def test_reclassification_keeps_annotations_and_notes(self):
        workflow.bind('inbox','paper');reader.put({'id':'mark','paper_id':'paper','note':'my thought','answer':'explanation'})
        intake.organize('inbox','Robotics / Control');summary=workflow.paper_summary('paper');self.assertEqual(summary['links'][0]['collection'],'Robotics / Control');self.assertEqual(summary['highlights'],1);self.assertEqual(summary['annotation_notes'],1);self.assertEqual(R.get('paper')['notes'],'Personal note')
    def test_model_suggestion_without_source_evidence_not_imported(self):
        item=dict(self.item,messages=[{'role':'user','content':'https://x.com/a/status/1'}],result={'papers':[{'title':'Invented scientific paper title','url':'https://arxiv.org/abs/2303.04137'}]});self.assertEqual(workflow.evidence_papers(item),[])
    def test_social_source_anchor_is_used(self):
        item=dict(self.item,messages=[{'role':'user','content':'https://x.com/a/status/1'}],materials=[{'url':'https://x.com/a/status/1','paper_links':['https://arxiv.org/abs/2303.04137']}]);self.assertEqual(workflow.evidence_papers(item)[0]['basis'],'source-link')
    def test_analysis_failure_does_not_claim_complete(self):
        p=dict(self.paper,reports=[])
        with patch.object(R,'add',return_value=p),patch.object(R,'start',side_effect=ValueError('source unavailable')):
            workflow.run('inbox',workflow.evidence_papers(self.item))
        item=intake.get('inbox');self.assertEqual(item['pipeline']['status'],'partial');self.assertEqual(item['pipeline']['items'][0]['analysis_status'],'error')
    def test_restart_preserves_links_and_marks_retry(self):
        workflow.bind('inbox','paper');workflow.update('inbox',status='running');workflow.init();self.assertEqual(intake.get('inbox')['pipeline']['status'],'interrupted');self.assertEqual(len(workflow.paper_summary('paper')['links']),1)
    def test_new_paper_starts_analysis_before_graph(self):
        p=dict(self.paper,reports=[]);R.save(p)
        def analyze(pid):
            latest=R.get(pid);latest['reports']=[{'tldr':'New analysis'}];R.save(latest);return {'id':'job','status':'done'}
        with patch.object(R,'add',return_value=p),patch.object(R,'start',side_effect=analyze) as start,patch.object(R,'snapshot',return_value={'id':'job','status':'done'}),patch.object(reader,'document',return_value={}),patch.object(workflow,'graph_for',return_value={'status':'ready','id':'W1','nodes':12}):
            workflow.run('inbox',workflow.evidence_papers(self.item));start.assert_called_once_with('paper')
        self.assertEqual(intake.get('inbox')['pipeline']['status'],'done')
    def test_mismatched_proposed_title_does_not_create_record(self):
        candidate={'url':'https://arxiv.org/abs/2303.04137','basis':'explicit-title','title':'Wrong paper'}
        with patch.object(R,'metadata',return_value={'title':'Actual paper'}),patch.object(R,'add') as add:
            workflow.run('inbox',[candidate]);add.assert_not_called()
        self.assertEqual(intake.get('inbox')['pipeline']['status'],'partial')
    def test_post_extraction_ignores_other_page_links(self):
        html='<html><title>Post</title><article>'+('Actual post text. '*30)+'<a href="https://arxiv.org/abs/2303.04137">paper</a></article><aside><a href="https://arxiv.org/abs/9999.99999">other post</a></aside></html>'
        with patch.object(R,'fetch',return_value=html.encode()):sources,materials=intake.collect('https://x.com/author/status/1')
        self.assertEqual(materials[0]['paper_links'],['https://arxiv.org/abs/2303.04137'])
    def test_intake_launches_workflow_automatically(self):
        result={'title':'Paper','summary':'Summary','reply':'Classified','collection':'Robotics','concepts':[],'papers':[],'connections':[]}
        with patch.object(intake,'collect',return_value=([],[])),patch.object(R,'cli',return_value=json.dumps(result)),patch.object(workflow,'start') as start:
            intake.work('inbox');start.assert_called_once_with('inbox')
        self.assertTrue(intake.get('inbox')['organized'])
    def test_existing_link_survives_unavailable_social_source(self):
        item=dict(self.item,messages=[{'role':'user','content':'https://x.com/a/status/1'},{'role':'user','content':'분류만 변경'}],materials=[],pipeline={'items':[{'paper_id':'paper'}]})
        papers=workflow.evidence_papers(item);self.assertEqual(papers[0]['basis'],'existing-library-link');self.assertEqual(papers[0]['url'],'https://arxiv.org/abs/2303.04137')
