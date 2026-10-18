"""Read-only wikilinks over personal notes; generated reports are not indexed."""
import json
import re
import unicodedata
import research as R

MAX_NODES = 10000
MAX_NOTE = 100000
MAX_TEXT = 5000000
MAX_LINKS = 200
WIKI = re.compile(r'(?<!\\)\[\[([^\[\]\n]{1,500})\]\]')
CODE = re.compile(r'(?ms)^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1[^\n]*$|`[^`\n]*`')


def key(value):
    return ' '.join(unicodedata.normalize('NFKC', value).casefold().split())


def links(kind, ident):
    if kind not in ('paper', 'concept') or not isinstance(ident, str) or not 0 < len(ident) <= 100:
        raise ValueError('논문 또는 개념 ID를 지정하세요.')
    with R.db() as c:
        c.execute('PRAGMA query_only=ON')
        c.execute('BEGIN')
        return _links(c, kind, ident)


def _links(c, kind, ident):
    nodes = []
    truncated = False
    for node_kind, query in (
        ('paper', "SELECT id,json_extract(body,'$.title'),length(json_extract(body,'$.notes')),NULL FROM records ORDER BY id LIMIT ?"),
        ('concept', "SELECT id,json_extract(body,'$.name'),length(json_extract(body,'$.notes')),json_extract(body,'$.papers') FROM knowledge WHERE kind='concept' ORDER BY id LIMIT ?")):
        rows = c.execute(query, (MAX_NODES + 1,)).fetchall()
        truncated |= len(rows) > MAX_NODES
        for row in rows[:MAX_NODES]:
            note_length = row[2] if isinstance(row[2], int) else 0
            truncated |= note_length > MAX_NOTE
            try:
                papers = json.loads(row[3]) if row[3] else []
            except (ValueError, TypeError):
                papers = []
            nodes.append({'kind': node_kind, 'id': row[0], 'title': row[1] or '',
                          'note_length': note_length, 'papers': papers if isinstance(papers, list) else []})
    by_id = {(n['kind'], n['id']): n for n in nodes}
    selected = by_id.get((kind, ident))
    if not selected:
        raise ValueError('논문·개념을 찾을 수 없습니다. 색인 한도를 초과했을 수 있습니다.' if truncated else '논문·개념을 찾을 수 없습니다.')
    by_name = {}
    for node in nodes:
        by_name.setdefault(key(node['title']), []).append(node)

    def public(node):
        return {k: node[k] for k in ('kind', 'id', 'title')}

    def resolve(target):
        prefix, separator, value = target.partition(':')
        if separator and prefix in ('paper', 'concept'):
            found = by_id.get((prefix, value))
            return [found] if found else []
        return by_name.get(key(target), [])

    outgoing, incoming, associations = [], [], []
    remaining = MAX_TEXT
    # Always index the selected personal note before applying the aggregate budget.
    for source in [selected] + [n for n in nodes if n is not selected]:
        limit = min(remaining, MAX_NOTE)
        truncated |= source['note_length'] > limit
        if not source['note_length'] or not limit:
            continue
        table = 'records' if source['kind'] == 'paper' else 'knowledge'
        row = c.execute(f"SELECT substr(json_extract(body,'$.notes'),1,?) FROM {table} WHERE id=?", (limit, source['id'])).fetchone()
        note = row[0] if row and isinstance(row[0], str) else ''
        remaining -= len(note)
        masked = CODE.sub(lambda m: ' ' * len(m.group()), note)
        matches = list(WIKI.finditer(masked))
        truncated |= len(matches) > MAX_LINKS
        for match in matches[:MAX_LINKS]:
            target, separator, alias = match.group(1).partition('|')
            target = target.strip()
            if not target:
                continue
            label = alias.strip() if separator else target
            candidates = resolve(target)
            truncated |= len(candidates) > 20
            edge = {'target': target, 'label': label or target,
                    'status': 'resolved' if len(candidates) == 1 else 'ambiguous' if candidates else 'unresolved',
                    'node': public(candidates[0]) if len(candidates) == 1 else None,
                    'candidates': [public(n) for n in candidates[:20]] if len(candidates) > 1 else [],
                    'snippet': note[max(0, match.start()-80):match.end()+80],
                    'start': match.start(), 'end': match.end()}
            if source is selected:
                outgoing.append(edge)
            if len(candidates) == 1 and candidates[0] is selected:
                if len(incoming) < MAX_LINKS:
                    incoming.append({**edge, 'node': public(source)})
                else:
                    truncated = True
    if kind == 'concept':
        related = [by_id.get(('paper', pid)) for pid in selected['papers'] if isinstance(pid, str)]
    else:
        related = [n for n in nodes if n['kind'] == 'concept' and ident in n['papers']]
    seen = set()
    for node in related:
        if node and (node['kind'], node['id']) not in seen:
            seen.add((node['kind'], node['id']))
            if len(associations) < MAX_LINKS:
                associations.append({'type': 'paper-concept', 'node': public(node)})
            else:
                truncated = True
    return {'node': public(selected), 'outgoing': outgoing, 'incoming': incoming,
            'associations': associations, 'truncated': truncated}
