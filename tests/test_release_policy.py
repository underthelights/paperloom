from pathlib import Path
import unittest


class ReleasePolicyTests(unittest.TestCase):
    def test_release_triggers_are_tags_and_explicit_dispatch(self):
        source=(Path(__file__).parents[1]/'.github/workflows/release.yml').read_text()
        events=source.split('\non:\n',1)[1].split('\npermissions:',1)[0]
        self.assertRegex(events,r'(?m)^  push:\n    tags: \[\x27v\*\x27\]$')
        self.assertRegex(events,r'(?m)^  workflow_dispatch:$')
        self.assertNotRegex(events,r'(?m)^\s+(?:branches|branches-ignore|schedule|workflow_run|pull_request):')
        self.assertRegex(source,r"if: startsWith\(github.ref, 'refs/tags/v'\) \|\| github.ref == 'refs/heads/develop'")
        self.assertIn('run: python scripts/publish_release.py',source)

    def test_branch_changes_still_run_ci(self):
        source=(Path(__file__).parents[1]/'.github/workflows/ci.yml').read_text()
        events=source.split('\non:\n',1)[1].split('\npermissions:',1)[0]
        self.assertRegex(events,r'(?m)^  push:\n    branches: \[main, develop\]$')
        self.assertRegex(events,r'(?m)^  pull_request:$')
