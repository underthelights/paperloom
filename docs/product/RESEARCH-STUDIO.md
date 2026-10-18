# Research workspace interface

The workspace prioritizes reading and evidence over introductory copy and tool panels. Existing alphaXiv paper/author/source presentation and Zotero's library/collection organization were reviewed as references. This implementation uses its own layout and assets.

## Information hierarchy

- Sidebar: four persistent destinations, compact icons and recent papers. Active navigation follows `aria-current`, independent of layout classes or hover.
- Library: bibliographic rows with aligned title/authors, year, collection and state. Search and sort are always available; less common filters expand on demand. Row actions remain reachable by keyboard.
- Paper: title, source identity, authors, year and review state. Additional actions and affiliations expand under “정보·작업”. Five primary views cover source, review, operations, highlights and related papers. PDF, code, concepts, authors and original references remain reachable in the “자료” disclosure.
- Reader: a single toolbar for contents, annotation export and translation/evidence preferences. Preferences open as a popover without moving source text. The duplicate source title and author cover fold together while preserving original DOM text order and annotation coordinates.
- Review: summary before figures; review limitations and the overview figure remain available in disclosures. Source evidence is visibly distinguished from personal notes.
- Context panel: closed by default, explicit “대화·노트” action with expanded state; selection-to-question can open it. It does not reserve width while closed.
- Inbox: capture form, actual pending counts, recent reading and saved discoveries. The full relation graph is secondary and constructed when opened.

## Visual system

`studio.css` defines the final shared surface, spacing and type hierarchy. Light mode uses white documents and a neutral sidebar; dark mode uses charcoal surfaces. Muted blue is reserved for links, focus and selection. The logo, menus and row actions share restrained sizing. Original paper typography and MathML remain distinct from interface text; Korean translations use a readable system font. No external fonts, icon service or animation framework was added.

## Verification

Browser fixtures use actual cached DreamZero HTML, translations and an existing report. No analysis is triggered and no production data is mutated. Checks cover 1440px and 1100px, both themes, keyboard navigation and Escape focus return, reader settings without layout shift, context-panel visibility, source-offset integrity, catalog search/sort/filter/reset, draft preservation and lazy inbox maps. All 336 cached evidence quotations retained their source positions. Screenshots cover inbox, library, source, review and concept notes.

Visual updates can be served through existing installed asset paths while an older backend finishes analysis. This compatibility bundle includes the same UI assets and shows an explicit update notice for unavailable linked-note endpoints. Full backend publication remains a separate pending package; neither path stops running analysis.
