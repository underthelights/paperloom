import unittest
import research as R


class WalkthroughTests(unittest.TestCase):
    source = 'https://github.com/example/model/blob/abc/model.py#L10-L15'

    def step(self, **changes):
        return {'id':'layout','title':'Layout','explanation':'B=batch; T=frames; C=channels',
                'operation':'permute(0,4,1,2,3)','input_shape':'[B,T,H,W,C]',
                'output_shape':'[B,C,T,H,W]','equation':'','mode':'shared',
                'verification':'source','evidence':[{'url':self.source,'label':'model.py'}],
                'concepts':['Video Latents'],'mechanics':[],**changes}

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

    def mechanic(self, **changes):
        return {'title':'Contraction','explanation':'Sum the Din axis',
                'input_shape':'A:[B,N,Din], W:[Din,Dout]','output_shape':'[B,N,Dout]',
                'equation':'Y[b,n,j] = sum_k A[b,n,k] W[k,j]',
                'assumptions':'Real-valued matrix multiplication','basis':'mathematical',
                'evidence':[],**changes}

    def test_mathematical_mechanics_need_no_source_but_code_does(self):
        math=self.mechanic()
        code=self.mechanic(basis='code')
        cited=self.mechanic(basis='code',evidence=[{'url':self.source,'label':'code'}])
        steps=self.normalize([self.step(mechanics=[math,code,cited])])['steps'][0]['mechanics']
        self.assertEqual(steps[0],math)
        self.assertEqual(steps[1]['basis'],'unknown')
        self.assertEqual(steps[2],cited)
        self.assertEqual(steps[0]['assumptions'],'Real-valued matrix multiplication')

    def test_mechanics_payloads_and_untrusted_sources_are_safe(self):
        for invalid in (None,[],{},True,42):
            step=self.normalize([self.step(mechanics=invalid)])['steps'][0]
            self.assertEqual(step['mechanics'],[])
            for field in ('basis','input_shape','output_shape','equation','assumptions','evidence'):
                mechanics=self.normalize([self.step(mechanics=[self.mechanic(**{field:invalid})])])['steps'][0]['mechanics']
                self.assertEqual(len(mechanics),1)
                if field in ('input_shape','output_shape'):
                    self.assertEqual(mechanics[0][field],'확인 불가')
                    self.assertEqual(mechanics[0]['basis'],'unknown')
        item=self.mechanic(basis='code',evidence=[{'url':'https://unread.org'}])
        self.assertEqual(self.normalize([self.step(mechanics=[item])])['steps'][0]['mechanics'][0]['basis'],'unknown')

    def test_mechanics_bounds_and_illustration_basis(self):
        item=self.mechanic(title='a\x00b',explanation='e'*7000,basis='illustrative')
        mechanics=self.normalize([self.step(mechanics=[item]*100)])['steps'][0]['mechanics']
        self.assertEqual(len(mechanics),12)
        self.assertEqual(mechanics[0]['title'],'ab')
        self.assertEqual(len(mechanics[0]['explanation']),6000)
        self.assertEqual(mechanics[0]['basis'],'illustrative')
