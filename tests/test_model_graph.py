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

    def test_untrusted_field_types_preserve_valid_relations(self):
        source='https://example.org/paper'
        nodes=[{'id':'a','label':'A'},{'id':'b','label':'B'}]
        edge={'source':'a','target':'b','kind':'adopted','reason':'Backbone','evidence':[{'url':source}]}
        for invalid in ([],{},None,42,True):
            for field in ('source','target','reason'):
                with self.subTest(field=field,invalid=invalid):
                    graph=R.normalize_model_graph({'center':invalid,'nodes':nodes,'edges':[{**edge,field:invalid},edge]},[{'url':source}])
                    self.assertEqual(len(graph['edges']),1)
                    self.assertEqual(graph['center'],'a')
            graph=R.normalize_model_graph({'nodes':nodes,'edges':[{**edge,'evidence':[{'url':invalid},{'url':source}]}]},[{'url':source}])
            self.assertEqual(graph['edges'][0]['evidence'],[{'url':source,'label':'근거'}])

    def test_malformed_node_ids_and_source_manifests_do_not_create_evidence(self):
        for invalid in ([],{},None,42,True,'','a'*101):
            graph=R.normalize_model_graph({'nodes':[{'id':invalid,'label':'Invalid'},{'id':'b','label':'B'}]},None)
            self.assertEqual([n['id'] for n in graph['nodes']],['b'])
        edge={'source':'a','target':'b','kind':'related','reason':'Comparison','evidence':[{'url':'https://example.org'}]}
        for sources in (None,{},'https://example.org'):
            graph=R.normalize_model_graph({'nodes':[{'id':'a','label':'A'},{'id':'b','label':'B'}],'edges':[edge]},sources)
            self.assertEqual(graph['edges'],[])
