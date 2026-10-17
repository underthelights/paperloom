import subprocess
from pathlib import Path
files=subprocess.check_output(['git','ls-files','-z'],text=True).split('\0')
for name in filter(None,files):
    p=Path(name)
    if any(x in p.parts for x in ('data','work','.venv','.manim-venv','node_modules','dist','build')) or p.name in ('research-seed.json','notion-candidates.json','.env','IMPORT-REPORT.json') or '.sqlite3' in p.name:raise SystemExit('Private/generated path tracked: '+name)
    if p.stat().st_size>20*1024*1024:raise SystemExit('Unexpected large source file: '+name)
print('Public source boundary checked.')
