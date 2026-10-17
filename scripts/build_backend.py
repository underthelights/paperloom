import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
os.chdir(root)
public = root / 'build/public-inputs'
if public.exists(): shutil.rmtree(public)
public.mkdir(parents=True)
shutil.copytree(root / 'research-skills', public / 'research-skills', ignore=shutil.ignore_patterns('notion-candidates.json'))
(public / 'research-seed.json').write_text('[]')
public_runs = root / 'build/research-seed-runs-public'
if public_runs.exists(): shutil.rmtree(public_runs)
public_runs.mkdir(parents=True)
subprocess.run([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
    '--onedir', '--name', 'paperloom-server', '--distpath', 'build/backend-dist',
    '--workpath', 'build/pyinstaller', '--specpath', 'build',
    '--add-data', f'{root / "static"}{os.pathsep}static',
    '--add-data', f'{public / "research-skills"}{os.pathsep}research-skills',
    '--add-data', f'{public / "research-seed.json"}{os.pathsep}.',
    '--add-data', f'{root / "manim_scenes.py"}{os.pathsep}.',
    '--hidden-import', 'pypdf', '--hidden-import', 'bs4', 'app.py'], check=True)
seed = root / 'build/seed'
seed.mkdir(parents=True, exist_ok=True)
target=seed/'library.sqlite3'
if target.exists(): target.unlink()
with sqlite3.connect(target) as connection:
    connection.executescript("CREATE TABLE papers(id TEXT PRIMARY KEY, identity TEXT UNIQUE, body TEXT NOT NULL); CREATE TABLE concepts(name TEXT PRIMARY KEY COLLATE NOCASE, note TEXT NOT NULL DEFAULT '', updated REAL NOT NULL DEFAULT 0); CREATE TABLE settings(key TEXT PRIMARY KEY, value TEXT NOT NULL); CREATE TABLE events(id INTEGER PRIMARY KEY, created REAL, message TEXT);")
pdfs=seed/'pdfs'
if pdfs.exists(): shutil.rmtree(pdfs)
print('Backend ready. Public build contains no personal library, Notion metadata, or research runs.')
