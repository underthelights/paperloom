"""Publish the tested commit; discard superseded develop release attempts."""
import os
from pathlib import Path
import subprocess


def publish(env=os.environ, asset_dir=Path('release-assets')):
    prerelease = env['PRERELEASE'] == 'true'
    commit = env['COMMIT']

    def superseded():
        if not prerelease:
            return False
        head = subprocess.check_output(
            ['gh', 'api', f"repos/{env['GH_REPO']}/git/ref/heads/develop", '--jq', '.object.sha'],
            text=True).strip()
        if not head:
            raise RuntimeError('Cannot verify develop head; refusing publication')
        return head != commit

    if superseded():
        print('Skipping superseded develop build; tested artifacts remain in this workflow run.')
        return
    assets = sorted(str(path) for path in asset_dir.iterdir() if path.is_file())
    if not assets:
        raise RuntimeError('No tested release assets found')
    tag = env['TAG']
    args = ['gh', 'release', 'create', tag, *assets, '--title', f'Paperloom {tag}', '--generate-notes']
    args += ['--target', commit, '--prerelease', '--latest=false'] if prerelease else ['--verify-tag', '--latest']
    result = subprocess.run(args)
    if result.returncode:
        if superseded():
            print('Develop advanced during publication; skipping obsolete release attempt.')
            return
        raise subprocess.CalledProcessError(result.returncode, args)


if __name__ == '__main__':
    publish()
