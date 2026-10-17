import json, unittest
from unittest.mock import patch
from test_research import ResearchTests
import intake, research, reader
import paperloom_workflow as workflow

class IntakeTests(unittest.TestCase):
    tearDown=ResearchTests.tearDown
    def setUp(self):
        ResearchTests.setUp(self);intake.init();reader.init();workflow.ACTIVE.clear();workflow.init()
    def fixture(self):
        return {'title':'Action priors','summary':'User idea','reply':'Place in robot learning','collection':'Robot Learning','concepts':['Action priors'],'connections':[{'paper_id':'known','reason':'same topic'},{'paper_id':'invented'}],'papers':[]}
    def test_connection_ids_and_basis(self):
        result=intake.validate(self.fixture(),[{'id':'known','title':'Paper','basis':'title'}])
        self.assertEqual(len(result['connections']),1);self.assertEqual(result['connections'][0]['basis'],'title')
    def test_blocked_post_does_not_invoke_model(self):
        with patch('intake.threading.Thread'),patch.object(intake,'collect',return_value=([{'url':'https://x.com/u/status/1','status':'blocked'}],[])),patch.object(research,'cli') as cli:
            item=intake.start('https://x.com/u/status/1');intake.work(item['id']);self.assertEqual(intake.get(item['id'])['status'],'needs_text');cli.assert_not_called()
    def test_conversation_and_organization_persist(self):
        with patch('intake.threading.Thread'),patch.object(intake,'collect',return_value=([],[])),patch.object(intake,'shortlist',return_value=[]),patch.object(research,'cli',return_value=json.dumps(self.fixture())):
            item=intake.start('Action priors for robot learning');intake.work(item['id']);intake.organize(item['id'],'Robotics / Priors');self.assertTrue(intake.get(item['id'])['organized'])
            intake.start('Move to action representation',item['id']);intake.work(item['id']);item=intake.get(item['id']);self.assertEqual(len(item['messages']),4);self.assertEqual(len(item['history']),1);self.assertTrue(item['organized']);self.assertEqual(item['input'],'Action priors for robot learning')
    def test_running_item_rejects_duplicate(self):
        with patch('intake.threading.Thread'):
            item=intake.start('test');
            with self.assertRaises(ValueError):intake.start('again',item['id'])
