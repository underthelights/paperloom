# Guide 2: 논문 및 데이터셋 분석, 개요 작성

> **선행 조건 — 출력 품질 헌장.** 이 가이드의 모든 포맷 규칙은 `AGENTS.md`의 「출력 품질 헌장」 위에서 동작한다. 헌장의 **설명 사다리**(① 직관/비유 한 줄 → ② 정식 정의 → ③ 수식(LaTeX) → ④ 몇 줄 유도/분해 → ⑤ 코드 대응)는 아래 모든 섹션, 특히 `Methodology`와 `Key Equations`의 하한선이다. 수식 없는 말뭉개기와 직관·유도 없는 수식 투척은 둘 다 미달이다.

## 1. 논문 리포트 포맷 (`papers/*.md`)
`papers/*.md`는 method / system / model paper 전용입니다. 핵심 dataset / benchmark paper는 `datasets/*.md`로 분리하십시오.

Sub 2는 전달받은 각 논문에 대해 아래 포맷으로 마크다운 파일을 생성하십시오.
* **Language:** 사용자가 별도로 요청하지 않는 한 모든 markdown 산출물은 한국어로 작성하십시오. 논문 제목, 모델명, 손실 함수, 데이터셋, 지표, 수식은 원문 영어를 병기할 수 있습니다.
* **Evidence Tags:** 구현/수식/실험 설명에는 가능하면 `[paper]`, `[code]`, `[repo]`, `[inference]` 태그를 붙여 근거를 분리하십시오. 추론을 사실처럼 단정하지 마십시오.
  supplementary, appendix, supplement를 직접 근거로 쓴 경우에는 `[supp]` 태그를 사용할 수 있습니다.
* **Title & Authors:** (링크 포함)
* **Report Scope Status:** 가능하면 이 논문이 `main scope representative`, `recent frontier representative`, `adjacent branch supplementary`, `deferred frontier` 중 어디에 속하는지 짧게 적으십시오.
* **Problem Setting & Relation to Prior Work:** 이 논문이 정확히 어떤 문제를 풀고, 어디까지가 기존 방법이며, 어디부터가 이 논문의 기여인지 먼저 분리해서 설명하십시오.
* **Core Contribution:** 3줄 요약이 아니라, 필요하면 3~5개 bullet로 논문의 핵심 기여를 분명히 쓰십시오.
* **Methodology & Implementation Walkthrough:** 아키텍처, 핵심 알고리즘, 목적 함수(Loss), 수식, 모듈 관계를 매우 구체적으로 서술하십시오. 모호한 표현을 피하고 수치, 모듈명, 텐서 shape, 변수 의미를 명시하십시오.
  이 섹션은 논문 method 요약과 code 구현 설명을 **분리된 두 블록으로 쓰지 말고**, 하나의 통합된 설명으로 작성해야 합니다.
  즉 `논문이 주장하는 구조 -> 실제 forward flow -> 각 주요 모듈이 코드에서 어떻게 구현되는지`가 한 흐름으로 이어져야 합니다.
  이 섹션은 단순한 구조 나열이 아니라, 독자가 `왜 이런 모듈이 필요한지`, `forward에서 표현이 어떻게 바뀌는지`, `코드에서 어디서 계산되는지`까지 따라갈 수 있게 써야 합니다.
  각 주요 모듈 설명은 가능한 한 `target bottleneck -> design principle -> core operator -> why not simpler baseline -> code realization` 흐름으로 쓰십시오.
  반드시 `문제 맥락 -> 전체 구조 overview -> end-to-end forward flow -> 모듈별 deep dive(코드 근거 포함) -> 수식/손실 -> 학습/추론 동작` 순서가 읽히도록 구성하십시오.
  가능하면 Methodology 첫 부분에 아래와 같은 `Module Snapshot Table`을 포함하십시오.
  - `Module`
  - `Target bottleneck`
  - `Input`
  - `Core operator`
  - `Output / Shape`
  - `Why not simpler baseline`
  - `Code path`
  - `Evidence`
  Methodology 내부의 권장 하위 구조는 다음과 같습니다.
  1. **Architecture Overview**
     - 입력과 출력이 전체적으로 무엇인지
     - 어떤 stage들로 나뉘는지
     - 논문의 핵심 설계 원리가 한 문단 안에서 보이도록 서술
  2. **Key Equations** (헌장 설명 사다리 ①~⑤를 수식마다 적용)
     - 논문의 핵심 수식 `1~3`개를 실제로 적기
     - equation 번호 또는 위치를 적고, 필요하면 LaTeX로 재작성
     - markdown에서는 inline 수식은 `$...$`, display 수식은 `$$...$$`를 사용
     - 각 수식은 다음을 **모두** 갖춰야 한다:
       - **직관 한 줄:** 수식을 보기 전에, 이 식이 결국 무엇을 하려는지 비전공자도 알 수 있게 1문장 (헌장 ①)
       - **기호 정의:** 등장하는 모든 기호의 의미·차원·텐서 shape을 그 자리에서 정의 (헌장 ②)
       - **유도/분해:** 핵심 objective/loss/update rule **최소 1개**는 단순 인용에 그치지 말고 몇 줄의 유도·분해·극한 해석을 붙여 `이 항이 왜 여기 있는지`, `식이 0/최대가 되면 무엇을 뜻하는지`를 보일 것 (헌장 ④). 단순 정의식(예: 단순 보간식)은 유도 생략 가능하나, 학습을 좌우하는 식은 유도가 필수.
       - **의미 해설:** 이 수식이 실제로 무엇을 계산/강제하는지 `1~2`문장 (헌장 ③)
       - 가능하면 단순 baseline(예: plain MSE, vanilla softmax)과 비교해 `왜 이 형태인지` 한 줄
  3. **End-to-End Forward Flow**
     - stage `1 -> 2 -> 3 -> ...` 형태로, 표현이 어디서 어떻게 바뀌는지 순서대로 적기
     - 가능하면 각 stage마다 tensor / feature shape와 대표 함수명을 붙이기
  4. **Module Snapshot Table**
     - 아래 모듈별 deep dive를 읽기 전에 전체 구조를 한눈에 볼 수 있게 구성
  5. **Module Deep Dive**
     - 각 주요 모듈에 대해 `target bottleneck -> design principle -> 입력 표현 -> 핵심 계산 / core operator -> 출력 표현 -> why not simpler baseline -> 다음 단계 -> 코드 anchor`를 한 덩어리로 설명
     - 이때 paper 설명과 code path를 따로 떼지 말고 같은 단락/소단락 안에서 연결
     - `enhance`, `fuse`, `align`, `refine` 같은 표현만 쓰고 실제 메커니즘을 설명하지 않으면 불충분합니다.
  6. **Equation / Loss / Implementation Mapping**
     - 주요 수식과 손실, matching, aggregation이 code에서 어떤 함수/변수와 대응되는지 적기
  7. **Training / Inference Behavior**
     - 학습 시 forward와 추론 시 forward가 어디서 갈라지는지, window inference / post-processing / memory update 같은 차이를 설명
  8. **Actual Code Excerpts**
     - 공식 코드가 있으면 실제 코드 발췌 `1~2`개를 넣고, 각 줄 또는 코드 덩어리가 무엇을 하는지 설명
     - 가능하면 survey용 짧은 inline comment를 덧붙인 annotated snippet 또는 코드 블록 바로 아래 줄단위 해설을 함께 제공
  최소한 다음 항목을 반드시 포함하십시오.
  1. 이 논문의 method가 풀려는 핵심 병목
     - 기존 방법이 어디서 부족했는지
     - 이 논문이 어떤 설계 원리로 그 부족함을 메우는지
  2. 전체 파이프라인 overview와 입력 / 출력
  3. end-to-end forward flow
     - 어떤 표현이 어떤 순서로 이동하는지
     - 어디서 branch가 생기고 다시 합쳐지는지
     - 학습과 추론에서 경로가 달라지는지
  4. backbone / encoder / decoder 또는 주요 서브모듈
  5. module-by-module 설명
     - 각 모듈이 해결하려는 target bottleneck / failure mode가 무엇인지
     - 그 병목을 푸는 design principle이 무엇인지
     - 각 모듈의 입력이 무엇인지
     - 출력이 무엇인지
     - tensor / feature shape이 어떻게 되는지
     - 그 모듈을 넣은 motivation이 무엇인지
     - 핵심 연산자(core operator)가 무엇인지
     - 바로 이전 단계의 어떤 표현을 받아서, 다음 단계에 무엇을 넘기는지
     - 단순한 대안(mean pooling, concat, vanilla attention, global cosine 등)과 비교했을 때 왜 필요한지
     - 어떤 함수/클래스가 이 모듈을 구현하는지
     - 가능하면 경로와 line reference도 함께 적으십시오.
  6. frame / token / patch / query sampling strategy
  7. matching granularity
  8. aggregation / fusion / reranking 방식
  9. training objective와 주요 수식
  10. 실제 핵심 수식 `1~3`개
     - equation 번호/원문 또는 LaTeX 재작성
     - inline은 `$...$`, block은 `$$...$$` 사용
     - 각 기호의 의미
     - 이 수식이 실제로 무엇을 의미하는지 `1~2`문장 comment
     - 왜 중요한지
  11. equation-to-code mapping
     - 어떤 함수/변수/설정이 수식의 각 항과 대응되는지
  12. inference-time detail 또는 post-processing
  13. **핵심 구현 포인트**
     - 공식 코드가 있으면 `1~2`개의 짧은 **실제 코드 발췌**를 넣으십시오.
     - 각 발췌에는 `파일 경로`, `line reference`, `클래스/함수명`, `이 줄이 의미하는 바`, `shape/변수 설명`, `왜 중요한지`를 함께 적으십시오.
     - 가능하면 코드 블록 안에 survey용 짧은 inline comment를 달거나, 코드 블록 바로 아래에 줄단위 주석 해설을 붙이십시오.
     - 긴 코드 dump는 금지합니다. 핵심 동작만 짧게 발췌하십시오.
     - pseudocode는 코드가 없거나, 실제 코드가 지나치게 장황해 핵심만 재구성해야 할 때에만 보조적으로 허용됩니다.
     - 공식 코드가 있는 full report에서는 최소 `1`개의 실제 코드 발췌가 필수입니다.
  가능하면 `문제 맥락 -> 전체 구조 overview -> forward flow -> 모듈 deep dive -> 수식/손실 -> 학습/추론 -> 구현 근거` 순서가 자연스럽게 읽히도록 구성하십시오.
  `backbone / transformer / head` 수준의 얕은 요약 bullet만으로 Methodology를 끝내지 마십시오.
  공식 코드가 있는 논문에서는 Methodology 안의 각 주요 모듈 설명에 code anchor가 직접 녹아 있어야 합니다. 코드를 별도 부록으로 밀어 넣고 Methodology를 논문 요약으로만 쓰지 마십시오.
* **Equation & Variable Explanation:** 실제로 제시한 핵심 수식 `1~3`개를 기준으로, 각 변수와 기호가 무엇을 의미하는지 텍스트로 풀어 설명하십시오. 단순 변수 사전만 두지 말고, 각 수식이 어떤 objective / update / matching rule을 표현하는지 `1~2`문장으로 풀어 쓰십시오.
* **Implementation Anchor Table (권장, supplementary):** 공식 코드가 있으면 빠른 참조용으로 별도의 짧은 표/섹션을 둘 수 있습니다. 다만 이 섹션은 **보조용**이며, Methodology 안에서 이미 통합 설명이 끝나 있어야 합니다.
  최소한 다음을 포함하십시오.
  1. 관련 파일 경로
  2. 클래스 / 함수명
  3. 주요 변수의 의미
  4. forward pass에서 tensor shape가 어떻게 변하는지
  5. 논문 수식이 코드의 어느 부분에서 대응되는지
  6. `파일 목록`에서 끝내지 말고, 최소 `2~4`개의 구체적인 함수/클래스에 대해 “여기서 무엇을 계산하는지”를 문장으로 설명하십시오.
  7. 가능하면 경로와 line reference를 함께 적으십시오.
  이 섹션은 Methodology를 대체할 수 없습니다. Methodology가 얕고, code 설명이 여기 한 섹션에만 몰려 있으면 불완전한 report입니다.
  공식 코드가 있고 clone에 성공했다면 local repository 분석을 기준으로 쓰십시오. README / repo tree만 보고 추정한 경우는 그렇게 명시하십시오.
  공식 코드가 없으면 `No official code available`를 명시하십시오.
* **Experimental / Evaluation Setup:** 논문 본문과 공식 코드/config를 종합하여, 이 논문이 실제로 어떤 설정에서 학습/평가/배치되는지 하나의 독립 단락/섹션으로 정리하십시오.
  이 섹션은 단순 hyperparameter 나열이 아니라, `재현 관점에서 어떤 선택들이 중요한지`가 드러나야 합니다.
  empirical ML에서는 dataset/split과 training/inference recipe가 중심이고, system paper라면 hardware / runtime / deployment constraint가 더 중요할 수 있습니다.
  아래 항목을 가능한 한 고정 슬롯처럼 채우십시오. 해당이 없으면 `N/A`, 찾지 못했으면 `Not found in paper`, `Not found in code`처럼 명시하십시오.
  1. dataset / split / benchmark / evaluation protocol
  2. sampling strategy / input length / context window / episode setting
  3. resolution / resize / crop / preprocessing / hardware / environment
  4. backbone / pretrained weights / architecture config / system config
  5. optimizer / learning rate / schedule / epoch 또는 iteration 수 / batch size
  6. augmentation / auxiliary supervision / loss weight / joint training / regularization
  7. inference or deployment setting: window size, memory bank, threshold, post-processing, latency budget, resource constraint 등
  8. 논문 본문과 repo config가 다르면 그 차이
  9. 이 setting이 main result와 ablation 해석에 왜 중요한지
  가능하면 `[paper]`, `[code]`, `[repo]`를 함께 써서 무엇이 논문 명시값이고 무엇이 config 확인값인지 구분하십시오.
* **Experiments & Performance:** 주요 평가 결과와 비교 우위를 설명하십시오.
  반드시 다음을 포함하십시오.
  1. 주요 evaluation axis의 main result table
  2. 비교 대상 논문의 `학회/저널`과 `연도`
  3. 논문이 주장하는 핵심 비교 포인트에 대한 해석
  4. ablation study table 또는 핵심 분석 table의 **실제 수치가 들어간 markdown table**
  5. 가능하면 table 번호(Table 2, Table 3 등)와 setting을 함께 적으십시오.
  6. 각 ablation / analysis table 아래에는 수치 변화(`+/-`)를 근거로 2~4개 takeaway를 적으십시오.
  7. 논문에 실질적인 ablation table이 없다면 `No substantial ablation table in paper`라고 명시하고, 그 대신 어떤 분석 표를 대체로 봤는지 적으십시오.
  8. 이 논문이 representative paper set에 포함된 이유
     - top-tier main-track strong paper인지
     - evaluation axis에서 반복 비교되는 핵심 논문인지
     - recent strong arXiv / preprint인지
* **Limitations & Future Work:** 논문에서 언급된 한계점과 디렉터(Main)가 판단한 한계점을 함께 적으십시오.

다음 상태는 `papers/*.md` 완료로 간주하지 마십시오.

* Methodology가 전체 구조 overview, forward flow, module deep dive 없이 모듈 이름만 나열하는 경우
* module motivation은 있지만 `어떤 failure mode를 겨냥하는지`, `어떤 메커니즘으로 해결하는지`, `왜 단순 baseline보다 나은지`가 없는 경우
* Methodology 안에서 code anchor가 거의 언급되지 않고, paper 설명과 code 설명이 분리되어 따로 노는 경우
* Implementation Anchor Table이 있더라도 Methodology 자체는 여전히 논문 요약에 머무르는 경우
* Implementation Anchor Table이 파일 경로 목록만 있고 실제 함수/클래스 설명이 없는 경우
* 공식 코드가 있는데 실제 코드 발췌 없이 generic pseudocode만 있는 경우
* 핵심 수식이 있는 논문인데 actual equation excerpt, 변수 설명, 수식 의미 해설, equation-to-code mapping이 없는 경우
* 핵심 개념·모듈·objective를 설명하면서 헌장 설명 사다리의 ① 직관 한 줄을 건너뛰어 비전공자가 무슨 일이 일어나는지 알 수 없는 경우
* 학습을 좌우하는 핵심 loss/objective/update rule이 수식만 인용되고, 유도·분해·극한 해석(헌장 ④)이 전혀 없어 `왜 이 식인지`를 따라갈 수 없는 경우
* 실제 코드 발췌는 있지만 inline comment나 줄단위 설명이 없어 구현 의도를 따라가기 어려운 경우
* Experimental / Evaluation Setup 섹션이 없거나, dataset/protocol, resolution/hardware, optimizer/schedule, batch size, inference/deployment setting, paper-code mismatch 중 핵심 항목이 비어 있어 재현 관점에서 중요한 setting을 알 수 없는 경우
* Ablation 섹션에 숫자 table 없이 해석 bullet만 있는 경우
* 논문에서 직접 확인한 내용과 코드/추론 기반 내용을 구분하지 않은 경우

## 1.5 데이터셋 / 벤치마크 / 프로토콜 리포트 포맷 (`datasets/*.md`)
핵심 dataset / benchmark / evaluation protocol / task-defining artifact는 `papers/`가 아니라 `datasets/` 아래에 작성하십시오.

dataset report는 method paper보다 형식이 다르며, 최소한 다음을 포함하십시오.

* **Title & Authors:** 링크 포함
* **Task Definition & Motivation:** 이 dataset / benchmark / protocol / task-defining artifact가 어떤 문제를 정의하거나 재정의했는지, 왜 중요한지
* **Artifact Composition / Setup:** 샘플 수, video/image 수, category 수, split, annotation type, sequence length, modality, hardware regime, environment assumption 등 핵심 통계 또는 설정
* **Evaluation Protocol & Metrics:** 평가 metric, matching rule, split protocol, challenge setting, runtime/constraint rule 등 핵심 프로토콜
* **Why This Artifact Matters:** 기존 benchmark / protocol / setting과 어떤 차이를 만드는지, 어떤 failure mode를 드러내는지
* **Main Baselines / Anchor Table:** 논문 본문 또는 공식 문서에서 제시한 대표 baseline / leaderboard snapshot / comparison-anchor를 실제 수치와 함께 표로 정리
* **Comparison-Anchor Connection:** 후속 method paper들이 이 artifact를 기준으로 반복 비교하는 anchor paper가 무엇인지 간단히 정리
* **Biases / Limitations:** class imbalance, occlusion bias, annotation noise, closed/open-vocabulary limitation 등
* **Role in Representative Set:** 왜 이 task-defining artifact가 full report 대상인지

다음 상태는 `datasets/*.md` 완료로 간주하지 마십시오.

* artifact 이름만 적고 split / metric / protocol 설명이 없는 경우
* baseline 또는 anchor table 없이 서술만 있는 경우
* 이 artifact가 후속 논문 선택에 어떤 영향을 주는지 설명이 없는 경우

## 2. 개요 포맷 (`overview.md`)
Main Agent는 Sub 2의 리포트가 모두 완료되면 전체 동향을 종합하여 작성하십시오.
* **Language:** overview 역시 기본적으로 한국어로 작성하십시오.
* **Introduction:** 해당 분야의 발전 역사 및 현재 쟁점.
* **Representative Paper Map:** 대표 논문을 연도, venue, 핵심 의미 기준으로 한눈에 보이게 정리하십시오.
* **Taxonomy (분류체계):** 발견된 방법론들을 2~3가지의 주요 접근법으로 구조화하여 분류.
* **Evaluation-Axis Coverage:** 핵심 dataset / benchmark / protocol / setting별로 어떤 대표 논문이 포함되었는지 드러나는 표나 섹션을 포함하십시오.
* **Performance / Evaluation Comparison:** 주요 evaluation axis에 대한 대표 모델/시스템의 비교 표(Table)를 작성하십시오.
  이 표에는 최소한 `Method/System`, `Venue/Journal`, `Year`, `Evaluation Axis`, `Metric`, `Result`가 드러나야 합니다.
* **Coverage Notes:** 어떤 논문을 대표 논문으로 선택했는지, 그리고 citation/evaluation-axis 기준에서 어떤 탐색을 수행했는지 간단히 적으십시오.
  가능하면 task-defining artifact reference 탐색, cited-by expansion, recent arXiv / preprint sweep 여부도 함께 적으십시오.
  가능하면 어떤 논문들이 `comparison-anchor paper`로 반복 등장했는지도 함께 적으십시오.
  recent frontier paper 중 full report로 올리지 않은 항목이 있다면 `adjacent branch`, `deferred frontier`, `excluded` 중 어디에 속하는지와 그 이유도 적으십시오.
* **Quality Notes:** 이번 run에서 어떤 papers가 code-grounded methodology, numeric ablation table, review gate를 통과했는지 간단히 적으십시오.
* **Future Directions:** 파이프라인이 도출한 향후 연구의 유망한 방향.
