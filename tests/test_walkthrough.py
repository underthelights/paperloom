import unittest
import research as R


class WalkthroughTests(unittest.TestCase):
    source = 'https://github.com/example/model/blob/abc/model.py#L10-L15'

    def step(self, **changes):
        return {'id':'layout','title':'Layout','explanation':'B=batch; T=frames; C=channels',
                'operation':'permute(0,4,1,2,3)','input_shape':'[B,T,H,W,C]',
                'output_shape':'[B,C,T,H,W]','equation':'','mode':'shared',
                'verification':'source','evidence':[{'url':self.source,'label':'model.py'}],
                'concepts':['Video Latents'],**changes}

    def normalize(self, steps, sources=None):
        return R.normalize_walkthrough({'title':'Trace','scope':'Static code inspection','steps':steps},
                                      [{'url':self.source}] if sources is None else sources)

    def test_valid_source_trace_preserves_shapes_and_concepts(self):
        step=self.step()
        self.assertEqual(self.normalize([step])['steps'],[step])

    def test_legacy_or_malformed_payload_is_empty(self):
        for value in (None,[],42,True,'trace',{'steps':{}},{'steps':[None,[],42,{}]}):
            self.assertEqual(R.normalize_walkthrough(value,None)['steps'],[])

    def test_missing_or_unread_evidence_is_unknown(self):
        for sources in ([],{},'url',42):
            step=self.normalize([self.step()],sources)['steps'][0]
            self.assertEqual(step['verification'],'unknown')
            self.assertEqual(step['evidence'],[])
        for link in ('javascript:alert(1)','http://example.org','https://unread.org',
                     'https://name:secret@example.org','https://example.org/\nfoo'):
            step=self.normalize([self.step(evidence=[{'url':link}])],[{'url':link}])['steps'][0]
            if link == 'https://unread.org':
                step=self.normalize([self.step(evidence=[{'url':link}])])['steps'][0]
            self.assertEqual(step['verification'],'unknown')

    def test_invalid_types_do_not_crash_or_invent_shapes(self):
        for invalid in (None,{},[],True,42):
            for field in ('id','operation','input_shape','output_shape','equation','mode','verification','evidence','concepts'):
                step=self.normalize([self.step(**{field:invalid})])['steps'][0]
                if field in ('input_shape','output_shape'):
                    self.assertEqual(step[field],'확인 불가')
                    self.assertEqual(step['verification'],'unknown')
            self.assertEqual(self.normalize([self.step(title=invalid)])['steps'],[])
            self.assertEqual(self.normalize([self.step(explanation=invalid)])['steps'],[])
            step=self.normalize([self.step(evidence=[{'url':invalid},{'url':self.source,'label':invalid}])])['steps'][0]
            self.assertEqual(step['evidence'],[{'url':self.source,'label':'근거'}])

    def test_bounds_unique_ids_and_plain_fields(self):
        steps=self.normalize([self.step(id='same',explanation='x'*7000,
            concepts=['A','A',{},'B']+['C']*20,evidence=[{'url':self.source}]*50)]*100)['steps']
        self.assertEqual(len(steps),40)
        self.assertEqual(len({s['id'] for s in steps}),40)
        self.assertEqual(len(steps[0]['explanation']),6000)
        self.assertEqual(steps[0]['concepts'],['A','B','C'])
        self.assertEqual(len(steps[0]['evidence']),1)
        self.assertEqual(self.normalize([self.step(title='a\x00b')])['steps'][0]['title'],'ab')

    def test_illustration_never_promoted_by_citation(self):
        step=self.normalize([self.step(verification='illustrative')])['steps'][0]
        self.assertEqual(step['verification'],'illustrative')
