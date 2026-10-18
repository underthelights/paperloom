# Linked notes and reader responsiveness

Personal paper and concept notes support `[[Title]]`, `[[Title|label]]`, and stable `[[paper:id|label]]` / `[[concept:id|label]]` links. The context panel shows outgoing references, incoming references with source snippets, and separately typed existing paper–concept associations. Missing and ambiguous targets remain explicit; browsing never creates notes or starts analysis. Generated briefs are not indexed as personal links. The endpoint bounds nodes, note characters and matches and reports partial coverage.

Paper connections open from the compact “연결 노트” disclosure; concepts have the same panel. Navigation saves the active personal note first. Notebook model maps and Manim controls are collapsed, with model-map construction deferred until opening.

Reader highlight ranges now share a text-node index within one batch, while retaining UTF-16 offsets and excluding generated nodes. Identical translation responses skip DOM mutation; collapsed equation explanations defer KaTeX until expanded. Workspace state refreshes are coalesced and only changed sidebar/progress data rebuilds DOM. Polling uses 4 seconds while busy, 15 seconds while idle, and 30 seconds in hidden windows. Summary queries project metadata in SQLite rather than deserialize full reports in Python.

## Verification measurements

Local headless Chrome, cached DreamZero source: 279 translation blocks and 336 automatic highlights. This measures rendering functions, not total startup time or AI execution. All 336 source quotations matched before and after.

| Operation | Before | After |
| --- | ---: | ---: |
| Equation panel installation | 42.7 ms | 14.7 ms |
| First bilingual/highlight apply | 708.1 ms | 22.7 ms |
| Identical response apply, median of 5 | 704.7 ms | 0.7 ms |

Local summary function, 6-paper library, median of 10 calls: 5.68 ms to 2.50 ms, identical projected records. Results depend on machine and document; they do not establish a general Rust-versus-Python comparison.

Tests: reader-performance.cjs, reader-equations.cjs, workspace-refresh.cjs, workspace-links.cjs, reader-tabs.cjs, test_workspace_links.py and test_research.py. User data and running analysis are not used as mutation targets in tests.
