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
- `develop`: development code; pushes run CI without creating releases. To publish a tested development ZIP, manually run the **Release** workflow on `develop`.
- Development builds use a separate **Paperloom Dev** data directory. They do not migrate or overwrite the stable library.
- Release ZIPs contain an unsigned macOS arm64 app. Signing/notarization and automatic updates are not configured. A new GitHub release does not replace the installed app.

See [release process](docs/RELEASING.md), [review policy](docs/REVIEW.md), and [known limitations](docs/LIMITATIONS.md).

## Manim

Install the optional renderer separately:

```sh
brew install cairo pango pkg-config
python3 -m venv "$HOME/.paperloom-manim"
"$HOME/.paperloom-manim/bin/python" -m pip install manim==0.22.0
```

Set `PAPERLOOM_MANIM_PYTHON` to that Python executable, or write `{"python":"/absolute/path/to/python"}` to `~/Library/Application Support/Paperloom/manim-runtime.json`.

Scenes are trusted, fixed Python templates with numeric parameters. The app does not execute AI-generated animation code. The paper walkthrough also renders source-bound tensor operations in `TensorTraceScene`: training/inference paths, splitting, concatenation, patch projection, attention and reductions. Select a stage or individual operation to play its local MP4 and inspect pinned source, equations and recorded derivations. DreamZero-specific diagrams require the matching audited commit and dimensions; other profiles use labeled shape diagrams. These videos visualize recorded shapes, not measured model execution. Generated clips are cached by analysis and scene content, with up to 128 recent clips retained per paper.

## Data and evidence

Stable macOS data lives in `~/Library/Application Support/Paperloom/data`; development builds use `Paperloom Dev/data`. Back up the complete data directory before changing machines. The application binds to loopback only. iPad synchronization and handwriting are not implemented.

Author affiliations, education, and paper relationships retain source links and uncertainty. A model-generated brief or graph edge is not a verified scientific conclusion. Blocked social pages require pasted text or a direct paper URL.

Research guidance is in `research-skills/`, with provenance and the upstream ELI5 license. Bundled third-party licenses are in `LICENSES/`.

### 로컬 PDF 추가

`논문 추가`에서 PDF를 선택하거나 파일을 놓을 수 있습니다. arXiv 등록 여부와 관계없이 원본 PDF를 저장하고 즉시 열람합니다. 제목을 직접 지정할 수 있으며 같은 파일은 SHA-256으로 중복을 방지합니다. `추가 후 원문·코드 분석 시작`을 끄면 AI 분석 없이 저장합니다.

- 한 파일 최대 24MB, 500쪽, 추출 본문 200만 자입니다. 암호화된 PDF는 먼저 잠금을 해제해야 합니다.
- `추출 본문`은 페이지 번호를 유지한 PDF 텍스트이며 번역·하이라이트·메모에 연결됩니다. 원본 HTML이나 복원된 TeX가 아닙니다. 다단 배치, 수식, 표는 PDF 탭과 대조해야 합니다.
- 충분한 텍스트가 없는 PDF는 저장·열람할 수 있지만 자동 분석을 시작하지 않습니다. 스캔 문서는 OCR 처리 후 추가하세요.
- PDF 분석은 저장한 본문으로 진행하며, 공개 논문·공식 코드의 동일성이 확인되지 않으면 확인 불가로 남깁니다. 분석·번역은 Codex에 본문을 전달하고 사용량을 소비합니다.
- 파일과 추출 결과는 현재 프로필의 `data/research/uploads`에 보관합니다. 연구 라이브러리를 수동 백업할 때 `data/research` 전체를 포함하세요. 기존 `/api/backup`은 구형 라이브러리 백업이므로 연구 라이브러리 전체 백업을 대신하지 않습니다.

검증: `python -m unittest discover -s tests -p test_pdf_import.py`, `node tests/pdf-import-ui.cjs` (Playwright Chrome 필요, 격리된 임시 데이터, AI 호출 없음).

## Sentence-aligned reading

Original HTML and Korean translations can be paired by source-anchored sentences. Hover or focus either language to locate its counterpart. AI category colors use independently validated exact English and Korean quotes. Selecting a Korean phrase saves that phrase and its corresponding full English sentence; cross-sentence Korean selections are currently unsupported. Existing paragraph translations remain available while missing sentence alignments are generated. Translation snapshots preserve prior Korean selections across later changes. AI translations and classifications still require comparison with the source.

## Background paper jobs

Paper collection, analysis, bilingual translation and concept generation share a FIFO admission queue: up to2 Codex processing calls run concurrently, with up to10 waiting. Interactive chat uses its separate streaming path. The top toolbar lists jobs across papers; paragraph counts drive translation progress, while analysis shows its current operation. Existing running jobs are preserved until the app is closed.

## Concept learning

Open 개념 노트 and enter a concept name. Latent Action includes a source-reviewed starting guide comparing LAPA, Genie and UniVLA, with pinned code references and separate source-derived shapes versus pedagogical numbers. Other concepts can generate the same structured guide through 학습자료 준비. Read explanations, compare papers, inspect typed source-linked graph edges and write an answer before revealing the reference answer. Answers and self-reported understanding are stored separately from research notes and included in Markdown/Jupyter exports. This is not an automatic mastery score or a spaced-repetition scheduler.


Once the original text of an arXiv paper or uploaded PDF is collected, a separate concept job extracts up to four central concepts, verifies quoted passages against that completed report's original text, and generates the same learning-guide format. Exact existing names or registered aliases reuse notebooks; related or contrasting concepts retain separate relations with evidence. The paper's 공통 개념 tab shows definitions, source passages, notebook links, and the local paper/concept graph. Personal notes and answers are preserved. Failed or cancelled concept jobs can retry without rerunning the paper analysis; automatic links are updated transactionally and manual links remain. This bounded pass is not an exhaustive list of every term in a paper.
