import unittest
from bs4 import BeautifulSoup
import research

class BibliographyTests(unittest.TestCase):
    def test_block_title_excludes_authors_and_venue(self):
        soup=BeautifulSoup('<li class="ltx_bibitem" id="bib1"><span class="ltx_bibblock">A. Author.</span><span class="ltx_bibblock">A Robot Policy.</span><span class="ltx_bibblock">Venue 2026.</span></li>','html.parser')
        ref=research.bibliography(soup,'2602.15922')[0]
        self.assertEqual(ref['title'],'A Robot Policy');self.assertIn('A. Author.',ref['citation']);self.assertTrue(ref['source'].endswith('#bib1'))
    def test_explicit_title_wins(self):
        soup=BeautifulSoup('<li class="ltx_bibitem"><span class="ltx_bib_title">Correct.</span><span class="ltx_bibblock">Author.</span><span class="ltx_bibblock">Other.</span></li>','html.parser')
        self.assertEqual(research.bibliography(soup,'x')[0]['title'],'Correct')
