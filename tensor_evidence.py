"""Bounded source inventory and static trace evidence checks. Never imports research code."""
import hashlib
import json
import os
import stat
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit


def inventory(root, code):
    result = {'repository': code.get('url', ''), 'commit': code.get('commit', ''),
              'files': [], 'limitations': [], 'execution': 'static-only'}
    if code.get('status') != 'cloned':
        result['limitations'].append(code.get('reason') or '공식 코드 확보 실패')
        return result
    root = Path(root).resolve()
    head = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], timeout=20).decode().strip()
    if head != code.get('commit'):
        result['limitations'].append('체크아웃 커밋이 수집 기록과 다릅니다.')
        return result
    dirty = subprocess.run(['git', '-C', str(root), 'diff', '--quiet', '--no-ext-diff', '--no-textconv', 'HEAD', '--'], timeout=20)
    if dirty.returncode:
        result['limitations'].append('고정 커밋과 작업 파일이 다르거나 비교에 실패했습니다.')
        return result
    paths = subprocess.check_output(['git', '-C', str(root), 'ls-files', '-z'], timeout=20).decode().split('\0')
    total_bytes = 0
    for name in sorted(paths[:30000], key=lambda name: (not any(x in name.lower() for x in ('config', 'train', 'infer')), name)):
        if not name or Path(name).suffix.lower() not in ('.py', '.json', '.yaml', '.yml', '.toml', '.sh', '.md', '.cpp', '.h', '.cu'):
            continue
        path = root / name
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
            continue
        size = path.stat().st_size
        if size > 1024 * 1024:
            result['limitations'].append('1 MiB 초과 파일 제외: ' + name)
            continue
        if total_bytes + size > 64 * 1024 * 1024:
            result['limitations'].append('텍스트 인벤토리 64 MiB 제한; 나머지 파일 제외')
            break
        try:
            fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
            with os.fdopen(fd, 'rb') as source:
                opened = os.fstat(source.fileno())
                current = path.lstat()
                if not stat.S_ISREG(opened.st_mode) or stat.S_ISLNK(current.st_mode) or (opened.st_dev, opened.st_ino) != (current.st_dev, current.st_ino) or not path.resolve().is_relative_to(root):
                    continue
                raw = source.read(1024 * 1024 + 1)
        except OSError:
            result['limitations'].append('읽기 중 파일 변경 또는 접근 실패: ' + name)
            continue
        if len(raw) > 1024 * 1024 or total_bytes + len(raw) > 64 * 1024 * 1024:
            result['limitations'].append('읽기 크기 제한 초과: ' + name)
            continue
        size = len(raw)
        total_bytes += len(raw)
        if b'\0' in raw:
            continue
        text = raw.decode('utf-8', 'replace')
        result['files'].append({'path': name, 'lines': len(text.splitlines()),
            'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': size,
            'config_candidate': any(x in name.lower() for x in ('config', 'train', 'infer', 'eval', 'deploy')),
            'lfs_pointer': text.startswith('version https://git-lfs.github.com/spec/v1')})
    if subprocess.run(['git', '-C', str(root), 'diff', '--quiet', '--no-ext-diff', '--no-textconv', 'HEAD', '--'], timeout=20).returncode:
        result['files'] = []
        result['limitations'].append('수집 중 작업 파일 변경 또는 비교 실패; 근거 인벤토리를 폐기했습니다.')
    if len(paths) > 30000:
        result['limitations'].append('tracked 파일 목록 30000개 제한')
    return result


def validate_trace(trace, manifest):
    """Checks existence/bounds and completeness, not semantic execution correctness."""
    issues = []
    files = {f['path']: f for f in manifest.get('files', [])}
    repository, commit = manifest.get('repository', '').rstrip('/'), manifest.get('commit', '')
    prefix = repository + '/blob/' + commit + '/'

    def anchor(link):
        if not isinstance(link, str) or not repository or not re.fullmatch(r'[0-9a-f]{40}', commit) or not link.startswith(prefix):
            return False
        parsed = urlsplit(link)
        path = unquote(parsed.path.split('/blob/' + commit + '/', 1)[-1])
        found = files.get(path)
        lines = re.fullmatch(r'L([1-9]\d*)(?:-L([1-9]\d*))?', parsed.fragment)
        return bool(found and not found['lfs_pointer'] and lines and
                    1 <= int(lines[1]) <= int(lines[2] or lines[1]) <= found['lines'])

    profile = trace.get('execution_profile') or {}
    if profile.get('repository', '').rstrip('/') != repository or profile.get('commit') != commit:
        issues.append('선택 구현 repository/commit이 수집한 코드와 일치하지 않습니다.')
    if profile.get('config') not in files or files.get(profile.get('config'), {}).get('lfs_pointer'):
        issues.append('선택 config 파일을 수집한 코드에서 확인하지 못했습니다.')
    dimensions = profile.get('dimensions') or []
    if not dimensions:
        issues.append('설정별 차원 정의가 없습니다.')
    for d in dimensions:
        if not anchor(d.get('source')):
            issues.append('차원 근거 행 확인 실패: ' + str(d.get('symbol', '?')))
    steps = trace.get('steps') or []
    modes = {s.get('mode') for s in steps}
    if not steps or not {'training', 'inference'} <= modes:
        issues.append('학습과 추론 경로가 모두 기록되지 않았습니다.')
    for step in steps:
        refs = step.get('evidence') or []
        if step.get('verification') == 'source' and not any(anchor(e.get('url')) for e in refs):
            step['verification'] = 'unknown'
            issues.append('단계의 고정 코드 행 확인 실패: ' + step['title'])
        if step.get('verification') != 'source':
            issues.append('확인하지 못한 코드 단계: ' + step['title'])
        operations = step.get('shape_trace') or []
        if not operations:
            issues.append('축별 연산 추적 누락: ' + step['title'])
        if operations and not any(item.get('basis') == 'code' for item in operations):
            issues.append('코드에 근거한 축별 연산이 없습니다: ' + step['title'])
        for item in [*operations, *(step.get('mechanics') or [])]:
            if item.get('basis') == 'code' and not any(anchor(e.get('url')) for e in item.get('evidence', [])):
                item['basis'] = 'unknown'
                issues.append('내부 연산 코드 행 확인 실패: ' + item['title'])
            if item.get('basis') not in ('code', 'mathematical', 'illustrative'):
                issues.append('확인하지 못한 내부 연산: ' + item['title'])
    issues = list(dict.fromkeys(issues))
    return {'status': 'needs_review' if issues else 'source_checked', 'issues': issues[:100],
            'execution': 'static-only', 'checked_files': len(files),
            'meaning': '고정 커밋의 파일·행 존재와 경로 완결성 검사. 수학적 정확성 또는 실제 forward 실행 검증이 아닙니다.'}


def write_inventory(run, code):
    try:
        manifest = inventory(Path(run) / 'code', code)
    except (OSError, subprocess.SubprocessError, UnicodeError) as exc:
        manifest = {'repository': code.get('url', ''), 'commit': code.get('commit', ''), 'files': [],
                    'limitations': ['코드 목록 수집 실패: ' + str(exc)[:600]], 'execution': 'static-only'}
    (Path(run) / 'code-inventory.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    return manifest
