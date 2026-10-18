import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import research
import tensor_evidence as T


class TensorEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.code = self.root / 'code'
        self.code.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.code)], check=True)
        (self.code / 'train.py').write_text('import os\nraise RuntimeError("must never execute")\n')
        (self.code / 'config.json').write_text('{"dim": 16}\n')
        (self.code / 'linked.py').symlink_to(self.root / 'outside.py')
        (self.root / 'outside.py').write_text('private')
        (self.code / 'lfs.py').write_text('version https://git-lfs.github.com/spec/v1\noid sha256:test\nsize 100\n')
        subprocess.run(['git', '-C', str(self.code), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(self.code), '-c', 'user.name=Test', '-c', 'user.email=test@example.org',
                        'commit', '-qm', 'fixture'], check=True)
        self.status = {'status': 'cloned', 'url': 'https://github.com/test/repo',
                       'commit': subprocess.check_output(['git', '-C', str(self.code), 'rev-parse', 'HEAD'], text=True).strip()}
        self.manifest = T.inventory(self.code, self.status)
        self.link = self.status['url'] + '/blob/' + self.status['commit'] + '/train.py#L1-L2'
        self.config = self.link.replace('train.py#L1-L2', 'config.json#L1')

    def tearDown(self):
        self.tmp.cleanup()

    def trace(self):
        row = {'title': 'project', 'operation': 'linear', 'explanation': 'contract last axis',
               'input_shape': '[B,16]', 'output_shape': '[B,32]', 'basis': 'code',
               'assumptions': 'configuration', 'evidence': [{'url': self.link}]}
        step = {'id': 'projection', 'title': 'Projection', 'explanation': 'source inspection',
                'mode': 'training', 'verification': 'source', 'operation': 'linear',
                'input_shape': '[B,16]', 'output_shape': '[B,32]', 'evidence': [{'url': self.link}],
                'shape_trace': [row]}
        return {'title': 'Trace', 'execution_profile': {'repository': self.status['url'],
            'commit': self.status['commit'], 'config': 'config.json', 'mode': 'training',
            'scope': 'static', 'dimensions': [{'symbol': 'D', 'value': '16', 'source': self.config, 'meaning': 'width'}],
            'unknowns': ['B runtime']}, 'steps': [step, {**copy.deepcopy(step), 'id': 'sample', 'mode': 'inference'}]}

    def test_inventory_never_imports_code_and_excludes_external_symlink(self):
        files = {f['path']: f for f in self.manifest['files']}
        self.assertNotIn('linked.py', files)
        self.assertEqual(files['train.py']['lines'], 2)
        self.assertTrue(files['lfs.py']['lfs_pointer'])
        self.assertEqual(len(files['config.json']['sha256']), 64)

    def test_normalization_preserves_profile_and_real_operations(self):
        trace = research.normalize_walkthrough(self.trace(), [{'url': self.link}, {'url': self.config}])
        self.assertEqual(trace['execution_profile']['dimensions'][0]['value'], '16')
        self.assertEqual(trace['steps'][0]['shape_trace'][0]['operation'], 'linear')
        self.assertEqual(T.validate_trace(trace, self.manifest)['status'], 'source_checked')
        raw=self.trace();raw['steps'][0]['shape_trace'][0].update(operation='x @ W',equation='y_ij = sum_k x_ik W_kj')
        row=research.normalize_walkthrough(raw,[{'url':self.link},{'url':self.config}])['steps'][0]['shape_trace'][0]
        self.assertEqual(row['operation'],'x @ W')
        self.assertEqual(row['equation'],'y_ij = sum_k x_ik W_kj')

    def test_inventory_failure_preserves_explicit_limit_and_partial_repair_keeps_steps(self):
        with patch.object(T,'inventory',side_effect=subprocess.TimeoutExpired('git',20)):
            manifest=T.write_inventory(self.root,self.status)
        self.assertEqual(manifest['files'],[])
        self.assertIn('코드 목록 수집 실패',manifest['limitations'][0])
        bad={'walkthrough':self.trace(),'sources':[{'url':self.link},{'url':self.config}]}
        bad['walkthrough']['execution_profile']['config']='unavailable.json'
        with patch.object(research,'mark'),patch.object(research,'cli',side_effect=[json.dumps(bad),'{}']):
            result,sources=research.analyze_tensor_trace('test',self.root,self.status,self.manifest)
        self.assertEqual(len(result['steps']),2)
        self.assertEqual(len(sources),2)
        self.assertEqual(json.loads((self.root/'tensor-trace-normalized.json').read_text()),result)
        self.assertIn('보정 응답',result['validation']['issues'][-1])

    def test_bad_anchors_configs_and_training_coverage_never_pass(self):
        for link in (self.link.replace('#L1-L2', '#L1-L999'), self.link.replace('train.py', 'missing.py'),
                     self.link.replace('train.py#L1-L2', 'lfs.py#L1'), self.link.replace(self.status['commit'], 'main')):
            trace = self.trace()
            trace['steps'][0]['evidence'] = [{'url': link}]
            self.assertEqual(T.validate_trace(trace, self.manifest)['status'], 'needs_review')
            self.assertEqual(trace['steps'][0]['verification'], 'unknown')
        trace = self.trace(); trace['execution_profile']['config'] = 'missing.json'
        self.assertEqual(T.validate_trace(trace, self.manifest)['status'], 'needs_review')
        trace = self.trace(); trace['steps'] = trace['steps'][:1]
        self.assertEqual(T.validate_trace(trace, self.manifest)['status'], 'needs_review')

    def test_dedicated_stage_repairs_failed_trace_and_preserves_missing_code(self):
        good = {'walkthrough': self.trace(), 'sources': [{'url': self.link}, {'url': self.config}]}
        bad = copy.deepcopy(good); bad['walkthrough']['execution_profile']['config'] = 'missing.json'
        with patch.object(research, 'mark'), patch.object(research, 'cli', side_effect=[json.dumps(bad), json.dumps(good)]) as worker:
            result, sources = research.analyze_tensor_trace('test', self.root, self.status, self.manifest)
        self.assertEqual(worker.call_count, 2)
        self.assertEqual(result['validation']['status'], 'source_checked')
        self.assertTrue((self.root / 'tensor-trace-normalized.json').exists())
        with patch.object(research, 'cli') as worker:
            result, _ = research.analyze_tensor_trace('test', self.root, {'status': 'unavailable'}, {})
        worker.assert_not_called()
        self.assertEqual(result['steps'], [])
        self.assertEqual(result['validation']['status'], 'needs_review')

    def test_focused_patch_adds_missing_path_and_retains_source_metadata(self):
        first={'walkthrough':self.trace(),'sources':[{'url':self.link},{'url':self.config}]}
        inference=first['walkthrough']['steps'].pop()
        patch_response={'walkthrough_patch':{'append_steps':[inference]},'sources':[]}
        with patch.object(research,'mark'),patch.object(research,'cli',side_effect=[json.dumps(first),json.dumps(patch_response)]) as worker:
            result,sources=research.analyze_tensor_trace('test',self.root,self.status,self.manifest)
        self.assertEqual(result['validation']['status'],'source_checked')
        self.assertEqual(len(result['steps']),2)
        self.assertEqual(len(sources),2)
        self.assertEqual(worker.call_args_list[1].kwargs['reasoning'],'medium')
        self.assertEqual(result['execution_profile']['config'],'config.json')

    def test_partial_audit_and_cancellation_are_not_silently_passed(self):
        with patch.object(research, 'mark'), patch.object(research, 'cli', side_effect=ValueError('timeout')):
            trace, _ = research.analyze_tensor_trace('test', self.root, self.status, self.manifest)
        self.assertEqual(trace['validation']['status'], 'needs_review')
        with patch.object(research, 'mark'), patch.object(research, 'cli', side_effect=InterruptedError):
            with self.assertRaises(InterruptedError):
                research.analyze_tensor_trace('test', self.root, self.status, self.manifest)

    def test_modified_tracked_sources_cannot_claim_pinned_commit(self):
        (self.code / 'train.py').write_text('injected\n' * 100)
        manifest = T.inventory(self.code, self.status)
        self.assertEqual(manifest['files'], [])
        self.assertTrue(manifest['limitations'])
        self.assertEqual(T.validate_trace(self.trace(), manifest)['status'], 'needs_review')

    def test_illustrations_and_unknown_operations_never_pass_source_gate(self):
        trace = self.trace()
        for step in trace['steps']:
            step['verification'] = 'illustrative'
            step['shape_trace'][0]['basis'] = 'illustrative'
        self.assertEqual(T.validate_trace(trace, self.manifest)['status'], 'needs_review')
        trace = self.trace()
        trace['steps'][0]['shape_trace'][0]['basis'] = 'unknown'
        self.assertEqual(T.validate_trace(trace, self.manifest)['status'], 'needs_review')
        trace = self.trace()
        trace['steps'][0]['mechanics'] = [{'title': 'unresolved', 'basis': 'unknown'}]
        self.assertEqual(T.validate_trace(trace, self.manifest)['status'], 'needs_review')

    def test_concurrent_source_change_discards_manifest(self):
        real_open = T.os.open
        def changing_open(path, flags):
            if Path(path).name == 'train.py':
                Path(path).write_text('changed after initial cleanliness check\n')
            return real_open(path, flags)
        with patch.object(T.os, 'open', side_effect=changing_open):
            manifest = T.inventory(self.code, self.status)
        self.assertEqual(manifest['files'], [])
        self.assertTrue(any('수집 중' in issue for issue in manifest['limitations']))
