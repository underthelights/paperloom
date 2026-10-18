import json
from pathlib import Path
import unittest


class DreamZeroSourceTraceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.trace = json.loads((Path(__file__).resolve().parents[1] / 'static/dreamzero-walkthrough.json').read_text())
        cls.steps = {s['id']: s for s in cls.trace['steps']}

    def test_selected_configuration_contract(self):
        profile = self.trace['execution_profile']
        self.assertEqual(profile['config'], 'scripts/train/droid_training_lora.sh')
        self.assertEqual(profile['commit'], 'ab790c198fbce33503358efbbd4187ce9a89adf3')
        dims = {d['symbol']: d['value'] for d in profile['dimensions']}
        self.assertEqual(int(dims['D']), 5120)
        self.assertEqual(int(dims['heads']), 40)
        self.assertEqual(int(dims['D']) // int(dims['heads']), 128)
        self.assertIn('128', dims['dh'])
        for dim in profile['dimensions']:
            self.assertIn('/blob/' + profile['commit'] + '/', dim['source'])
            self.assertRegex(dim['source'], r'#L\d+(?:-L\d+)?$')

    def test_conditioning_patch_and_teacher_lengths(self):
        self.assertIn('36', self.steps['conditioning']['output_shape'])
        self.assertEqual(16 + 4 + 16, 36)
        self.assertEqual((352 // 8 // 2) * (640 // 8 // 2), 880)
        self.assertIn('880F', self.steps['patch']['output_shape'])
        f = 1 + (33 - 1) // 4
        actions = (f - 1) * (24 // 2)
        states = (f - 1) // 2
        self.assertEqual((f, actions, states), (9, 96, 4))
        self.assertEqual(880 * f + actions + states, 8020)
        self.assertEqual(2 * 880 * f + actions + states, 15940)
        teacher = json.dumps(self.steps['teacher'], ensure_ascii=False)
        self.assertIn('15940', teacher)
        self.assertIn('조건', teacher)

    def test_real_operations_not_toy_substitution(self):
        action = json.dumps(self.steps['action']['shape_trace'], ensure_ascii=False)
        self.assertIn('10240', action)
        self.assertIn('swish', action)
        self.assertIn('1024', action)
        loss = json.dumps(self.steps['loss']['shape_trace'], ensure_ascii=False)
        self.assertIn('(1,3,4)', loss)
        self.assertIn('mean(dim=2)', loss)
        self.assertIn('유효 mask 합으로 나누는 것이 아니다', loss)
        for step in self.trace['steps']:
            self.assertTrue(step['shape_trace'])
            self.assertTrue(all(row['basis'] != 'illustrative' for row in step['shape_trace']))
        sample = json.dumps(self.steps['sample']['shape_trace'], ensure_ascii=False)
        self.assertIn('배포 checkpoint', sample)
        self.assertIn('σnext−σ', sample)


if __name__ == '__main__':
    unittest.main()
