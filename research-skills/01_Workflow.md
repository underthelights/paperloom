# Guide 1: 워크플로와 디렉터리 구조

## 1. 디렉터리 및 네이밍 규칙
작업 중인 [Topic]에 대해 반드시 아래 구조와 파일명 규칙을 엄수하십시오.
* **Topic Folder Rule:** topic 폴더는 survey 실행일 기준 YYYY-MM-DD 날짜 prefix를 붙여 `[YYYY-MM-DD_Topic]` 형식으로 만드십시오. 예: `2026-06-06_World_Model_for_Robot_Learning/`
* **Naming Rule:** `[Conf_Year_Author_Title].md` (예: `[CVPR_2023_Smith_Video_Retrieval].md`)
[workspace_root]/
 └── Survey_Results/
      └── [YYYY-MM-DD_Topic]/
           ├── overview.md
           ├── papers/
           │    └── [Conf_Year_Author_Title].md
           ├── datasets/
           │    └── [Conf_Year_Author_Title].md
           ├── codes/
           │    ├── [Repo_Name]/ (git clone directory)
           │    └── [Conf_Year_Author_Title]_analysis.md
           ├── notes/ (선택: search ledger, clone queue, report queue 같은 작업 노트)
           └── sources/ (선택: 수집한 PDF, tex, API 응답 dump 같은 원자료)

모든 survey 산출물은 반드시 `Survey_Results/[YYYY-MM-DD_Topic]/` 아래에 저장하십시오. 워크스페이스 루트 바로 아래에 topic 폴더를 새로 만들지 마십시오.
`papers/`는 method / system / model paper 전용으로 쓰고, 핵심 dataset / benchmark / evaluation protocol paper는 `datasets/` 아래에 저장하십시오. `papers/datasets/` 같은 중첩 구조는 만들지 마십시오.

## 2. 필터링 및 중단 조건 (Main Agent 권한)
Main 에이전트는 Sub 1이 가져온 논문을 다음 기준으로 엄격히 평가하고, 조건에 맞지 않으면 즉각 폐기(Drop)하거나 서베이를 중단(Stop)하십시오.

* **[Drop] 저품질/무관련 논문 배제 기준:**
  1. Venue Tier: `04_Conf_Journal_List.md`에 포함되지 않은 학회/저널이면서 출판된 지 2년이 넘었는데 인용수가 10회 미만인 논문.
  2. Outdated: 기초(Foundational) 논문이 아님에도 불구하고 출판된 지 5년 이상 경과하여 현재 SOTA(State-of-the-Art)와 거리가 먼 논문.
  3. Low Relevance: 타겟 Topic과 키워드는 겹치나 실제 풀고자 하는 문제(Task)가 다른 경우.
* **[Pre-Stop] 중단 전에 반드시 먼저 충족해야 하는 커버리지 게이트:**
  1. 해당 분야의 `main scope`, `adjacent branch`, `out-of-scope`가 정리되어 있을 것.
  2. 해당 분야의 핵심 `evaluation axis` 목록이 정리되어 있을 것. 여기서 evaluation axis는 dataset / benchmark / evaluation protocol / deployment setting / system constraint / challenge track 등을 포함합니다.
  3. 각 핵심 evaluation axis마다 최소한 `task-defining artifact + comparison-anchor paper + recent frontier paper`가 포함되어 있을 것.
  4. `foundational / turning-point / recent strong papers`의 시간축 커버리지가 확보되어 있을 것.
  5. citation 또는 영향력 기반으로 확장한 high-impact paper 후보를 한 번 이상 점검했을 것.
  6. 대표 논문 중 공식 GitHub가 있는 항목은 코드 availability 확인에 그치지 말고 실제 clone을 시도했을 것. clone 및 코드 분석까지 완료했거나, 실패 원인을 기록했을 것.
  7. 핵심 evaluation axis를 정의하는 benchmark / dataset / protocol / survey / system paper의 reference / related work에 등장하는 대표 논문과, 그 축을 인용한 후속 주요 논문을 한 번 이상 점검했을 것.
  8. 최근 `arXiv` 또는 이에 준하는 preprint source에서 최신 관련 논문을 별도로 훑어 보았고, 채택 여부를 판단했을 것.
  9. 핵심 evaluation axis에서 반복 비교되는 top-tier main-track 논문과, 최근 strong result를 내는 arXiv / OpenReview preprint를 모두 포함 후보로 검토했을 것.
  10. 핵심 evaluation axis의 main result table뿐 아니라, related work, comparison table, leaderboard snapshot, challenge report 등에서 반복 등장하는 `comparison-anchor paper`를 식별하고 포함/제외를 판단했을 것.
* **[Stop] 서베이 완료(Saturation) 판단 기준:**
  1. 위의 `Pre-Stop` 조건을 모두 만족한 상태에서, 핵심 evaluation axis 이름, 파생 키워드, 최근 venue/year, citation-driven expansion 경로를 각각 점검했음에도 axis-critical paper나 high-impact paper의 중요한 누락이 더 이상 발견되지 않을 때.
  2. 새로 발견되는 논문이 기존 대표 논문의 소규모 변형, 동일 evaluation axis의 경미한 개선, 또는 본 topic의 `main scope` 밖 `adjacent branch` 확장에 머무를 때.
  3. 새 검색 결과가 `taxonomy상 새 범주`, `새로운 evaluation axis`, `새로운 protocol/setting`, `새로운 system constraint`를 추가하지 못하고 기존 정리의 세부 변형만 늘릴 때.
  4. 단, `대표 논문으로 선정한 항목들에 대한 papers/*.md가 모두 생성되기 전에는 stop으로 간주하지 마십시오.`

## 2.4 범위 잠금과 공통 용어
Main 에이전트는 본격 탐색에 들어가기 전에 아래 용어를 먼저 확정하거나, 최소한 working assumption으로 기록하십시오.

* **Main Scope:** 이번 run에서 full report 대상으로 직접 다루는 중심 문제 / 설정 / task 범위입니다.
* **Adjacent Branch:** 주제와 가깝지만 main scope와는 다른 하위 문제, 응용 setting, modality shift, open-vocabulary 확장, weakly-supervised branch, system variant 등을 뜻합니다.
* **Out-of-Scope:** 현재 survey의 중심 범위를 벗어난 주제입니다.
* **Core Evaluation Axis:** representative set를 닫기 전에 반드시 확인해야 하는 평가 축입니다. 일반적으로 dataset / benchmark / protocol / deployment setting / system constraint / challenge track / hardware regime 등이 여기에 해당합니다.
* **Task-Defining Artifact:** dataset / benchmark / protocol / seminal system paper처럼 field의 평가 기준이나 문제 정의를 세우는 artifact입니다.
* **Comparison-Anchor Paper:** 후속 논문들이 related work, main table, comparison table, leaderboard, challenge report에서 반복 비교하는 기준 논문입니다.
* **Recent Frontier Paper:** 최근 2~3년 내 발표된 strong paper로서 main scope 안의 핵심 evaluation axis에서 의미 있는 성능, 새로운 설계, 반복 비교 신호를 갖는 항목입니다.
* **Deferred Frontier:** 중요하지만 현재 batch에서 아직 full report로 승격하지 못한 recent frontier paper입니다.
* **Code-Ready Paper:** official code clone과 기본 코드 분석까지 완료되어 synthesis만 하면 `papers/*.md`로 닫을 수 있는 논문입니다.

## 2.5 기본 커버리지
사용자가 별도로 축약을 요청하지 않는 한, Main 에이전트는 다음 범위를 기본값으로 사용하십시오.
* **Scope Lock Policy:** survey를 시작할 때 이번 run의 `main scope`, `adjacent branch`, `out-of-scope`를 먼저 정하십시오. overview-only 판단과 representative selection은 이 scope lock을 기준으로 해야 합니다.
* **Representative Paper Set:** 대표 논문 수를 미리 고정하지 마십시오. 넓은 분야는 많이, 좁은 분야는 적게 포함하는 것이 정상입니다.
* **No Fixed Cap:** `대표 논문 12편`, `핵심 논문 10편`처럼 임의 상한을 먼저 정하지 마십시오. 먼저 넓게 후보를 수집하고, coverage 근거를 본 뒤에만 대표세트를 닫으십시오.
* **Count Policy:** 논문 개수는 목표치가 아니라 coverage를 수행한 뒤의 결과값입니다. `n편 채우기`를 stop 기준으로 사용하지 마십시오.
* **Coverage Mix:** 최소한 `foundational paper`, `turning-point paper`, `최근 2~3년 strong paper`, `핵심 task-defining artifact`를 모두 포함하십시오.
* **Evaluation-Axis Coverage Policy:** 대표세트를 닫기 전에 각 핵심 evaluation axis마다 최소 `task-defining artifact + comparison-anchor paper + recent frontier paper`가 채워졌는지 확인하십시오.
* **Comparison-Anchor Policy:** 특정 분야의 후속 논문들에서 반복적으로 언급되고, 핵심 evaluation table / comparison table에 자주 등장하는 논문은 `comparison-anchor paper`로 간주하고 기본적으로 대표 논문 포함 후보로 취급하십시오.
* **Anchor Coverage Policy:** 대표세트를 닫기 전에 각 핵심 evaluation axis마다 “후속 논문들이 무엇을 기본 비교군으로 삼는가”를 확인하십시오. task-defining artifact, turning-point paper와 별개로, 실제 field standard comparison anchor가 있으면 빠지지 않도록 하십시오.
* **Anchor Exclusion Policy:** `comparison-anchor paper`를 full report에서 제외했다면 `overview.md`에 제외 이유를 적으십시오. 단순히 paper 수를 줄이기 위한 제외는 허용하지 않습니다.
* **Top-tier Inclusion Policy:** 핵심 evaluation axis에서 strong result를 보고하거나, 핵심 설정에서 중요한 질적 기여를 보이는 main-track top-tier 논문은 기본적으로 대표 논문 포함 후보입니다.
* **Recent Strong Preprint Policy:** 최근 `arXiv` / `OpenReview` preprint라도 핵심 evaluation axis에서 high-performing이거나 여러 표/리더보드/비교 문맥에서 강한 비교군으로 반복 등장하면 기본적으로 대표 논문 포함 후보입니다.
* **Recent Frontier Promotion Policy:** 최근 2~3년 내의 main-scope strong paper는 기본적으로 full report 대상으로 승격하십시오. 단순히 “이번 배치는 기초/정전(canonical) 논문 우선”이라는 이유만으로 overview-only로 남기지 마십시오.
* **Code-Ready Promotion Rule:** official code clone과 code analysis가 완료된 recent frontier paper는, task shift / source blockage / 명백한 중복 같은 사유가 없는 한 `papers/*.md`까지 닫는 것을 기본값으로 하십시오.
* **Overview-Only Type Policy:** overview-only 항목은 `adjacent branch`, `deferred frontier`, `excluded from representative set` 중 하나로 분류하십시오. 모든 overview-only 항목은 왜 full report가 아닌지 이유를 남겨야 합니다.
* **Overview-Only Restriction:** `main scope` 안의 recent frontier paper를 overview-only로 둘 수 있는 사유는 `adjacent branch가 아님에도 task shift가 큼`, `기존 full report와 실질적으로 중복`, `source/code 접근 불가`, `사용자가 명시적으로 scope를 줄임` 정도로 제한하십시오.
* **Explicit Exclusion Policy:** 위 후보를 full report에서 제외했다면 `overview.md`에 제외 이유를 적으십시오. 단순히 paper 수를 줄이기 위한 제외는 허용하지 않습니다.
* **Overview Breadth:** `overview.md`에는 taxonomy뿐 아니라 representative paper map과 benchmark landscape를 함께 정리하십시오.
* **Evaluation-Axis-Driven Coverage:** 먼저 핵심 evaluation axis를 식별한 뒤, axis별 대표 논문을 역으로 채우십시오. empirical ML에서는 dataset/benchmark가 대표 axis지만, system/agent/robotics/HCI 분야처럼 protocol, hardware, latency, deployment constraint가 더 중요한 경우에는 그 축을 우선하십시오.
* **Dataset Artifact Policy:** 핵심 dataset / benchmark / protocol paper는 method paper와 분리하여 `datasets/*.md`로 정리하십시오. dataset report는 task 정의, 규모, split, metric, protocol, bias, 대표 baseline, 이후 method coverage와의 연결을 포함해야 합니다. dataset이 아닌 protocol/system artifact라도 같은 포맷을 응용해 정리하십시오.
* **Citation-Aware Expansion:** 가능하면 `Google Scholar`를 사용하고, 접근이 어렵거나 불안정하면 `Semantic Scholar`, `OpenAlex`, 공식 venue 검색 결과 등으로 인용도와 영향력을 보조적으로 확인하십시오.
* **Citation Signal Policy:** citation count와 impact는 representative selection의 보조 신호로 사용하십시오. high-impact paper 누락을 복구하고, 비슷한 역할의 후보들 사이 우선순위를 정하는 데 활용하되, 단독 기준으로 사용하지 마십시오.
* **Age-Normalized Citation Policy:** 최근 2~3년의 `recent frontier paper`는 누적 citation이 낮을 수 있으므로, raw citation보다 `main scope 적합성`, `top-tier 여부`, `핵심 evaluation axis에서의 strong result`, `comparison-anchor 신호`를 우선하십시오.
* **Citation Tie-Break Rule:** 같은 evaluation axis에서 비슷한 역할을 수행하는 후보가 여러 개일 때는 citation/impact를 tie-break 신호로 사용할 수 있습니다. 다만 older paper의 높은 누적 citation만으로 recent frontier를 밀어내지 마십시오.
* **Axis Citation Expansion:** 각 핵심 evaluation axis를 정의하는 benchmark / dataset / protocol / system artifact가 인용하는 prior 대표 논문과, 그 artifact를 인용한 후속 논문들을 함께 확인하십시오.
* **Recent Preprint Sweep:** top-tier venue 검색만으로 끝내지 말고, 최근 `arXiv`, `OpenReview`, 공식 프로젝트 페이지에 공개된 최신 preprint도 별도로 확인하십시오. 특히 최근 1년 내 관련 축에서 등장한 strong paper는 venue 미확정이어도 누락 방지 후보로 검토하십시오.
* **Stop Priority:** taxonomy 포화보다 `핵심 evaluation axis coverage 충족 여부`, `recent frontier promotion 상태`, `중요 high-impact paper 누락 여부`를 더 우선해서 보십시오.
* **Code Coverage:** 공식 GitHub가 있는 대표 논문은 기본적으로 실제 코드를 clone하여 분석하십시오. availability 확인만 하고 clone을 건너뛰지 마십시오. 코드가 없거나 private이거나 깨져 있으면 실패로 처리하지 말고 상태와 실패 원인을 기록하십시오.
* **Code-First Policy:** 공식 코드가 있는 논문은 가능하면 `code analysis -> paper.md 작성` 순서를 따르십시오. method 설명을 논문 요약만으로 먼저 확정하지 마십시오.
* **Synthesis Policy:** 공식 코드가 있는 논문은 `code evidence`와 `paper evidence`를 따로 수집한 뒤, 핵심 수식 `1~3`개와 실제 코드 발췌 `1~2`개를 포함하는 합성(synthesis)으로 최종 `paper.md`를 닫으십시오. 경로만 나열한 code reference나 논문 문장 재서술만으로 최종본을 확정하지 마십시오.
* **Integrated Methodology Policy:** `papers/*.md`에서 논문 method 설명과 code 구현 설명을 분리된 두 섹션으로 따로 놀게 두지 마십시오. `전체 구조 overview -> forward flow -> 모듈별 설명` 안에 code 근거와 함수/클래스/line anchor가 자연스럽게 통합되어야 합니다.
* **Method Quality Gate:** `papers/*.md`의 Methodology는 최소한 `전체 구조 overview`, `end-to-end forward flow`, `모듈별 입력/출력`, `tensor shape`, `모듈 motivation`, `전후 call flow`, `핵심 수식`, `학습/추론 흐름`, `구현 근거`가 들어 있어야 합니다. `backbone / transformer / head` 수준의 얕은 bullet 몇 개만으로 통과시키지 마십시오.
* **Equation Grounding Policy:** 핵심 수식이 있는 논문은 `papers/*.md`에 실제 equation excerpt 또는 LaTeX 재작성, 변수 의미, 왜 중요한지, 그리고 code에서 대응되는 함수/변수를 함께 적으십시오. 수식 이름만 나열하는 것은 불충분합니다.
* **Actual Code Excerpt Policy:** official code가 있는 full report는 최소 `1`개의 실제 코드 발췌를 포함하십시오. 경로/line ref만 적거나 generic pseudocode만 두는 것은 불충분합니다.
* **Experimental / Evaluation Setup Policy:** 각 대표 method paper에는 논문과 code/config를 종합한 `Experimental / Evaluation Setup` 섹션이 있어야 합니다. dataset/protocol, input setting, resolution/hardware, model/system config, optimizer/schedule, augmentation/loss weight, inference/deployment setting, 논문-코드 차이를 정리하십시오.
* **Ablation Quality Gate:** 논문에 ablation 또는 핵심 analysis table이 있다면, 실제 수치가 들어간 markdown table을 반드시 포함하십시오. 수치 없는 해석 bullet만 적어 두는 것은 불완전합니다.
* **Evidence Tag Policy:** paper report에서는 가능하면 각 핵심 주장에 `[paper]`, `[code]`, `[repo]`, `[inference]` 중 근거 출처를 표시하십시오. 특히 구현 세부사항을 논문 본문에서 직접 확인하지 못했으면 `[code]` 또는 `[inference]`로 분리하십시오.
* **Table Policy:** `overview.md`와 `papers/*.md`의 주요 evaluation table에는 비교 대상 논문의 `학회/저널`과 `연도`를 반드시 표기하십시오.
* **Completion Policy:** survey는 `overview.md`만으로 완료되지 않습니다. 대표 method paper는 `papers/*.md`에, 핵심 task-defining artifact는 `datasets/*.md`에 각각 개별 문서가 있어야 하며, 공식 코드가 있으면 code analysis 또는 그 부재 사유가 포함되어야 합니다. 또한 각 report는 main agent의 품질 검수(review gate)를 통과해야 합니다.

## 2.6 추천 탐색 순서
Main 에이전트는 기본적으로 다음 순서로 탐색하십시오.
1. topic의 핵심 task 정의
2. `main scope / adjacent branch / out-of-scope` 잠금
3. 핵심 evaluation axis 식별
4. 핵심 dataset / benchmark / protocol / task-defining artifact를 `datasets/*.md` 대상 후보로 확정
5. 각 task-defining artifact의 reference와 cited-by를 통해 대표 논문 확장
6. 각 핵심 evaluation axis 이름으로 top-tier 논문 검색
7. 핵심 비교 표 / related work / leaderboard에서 comparison-anchor paper 식별
8. 최근 2~3년 venue/year 기준 recent frontier paper 검색
9. 최근 `arXiv` / `OpenReview` preprint sweep
10. citation/impact 기반 expansion
11. 대표 논문의 공식 코드 availability 확인
12. official code가 있는 recent frontier / representative paper는 clone 및 code analysis 선행
13. 논문 본문 기준 `paper evidence` 수집
14. `code evidence + paper evidence` 합성으로 code-aware paper.md 작성
15. recent frontier paper의 full report 승격 여부 점검
16. main agent review gate 통과 여부 점검
17. taxonomy 정리 및 누락 점검
18. Stop 여부 판단

## 3. 위임
필터링을 통과한 논문만 Sub 2(Paper)와 Sub 3(Code)에게 전달하여 개별 분석을 병렬 지시하십시오.

* 공식 GitHub가 있는 논문은 기본적으로 Sub 3(Code)에게도 전달하십시오.
* Sub 2는 논문 본문을 읽고 `문제 설정`, `핵심 기여`, `수식`, `main table`, `ablation table`, `실험 setting`, `불확실한 부분`을 먼저 정리하십시오.
* Sub 3는 repo를 읽고 `핵심 모듈`, `입출력 shape`, `call chain`, `loss`, `데이터 파이프라인`, `config`, `실험 setting`, `snippet 후보`, `paper와 code의 차이`를 먼저 정리하십시오.
* 공식 코드가 있는 논문은 `Sub 2의 paper evidence`와 `Sub 3의 code evidence`를 합성한 뒤에만 최종 `papers/*.md`를 닫으십시오.
* 핵심 dataset / benchmark / protocol / task-defining artifact는 `papers/`가 아니라 `datasets/` 아래에 작성하십시오.
* task-defining artifact 문서에서는 code clone이 없어도 되지만, 문제 정의, split, metric, protocol, 대표 baseline, comparison-anchor 연결은 반드시 정리하십시오.
* `papers/*.md`의 방법론 설명은 코드가 있을 경우 논문만이 아니라 실제 구현까지 연결해 설명해야 하며, 이 연결은 별도 부록이 아니라 Methodology 본문 안에서 보이도록 작성해야 합니다.
* 즉, 공식 코드가 있는 논문에서는 `paper analyst`가 `code engineer`보다 먼저 완료본을 내지 않는 것이 기본 원칙입니다.
* Main Agent는 `overview.md` 작성 전에 representative method paper는 `papers/*.md`, 핵심 task-defining artifact는 `datasets/*.md`로 모두 내려왔는지 확인하십시오.

## 3.1 증거 수집 -> 합성 -> 검수 파이프라인

Main Agent는 대표 논문 하나를 다음 4단계로 처리하십시오.

1. **Evidence A (Code):** code engineer가 repo 구조, 핵심 클래스/함수, tensor shape, call chain, config, snippet 후보를 정리한다.
2. **Evidence B (Paper):** paper analyst가 논문 본문에서 problem setting, module 설계 의도, main table, ablation/analysis table, equation 의미, 실험 setting을 정리한다.
3. **Synthesis:** paper writer(또는 synthesis 담당 analyst)가 위 두 증거를 합쳐 최종 `papers/*.md`를 작성한다. 이 단계에서는 `Methodology & Implementation Walkthrough`가 논문 문장 요약이 아니라 `paper claim + code evidence + 필요한 inference`가 결합된 설명이 되어야 하며, `Experimental / Evaluation Setup`도 paper와 config를 합쳐 재구성되어야 한다.
4. **Review Gate:** main agent가 각 `paper.md`를 열어 `method 깊이`, `forward flow 선명도`, `integrated code-grounding`, `equation grounding`, `actual code excerpt quality`, `experimental/evaluation setup`, `ablation 숫자`, `불확실성 표시`를 확인하고, line-ref only / pseudocode-only 초안이면 다시 반려한다.

공식 코드가 없는 논문이라도 `Evidence B -> Synthesis -> Review Gate`는 동일하게 적용하십시오. 다만 code-grounded 설명 대신 논문 본문과 수식에 근거한 설명을 더 엄격히 요구하십시오.

## 3.2 동적 멀티 에이전트 스케일링
사용자가 multi-agent / parallel work를 명시한 경우, director는 agent 수를 고정하지 말고 `단계`와 `대표 논문 수`를 기준으로 동적으로 늘리십시오.

* **검색 단계:** dataset/benchmark 수, venue bucket 수, preprint sweep 범위를 보고 search agent를 소수로 시작하십시오.
  - 보통 `1~3`개 search agent로 충분하지만, benchmark 축과 venue 축이 동시에 넓으면 `4~6`개까지 늘릴 수 있습니다.
* **논문 분석 단계:** paper list가 커질수록 여기가 주 병목이 됩니다.
  - representative paper가 `1~6편`이면 `1~2` analyst
  - `7~15편`이면 `3~4` analyst
  - `16~30편`이면 `5~8` analyst
  - 그 이상이면 batch를 나누어 `6~10`개 내외 active analyst를 유지하고, 끝난 agent에 다음 batch를 재배정하십시오.
* **코드 분석 단계:** official repo가 있는 대표 논문 수에 비례해 code engineer를 늘리십시오.
  - clone/구조 점검이 대기열로 쌓이면 `2~6`개 code agent를 병렬 운영하는 편이 낫습니다.
* **합성/검수 단계:** 개별 evidence가 모이기 시작하면 synthesis와 review가 병목이 될 수 있습니다.
  - director는 search/paper/code에만 슬롯을 다 쓰지 말고, 최소 `1~2`개 high-reasoning synthesis/review 슬롯(main agent 포함)을 남겨 두십시오.
* **재분배 원칙:** search가 끝났는데 paper writing이 밀리면 search agent를 줄이고 analyst/code engineer를 늘리십시오.
* **검수 우선 원칙:** 개별 agent 산출물이 많아도 review gate가 비어 있으면 얕은 초안이 누적됩니다. batch마다 `작성 -> 합성 -> 검수`를 닫고 다음 batch로 넘어가십시오.
* **배치 원칙:** 모든 논문을 한 번에 같은 priority로 보내지 말고, `foundational -> turning point -> recent strong` 순으로 batch를 짜고 director가 계속 재정렬하십시오.
* **완료 조건:** agent 수가 많아도 representative paper의 `papers/*.md`와 code analysis가 실제로 수렴했는지 director가 끝까지 확인해야 합니다.

## 3.3 권장 Reasoning Budget

가능할 때는 단계별로 다음 reasoning 수준을 기본값으로 삼으십시오.

* **Search / Scouting:** `medium`
  - breadth, source coverage, benchmark discovery가 목적일 때는 대개 충분합니다.
* **Code Analysis:** `high`
  - tensor shape, call chain, equation-to-code mapping, hidden engineering trick을 안정적으로 뽑아야 하므로 `medium`보다 높은 추론이 유리합니다.
* **Paper Analysis / Writing:** `high`
  - method를 모듈 단위로 풀고, main table과 ablation table을 구조적으로 읽어야 하므로 기본 `high`를 권장합니다.
* **Synthesis / Review:** 가능하면 `xhigh`
  - code evidence와 paper evidence를 충돌 없이 합치고, 얕은 설명이나 잘못된 해석을 걸러내는 단계는 가장 높은 reasoning budget을 우선 배정하십시오.

`xhigh`가 항상 가능하지 않다면, 최소한 final review는 main agent가 추가 검수 pass를 수행하여 보완하십시오.

## 3.5 재조사와 비교

기존 topic을 다시 조사할 때는 다음을 따르십시오.

1. 기존 결과 폴더는 그대로 보존 (이름을 바꾸거나 덮어쓰지 않음)
2. 새 결과는 새 실행일 기준 날짜 prefix를 붙인 `[YYYY-MM-DD_Topic]/` 폴더에 작성
3. 새 결과 폴더에 반드시 `compare_old_vs_new.md` 생성 (비교 대상 old 폴더 경로를 명시)
4. guide가 바뀐 뒤 첫 실행이거나 사용자가 비교를 원하면 `run_validation.md` 생성

## 4. 경고
절대 현재 워크스페이스 루트 밖의 다른 것들은 건들지 마시오.
`Survey_Results/Survey_Results/...` 같은 중첩 경로를 만들지 마시오.
