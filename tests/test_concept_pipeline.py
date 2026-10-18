import copy,json,unittest
from unittest.mock import patch
import test_knowledge
import research as R,knowledge as K,concept_pipeline as P

class ConceptPipelineTests(unittest.TestCase):
    tearDown=test_knowledge.KnowledgeTests.tearDown
    def setUp(self):
        test_knowledge.KnowledgeTests.setUp(self)
        P.init();self.pid='1';self.rid='report-one';self.token='token-one'
        self.paper=R.get(self.pid);self.paper.update(url='https://example.com/paper',reports=[{'id':self.rid}],last_run='test-run');R.save(self.paper)
        self.text='Flow Matching learns a continuous transport between noise and data distributions. FM denotes Flow Matching in this paper. '
        run=R.DATA/'runs'/self.rid;run.mkdir(parents=True);(run/'paper.txt').write_text(self.text*30)
        s=[{'label':'Paper','url':self.paper['url']}]
        self.guide={'version':1,'title':'Transport','summary':'Definition','sources':s,'sections':[{'id':'definition','title':'Definition','body':'Source-backed explanation','sources':s}],'questions':[{'id':'question','prompt':'What changes?','answer':'The distribution.','sources':s}],'nodes':[],'relations':[],'comparisons':[]}
        self.item={'name':'Flow Matching','aliases':['FM'],'definition':'Continuous transport','role':'method','evidence':[{'quote':self.text.split('. ')[0]+'.','url':self.paper['url'],'section':'Method'}],'guide':self.guide}
        self.queue()
    def queue(self,rid=None,token=None):
        if rid:self.rid=rid;self.paper['reports']=[{'id':rid}];R.save(self.paper)
        if token:self.token=token
        with R.db() as c:P.write(c,{'paper_id':self.pid,'report_id':self.rid,'token':self.token,'status':'queued'})
    def commit(self,items=None):return P.commit(self.pid,self.rid,self.token,items if items is not None else [self.item])
    def test_source_quote_and_url_validation(self):
        item=copy.deepcopy(self.item);item['evidence'][0]['quote']=item['evidence'][0]['quote'].replace(' ','\n ')
        self.assertEqual(len(P.validate({'concepts':[item]},self.paper,self.text)),1)
        for field,value in [('quote','This fabricated quotation is not present in the original source.'),('url','https://other.example/paper')]:
            item=copy.deepcopy(self.item);item['evidence'][0][field]=value
            with self.assertRaises(ValueError):P.validate({'concepts':[item]},self.paper,self.text)
        item=copy.deepcopy(self.item);item['aliases']=['FM','Invented abbreviation']
        self.assertEqual(P.validate({'concepts':[item]},self.paper,self.text)[0]['aliases'],['FM'])
    def test_exact_name_and_registered_alias_reuse(self):
        v=K.create('flow-matching');self.assertTrue(self.commit());self.assertEqual(len(K.concepts()),1)
        self.assertEqual(K.get(v['id'])['papers'],[self.pid])
        alias=copy.deepcopy(self.item);alias['name']='FM';self.assertTrue(self.commit([alias]));self.assertEqual(len(K.concepts()),1)
        self.assertEqual(K.create('FM')['id'],v['id'])
    def test_ambiguous_alias_rolls_back_all_changes(self):
        for name in ('First sense','Second sense'):
            v=K.create(name);v['aliases']=['FM'];K.put(v)
        alias=copy.deepcopy(self.item);alias['name']='FM'
        with self.assertRaises(ValueError):self.commit([self.item,alias])
        self.assertEqual(len(K.concepts()),2)
        with R.db() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM concept_evidence').fetchone()[0],0)
        self.assertEqual(P.load(self.pid)['status'],'queued')
    def test_idempotent_commit_and_personal_state_preserved(self):
        v=K.create('Flow Matching');v.update(notes='Personal proof',markdown='Existing notebook',study_progress={'answers':{'personal':{'answer':'My answer','understood':True}}});K.put(v)
        self.commit();first=K.get(v['id']);self.commit();second=K.get(v['id'])
        for field in ('notes','markdown','study_progress'):self.assertEqual(second[field],v[field])
        self.assertEqual(first['study_guide'],second['study_guide']);self.assertEqual(second['papers'],[self.pid]);self.assertEqual(second['pipeline_papers'],[self.pid])
        with R.db() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM concept_evidence').fetchone()[0],1)
    def test_stale_report_and_token_cannot_commit(self):
        self.assertFalse(P.commit(self.pid,self.rid,'obsolete', [self.item]));self.paper['reports'].append({'id':'new-report'});R.save(self.paper)
        self.assertFalse(self.commit());self.assertEqual(K.concepts(),[])
    def test_deactivation_preserves_notes_and_manual_links(self):
        self.commit();v=K.concepts()[0];K.edit({'id':v['id'],'notes':'Keep forever'})
        self.queue('report-two','token-two');self.commit([])
        self.assertEqual(K.get(v['id'])['papers'],[]);self.assertEqual(K.get(v['id'])['notes'],'Keep forever')
        with R.db() as c:self.assertEqual(c.execute('SELECT active FROM concept_evidence').fetchone()[0],0)
        self.commit();K.create('Flow Matching',self.pid);self.commit([])
        self.assertEqual(K.get(v['id'])['papers'],[self.pid])
    def test_existing_manual_link_is_never_marked_pipeline_owned(self):
        v=K.create('Flow Matching',self.pid);self.commit();self.commit([])
        self.assertEqual(K.get(v['id'])['papers'],[self.pid]);self.assertNotIn(self.pid,K.get(v['id']).get('pipeline_papers',[]))
    def test_worker_cancel_keeps_existing_notebook(self):
        v=K.create('Flow Matching');K.edit({'id':v['id'],'notes':'Preserved'})
        with patch.object(R,'cli',side_effect=InterruptedError()):P.worker(self.pid,self.rid,self.token)
        self.assertEqual(P.load(self.pid)['status'],'cancelled');self.assertEqual(P.load(self.pid)['error'],'')
        self.assertEqual(K.get(v['id'])['notes'],'Preserved');self.assertEqual(K.get(v['id'])['papers'],[])
        self.assertTrue(any(j.get('kind')=='concepts' and j['status']=='cancelled' for j in R.JOBS.values()))
    def test_worker_cancel_after_cli_prevents_commit(self):
        def response(jid,*args,**kwargs):R.JOBS[jid]['cancel']=True;return json.dumps({'concepts':[self.item]})
        with patch.object(R,'cli',side_effect=response):P.worker(self.pid,self.rid,self.token)
        self.assertEqual(P.load(self.pid)['status'],'cancelled');self.assertEqual(K.concepts(),[])
    def test_failed_second_item_rolls_back_existing_notebook_changes(self):
        v=K.create('Flow Matching');K.edit({'id':v['id'],'notes':'Original'})
        for name in ('Other sense one','Other sense two'):
            other=K.create(name);other['aliases']=['ambiguous'];K.put(other)
        before=K.get(v['id']);bad=copy.deepcopy(self.item);bad['name']='ambiguous'
        with self.assertRaises(ValueError):self.commit([self.item,bad])
        self.assertEqual(K.get(v['id']),before)
        with R.db() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM concept_evidence').fetchone()[0],0)
    def test_start_same_report_is_deduplicated(self):
        with patch.object(P.threading,'Thread') as thread:
            P.start(self.pid);self.assertEqual(thread.call_count,0)
        self.commit()
        with patch.object(P.threading,'Thread') as thread:
            P.start(self.pid);self.assertEqual(thread.call_count,0)
            P.start(self.pid,retry=True);self.assertEqual(thread.call_count,1)
    def test_source_uses_completed_report_not_running_analysis(self):
        running=R.DATA/'runs'/self.paper['last_run'];running.mkdir(parents=True)
        (running/'paper.txt').write_text('Unfinished different source '*100)
        _,rid,text=P.source(self.pid)
        self.assertEqual(rid,self.rid);self.assertEqual(text,self.text*30)
    def test_connections_require_existing_id_typed_relation_and_source(self):
        v=K.create('Existing topic')
        link={'concept_id':v['id'],'type':'contrasts','reason':'Different representation','evidence':self.item['evidence']}
        self.assertEqual(P.connections({'connections':[link]},self.paper,self.text),[link])
        for mutation in ({'concept_id':'missing'},{'type':'adopts'},{'type':'citation'},{'reason':''},{'evidence':[{'quote':'This invented quote does not appear in this source document.','url':self.paper['url']}]},{'evidence':[{'quote':self.item['evidence'][0]['quote'],'url':'https://example.com/other'}]}):
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):P.connections({'connections':[{**link,**mutation}]},self.paper,self.text)
    def test_related_backlink_preserves_existing_notebook_and_typed_graph(self):
        import workspace_links
        v=K.create('Other representation','2');v.update(notes='Keep [[paper:2|prior paper]]',markdown='Existing derivation',study_progress={'answers':{'mine':{'answer':'Personal'}}});K.put(v)
        link={'concept_id':v['id'],'type':'contrasts','reason':'Representation differs','evidence':self.item['evidence']}
        self.assertTrue(P.commit(self.pid,self.rid,self.token,[self.item],[link]))
        after=K.get(v['id'])
        for field in ('notes','markdown','study_progress'):self.assertEqual(after[field],v[field])
        self.assertEqual(after['papers'],['2',self.pid]);self.assertEqual(after['paper_connections'][self.pid]['type'],'contrasts')
        graph=P.result(self.pid);self.assertEqual(len(graph['concepts']),1);self.assertEqual(graph['related_concepts'][0]['id'],v['id'])
        self.assertTrue(any(e['type']=='contrasts' and e['target']=='concept:'+v['id'] for e in graph['edges']))
        backlinks=workspace_links.links('concept',v['id']);self.assertEqual({e['node']['id'] for e in backlinks['associations']},{'2',self.pid})
        self.commit();after=K.get(v['id']);self.assertEqual(after['papers'],['2']);self.assertFalse(after['paper_connections'][self.pid]['active']);self.assertEqual(after['notes'],v['notes'])
    def test_superseded_token_worker_does_not_leave_running_job(self):
        self.queue(token='replacement-token')
        before=set(R.JOBS)
        with patch.object(R,'cli') as cli:P.worker(self.pid,self.rid,'token-one')
        self.assertFalse(cli.called);self.assertEqual(set(R.JOBS),before)
        self.assertEqual(P.load(self.pid)['token'],'replacement-token')
    def test_nearby_graph_uses_other_paper_evidence_or_explicit_unknown(self):
        v=K.create('Flow Matching','2');self.commit()
        def edge():return next(e for e in P.result(self.pid)['edges'] if e['source']=='paper:2')
        self.assertEqual(edge()['evidence_url'],'');self.assertEqual(edge()['evidence_basis'],'library-membership')
        v=K.get(v['id']);v.setdefault('paper_connections',{})['2']={'active':True,'evidence':[{'url':'https://example.com/other-paper'}]};K.put(v)
        self.assertEqual(edge()['evidence_url'],'https://example.com/other-paper');self.assertEqual(edge()['evidence_basis'],'source-quote')
        v['paper_connections']['2']['active']=False;K.put(v)
        self.assertEqual(edge()['evidence_url'],'')
    def test_first_paper_source_only_pipeline_without_report(self):
        self.paper.update(reports=[],last_run=self.rid);R.save(self.paper)
        _,rid,text=P.source(self.pid);self.assertEqual(rid,self.rid);self.assertEqual(text,self.text*30)
        with patch.object(R,'cli',return_value=json.dumps({'concepts':[self.item]})) as cli:P.worker(self.pid,self.rid,self.token)
        self.assertEqual(P.load(self.pid)['status'],'ready');self.assertEqual(len(K.concepts()),1)
        self.assertTrue(cli.called)
    def test_explicit_new_source_does_not_mix_old_report(self):
        run=R.DATA/'runs'/'new-source';run.mkdir();(run/'paper.txt').write_text(self.text*30)
        self.paper.update(last_run='new-source',reports=[{'id':self.rid,'method':'OLD_REPORT_SENTINEL'}]);R.save(self.paper)
        self.assertEqual(P.source(self.pid)[1],self.rid);self.assertEqual(P.source(self.pid,'new-source')[1],'new-source')
        with self.assertRaises(ValueError):P.source(self.pid,'unrelated-source')
        with R.db() as c:P.write(c,{'paper_id':self.pid,'report_id':'new-source','token':self.token,'status':'queued'})
        with patch.object(R,'cli',return_value=json.dumps({'concepts':[self.item]})) as cli:P.worker(self.pid,'new-source',self.token)
        self.assertNotIn('OLD_REPORT_SENTINEL',cli.call_args.args[1]);self.assertEqual(P.load(self.pid)['status'],'ready')
