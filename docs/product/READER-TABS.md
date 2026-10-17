# HTML reading workspace

- Opened library papers stay in a horizontal, closable tab strip. The plus button opens the catalog. Switching papers restores each paper's selected view and HTML scroll position; tab metadata is stored locally.
- HTML reading collapses bibliographic metadata into a single title row. “논문 정보 펼치기” restores the metadata. The analysis stage stays visible in a compact status row.
- Internal citations open a non-modal preview without scrolling the article. Escape or the close button returns focus to the citation. External source links open separately. The preview does not change the original text or annotation offsets.
- English and Korean paragraphs align in two columns, with natural line wrapping and reduced paragraph padding. Narrow windows stack the translation below its source. Original mathematics remains intact.

Validation: `node tests/reader-tabs.cjs` exercises two isolated papers, compact header height, citation preview, Escape, scroll restoration, and closing the active tab. `node tests/bilingual-navigation.cjs` verifies original text offsets and mathematics after bilingual rendering. Fixtures never enter the personal library.
