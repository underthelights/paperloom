# Paperloom 연구 작업 공간: 기능별 상세 명세 v1

작성: 2026-10-17. 기준 코드: main 318c693 및 이 문서와 같은 브랜치의 UI 변경.
문서의 **목표 / 제안 API / 합격 조건은 구현 완료를 의미하지 않는다**. 현황은 로컬 소스 조사 결과이며 경쟁 서비스의 기능은 아래 공식 공개 자료에 한정한다. 로그인 후 동작, 유료 기능의 정확도, 전체 서비스의 사용성은 검증하지 않았다.

## 1. 제품 결정

Paperloom의 중심 객체는 논문 파일뿐 아니라 **근거가 있는 개념 노트북**이다. 기본 흐름은 `발견 → 수집함 → 논문 원문 → 하이라이트 → 개념 비교 → 연결 탐색 → 다음 읽기`다. 모든 단계에서 이전 문맥으로 돌아갈 수 있어야 한다.

사용자가 X 링크 하나를 넣으면 출처를 보존하고 논문을 확인하여 서가를 제안한다. 읽다가 선택한 수식은 해당 논문 버전에 고정된 근거가 되고, 개념 노트북에 연결된다. 그래프의 간선은 클릭했을 때 연결 이유와 원자료가 나와야 한다. 관련 논문 추천, 논문의 주장, 사용자의 해석, AI의 추론은 서로 구분한다.

## 2. 공식 서비스 조사와 도입 판단

| 서비스 / 공식 출처 | 확인한 기능 | Paperloom에 도입할 설계 | 그대로 가져오지 않을 부분 |
|---|---|---|---|
| [alphaXiv](https://www.alphaxiv.org/) | 논문·연구자·기관을 함께 표시하는 탐색 화면 | 제목 아래 한 줄 기여, 압축된 저자·기관, 개별 인물로 이동 | 인기순 피드를 개인 연구 우선순위로 간주하지 않음 |
| [Connected Papers 소개](https://www.connectedpapers.com/about), [홈](https://www.connectedpapers.com/) | 유사도 기반 지도, 선행·후속 연구 탐색 | 간선 종류, 근거, 시간 필터를 갖춘 논문 지도 | 가까운 배치를 인과관계 또는 직접 인용으로 오인하지 않음 |
| [Moonlight 공식 안내](https://docs.themoonlight.io/help/articles/4008366-whats-moonlight), [기능 설명 PDF](https://www.themoonlight.io/welcome-to-moonlight.pdf) | 선택 영역 설명·번역·대화, 수식 복사, 그림 설명, 인용 미리보기 | 원문 안 선택 도구와 근거 서랍, 본문 위치를 유지하는 미리보기 | AI 설명을 원문 사실로 자동 확정하지 않음 |
| [Zotero 검색](https://www.zotero.org/support/searching), [PDF와 노트](https://www.zotero.org/support/pdf_reader) | 저장 검색, 전문 검색, 주석에서 노트로 이동하면서 인용·원문 링크 유지 | 계속 늘어나는 서가, 스마트 컬렉션, 재사용 가능한 근거 블록 | 폴더 하나에만 자료가 속하는 구조를 강제하지 않음 |
| [Litmaps Monitor](https://docs.litmaps.com/en/articles/9126249-monitor-get-alerts-for-important-research) | 지도에 기반한 정기 검색과 새 결과 확인 | 관심 개념·지도에 맞춘 새 논문 검토함 | 발견 결과를 자동으로 읽은 논문이나 확정된 지식으로 승격하지 않음 |
| [Elicit systematic review](https://elicit.com/solutions/systematic-review) | 문헌 검토·선별·정보 추출·근거 표 | 논문별 방법·가정·실험을 비교하는 근거 표 | 출처가 다른 벤치마크 숫자를 단일 순위로 합치지 않음 |

Connected Papers 소개는 검색 결과에 기능 설명이 있었으나 본문 직접 열기는 JavaScript 안내만 반환했다. 사용자가 제시한 action-prior 브리프 URL은 이번 웹 도구에서 열리지 않아 세부 레이아웃을 확인할 수 없었다. 해당 페이지를 재현했다고 주장하지 않는다. 경쟁 서비스의 비공개 알고리즘이나 API 사용 권한은 확인되지 않았다. 구현은 자체 데이터 모델과 공개 출처를 사용한다.

## 3. 현재 화면 진단과 정보 구조

첨부 화면의 모든 메뉴가 비슷한 테두리 버튼이어서 주요 행동과 이동 메뉴가 구별되지 않는다. 작은 보조 글씨, 장식적인 큰 제목, 넓은 빈 지도는 실제 연구 작업보다 시각적으로 앞선다. 개념 화면에서 연결 탐색이 강조되는 현상은 레이아웃용 `discovery-mode`와 선택 메뉴의 결합으로 설명된다. 코드에는 CSS 보정이 있지만 명시적인 현재 위치가 필요하다.

### 이번 브랜치에 구현한 범위

- 메뉴에 용도를 설명하는 한 줄 문구, 순서 표시, 선택 위치의 왼쪽 강조선을 추가했다.
- `aria-current=page`를 별도로 관리한다. 레이아웃 모드가 메뉴 선택 상태를 결정하지 않는다.
- 수집함 → 서가 → 연결 탐색 → 개념 노트북 순서로 배치했다. 논문 열기는 서가에 속한다.
- 밝은/어두운 테마의 보조 글씨 대비를 높이고 논문 목록 글씨를 확대했다.
- 한국어 제목을 본문과 같은 산세리프 계열로 바꾸고 논문 탭의 가로 스크롤을 허용했다.
- 개념 지도에 경계·배경을 주고, 개념이 2개 미만이면 큰 빈 지도 대신 다음 행동을 안내한다. 연결선이 없는 지도는 기본적으로 접는다. 아래 기능 명세의 신규 백엔드는 이 변경에 포함하지 않는다.

### 목표 화면 구조

```text
왼쪽: 연구 공간             가운데: 현재 작업                  오른쪽: 문맥 서랍
수집함                     링크 입력 / 진행 중 / 검토할 분류   대화·근거·작업 기록
라이브러리 서가             검색 / 저장 보기 / 논문 표          선택 논문 미리보기
논문 연결 탐색              그래프 ↔ 목록 / 관계·연도 필터      연결 이유 / 근거 / 저장
개념 노트북                 개념 목록 → 수식·비교·시각화        원문 근거 / 관련 개념

논문 작업: 개요 | 원문 | 근거·메모 | 연결 논문 | 코드 | 저자
개념 작업: 설명 | 논문 비교 | 수식 실험 | 영상 | 내 노트
```

목표 디자인 규칙: 본문 15–16px/행간 1.7 이상, 보조 정보 12px 이상, 주요 버튼 높이 44px 이상. 본문 대비 4.5:1 이상을 자동 측정한다. 색만으로 선택·실패·관계 종류를 표현하지 않는다. 1440×900 / 1280×800 / 1024×768 및 200% 확대에서 주요 동작이 접근 가능해야 한다. 좁은 창에서는 서랍을 덮개로 열고 본문 최소 폭을 강제하지 않는다. 이 반응형 목표 전체는 아직 미구현이다.

## 4. 기능별 명세

### F01 · 수집함과 자동 분류 — P0

**현황:** `intake.py`, `paperloom_workflow.py`, `static/inbox.js`. 링크·텍스트 입력, arXiv 확인, 분류·개념 연결·후속 분석이 있다. 브라우저 공유 확장은 없다.

**목표:** X/LinkedIn/arXiv/DOI/텍스트/PDF를 같은 수집함에서 받아 중복을 판정하고 분석 범위를 보여준다.

**화면·동작:** 입력 → 출처 카드 → 확인한 논문 → 추천 서가·개념·연결 이유 → 처리 단계. `수집 / 원문 확보 / 분석 / 분류 / 그래프` 각각 상태와 오류를 표시한다. 추천 분류는 사용자가 수정할 수 있고 수정 이후 자동 재분류가 덮어쓰지 않는다. 원문을 얻지 못하면 본문 붙여넣기·파일 추가로 이어진다.

**데이터/제안 계약:** `IntakeSource(id,url,canonical_url,raw_text,fetched_at,status)`; `ImportProposal(paper_id,collection_id,concept_ids,evidence_ids,decision)`. `POST /api/intakes`는 idempotency key와 source 목록을 받고 202 + job_id를 반환한다. 기존 `/api/inbox`와 호환 계층을 둔다.

**오류·합격:** 같은 DOI/arXiv 버전 링크를 3회 넣어도 논문 객체는 하나다. 서로 다른 판본은 `PaperVersion`으로 구분한다. X 접근 실패가 분석 성공으로 보이지 않는다. 입력 출처를 모든 생성 논문에서 역추적할 수 있다. 429는 재시도 시간을 표시하고 수동 수정은 보존한다.

### F02 · 도서관형 서가와 통합 검색 — P0

**현황:** `knowledge.catalog`는 제목·저자·개념·분류·연도 필터와 페이지 단위 목록을 제공한다. 본문 전문 검색과 저장 검색은 없다.

**목표:** 10,000개 자료에서도 목록을 끝없이 스크롤하지 않고 검색·저장 보기로 찾는다.

**화면·동작:** 표/카드 전환, 읽기 상태(미독/읽는 중/읽음/보류), 별표, 최근 읽기, 필터 칩, 저장 보기. 표 기본 열은 제목·연도·핵심 개념·읽기 상태·분석 상태·최근 활동. 저자는 3명 이후 `외 N명`; 전체 명단은 서랍으로 연다. 다중 선택으로 태그·컬렉션을 편집한다. 읽기 상태와 분석 성공을 분리한다.

**데이터/계약:** SQLite FTS5에 제목·초록·본문·사용자 노트를 별도 필드로 인덱싱한다. `SavedView(id,name,predicate_json,sort,columns)`; `ReadingState(paper_id,status,position,last_opened_at)`. `GET /api/library/search?q=&filters=&cursor=&limit=50`은 snippet, hit_field, total 또는 has_more를 제공한다. 조건은 허용된 AST로 검증하며 SQL 문자열을 저장하지 않는다.

**합격:** 새 논문 추가 시 저장 보기 결과가 자동 갱신된다. 원문 미수집/미색인/색인완료를 구분한다. 동일 정렬값도 id를 tie-breaker로 사용해 페이지 중복을 막는다. 목표 성능은 M계열 Mac의 합성 10,000건, warm cache, 100개 질의 p95 < 250ms이며 아직 측정 전이다.

### F03 · 근거 중심 논문 개요 — P0

**현황:** 브리프와 원문·코드·연구실 탭이 있다. 구조화된 주장별 근거 모델은 부족하다.

**목표:** 첫 화면에서 문제, 새 기여, 실제 결과, 한계, 내가 읽어야 하는 이유를 파악한다.

**화면:** 한 줄 기여 → 문제/방법/증거/한계 카드 → 핵심 그림 → 주요 수식 → 코드 대응 → 내 라이브러리와의 연결. 원문·코드·프로젝트·데이터셋은 확인된 링크만 버튼으로 노출한다. 전체 저자 명단이 본문을 밀어내지 않게 한다.

**데이터/계약:** `Claim(id,paper_version_id,type,text,evidence_ids,verification)`와 `Evidence(locator,quote,source_url,content_hash,checked_at)`. `GET /api/papers/:id/brief`는 문단과 근거 ID를 함께 제공한다. 소스 코드 연결은 commit SHA + path + line 범위로 고정한다.

**합격:** 사실 주장 카드의 근거를 클릭하면 해당 원문 위치로 간다. 증거 없는 추론에는 `추론` 표시를 한다. 논문의 자체 주장과 독립 재현을 구분한다. 정확도 수치에는 데이터셋·split·지표·실험 조건이 함께 있어야 한다.

### F04 · HTML/PDF 원문 읽기 — P0

**현황:** `reader.py`의 정제된 HTML·수식·이미지 캐시, HTML 주석과 설명이 있다. PDF는 기본 페이지 렌더링 중심이다.

**목표:** 원문을 떠나지 않고 문장·수식·그림·인용을 이해한다.

**화면·동작:** 문서 목차 / 본문 / 근거 서랍. 선택 툴바 `하이라이트 · Explain · ELI5 · 번역 · 개념에 연결`. 수식에는 LaTeX 복사, 그림에는 영역 선택과 caption 기반 질문. 인용과 내부 그림 번호는 팝오버로 미리 본다. 뒤로 가면 원래 위치와 선택을 복구한다. PDF text layer와 사각형 영역 주석을 지원한다.

**데이터/계약:** `DocumentVersion(id,format,hash,source_url)`; anchor는 HTML `TextQuoteSelector + TextPositionSelector`, PDF `page + normalized_rects + quote`의 tagged union. `POST /api/reader/explain`은 anchor와 explicit context_ids를 받는다. 수식 원본 LaTeX가 없으면 OCR 결과로 표시한다.

**합격:** 확대·창 폭 변경 후에도 주석이 유지된다. 새 문서 hash에서 재결합에 실패하면 `원문 위치 재확인 필요`이며 임의 위치에 붙이지 않는다. PDF가 이미지뿐이면 텍스트 선택 불가/OCR 필요를 설명한다. 그림 질문은 해당 영역과 caption을 출처로 기록한다.

### F05 · 하이라이트·메모·근거 재사용 — P0

**현황:** 주석·설명 이력·개념 연결·Markdown 내보내기와 주석 삭제 시 개념 참조 정리가 있다.

**목표:** 같은 인용을 여러 노트에 재사용하되 원문과 해석을 잃지 않는다.

**동작:** 주석 서랍에서 `정의 / 가정 / 방법 / 결과 / 의문` 라벨을 지정한다. 노트북에 끌어 넣으면 사본 대신 근거 블록을 만든다. 원문 인용, 내 메모, AI 설명을 별도 영역으로 표시한다. 원문으로 이동·연결된 개념 보기·Markdown 인용 복사를 제공한다.

**데이터/계약:** `Annotation`, `NoteBlock(type,body,revision)`, `EvidenceLink(from_id,to_id,relation)`. 저장은 revision 기반 compare-and-swap; 409는 두 초안을 모두 보존한다. 삭제는 참조 개수와 영향을 표시하고 transaction으로 처리한다.

**합격:** 주석 하나를 두 개념에서 참조해도 원문 위치가 동일하다. 주석 삭제 후 dangling ID가 없다. 사용자가 쓴 메모가 AI 재생성으로 덮어써지지 않는다. export에는 제목·저자·판본·locator·출처 URL이 포함된다.

### F06 · 근거를 설명하는 논문 그래프 — P0

**현황:** `discovery.py`의 OpenAlex 표본과 직접 인용·bibliographic coupling·표본 co-citation, 노드 저장, 간선 근거가 있다. 표본 제한과 원문 fallback을 표시한다.

**목표:** 무엇이 연결되는지뿐 아니라 왜 연결되는지를 보여준다. 논문 지도와 개념 지도는 전환 가능한 별도 보기다.

**동작:** seed 1–5개, 연도/관계/내 서가 필터, 그래프↔목록, 선택 노드 미리보기, 읽기 큐, 저장 지도. 기본 그래프는 최대 80노드로 제한하고 추가 탐색을 명시한다. 선택한 노드 이외의 라벨은 확대 수준에 따라 줄인다. 범례에는 직접 인용·참고문헌 유사·같은 개념을 서로 다른 선으로 표시한다.

**계산:** 참고문헌 집합 R에 대해 `BC(i,j)=|Ri∩Rj|/sqrt(|Ri||Rj|)`. 관측한 인용 문헌 집합 C에 대해서만 `CC_sample(i,j)=|Ci∩Cj|/sqrt(|Ci||Cj|)`를 계산한다. 분모가 0이면 `unknown`으로 보존하고 관측된 유사도 0과 구별한다. 직접 인용은 별도 방향 간선이다. 결합 점수·수집 범위·알고리즘 버전을 저장한다. 현재 구현이 이 목표 전체를 만족한다는 뜻은 아니다.

**데이터/계약:** `GraphSnapshot(id,seeds,query,provider,retrieved_at,coverage,algorithm_version)`; `Edge(type,direction,score,evidence_ids)`. `POST /api/graphs`는 job_id, `GET /api/graphs/:id`는 snapshot을 반환한다.

**합격:** 모든 간선 선택 시 종류·근거 문헌·조회일·표본 범위가 보인다. 새 논문이 색인에 없으면 관계 없음으로 단정하지 않는다. 키보드만으로 같은 정보의 목록 보기에 접근한다. 재개 시 seed·필터·배치가 유지된다.

### F07 · 개념 노트북과 수학 전개 — P0, 핵심 차별점

**현황:** 공통 개념 자동 연결, 원문·주석 기반 Markdown 전개, 개인 노트, 공유 논문 기반 16개 노드 지도, ipynb 내보내기가 있다. 현재 ipynb는 실행형 수학 실험장이 아니다.

**목표:** asynchronous inference와 temporal ensemble을 단순 태그가 아닌 정의·가정·수식·코드·적용 논문으로 탐구한다.

**화면:** `직관 → 선행 개념 → 정의·기호 → 유도 → 수치 예제 → 코드 → 논문 비교 → 실패 조건`. 각 단계는 근거·사용자 메모·질문을 갖는 블록이다. 논문별로 다른 정의를 공통 정의에 섞지 않는다. 개념 간 `선행 지식 / 특수 사례 / 대안 / 함께 사용` 관계는 승인된 근거와 함께 표시한다.

**데이터/계약:** `Concept(id,canonical_name,aliases)`, `ConceptDefinition(concept_id,paper_version_id,notation,assumptions,evidence_ids)`, `DerivationStep(input_symbols,equation,reason,evidence_ids)`. `POST /api/concepts/:id/merge-preview`로 병합 영향을 확인한 뒤 transaction으로 병합한다. 되돌리기 이벤트를 보존한다.

**합격:** 동의어를 병합해도 논문·주석·메모가 사라지지 않는다. 각 식의 기호·차원·가정을 추적할 수 있다. 서로 다른 시간 기준의 action을 근거 없이 같은 시간의 앙상블로 결합하지 않는다. 자동 유도와 검증된 계산을 구별한다. 기초 설명을 접어도 원문 수식과 코드 대응은 남는다.

### F08 · 수식 실험과 Manim 영상 — P1

**현황:** 신뢰된 temporal ensemble / async inference 템플릿 2개, 로컬 렌더·재생·MP4 내보내기. 임의 논문에서 완전 자동 영상을 만드는 기능은 없다.

**목표:** 수식의 변수와 가정을 바꾸며 이해하고, 같은 명세에서 로컬 교육 영상을 만든다.

**동작:** 노트북 수식 선택 → storyboard(장면·기호·출처) → 파라미터 미리보기 → 수치 검증 → 저해상도 렌더 → MP4·소스 명세 export. 첫 템플릿은 `w_k=exp(-λ age_k)/Σ exp(-λ age_j)`와 `a=Σ w_k a_k`; λ 슬라이더가 표와 그래프를 동시에 갱신한다. 큐·예상 출력·오류 로그·취소를 표시한다.

**데이터/계약:** `SceneSpec(schema_version,template,parameters,assumptions,evidence_ids)`와 `RenderArtifact(spec_hash,runtime_version,path,status)`. 허용된 템플릿과 typed parameters만 실행한다. 임의 LLM Python을 자동 실행하지 않는다.

**합격:** λ=0이면 N개 가중치가 1/N이고 합이 허용 오차 1e-9 내에서 1이다. 음수 age·빈 배열·비유한 값은 거부한다. 영상에 교육용 예제/논문 재현 여부와 사용 수식을 표시한다. 재렌더 실패가 기존 MP4를 손상하지 않는다. 업로드는 범위 밖이며 로컬 export가 완료 조건이다.

### F09 · 여러 논문 비교와 Survey — P1

**현황:** 분석 지침과 개념 전개에 논문 비교가 있지만 구조화된 비교 표는 없다.

**목표:** 선택한 2–20개 논문을 같은 질문으로 비교하고 모순·빈 근거를 드러낸다.

**동작:** 연구 질문 → 포함/제외 기준 → 후보 검토 → 비교 열(문제·입력·출력·가정·데이터·방법·지표·비용·한계·코드) → 셀 근거 확인 → survey draft. 사용자 확인과 AI 추천을 별도 열로 둔다. 노트북에서 동일 개념을 사용한 논문만 비교할 수 있다.

**데이터/계약:** `Survey(question,criteria,version)`, `ScreeningDecision(paper_id,decision,reason,evidence_ids)`, `ExtractionCell(paper_id,column,value,evidence_ids,status)`. `POST /api/surveys/:id/extract`는 선택 열만 재생성하며 수정한 셀은 보호한다.

**합격:** 모든 비어 있지 않은 사실 셀은 근거나 미검증 표시를 가진다. 데이터셋·split·단위가 다른 결과는 자동 순위화하지 않는다. 제외 논문과 이유를 export에 남긴다. Markdown/CSV export에서도 셀의 출처를 추적할 수 있다.

### F10 · 저자·기관·연구실 — P1

**현황:** 압축 저자 표시, 검색·페이지 명단, 출처 기반 학력·링크 조사와 불확실한 신원 처리. 전역 인물 중복 해소가 부족하다.

**목표:** 수백 명의 공저자가 있어도 헤더를 짧게 유지하고 필요한 사람만 깊게 조사한다.

**동작:** 첫 저자 3명 + 외 N명; 기관 칩은 논문에 명시된 기관이며 주관 기관을 임의 지정하지 않는다. 전체 명단은 이름·기관·역할 검색 서랍. 개인 페이지는 논문 당시 소속 / 현재 확인한 소속 / 학력 / 사이트 / 해당 연구실 관련 논문을 나눠 표시한다.

**데이터/계약:** `Person(external_ids)`; `Affiliation(person_id,institution,lab,valid_at,evidence_id)`; `Education(degree,institution,status,dates,evidence_id)`. ORCID/OpenAlex ID를 우선하되 이름만으로 병합하지 않는다. 각 필드에 checked_at을 둔다.

**합격:** 동명이인은 후보 선택으로 남긴다. 학사·석사·박사 재학과 취득을 구분한다. LinkedIn URL은 실제 연결 근거가 없으면 생성하지 않는다. RT-2/OXE 규모의 합성 저자 500명에서도 헤더 높이는 변하지 않는다. 기관의 최근 논문은 검색 조건과 조회일을 표시한다.

### F11 · 문맥이 보이는 연구 대화 — P1

**현황:** 논문 대화와 수집함 대화, 선택 텍스트 설명이 있다. 문맥 범위와 영구 세션 모델의 확장이 필요하다.

**목표:** 질문 전에 어떤 논문·선택·개념을 참고하는지 사용자가 통제한다.

**동작:** composer 상단에 문맥 칩(논문/선택/개념/비교집합), 출처 상세, 제외 버튼. 답변에서 원문 열기·근거를 노트북에 넣기·후속 질문. 장문이 잘렸으면 잘린 범위와 원문 검색 동작을 표시한다. 정리 결과 적용과 단순 답변을 구분한다.

**데이터/계약:** `Conversation(scope,messages)`; 각 응답에 `ContextManifest(source_ids,versions,locators,truncation)`와 `AnswerCitation` 저장. 도구가 변경할 대상은 변경 전후 diff로 기록한다.

**합격:** 논문을 전환해도 이전 대화가 다른 논문의 근거인 것처럼 보이지 않는다. 인용을 클릭해 원문 근거를 찾을 수 있다. 근거가 없으면 확인 불가를 표시한다. 자동 분류 변경은 undo 가능하다. provider 실패 후 사용자 입력을 유지한다.

### F12 · 새 논문 감시와 읽기 큐 — P2

**현황:** 수집·그래프 조회는 수동 중심이다. 앱 내 주제 감시 기능은 미구현이다.

**목표:** 관심 개념·논문·저자에서 새 자료가 나오면 중복 없이 검토한다.

**동작:** 저장 지도에서 감시 켜기, 주간/수동 새로고침, 포함 키워드·제외 기준, 새 결과의 추천 이유. 자동 저장 대신 검토함을 기본으로 한다. 읽기 큐에 추가하면 출처 지도와 이유를 보존한다.

**데이터/계약:** `Watch(query,seeds,interval,last_cursor)`, `DiscoveryCandidate(identity,reason,evidence_ids,decision)`. 안정적인 논문 ID와 버전별 중복 해소. 실패 후 마지막 성공 cursor에서 재시도한다.

**합격:** 같은 결과를 다시 조회해도 새 알림이 중복되지 않는다. 감시 범위·마지막 성공일·색인 지연을 표시한다. 감시 해제 시 예약 작업이 멈춘다. 알림 없음과 조회 실패를 구분한다.

### F13 · 작업 상태·복구·설치 채널 — P0 기반 작업

**현황:** 분석 진행·부분 실패·재시도와 stable/dev 릴리즈가 있다. 실행 중 작업의 안전한 전환과 사용자에게 보이는 작업 센터를 보강한다.

**목표:** 긴 분석 중에 앱이 멈춘 것처럼 보이지 않으며 중단·재시작에도 결과를 보존한다.

**데이터/동작:** `Job(stage,status,attempt,checkpoint,error,retry_at,artifacts)`; 상태 전이는 `queued → running → succeeded | partial | failed | cancelled | interrupted`. 실제 하위 프로세스 종료 확인 전에는 cancelled로 표시하지 않는다. 재시도는 성공 artifact를 재사용한다. 비용은 실측 usage가 있을 때만 수치로 표시한다.

**합격:** 단계마다 마지막 활동과 다음 행동이 보인다. 앱 강제 종료 fixture에서 재실행 후 interrupted를 보여주고 재시도할 수 있다. 완료 결과를 새 오류로 삭제하지 않는다. 기본 설치는 `/Applications/Paperloom.app` 하나이며 dev 릴리즈가 임의로 별도 앱을 설치하지 않는다. DB migration 전에 백업·무결성 검사를 수행한다.

### F14 · 내보내기와 향후 iPad 필기 — P2

**현황:** Markdown/ipynb/MP4 일부 export. iPad 필기·동기화는 미구현이다.

**목표:** 노트와 근거를 이동 가능하게 만들고 이후 Pencil 필기를 같은 문서에 연결한다.

**데이터/동작:** export manifest에 schema_version, 안정 ID, 문서 hash, 링크, attachment checksum을 기록한다. 필기는 `document_version + page/section + normalized coordinates + strokes`로 저장한다. 오프라인 변경은 revision과 device_id를 사용하며 동시 수정은 충돌 사본을 제공한다.

**합격:** export→빈 프로필 import 후 논문/주석/개념 연결과 attachment checksum이 같다. 계정·동기화 구성 전에는 다른 기기에서 사용 가능하다고 표시하지 않는다. HTML reflow에 고정 좌표 필기를 그대로 붙이지 않는다. iPad 구현에 앞서 export/restore round trip을 통과한다.

## 5. 공통 데이터·API 규칙

- 기존 record JSON을 즉시 전면 교체하지 않는다. `schema_version`을 도입하고 새 정규화 테이블을 추가한 뒤 backfill·검증·읽기 전환 순서로 이행한다. 실패 시 기존 읽기 경로로 복구한다.
- UUID는 내부 참조, DOI/arXiv/OpenAlex는 외부 식별자다. 논문과 판본을 분리한다. 외부 ID 없는 후보는 별도 provenance와 검토 상태를 가진다.
- 변경 API는 검증 실패 400, 없는 객체 404, revision 충돌 409, 비동기 작업 202를 사용한다. 오류 body는 `{code,message,retryable,details}`로 통일한다.
- 다운로드·URL 수집의 SSRF·크기 제한을 유지한다. 원문/코드/댓글은 분석 입력이며 시스템 지침이 아니다. 토큰·개인 DB·비공개 노트는 release artifact나 telemetry에 포함하지 않는다.
- 사용자 메모 수정과 생성된 분석 결과는 별도 revision이다. 생성 결과는 출처 버전·prompt 버전·모델·생성일을 기록한다. 실제 검증 수준을 숫자형 신뢰도처럼 임의 표시하지 않는다.
- 데이터가 없을 때의 `unknown`, 조회하지 않은 `not_requested`, 실패 `failed`, 실제 빈 결과 `empty`를 구분한다.

## 6. 구현 순서와 검증 게이트

| 단계 | 범위 | 완료 조건 |
|---|---|---|
| A · 현재 변경 | 메뉴 선택·설명·글씨·대비 / 이 명세 | 밝게·어둡게 화면 확인, 메뉴 전환 단일 선택, 기존 테스트 통과 |
| B · 읽기 기반 | F01/F02/F03/F04/F05/F13 | 링크 입력→원문→주석→노트북 연결 E2E, 복구 테스트, 검색 성능 기록 |
| C · 지식 연결 | F06/F07/F09/F11 | 간선·비교 셀·유도 단계에서 원문 근거로 왕복, 문맥 격리 테스트 |
| D · 확장 | F08/F10/F12/F14 | 수치 검증, 인물 식별 fixture, 감시 중복 해소, export round trip |

일정은 산정 전이다. P0는 다음 구현 우선순위이며 이번 UI 변경에 모두 포함되는 기능이 아니다.

필수 fixture: 비어 있는 라이브러리, 10,000개 합성 메타데이터, 공저자 500명, HTML 없는 PDF, 같은 제목 다른 판본, 동일 문구가 반복되는 본문, 미색인 최신 논문, 끊어진 링크, 충돌하는 노트 수정, 분석 중 종료. 실제 개인 라이브러리는 테스트 fixture로 커밋하지 않는다.

출시 전: unit + API transaction + navigation E2E + light/dark 스크린샷 + 키보드 접근 + 데이터 백업/복원. 성능 수치와 서비스 정확도는 측정 결과가 없으면 달성했다고 기록하지 않는다.

## 7. 이번 변경의 검증 기록

- Python unit test runner: 65 tests 통과. 이 숫자는 runner 출력이며 고유 시나리오 수를 의미하지 않는다.
- 변경한 JavaScript 4개 파일: Node syntax check 통과.
- `node tests/workspace-navigation.cjs`: 합성 API 응답 + 별도 headless Chrome에서 메뉴 왕복, 현재 메뉴 단일 선택, JavaScript 오류 없음 확인. 실제 개인 DB·실행 앱·AI 분석을 사용하지 않는다. Chrome이 기본이며 `PLAYWRIGHT_CHANNEL`로 설치된 Playwright 채널을 선택할 수 있다.
- 1440×900 밝은/어두운 테마 스크린샷을 확인했다. 전체 반응형·전체 대비 기준·신규 명세 기능의 검증은 아직 수행하지 않았다.
