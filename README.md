# Paperloom

Local-first Electron workspace for reading papers, connecting concepts, and building an evidence-linked research library.

## Features

- arXiv source ingestion, Codex research briefs, code and author/lab evidence.
- HTML originals, persistent highlights, notes, and contextual explanations.
- Related-paper graph using sampled OpenAlex citations and bibliographic coupling.
- Concept notebooks: cross-paper comparison, equations, derivations, linked highlights, Markdown/Jupyter export.
- Manim educational scenes for temporal ensembling and asynchronous inference; local MP4 export.
- Searchable library shelves and compact, searchable author profiles with source-linked education.
- Light/dark/system themes.

Public builds start with an **empty library**. Personal databases, Notion snapshots, research runs, credentials, and local model runtimes are not published.

## Run from source

Python 3.12+ and Node.js 22+ are recommended. macOS Apple Silicon is the release platform currently tested.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-build.txt
npm ci
npm start
```

For a local browser server, run `sh start.command` (macOS) or `start.bat` (Windows). Windows packaging and full feature parity are not yet validated.

AI features require a separately installed and authenticated Codex CLI. No API credentials ship with the application. Metadata browsing does not require AI authentication. Analysis uses your Codex usage allowance.

## Build and test

```sh
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
.venv/bin/python scripts/build_backend.py
npm run pack
```

The build stages sanitized inputs even if private seeds exist locally. It excludes personal libraries and research runs. Native tests named `*-desktop.cjs` are opt-in integration checks; some require a local research fixture or an authenticated Codex account. CI uses `tests/public-desktop.cjs`, which requires neither.

## Release channels

- `main`: stable code; `vX.Y.Z` tags create regular releases.
- `develop`: development code; pushes create numbered prereleases after checks and a native smoke test.
- Development builds use a separate **Paperloom Dev** data directory. They do not migrate or overwrite the stable library.
- Release ZIPs contain an unsigned macOS arm64 app. Signing/notarization and automatic updates are not configured.

See [release process](docs/RELEASING.md), [review policy](docs/REVIEW.md), and [known limitations](docs/LIMITATIONS.md).

## Manim

Install the optional renderer separately:

```sh
brew install cairo pango pkg-config
python3 -m venv "$HOME/.paperloom-manim"
"$HOME/.paperloom-manim/bin/python" -m pip install manim==0.22.0
```

Set `PAPERLOOM_MANIM_PYTHON` to that Python executable, or write `{"python":"/absolute/path/to/python"}` to `~/Library/Application Support/Paperloom/manim-runtime.json`.

Scenes are trusted, fixed Python templates with numeric parameters. The app does not execute AI-generated animation code. Arbitrary equations are explained in notebooks; only the two supplied scene templates are currently animated.

## Data and evidence

Stable macOS data lives in `~/Library/Application Support/Paperloom/data`; development builds use `Paperloom Dev/data`. Back up the complete data directory before changing machines. The application binds to loopback only. iPad synchronization and handwriting are not implemented.

Author affiliations, education, and paper relationships retain source links and uncertainty. A model-generated brief or graph edge is not a verified scientific conclusion. Blocked social pages require pasted text or a direct paper URL.

Research guidance is in `research-skills/`, with provenance and the upstream ELI5 license. Bundled third-party licenses are in `LICENSES/`.
