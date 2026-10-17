# Guide 5: 실행 체크리스트와 완료 조건

이 문서는 survey가 **실제로 완료되었는지** 판단하기 위한 실행 체크리스트다.  
Main Agent는 `overview.md`만 만들고 종료해서는 안 되며, 이 문서의 조건을 만족해야 survey를 완료로 간주한다.

## 1. 기본 완료 조건

아래 항목이 모두 충족되어야 survey 완료로 본다.

1. `Survey_Results/[YYYY-MM-DD_Topic]/overview.md`가 존재한다.
2. 대표 method paper로 선정한 각 논문마다 `Survey_Results/[YYYY-MM-DD_Topic]/papers/[Venue_Year_FirstAuthor_ShortTitle].md`가 존재한다.
3. 핵심 task-defining artifact로 선정한 각 항목마다 `Survey_Results/[YYYY-MM-DD_Topic]/datasets/[Venue_Year_FirstAuthor_ShortTitle].md`가 존재한다.
4. 각 `papers/*.md`의 `Methodology & Implementation Walkthrough`에 최소한 `전체 구조 overview`, `end-to-end forward flow`, `module snapshot table 또는 동등 수준의 모듈별 구조 설명`, `입력/출력`, `tensor shape`, `모듈 motivation`, `target bottleneck`, `core operator`, `why not simpler baseline`, `학습/추론 흐름`, `code anchor`가 통합되어 있다.
5. 공식 코드가 있는 대표 논문은 Methodology 본문 안에서 단순 경로 나열이 아니라 구체적인 함수/클래스 설명과 구현 근거를 제공한다. 별도의 implementation appendix가 있더라도 본문이 얕으면 통과로 보지 않는다.
6. 각 `papers/*.md`에 `Experimental / Evaluation Setup` 섹션이 있고, dataset/protocol, num_frames 또는 input length, resolution 또는 hardware/environment, backbone 또는 핵심 system config, optimizer/schedule, batch size, augmentation 또는 auxiliary supervision, inference/deployment setting, paper-code mismatch가 정리되어 있다.
7. `Experiments & Performance`에 main result table이 있고, ablation 또는 핵심 analysis table이 실제 숫자와 함께 들어 있다. 논문에 실질적 ablation이 없으면 그 사실이 명시되어 있다.
8. 각 `datasets/*.md`에는 최소한 artifact 규모/설정, split, metric, protocol, 대표 baseline 또는 comparison-anchor table, artifact의 의미와 한계가 들어 있다.
9. 공식 GitHub가 있는 대표 논문은 기본적으로 실제 clone을 시도했고, 성공 시 `Survey_Results/[YYYY-MM-DD_Topic]/codes/[Repo_Name]/`와 `codes/*_analysis.md`가 존재한다. 실패 시에는 왜 clone / 코드 분석을 하지 못했는지 exact reason이 paper report 또는 validation에 명시되어 있다.
10. `overview.md`에는 대표 논문 지도, taxonomy, evaluation-axis coverage, performance comparison, open problems가 들어 있다.
11. `papers/*.md`와 `datasets/*.md`는 `Guide 2`의 상세 포맷을 따른다.
12. 핵심 evaluation axis에서 strong result를 내는 top-tier main-track 논문과 recent strong arXiv / OpenReview paper를 모두 검토했고, 제외한 항목은 이유가 기록되어 있다.
13. 핵심 evaluation axis에서 후속 논문들이 반복적으로 비교하는 `comparison-anchor paper`를 식별했고, 포함/제외 판단이 기록되어 있다.
14. representative selection 과정에서 citation/impact를 보조 신호로 사용했고, high-impact omission audit 또는 유사 후보 tie-break 판단이 `overview.md`, `run_validation.md`, 또는 작업 메모에 기록되어 있다. 최근 2~3년 논문은 raw citation이 낮다는 이유만으로 대표세트에서 밀려나지 않는다.
15. 공식 코드가 있는 논문은 가능하면 `code analysis -> synthesis -> paper.md` 순서가 지켜졌고, 최소한 paper.md의 method와 experimental/evaluation setup이 code analysis와 정합적이다.
16. 핵심 수식이 있는 `papers/*.md`는 실제 equation excerpt 또는 LaTeX 재작성, `$...$` / `$$...$$` 기반의 읽기 쉬운 표기, 변수 설명, 수식 의미 해설, equation-to-code mapping을 포함한다.
17. official code가 있는 `papers/*.md`는 최소 `1`개 이상의 **실제 코드 발췌**를 포함한다. generic pseudocode만으로 대체하면 통과로 보지 않으며, 각 발췌에는 inline comment 또는 줄단위 설명이 함께 있어야 한다.
18. main scope 안의 recent frontier paper 중 source 접근과 code analysis가 가능한 항목은 원칙적으로 full report가 있어야 한다. overview-only로 남길 경우 `adjacent branch`, `duplicate coverage`, `source/code blocked`, `explicit user scope limit` 중 하나의 사유가 기록되어 있다.
19. overview-only 항목은 `adjacent branch`, `deferred frontier`, `excluded` 중 하나로 분류되어 있고, `overview.md`와 `run_validation.md`에 같은 분류와 이유가 기록되어 있다.
20. representative report는 main agent review gate를 통과했다. review gate는 최소한 `method 깊이`, `forward flow 선명도`, `module rationale quality`, `integrated code grounding`, `equation grounding`, `actual code excerpt quality`, `experimental/evaluation setup`, `numeric ablation`, `evaluation-axis coverage`, `comparison-anchor coverage`, `citation/high-impact coverage`, `recent frontier promotion`, `evidence tag`, `불확실성 표시`를 확인한다.

위 1~20 중 하나라도 빠지면 survey는 `incomplete`다.

## 2. overview-only 중단 금지

다음 상태는 survey 완료가 아니다.

- `overview.md`만 있고 `papers/*.md`가 거의 없는 상태
- 핵심 task-defining artifact가 overview에만 있고 `datasets/*.md`가 없는 상태
- representative paper shortlist만 정해두고 개별 paper report를 쓰지 않은 상태
- code availability만 정리하고 실제 paper report와 code analysis를 연결하지 않은 상태
- recent sweep / scouting 결과만 적고 archival survey 산출물을 완성하지 않은 상태
- top-tier paper와 recent strong preprint를 충분히 검토하지 않은 채 대표세트를 임의 개수로 빨리 닫은 상태
- 핵심 evaluation axis에서 반복 비교되는 comparison-anchor paper를 식별하지 않은 상태
- citation/impact expansion을 했다고 적어 놓고도 high-impact omission audit이나 tie-break 근거를 남기지 않은 상태
- main scope 안의 recent frontier paper를 특별한 이유 없이 overview-only로 남긴 상태
- method 설명이 전체 구조 overview와 forward flow 없이 모듈 bullet만 남아 있는 상태
- method 설명에 입력/출력/shape/motivation이 빠져 있어 실제 구조를 따라갈 수 없는 상태
- module motivation은 있지만 target bottleneck, core operator, simpler baseline 대비 이유가 없어 원리가 드러나지 않는 상태
- code 설명이 Methodology 안에 통합되지 않고, 별도 섹션에서 경로만 나열하는 상태
- 실제 코드 발췌가 있어도 init/config 수준이고 핵심 메커니즘 block를 보여주지 못하는 상태
- Experimental / Evaluation Setup이 없거나 재현에 필요한 핵심 setting이 빠진 상태
- 핵심 수식이 있는 논문인데 actual equation excerpt, notation 설명, 수식 의미 해설, equation-to-code mapping이 빠진 상태
- 공식 코드가 있는데 실제 코드 발췌 없이 generic pseudocode만 있거나, 코드 발췌에 설명 comment가 거의 없는 상태
- ablation 섹션에 숫자 table 없이 해석 bullet만 있는 상태
- 공식 코드가 있는데도 code analysis 없이 논문 요약만으로 method를 써버린 상태

Main Agent는 이런 상태에서 작업을 끝내지 말아야 한다.

## 3. 대표 논문 수와 paper report 수의 관계

- 대표 method paper를 `N편` 선정했다면, 원칙적으로 `papers/*.md`도 최소 `N개` 있어야 한다.
- 핵심 task-defining artifact를 `M개` 선정했다면, 원칙적으로 `datasets/*.md`도 최소 `M개` 있어야 한다.
- overview-only 항목은 허용되지만, 그것은 **대표 논문으로 선정하지 않은 논문**에 한정된다.
- 즉, `overview.md`의 대표 논문 지도에 full report 대상이라고 올린 항목은 method면 `papers/*.md`, task-defining artifact면 `datasets/*.md`가 반드시 있어야 한다.

## 4. 재조사(resurvey) / 기존 topic 덮어쓰기 규칙

기존 topic을 다시 조사할 때는 다음을 따른다.

1. 기존 결과 폴더는 그대로 보존한다. 이름을 바꾸거나 덮어쓰지 않는다.
2. 새 결과는 새 실행일 기준 날짜 prefix를 붙인 `[YYYY-MM-DD_Topic]/` 폴더에 작성한다.
3. 새 결과 폴더에는 반드시 `compare_old_vs_new.md`를 만들고, 비교 대상 old 폴더 경로를 명시한다.

`compare_old_vs_new.md`에는 최소한 다음을 포함한다.

- old와 new의 대표 논문 수
- old와 new의 task-defining artifact report 수
- old와 new의 code analysis 수
- evaluation-axis coverage 차이
- comparison-anchor coverage 차이
- 새로 추가된 recent papers
- 빠졌거나 제외된 논문과 그 이유
- guide 업데이트에 따라 실제로 달라진 점

## 5. guide 업데이트 후 validation 규칙

guide가 바뀐 뒤 처음 수행하는 survey 또는 resurvey에서는 반드시 `run_validation.md`를 만든다.

파일 위치:
- `Survey_Results/[YYYY-MM-DD_Topic]/run_validation.md`

이 문서에는 최소한 다음 체크리스트를 적는다.

- `overview.md` 생성 여부
- 대표 논문 수
- 생성된 `papers/*.md` 수
- 생성된 `datasets/*.md` 수
- `method quality gate` 통과 paper 수
- `module rationale gate` 통과 paper 수
- `integrated methodology/code grounding` 통과 paper 수
- `experimental/evaluation setup` 통과 paper 수
- `numeric ablation table` 포함 paper 수
- `code-grounded methodology` 통과 paper 수
- `equation grounding` 통과 paper 수
- `notation / equation comment` 통과 paper 수
- `comparison-anchor coverage` 충족 여부
- `citation/high-impact audit` 수행 여부
- `recent frontier reviewed` 수
- `recent frontier promoted to full report` 수
- `recent frontier deferred` 수와 사유
- 공식 코드가 있는 대표 논문 수
- 실제 clone 시도 수
- 실제 코드 분석 수행 수
- task-defining artifact reference 탐색 여부
- task-defining artifact cited-by 탐색 여부
- recent arXiv / OpenReview sweep 여부
- recent top-tier main-track paper coverage 여부
- recent strong preprint coverage 여부
- overview-only audit table 존재 여부
- setup completeness 세부 체크 여부
- actual code excerpt 세부 체크 여부
- mechanism-level code excerpt 세부 체크 여부
- annotated code excerpt 세부 체크 여부
- equation-to-code mapping 세부 체크 여부
- pseudocode-only paper 수
- table에 venue/year 표기 여부
- representative paper별 review gate 통과 여부
- old vs new compare 문서 생성 여부
- multi-agent를 썼다면 단계별 agent scaling 적용 여부

`run_validation.md`에는 가능하면 아래 표도 함께 적으십시오.

| Candidate | Scope | Frontier? | Code Clone | Code Analysis | Full Report | If No, Why |
|---|---|---|---|---|---|---|
| paper name | main / adjacent / out | yes / no | done / blocked | done / partial / none | yes / no | deferred reason |

## 6. 사용자가 비교를 원할 때의 동작

사용자가 `guide 업데이트 후 어떻게 달라졌는지`, `old와 new를 비교해달라`, `가이드가 실제로 반영됐는지 보자`라고 말하면:

1. `compare_old_vs_new.md`를 만든다.
2. `run_validation.md`를 만든다.
3. 최종 응답에서는 반드시
   - 어떤 가이드 항목이 새로 적용됐는지
   - 이전 결과와 무엇이 달라졌는지
   - 아직 미완료인 항목이 있는지
   를 명시한다.

## 7. 미완료 상태의 응답 규칙

시간, 툴 제약, 코드 clone 실패 등으로 모든 paper report를 완성하지 못했다면:

- survey를 완료라고 말하지 않는다.
- 어떤 항목이 남았는지 구체적으로 적는다.
- 가능한 경우 바로 이어서 남은 paper report를 계속 작성한다.

기본 원칙은 간단하다.

**survey = overview + representative paper reports + (가능한 경우) code analyses + validation**
  
여기서 `representative paper reports`는 `papers/*.md`의 method report와 `datasets/*.md`의 task-defining artifact report를 함께 의미하며, 단순 파일 개수가 아니라 `method quality gate + evaluation-axis coverage gate + comparison-anchor gate + numeric ablation gate + code-grounding gate + review gate`를 통과한 보고서를 뜻한다.
