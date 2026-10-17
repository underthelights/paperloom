import unittest
from unittest.mock import patch
import test_research as base
import discovery,research

class DiscoveryTests(unittest.TestCase):
    tearDown=base.ResearchTests.tearDown
    def setUp(self):base.ResearchTests.setUp(self)
    def work(self,i,refs):return dict(id=i,title=i,year=2024,authors=[],citations=3,doi=None,url='https://openalex.org/'+i,arxiv=None,abstract='',references=refs,related=[],source='https://openalex.org/'+i)
    def test_coupling_cocitation_and_direction(self):
        a=self.work('W1',['W3','W4']);b=self.work('W2',['W3','W4']);c=self.work('W3',[]);d=self.work('W5',['W1','W2'])
        g=discovery.assemble(a,[b,c],[d],[]);edge=next(e for e in g['edges'] if e['source']=='W1' and e['target']=='W2')
        self.assertEqual(edge['coupling'],1);self.assertEqual(edge['cocitation'],1);self.assertEqual(edge['score'],1);self.assertEqual(edge['citations'],[])
        direct=next(e for e in g['edges'] if e['source']=='W1' and e['target']=='W3');self.assertEqual(direct['citations'],[{'from':'W1','to':'W3'}]);self.assertEqual(next(n for n in g['nodes'] if n['id']=='W5')['role'],'derivative')
    def test_import_deduplicates_and_preserves_notes(self):
        w=self.work('W1',[]);g=discovery.assemble(w,[],[],[])
        with patch.object(discovery,'graph',return_value=g):
            p=discovery.import_work('W1','W1');p['notes']='personal';research.save(p);again=discovery.import_work('W1','W1');self.assertEqual(p['id'],again['id']);self.assertEqual(again['notes'],'personal')
    def test_external_id_validation(self):
        for value in ['../private','https://evil.invalid/x','W1?api_key=x']:
            with self.assertRaises(ValueError):discovery.wid(value)
    def test_empty_references_are_not_similarity(self):
        g=discovery.assemble(self.work('W1',[]),[self.work('W2',[])],[],[]);self.assertEqual(g['edges'],[])
    def test_unindexed_citations_use_original_with_provenance(self):
        seed=self.work('W1',[]);seed['title']='Local paper'
        research.save({'id':'local','identity':'local','title':'Local paper','references':[{'title':'Robot Policy','citation':'Robot Policy (2024)','source':'https://arxiv.org/html/1#ref'}]})
        target=self.work('W2',[]);target['title']='Robot Policy'
        with patch.object(discovery,'search',return_value=[target]):works,notices=discovery.original_references(seed)
        self.assertEqual(seed['references'],['W2']);self.assertEqual(seed['reference_matches'][0]['match'],'title-and-year')
        graph=discovery.assemble(seed,works,[],notices);self.assertEqual(graph['edges'][0]['citation_basis'],'original-bibliography-title-match')
