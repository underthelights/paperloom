import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import research as R
import workspace_links as W


class WorkspaceLinksTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.old=R.DB;R.DB=Path(self.temp.name)/'test.sqlite3'
        with R.db() as c:
            c.executescript('CREATE TABLE records(id TEXT PRIMARY KEY, identity TEXT, body TEXT); CREATE TABLE knowledge(id TEXT PRIMARY KEY,kind TEXT,body TEXT);')
        self.add('paper','p','Paper','[[Concept|read this]] [[concept:c|stable]] [[Missing]]')
        self.add('concept','c','Concept','Back to [[paper:p|paper]].',papers=['p'])

    def tearDown(self):
        R.DB=self.old;self.temp.cleanup()

    def add(self,kind,ident,title,notes,**extra):
        body={'id':ident,'title':title,'name':title,'notes':notes,**extra}
        with R.db() as c:
            c.execute('INSERT OR REPLACE INTO '+('records' if kind=='paper' else 'knowledge')+' VALUES(?,?,?)',(ident,ident if kind=='paper' else kind,json.dumps(body)))

    def test_aliases_backlinks_and_associations_are_distinct(self):
        result=W.links('paper','p')
        self.assertEqual([x['status'] for x in result['outgoing']],['resolved','resolved','unresolved'])
        self.assertEqual(result['outgoing'][0]['label'],'read this')
        self.assertEqual(result['outgoing'][0]['node']['id'],'c')
        self.assertEqual(result['incoming'][0]['node']['id'],'c')
        self.assertEqual(result['associations'],[{'type':'paper-concept','node':{'kind':'concept','id':'c','title':'Concept'}}])
        self.assertIn('[[Concept|read this]]',result['outgoing'][0]['snippet'])
        self.assertFalse(result['truncated'])

    def test_ambiguous_names_do_not_choose_or_create_a_node(self):
        self.add('paper','other','Concept','')
        before=R.DB.read_bytes()
        result=W.links('paper','p')
        self.assertEqual(result['outgoing'][0]['status'],'ambiguous')
        self.assertEqual(len(result['outgoing'][0]['candidates']),2)
        self.assertIsNone(result['outgoing'][0]['node'])
        self.assertEqual(result['outgoing'][1]['node']['id'],'c')
        self.assertEqual(R.DB.read_bytes(),before)

    def test_code_escaped_links_and_generated_reports_are_not_indexed(self):
        self.add('paper','p','Paper','`[[Concept]]`\n```python\n[[Concept]]\n```\n\\[[Concept]]\n[[Concept]]',reports=[{'tldr':'[[Concept]]'}])
        self.add('concept','c','Concept','',markdown='[[paper:p]]')
        result=W.links('paper','p')
        self.assertEqual(len(result['outgoing']),1)
        self.assertEqual(result['incoming'],[])

    def test_normalized_names_and_stable_ids_survive_rename(self):
        self.add('paper','p','Paper','[[  CONCEPT  ]] [[concept:c|old title]]')
        self.assertEqual(W.links('paper','p')['outgoing'][0]['status'],'resolved')
        self.add('concept','c','Renamed','')
        self.assertEqual([x['status'] for x in W.links('paper','p')['outgoing']],['unresolved','resolved'])

    def test_limits_report_incompleteness_without_deleting_notes(self):
        note='[[Concept]] '*10
        self.add('paper','p','Paper',note)
        with patch.object(W,'MAX_LINKS',2):
            result=W.links('paper','p')
            self.assertEqual(len(result['outgoing']),2)
            self.assertTrue(result['truncated'])
        with patch.object(W,'MAX_TEXT',12):
            self.assertTrue(W.links('paper','p')['truncated'])
        with R.db() as c:
            self.assertEqual(json.loads(c.execute('SELECT body FROM records WHERE id="p"').fetchone()[0])['notes'],note)

    def test_invalid_and_missing_selection(self):
        for kind,ident in [('other','p'),('paper',None),('paper','missing'),('concept',[])]:
            with self.assertRaises(ValueError):W.links(kind,ident)
