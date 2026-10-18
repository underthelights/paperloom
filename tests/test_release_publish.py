import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('publish_release', Path(__file__).parents[1] / 'scripts/publish_release.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ReleasePublishTests(unittest.TestCase):
    def test_superseded_develop_does_not_publish(self):
        with patch.object(module.subprocess, 'check_output', return_value='new\n'), patch.object(module.subprocess, 'run') as run:
            module.publish({'PRERELEASE':'true','COMMIT':'old','GH_REPO':'a/b'})
        run.assert_not_called()

    def test_current_head_keeps_exact_tested_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            assets=Path(directory); (assets/'app.zip').write_bytes(b'tested')
            with patch.object(module.subprocess, 'check_output', return_value='tested\n'), patch.object(module.subprocess, 'run', return_value=subprocess.CompletedProcess([],0)) as run:
                module.publish({'PRERELEASE':'true','COMMIT':'tested','GH_REPO':'a/b','TAG':'v1-dev.1'},assets)
            args=run.call_args.args[0]
            self.assertEqual(args[args.index('--target')+1],'tested')
            self.assertIn('--latest=false',args)

    def test_permission_failure_is_only_suppressed_if_branch_advanced(self):
        with tempfile.TemporaryDirectory() as directory:
            assets=Path(directory); (assets/'app.zip').write_bytes(b'tested')
            env={'PRERELEASE':'true','COMMIT':'tested','GH_REPO':'a/b','TAG':'v1-dev.1'}
            for heads,fail in ((['tested','new'],False),(['tested','tested'],True)):
                with patch.object(module.subprocess,'check_output',side_effect=heads),patch.object(module.subprocess,'run',return_value=subprocess.CompletedProcess([],1)):
                    if fail:
                        with self.assertRaises(subprocess.CalledProcessError):module.publish(env,assets)
                    else:module.publish(env,assets)

    def test_stable_release_requires_existing_tag_and_never_skips(self):
        with tempfile.TemporaryDirectory() as directory:
            assets=Path(directory); (assets/'app.zip').write_bytes(b'tested')
            with patch.object(module.subprocess,'check_output') as query,patch.object(module.subprocess,'run',return_value=subprocess.CompletedProcess([],1)) as run:
                with self.assertRaises(subprocess.CalledProcessError):
                    module.publish({'PRERELEASE':'false','COMMIT':'tested','TAG':'v1.0.0'},assets)
                query.assert_not_called()
                self.assertIn('--verify-tag',run.call_args.args[0])
