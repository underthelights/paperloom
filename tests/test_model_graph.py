import unittest
import research as R

class ModelGraphTests(unittest.TestCase):
    def test_relation_types_require_known_primary_evidence_and_valid_endpoints(self):
        source='https://example.org/paper'
        nodes=[{'id':'a','label':'A','paper_url':'javascript:alert(1)'},{'id':'b','label':'B'}]
        edge={'source':'a','target':'b','kind':'adopted','reason':'Explicit backbone','evidence':[{'url':source}]}
        graph=R.normalize_model_graph({'nodes':nodes,'edges':[edge,{**edge,'target':'missing'},{**edge,'kind':'citation'},{**edge,'evidence':[{'url':'https://unread.org'}]}]},[{'url':source}])
        self.assertEqual(len(graph['edges']),1)
        self.assertEqual(graph['edges'][0]['kind'],'adopted')
        self.assertEqual(graph['nodes'][0]['paper_url'],'')
        self.assertEqual(graph['center'],'a')
    def test_malformed_graph_and_unknown_evidence_are_not_promoted(self):
        for v in (None,[],{'nodes':{},'edges':{}},{'nodes':[None],'edges':[None]}):
            self.assertEqual(R.normalize_model_graph(v,[])['edges'],[])
