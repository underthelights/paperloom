import base64,io,json,unittest
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from pypdf import PdfWriter
from pypdf.generic import NameObject,DecodedStreamObject,DictionaryObject
import test_research as base
import research as R,reader


def pdf_bytes(text='Evidence and method. '*100,encrypted=False):
    writer=PdfWriter();page=writer.add_blank_page(width=612,height=792)
    font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
    page[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):writer._add_object(font)})})
    stream=DecodedStreamObject();stream.set_data(('BT /F1 12 Tf 30 740 Td ('+text+') Tj ET').encode())
    page[NameObject('/Contents')]=writer._add_object(stream)
    writer.add_metadata({'/Title':'Uploaded Research','/Author':'Test Author'})
    if encrypted:writer.encrypt('secret')
    out=io.BytesIO();writer.write(out);return out.getvalue()

class PdfImportTests(unittest.TestCase):
    tearDown=base.ResearchTests.tearDown
    def setUp(self):
        base.ResearchTests.setUp(self);reader.init()
    def upload(self,raw=None,**kwargs):
        return R.add_pdf({'content':base64.b64encode(raw if raw is not None else pdf_bytes()).decode(),'filename':'../../paper.pdf',**kwargs})
    def test_import_collect_and_annotation_without_arxiv_or_network(self):
        with patch.object(R,'fetch',side_effect=AssertionError('Network access')):
            p=self.upload();self.assertEqual(p['title'],'Uploaded Research');self.assertEqual(p['pdf_filename'],'paper.pdf')
            self.assertEqual(R.local_pdf_path(p).read_bytes(),pdf_bytes())
            run=R.DATA/'run';run.mkdir();text,refs,sources=R.collect(p,run)
            self.assertIn('[p.1]',text);self.assertEqual((run/'paper.pdf').read_bytes(),pdf_bytes())
            self.assertEqual(sources[0]['sha256'],p['pdf_sha256'])
            doc=reader.document(p['id']);start=doc['text'].index('Evidence');a=reader.save({'paper_id':p['id'],'version':doc['version'],'start':start,'end':start+8,'exact':'Evidence','note':'keep'})
            self.assertEqual(reader.annotations(p['id'])[0]['id'],a['id'])
            self.assertEqual(reader.document(p['id'])['version'],doc['version'])
            self.assertEqual(doc['format'],'pdf-text')
    def test_duplicates_preserve_notes_and_are_concurrency_safe(self):
        p=self.upload();p['notes']='private note';R.save(p)
        with ThreadPoolExecutor(max_workers=3) as pool:items=list(pool.map(lambda _:self.upload(title='Replacement'),range(3)))
        self.assertEqual({p['id']},{x['id'] for x in items});self.assertEqual(R.get(p['id'])['notes'],'private note')
        self.assertEqual(len(R.all_records()),1)
    def test_invalid_encrypted_and_oversized_do_not_save(self):
        for data in (b'not pdf',b'%PDF-corrupt',pdf_bytes(encrypted=True)):
            with self.assertRaises(Exception):self.upload(data)
        with self.assertRaises(ValueError):R.add_pdf({'content':'!not base64!'})
        with patch.object(R,'PDF_LIMIT',10):
            with self.assertRaises(ValueError):self.upload()
        self.assertEqual(R.all_records(),[])
    def test_scans_remain_readable_but_do_not_start_analysis(self):
        p=self.upload(pdf_bytes(''));self.assertEqual(p['pdf_extraction'],'needs_ocr');self.assertTrue(R.local_pdf_path(p).exists())
        with self.assertRaisesRegex(ValueError,'OCR'):R.start(p['id'])
    def test_pdf_text_is_escaped_in_reader(self):
        p=self.upload(pdf_bytes('<script>alert 1</script> & evidence'))
        doc=reader.document(p['id']);self.assertNotIn('<script>',doc['html']);self.assertIn('&lt;script&gt;',doc['html'])
    def test_analysis_pipeline_accepts_local_pdf(self):
        p=self.upload();jid='f'*32
        R.JOBS[jid]={'id':jid,'paper_id':p['id'],'status':'queued','stage':'queued','created':R.now(),'log':[],'cancel':False,'error':''}
        sections={k:'Evidence from uploaded PDF, p.1' for k in ('tldr','eli5','overview','method','experiments','code','labs','limitations','related_work','tensor_trace')}
        sections.update(sources=[],checks=[],model_graph={})
        def cli(jid,prompt,run,name,**kw):
            if name=='discovery':return json.dumps({'code':{'url':'','reason':'unverified'},'project_urls':[]})
            if name=='brief':return json.dumps(sections)
            return json.dumps({'verdict':'needs_review','issues':['Static test'],'corrections':[]})
        try:
            with patch.object(R,'cli',side_effect=cli),patch.object(R,'fetch',side_effect=AssertionError('arXiv fetch')):R.run_analysis(jid,p['id'])
            self.assertEqual(R.JOBS[jid]['status'],'done',R.JOBS[jid].get('error'))
            self.assertEqual(len(R.get(p['id'])['reports']),1)
        finally:R.JOBS.pop(jid,None)
