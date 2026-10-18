"""Local-only tensor animation selection, cache identity, and path boundaries."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tensor_motion as M


class TensorMotionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.data = Path(self.tmp.name)
        self.pid = 'a' * 32
        evidence = [{'url': 'https://github.com/test/model/blob/' + 'b' * 40 + '/model.py#L1-L2'}]
        step = {'id': 'projection', 'title': 'Projection', 'mode': 'shared',
                'verification': 'source', 'operation': 'linear', 'explanation': 'Project last axis.',
                'input_shape': '[B,16]', 'output_shape': '[B,32]', 'equation': 'y=xW+b',
                'evidence': evidence, 'mechanics': [], 'shape_trace': [
                    {'title': 'Contract', 'operation': 'matmul', 'input_shape': '[B,16]×[16,32]',
                     'output_shape': '[B,32]', 'basis': 'code', 'assumptions': 'static profile',
                     'evidence': evidence}]}
        self.paper = {'id': self.pid, 'title': 'Test paper', 'notes': 'PRIVATE_NOTE_TOKEN',
                      'raw_source': 'PRIVATE_RAW_TOKEN', 'reports': [{
                          'id': 'report-1', 'created': '2026-10-18', 'walkthrough': {
                              'title': 'Actual trace', 'scope': 'static',
                              'execution_profile': {'repository': 'https://github.com/test/model',
                                  'commit': 'b' * 40, 'config': 'config.json', 'mode': 'training',
                                  'scope': 'single config', 'unknowns': [], 'dimensions': []},
                              'steps': [step]}}]}
        self.addCleanup(patch.stopall)
        patch.object(M.R, 'get', side_effect=lambda pid: copy.deepcopy(self.paper)).start()
        patch.object(M.R, 'DATA', self.data).start()

    def test_selected_spec_has_no_personal_or_unrelated_fields(self):
        spec = M.select_spec(self.pid, 'training', 'projection')
        serialized = json.dumps(spec)
        self.assertIn('Projection', serialized)
        self.assertIn('[B,16]', serialized)
        self.assertNotIn('PRIVATE_NOTE_TOKEN', serialized)
        self.assertNotIn('PRIVATE_RAW_TOKEN', serialized)
        self.assertNotIn(str(self.data), serialized)

    def test_mode_and_source_change_invalidate_cache(self):
        train = M.select_spec(self.pid, 'training', 'projection')
        self.assertEqual(M.key(train), M.key(copy.deepcopy(train)))
        infer = M.select_spec(self.pid, 'inference', 'projection')
        self.assertNotEqual(M.key(train), M.key(infer))
        self.paper['reports'][0]['walkthrough']['steps'][0]['output_shape'] = '[B,64]'
        changed = M.select_spec(self.pid, 'training', 'projection')
        self.assertNotEqual(M.key(train), M.key(changed))

    def test_bad_selection_rejected(self):
        for mode, step, row in [('invalid', 'projection', -1), ('training', 'missing', -1),
                                ('training', 'projection', 99)]:
            with self.subTest(mode=mode, step=step, row=row), self.assertRaises(ValueError):
                M.select_spec(self.pid, mode, step, row)

    def test_video_path_traversal_rejected(self):
        for pid, digest in [('../escape', 'b' * 64), (self.pid, '../escape'),
                            (self.pid, '/tmp/video.mp4')]:
            with self.subTest(pid=pid, digest=digest), self.assertRaises(ValueError):
                M.video_file(pid, digest)

    def test_video_symlink_cannot_escape_data(self):
        digest = 'b' * 64
        directory = self.data / 'tensor-motion' / self.pid / digest
        directory.mkdir(parents=True)
        outside = self.data / 'outside.mp4'
        outside.write_bytes(b'private')
        (directory / 'video.mp4').symlink_to(outside)
        (directory / 'status.json').write_text(json.dumps({'status': 'ready'}))
        with self.assertRaises(ValueError):
            M.video_file(self.pid, digest)

    def test_duplicate_start_creates_one_worker_and_preserves_userdata(self):
        before = copy.deepcopy(self.paper)
        request = {'paper_id': self.pid, 'mode': 'training', 'step_id': 'projection',
                   'spec': {'operation': 'UNTRUSTED_POST_OVERRIDE'}}
        with patch.object(M.knowledge, 'runtime', return_value='/trusted/python'), \
             patch.object(M.threading, 'Thread') as worker:
            first = M.start(request)
            second = M.start(request)
        self.assertEqual(worker.call_count, 1)
        self.assertEqual(first['key'], second['key'])
        self.assertEqual(first['status'], 'queued')
        self.assertEqual(self.paper, before)
        self.assertNotIn('UNTRUSTED_POST_OVERRIDE', json.dumps(worker.call_args.kwargs['args'][1]))
        M.ACTIVE.clear()

    def test_renderer_uses_static_scene_and_atomic_completed_file(self):
        spec = M.select_spec(self.pid, 'training', 'projection')
        directory = M.directory(self.pid, M.key(spec))
        directory.mkdir(parents=True)
        def renderer(command, **kwargs):
            self.assertEqual(command[0:3], ['/trusted/python', '-m', 'manim'])
            self.assertEqual(command[-2:], [str(M.R.ROOT / 'tensor_scenes.py'), 'TensorTraceScene'])
            self.assertFalse(kwargs['shell'])
            self.assertEqual(kwargs['timeout'], 240)
            output = directory / 'media/videos/test/TensorTraceScene.mp4'
            output.parent.mkdir(parents=True)
            output.write_bytes(b'x' * 1200)
        with patch.object(M.subprocess, 'run', side_effect=renderer) as process:
            M._render(directory, spec, '/trusted/python')
        process.assert_called_once()
        self.assertEqual(M.video_file(self.pid, M.key(spec)).read_bytes(), b'x' * 1200)
        self.assertFalse((directory / 'video.writing').exists())
        self.assertFalse((directory / 'media').exists())
        self.assertEqual(json.loads((directory / 'status.json').read_text())['status'], 'ready')

    def test_failed_renderer_never_serves_stale_video_and_can_retry(self):
        spec = M.select_spec(self.pid, 'training', 'projection')
        directory = M.directory(self.pid, M.key(spec))
        directory.mkdir(parents=True)
        (directory / 'video.mp4').write_bytes(b'old file')
        (directory / 'render.lock').write_text('123')
        with patch.object(M.subprocess, 'run', side_effect=RuntimeError('render failed')):
            M._render(directory, spec, '/trusted/python')
        self.assertFalse((directory / 'render.lock').exists())
        with self.assertRaises(ValueError):
            M.video_file(self.pid, M.key(spec))
        with patch.object(M.knowledge, 'runtime', return_value='/trusted/python'), \
             patch.object(M.threading, 'Thread') as worker:
            status = M.start({'paper_id': self.pid, 'mode': 'training', 'step_id': 'projection'})
        self.assertEqual(status['status'], 'queued')
        worker.assert_called_once()
        M.ACTIVE.clear()

    def test_renderer_revision_changes_cache(self):
        first = M.select_spec(self.pid, 'training', 'projection')
        with patch.object(M, 'VERSION', M.VERSION + 1):
            second = M.select_spec(self.pid, 'training', 'projection')
        self.assertNotEqual(M.key(first), M.key(second))

    def test_source_excerpt_cannot_read_outside_clone(self):
        run = 'c' * 32
        self.paper['last_run'] = run
        directory = self.data / 'runs' / run / 'code'
        directory.mkdir(parents=True)
        outside = self.data / 'private.py'
        outside.write_text('private secret\n')
        (directory / 'model.py').symlink_to(outside)
        url = self.paper['reports'][0]['walkthrough']['steps'][0]['evidence'][0]['url']
        with self.assertRaises(ValueError):
            M.code_excerpt(self.pid, url)

    def test_source_excerpt_rejects_symlinked_clone_root(self):
        run = 'c' * 32
        self.paper['last_run'] = run
        parent = self.data / 'runs' / run
        parent.mkdir(parents=True)
        outside = self.data / 'private-source'
        outside.mkdir()
        (outside / 'model.py').write_text('private secret\nsecond line\n')
        (parent / 'code').symlink_to(outside, target_is_directory=True)
        url = self.paper['reports'][0]['walkthrough']['steps'][0]['evidence'][0]['url']
        with self.assertRaises(ValueError):
            M.code_excerpt(self.pid, url)

    def test_thread_start_failure_releases_lock_and_allows_retry(self):
        request = {'paper_id': self.pid, 'mode': 'training', 'step_id': 'projection'}
        spec = M.select_spec(self.pid, 'training', 'projection')
        directory = M.directory(self.pid, M.key(spec))
        with patch.object(M.knowledge, 'runtime', return_value='/trusted/python'), \
             patch.object(M.threading, 'Thread') as worker:
            worker.return_value.start.side_effect = RuntimeError('thread unavailable')
            with self.assertRaises(RuntimeError):
                M.start(request)
        self.assertFalse((directory / 'render.lock').exists())
        self.assertNotIn(M.key(spec), M.ACTIVE)
        self.assertEqual(M.get_status(self.pid, 'training', 'projection')['status'], 'error')
        with patch.object(M.knowledge, 'runtime', return_value='/trusted/python'), \
             patch.object(M.threading, 'Thread') as worker:
            self.assertEqual(M.start(request)['status'], 'queued')
        worker.assert_called_once()
        M.ACTIVE.clear()

    def test_start_uses_one_report_snapshot(self):
        first = M.select_spec(self.pid, 'training', 'projection')
        second = copy.deepcopy(self.paper)
        second['reports'][0]['walkthrough']['steps'][0]['output_shape'] = '[B,64]'
        with patch.object(M.R, 'get', side_effect=[copy.deepcopy(self.paper), second]) as read, \
             patch.object(M.knowledge, 'runtime', return_value='/trusted/python'), \
             patch.object(M.threading, 'Thread') as worker:
            status = M.start({'paper_id': self.pid, 'mode': 'training', 'step_id': 'projection'})
        self.assertEqual(read.call_count, 1)
        self.assertEqual(status['key'], M.key(first))
        self.assertEqual(M.key(worker.call_args.kwargs['args'][1]), status['key'])
        M.ACTIVE.clear()

    def test_code_excerpt_reads_pinned_git_blob_and_caps_lines(self):
        import subprocess
        run = 'c' * 32
        self.paper['last_run'] = run
        directory = self.data / 'runs' / run / 'code'
        directory.mkdir(parents=True)
        source = directory / 'model.py'
        source.write_text(''.join(f'original {i}\n' for i in range(450)))
        subprocess.run(['git', 'init', '-q', str(directory)], check=True)
        subprocess.run(['git', '-C', str(directory), 'add', 'model.py'], check=True)
        subprocess.run(['git', '-C', str(directory), '-c', 'user.name=Test',
                        '-c', 'user.email=test@example.org', 'commit', '-qm', 'source'], check=True)
        commit = subprocess.check_output(['git', '-C', str(directory), 'rev-parse', 'HEAD'], text=True).strip()
        trace = self.paper['reports'][0]['walkthrough']
        trace['execution_profile']['commit'] = commit
        url = 'https://github.com/test/model/blob/' + commit + '/model.py#L1-L450'
        trace['steps'][0]['evidence'] = [{'url': url}]
        source.write_text('DIRTY PRIVATE WORKTREE CONTENT\n')
        result = M.code_excerpt(self.pid, url)
        self.assertEqual(result['code'].splitlines()[0], 'original 0')
        self.assertEqual(result['code'].splitlines()[-1], 'original 399')
        self.assertEqual(result['end'], 400)
        self.assertTrue(result['truncated'])
        self.assertNotIn('PRIVATE', result['code'])

    def test_spec_preserves_math_and_unknown_boundaries(self):
        trace = self.paper['reports'][0]['walkthrough']
        trace['execution_profile']['unknowns'] = ['runtime batch size is unknown']
        trace['steps'][0]['mechanics'] = [{'title': 'Contraction', 'equation': 'y_j=sum_i x_i W_ij',
                                         'explanation': 'Reduce input feature axis.', 'basis': 'mathematical'}]
        spec = M.select_spec(self.pid, 'training', 'projection')
        self.assertEqual(spec['step']['mechanics'][0]['equation'], 'y_j=sum_i x_i W_ij')
        self.assertIn('runtime batch size is unknown', spec['profile']['unknowns'])

    def test_explanation_changes_still_invalidate_via_source_digest(self):
        before = M.select_spec(self.pid, 'training', 'projection')
        trace = self.paper['reports'][0]['walkthrough']
        trace['steps'][0]['mechanics'] = [{'title': 'New derivation', 'equation': 'x+y'}]
        after = M.select_spec(self.pid, 'training', 'projection')
        self.assertNotEqual(M.key(before), M.key(after))
        trace['execution_profile']['unknowns'] = ['new unresolved dimension']
        self.assertNotEqual(M.key(after), M.key(M.select_spec(self.pid, 'training', 'projection')))

    def _old_cache(self, name, status):
        import os
        folder = self.data / 'tensor-motion' / self.pid / name
        folder.mkdir(parents=True, exist_ok=True)
        (folder / 'status.json').write_text(json.dumps(status))
        (folder / 'video.mp4').write_bytes(b'cached')
        os.utime(folder, (1, 1))
        return folder

    def _recent_caches(self):
        import os
        for i in range(128):
            folder = self._old_cache(f'{i + 100:064x}', {'status': 'ready'})
            os.utime(folder, (1000 + i, 1000 + i))
        return f'{227:064x}'

    def test_prune_preserves_active_live_and_requested_caches(self):
        import os
        preserve = self._recent_caches()
        active = self._old_cache('1' * 64, {'status': 'ready'})
        live = self._old_cache('2' * 64, {'status': 'running', 'owner_pid': os.getpid()})
        stale = self._old_cache('3' * 64, {'status': 'error'})
        M.ACTIVE.add(active.name)
        try:
            M.prune(self.pid, preserve)
        finally:
            M.ACTIVE.discard(active.name)
        self.assertTrue(active.exists())
        self.assertTrue(live.exists())
        self.assertFalse(stale.exists())
        self.assertTrue(M.directory(self.pid, preserve).exists())

    def test_prune_never_deletes_noncache_directory(self):
        preserve = self._recent_caches()
        manual = self._old_cache('manual-backup', {'status': 'ready'})
        M.prune(self.pid, preserve)
        self.assertTrue(manual.exists())

    def test_prune_respects_live_lock_before_queued_status_write(self):
        import os
        preserve = self._recent_caches()
        locked = self._old_cache('4' * 64, {'status': 'error'})
        (locked / 'render.lock').write_text(str(os.getpid()))
        os.utime(locked, (1, 1))
        M.prune(self.pid, preserve)
        self.assertTrue(locked.exists())

    def test_cache_cleanup_failure_does_not_invalidate_completed_video(self):
        spec = M.select_spec(self.pid, 'training', 'projection')
        folder = M.directory(self.pid, M.key(spec))
        folder.mkdir(parents=True)
        def renderer(*args, **kwargs):
            output = folder / 'media/videos/TensorTraceScene.mp4'
            output.parent.mkdir(parents=True)
            output.write_bytes(b'x' * 1200)
        with patch.object(M.subprocess, 'run', side_effect=renderer), \
             patch.object(M, 'prune', side_effect=OSError('concurrent cleanup')):
            M._render(folder, spec, '/trusted/python')
        self.assertEqual(json.loads((folder / 'status.json').read_text())['status'], 'ready')
        self.assertEqual(M.video_file(self.pid, M.key(spec)).stat().st_size, 1200)

    def test_prune_skips_nonobject_status(self):
        preserve = self._recent_caches()
        malformed = self._old_cache('5' * 64, [])
        M.prune(self.pid, preserve)
        self.assertTrue(malformed.exists())
