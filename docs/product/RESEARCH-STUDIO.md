# Research workspace interface

The workspace prioritizes reading and evidence over introductory copy and tool panels. Existing alphaXiv paper/author/source presentation and Zotero's library/collection organization were reviewed as references. This implementation uses its own layout and assets.

## Information hierarchy

- Navigation: a 72px icon-and-label rail replaces the persistent paper sidebar. Search moves to a global command bar above the document tabs, with Enter opening matching library results. Active navigation follows `aria-current`, independent of layout classes or hover.
- Library: a master/detail workspace pairs bibliographic rows with a 300px selected-paper inspector. Row background or keyboard navigation changes the preview; title buttons and inspector actions open source, review or related papers. Previews fetch read-only metadata once per record update, cache at most 40 entries, and reject stale responses. Search and sort stay available; less common filters expand on demand.
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

## Synchronized operation walkthrough

The second video at https://x.com/kuan_yiii/status/2110599586385375554/video/2 and the author-linked https://acastapaloma.github.io/pi/ demonstrate synchronized observations, operation timelines and narration. Paperloom uses independently authored SVG and arithmetic; the reference model is not treated as DreamZero evidence.

DreamZero's existing 13 source-linked stages and 31 internal operations now pair a stage outline with a central interactive lab and an evidence panel. Each stage initializes the relevant phase and displays its actual documented input/output shape. The lab implements fixed 2×2 interpolation, velocity targets, MSE and its derivative, and constant-velocity Euler integration. Training and inference are explicitly distinguished. Playback follows observation → encoding → noise → velocity → integration → action → new observation. This is an educational example, not model execution or a measured tensor trace. Attention, patchification and permutation retain their separate numeric demonstrations. Other papers require their own evidence-linked walkthrough and do not receive DreamZero's lab.

Lab tests verify arithmetic, step mapping, source links, playback cleanup, mode switching, escaping, dark colors and narrow layouts without network requests.

## Source/config tensor traces

The default operation view now shows actual input → operation → output shapes and a source-linked axis-operation table. Numeric teaching labs are collapsed and created only on request. A compact profile identifies the selected repository, full commit, configuration, CLI overrides, dimensions and unresolved runtime values. DreamZero's bundled trace uses the official DROID LoRA script; its 176×320 camera views form a 352×640 mosaic, a 16×F×44×80 video latent and 880F patch tokens. T=33-derived values are conditional arithmetic, not captured tensors. Deployment dimensions are not silently substituted for the training profile.

Every new analysis now writes a bounded tracked-file inventory with hashes, line counts, configuration candidates and LFS limitations. A separate tensor-audit worker reads the actual code and one configuration, returns a structured profile and trace, then receives at most one repair attempt. The validator checks pinned commit/file/line existence and training/inference coverage. Symlinks outside the checkout and LFS pointers cannot substantiate source facts. This is not semantic or execution proof: the independent report reviewer still checks whether code operations support the stated dimensions. Missing evidence keeps the report in review; code-unavailable papers retain an explicit unavailable result. Source collection and analysis failures preserve previously saved papers and notes.

DreamZero was also passed through this dedicated audit against the cached official checkout, without importing the research repository or loading weights. Production publication retains the report's local provenance; no library records or run artifacts enter Git.
