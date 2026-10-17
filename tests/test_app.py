import base64,io,json,os,sys,tempfile,unittest,zipfile,threading
from pathlib import Path
from unittest.mock import patch
from urllib.request import Request,urlopen
from urllib.error import HTTPError
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import app,integrations
class LibraryTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=(app.DATA,app.DB)
  app.DATA=Path(self.tmp.name);app.DB=app.DATA/'library.sqlite3';(app.DATA/'pdfs').mkdir();app.init()
 def tearDown(self):app.DATA,app.DB=self.old;self.tmp.cleanup()
 def test_reimport_preserves_notes_and_reading(self):
  item={'title':'Diffusion Policy','DOI':'10.1/test','abstractNote':'Robot imitation learning with diffusion','tags':[{'tag':'Robotics'}]}
  app.import_items([item]);p=app.all_papers()[0];p.update(notes='내 생각',status='reading');app.save(p)
  app.import_items([item]);q=app.all_papers()[0]
  self.assertEqual(len(app.all_papers()),1);self.assertEqual(q['notes'],'내 생각');self.assertEqual(q['status'],'reading');self.assertIn('Diffusion',q['tags'])
 def test_notion_same_title_is_distinct(self):
  app.upsert({'title':'same'},'notion:a');app.upsert({'title':'same'},'notion:b');self.assertEqual(len(app.all_papers()),2)
 def test_backup_restore_preserves_concept_note_and_no_overwrite(self):
  p=app.upsert({'title':'robot learning','notes':'original','tags':['Robot Learning']})
  with app.connect() as c:c.execute("UPDATE concepts SET note='concept note',updated=123 WHERE name='Robot Learning'")
  blob=app.backup()
  with app.connect() as c:c.execute('DELETE FROM papers');c.execute('DELETE FROM concepts')
  self.assertEqual(app.restore(blob),1)
  with app.connect() as c:self.assertEqual(c.execute('SELECT note FROM concepts').fetchone()['note'],'concept note')
  q=app.get_paper(p['id']);q['notes']='changed';app.save(q);self.assertEqual(app.restore(blob),0);self.assertEqual(app.get_paper(p['id'])['notes'],'changed')
 def test_restore_rejects_path_traversal_before_write(self):
  p=app.upsert({'title':'safe'});p['pdf']='../../evil.pdf';stream=io.BytesIO()
  with zipfile.ZipFile(stream,'w') as z:z.writestr('library.json',json.dumps({'version':1,'papers':[p]}))
  with self.assertRaises(ValueError):app.restore(stream.getvalue())
  self.assertEqual(len(app.all_papers()),1)
 def test_zotero_pagination_and_repeat(self):
  batch=[{'key':str(n),'data':{'key':str(n),'itemType':'journalArticle','title':f'Paper {n}'}} for n in range(100)]
  with patch.object(app,'fetch',side_effect=[json.dumps(batch).encode(),b'[]']):self.assertEqual(app.sync_zotero(),100)
  with patch.object(app,'fetch',side_effect=[json.dumps(batch).encode(),b'[]']):app.sync_zotero()
  self.assertEqual(len(app.all_papers()),100)
 def test_arxiv_parser(self):
  atom=b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>http://arxiv.org/abs/2303.04137</id><title>Diffusion Policy</title><summary>Robot learning</summary><author><name>A</name></author><published>2023-03-07</published></entry></feed>'
  with patch.object(app,'fetch',return_value=atom):p=app.arxiv('https://arxiv.org/abs/2303.04137')
  self.assertEqual(p['year'],'2023');self.assertIn('Robot Learning',p['tags'])
 def test_cloud_requires_valid_project(self):
  with self.assertRaises(ValueError):integrations.cloud_sync('test',app)
 def test_http_origin_pdf_notes_and_persistence(self):
  server=app.ThreadingHTTPServer(('127.0.0.1',0),app.Handler);oldport=app.PORT;app.PORT=server.server_port
  threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{app.PORT}'
  def post(path,body,origin=None):
   req=Request(base+path,data=json.dumps(body).encode(),headers={'Content-Type':'application/json',**({'Origin':origin} if origin else {})});return json.loads(urlopen(req).read())
  try:
   with self.assertRaises(HTTPError) as e:post('/api/papers',{'title':'bad'},'https://evil.example')
   self.assertEqual(e.exception.code,403)
   p=post('/api/papers',{'title':'test','abstract':'test abstract'});post('/api/update',{'id':p['id'],'notes':'saved','status':'done'})
   from pypdf import PdfWriter
   writer=PdfWriter();writer.add_blank_page(width=100,height=100);pdf=io.BytesIO();writer.write(pdf)
   q=post('/api/pdf',{'id':p['id'],'name':'test.pdf','data':base64.b64encode(pdf.getvalue()).decode()})
   self.assertTrue((app.DATA/'pdfs'/q['pdf']).exists());self.assertEqual(q['notes'],'saved')
   r=urlopen(base+'/pdfs/'+q['pdf']);self.assertEqual(r.headers['Content-Type'],'application/pdf')
   post('/api/notes-import',{'name':'test.md','data':base64.b64encode('# My note\n내용'.encode()).decode()})
   self.assertEqual(len(app.all_papers()),2)
  finally:server.shutdown();server.server_close();app.PORT=oldport
if __name__=='__main__':unittest.main(verbosity=2)
