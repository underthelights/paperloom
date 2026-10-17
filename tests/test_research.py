import json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import research

class ResearchTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.old=(research.DATA,research.DB,research.SKILLS,research.ROOT)
        research.DATA=Path(self.temp.name);research.ROOT=research.DATA;research.DB=research.DATA/'research.sqlite3'
        research.SKILLS=research.DATA/'skills';research.SKILLS.mkdir()
        (research.SKILLS/'notion-candidates.json').write_text(json.dumps({'rows':[]}))
        (research.SKILLS/'PROVENANCE.json').write_text('{}');research.init()
    def tearDown(self):
        research.DATA,research.DB,research.SKILLS,research.ROOT=self.old;self.temp.cleanup()
    def test_metadata_import_drops_body_patents_and_duplicate_titles(self):
        r=research.import_candidates([{'Title':'A paper','text':'stale body','notes':'private'}, {'Title':'**A paper**'}, {'Title':'Patent','Accepted':'US Patent'},{'Title':''}])
        self.assertEqual((r['added'],r['duplicates'],r['patents'],r['untitled']),(1,1,1,1))
        p=research.all_records()[0];self.assertNotIn('text',p);self.assertEqual(p['notes'],'');self.assertEqual(p['status'],'candidate')
    def test_resolving_candidate_keeps_notes_and_reuses_record(self):
        research.import_candidates([{'Title':'A paper'}]);p=research.all_records()[0];p['notes']='my idea';research.save(p)
        with patch.object(research,'metadata',return_value={'title':'A paper','arxiv':'2303.04137v4','url':'https://arxiv.org/abs/2303.04137v4','authors':[]}):
            new=research.add('2303.04137v4');self.assertEqual(new['id'],p['id']);self.assertEqual(new['notes'],'my idea')
            again=research.add('2303.04137');self.assertEqual(again['id'],p['id']);self.assertEqual(len(research.all_records()),1)
    def test_review_failure_preserves_unverified_draft_status(self):
        with patch.object(research,'cli',side_effect=ValueError('timeout')):
            result=research.review_draft('job',research.DATA)
        self.assertEqual(result['verdict'],'needs_review')
        self.assertFalse(result['completed'])
        self.assertEqual(result['corrections'],[])
        with patch.object(research,'cli',return_value='{"verdict":"pass","issues":[],"corrections":[null]}'):
            self.assertEqual(research.review_draft('job',research.DATA)['verdict'],'needs_review')
        with patch.object(research,'cli',side_effect=InterruptedError()):
            with self.assertRaises(InterruptedError):research.review_draft('job',research.DATA)

    def test_candidate_cannot_run_analysis(self):
        research.import_candidates([{'Title':'Unknown'}]);p=research.all_records()[0]
        with self.assertRaisesRegex(ValueError,'원문'): research.start(p['id'])
    def test_private_sources_rejected(self):
        for url in ['http://example.com','https://localhost/a','https://127.0.0.1/a','https://user:pass@example.com','https://example.com:8765/a']:
            with self.assertRaises(ValueError): research.public_url(url)
    def test_mcp_metadata_whitelist(self):
        init=research.mcp({'jsonrpc':'2.0','id':1,'method':'initialize','params':{}})
        self.assertEqual(init['result']['serverInfo']['name'],'paperloom-research')
        response=research.mcp({'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'import_notion_metadata','arguments':{'rows':[{'Title':'MCP input','summary':'old summary'}]}}})
        self.assertEqual(json.loads(response['result']['content'][0]['text'])['added'],1)
        self.assertNotIn('summary',research.all_records()[0])
    def test_unproven_repo_does_not_clone(self):
        with patch.object(research.subprocess,'run') as run:
            result=research.clone_repo('unused',{'code':{'url':'https://github.com/a/b','evidence_url':'https://unrelated.example.com'},'project_urls':[]},research.DATA)
            self.assertEqual(result['status'],'unverified');run.assert_not_called()
    def test_chat_save_does_not_overwrite_concurrent_report_or_notes(self):
        research.import_candidates([{'Title':'Chat record'}]);p=research.all_records()[0];old=research.CHAT.get_paper(p['id'])
        p['notes']='new note';p['reports']=[{'tldr':'fresh'}];research.save(p);old['chat']=[{'role':'user','content':'question'}];research.CHAT.save(old)
        final=research.get(p['id']);self.assertEqual(final['notes'],'new note');self.assertEqual(final['reports'][0]['tldr'],'fresh');self.assertEqual(len(final['chat']),1)

    def test_cancelled_research_does_not_publish_report(self):
        research.import_candidates([{'Title':'Cancel fixture'}]);p=research.all_records()[0];p['arxiv']='2303.04137';research.save(p)
        jid='cancel-fixture';research.JOBS[jid]={'id':jid,'paper_id':p['id'],'cancel':True,'status':'cancelled','log':[]}
        with patch.object(research,'collect') as collect:
            research.run_analysis(jid,p['id']);collect.assert_not_called()
        self.assertEqual(research.get(p['id'])['reports'],[])
        research.JOBS.pop(jid)

    def test_analysis_review_preserves_concurrent_user_note(self):
        research.import_candidates([{'Title':'Pipeline fixture'}]);p=research.all_records()[0];p.update(arxiv='2303.04137',url='https://arxiv.org/abs/2303.04137');research.save(p)
        jid='pipeline-fixture';research.JOBS[jid]={'id':jid,'paper_id':p['id'],'cancel':False,'status':'queued','log':[]}
        report={k:'source-supported fixture' for k in ['tldr','eli5','overview','method','experiments','code','labs','limitations']};report.update(sources=[],checks=[])
        responses=[json.dumps({'code':{'url':'','reason':'unavailable'}}),json.dumps(report),json.dumps({'verdict':'needs_review','issues':['lab unavailable'],'corrections':[]})]
        def agent(*args,**kwargs):
            current=research.get(p['id']);current['notes']='written while analyzing';research.save(current)
            return responses.pop(0)
        with patch.object(research,'collect',return_value=('paper content',[],[])),patch.object(research,'cli',side_effect=agent):
            research.run_analysis(jid,p['id'])
        final=research.get(p['id']);self.assertEqual(final['notes'],'written while analyzing');self.assertEqual(final['status'],'review');self.assertEqual(len(final['reports']),1);self.assertEqual(research.JOBS[jid]['status'],'done')
        research.JOBS.pop(jid)



    def test_public_install_without_personal_seed(self):
        (research.SKILLS/'notion-candidates.json').unlink()
        with research.db() as c:c.execute("DELETE FROM meta WHERE key='seed'")
        research.init()
        self.assertEqual(research.all_records(),[])
