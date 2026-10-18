# 원문 수식 전개

HTML MathML의 독립 수식과 표 안 수식 아래에 단계별 전개를 표시한다. 원문 MathML·텍스트는 수정하지 않고, 생성된 패널에 `data-reader-generated`를 지정하여 기존 UTF-16 하이라이트 위치와 번역 placeholder를 보존한다. 기본 크기는 독립 수식 24px, 모바일 22px이다.

DreamZero(arXiv 2602.15922)의 식 (1)–(6)은 원문과 고정 코드 커밋을 확인한 28개 설명을 제공한다. 원문 anchor와 LaTeX가 모두 일치할 때만 적용한다. 설명은 목적, 기호, 유도, 텐서 적용, 교육용 숫자 예제 및 확인 한계를 구분한다. 논문의 데이터 방향 시간 t와 구현의 노이즈 방향 sigma=1−t를 혼동하지 않는다. 실제 GPU 실행 또는 모델 출력 검증을 의미하지 않는다.

다른 수식은 검증된 설명이 없음을 표시한다. 사용자가 전개 생성을 누르면 기존 reader annotation/explain 경로로 원문 문맥 기반 AI 설명을 생성하고 저장한다. 사용량이 발생한다. 원문에 없는 코드 shape·설정은 확인 불가로 표시하도록 요청한다. 이 경로는 저장소 코드를 새로 실행하거나 검증하지 않는다. 저장된 답변은 수식 아래에서 다시 열 수 있다. 수식 구조가 없는 PDF 추출 텍스트에는 이 패널이 자동 생성되지 않는다.

검증: `node tests/reader-equations.cjs`, `node tests/reader-tabs.cjs`, `node tests/paper-walkthrough.cjs`, Python unittest 전체. 실제 DreamZero HTML은 별도 브라우저 fixture에서 확인하며 개인 DB와 실행 중 분석은 변경하지 않는다.
