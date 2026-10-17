# Guide 3: 코드 수집 및 분석

## 1. Git Clone 실행 (Sub 3)
* 논문에 공식 GitHub 링크가 제공된 경우, 기본적으로 코드를 받아와 분석하십시오.
* 터미널 실행 권한을 사용하여 `Survey_Results/[YYYY-MM-DD_Topic]/codes/` 디렉토리로 이동한 후 `git clone [URL]`을 실행하십시오.
* 공식 코드가 여러 개인 경우, 논문 / 프로젝트 페이지에서 직접 연결한 primary official repository를 우선하십시오.
* 대표 논문으로 채택된 항목은 code availability 확인만 하고 넘어가지 말고, 기본적으로 실제 clone을 시도하십시오.
* clone이 실패했다면 `미시도`로 두지 말고, 네트워크 제한 / private repo / submodule 문제 / dependency breakage 등 실패 원인을 명확히 기록하십시오.
* 최근 strong top-tier / arXiv paper가 representative set로 승격되었고 공식 코드가 있으면, foundational paper보다 뒤로 미루더라도 clone 대기열에 반드시 넣으십시오.
* 공식 코드가 없거나 private이거나 clone은 되지만 실행/구조 확인이 어려우면, 실패로 끝내지 말고 상태를 명확히 기록하십시오.
* 공식 코드가 있는 논문에서는 Sub 3의 분석이 Sub 2의 최종 `paper.md`보다 선행되거나, 최소한 동시에 진행되어 Sub 2가 결과를 바로 흡수할 수 있어야 합니다.
* code engineer는 최종 `paper.md`를 직접 닫는 역할이 아니라, synthesis 단계에서 바로 사용할 수 있는 `implementation evidence`를 준비하는 역할임을 명심하십시오.

## 2. 코드 분석 포맷 (`codes/*_analysis.md`)
Sub 3는 클론된 레포지토리를 분석하고 아래 내용을 작성하십시오. 논문에 없는 구현 디테일을 찾는 것이 핵심입니다.
* **Language:** 사용자가 별도로 요청하지 않는 한 코드 분석 markdown도 한국어로 작성하십시오. 경로, 클래스명, 함수명, 라이브러리명은 원문 표기를 유지합니다.
* **Repository Metadata:** 저장소 URL, 확인한 branch / commit(가능하면), 주요 entry script를 적으십시오.
* **Environment & Setup:** 주요 프레임워크(PyTorch 등), 요구 라이브러리, 실행 엔트리포인트.
* **Paper-to-Code Mapping:** 논문의 핵심 모듈이 코드의 어느 파일 / 클래스 / 함수에 대응되는지 표나 bullet로 정리하십시오.
* **Design Motivation Mapping:** 각 핵심 모듈이 코드상 왜 필요한지, 어떤 prior baseline을 대체하거나 어떤 병목을 해결하는지 함께 적으십시오.
* **Module Rationale Mapping:** 각 핵심 모듈마다 `target bottleneck / failure mode`, `design principle`, `core operator`, `why not simpler baseline`, `code realization`을 한 묶음으로 남기십시오.
* **Core Logic Implementation:**
    * 네트워크 모델이 정의된 파일 경로 및 클래스명.
    * 각 핵심 모듈의 입력 / 출력 / tensor shape.
    * 변수명이 무엇을 의미하는지.
    * forward pass에서 feature가 어떻게 변형되는지.
    * 논문의 핵심 아이디어가 구현된 특정 함수, 코드 경로, call chain.
    * 각 단계가 다음 단계의 어떤 계산으로 이어지는지.
    * 단순한 file path listing으로 끝내지 말고, 적어도 `2~4`개 핵심 함수/클래스에 대해 “여기서 실제로 무엇을 계산하는가”를 문장으로 적으십시오.
* **Key Equation Capture:** 논문의 핵심 수식 `1~3`개를 적고, 각 수식의 기호 의미, `무엇을 계산/강제하는지`에 대한 짧은 해설, code에서 대응되는 함수/변수를 함께 정리하십시오.
* **Equation-to-Code Mapping:** 논문의 주요 수식이 코드에서 어떻게 구현되는지, 각 항이 어떤 변수에 대응되는지 설명하십시오.
* **Loss Function Details:** 실제 학습에 사용된 loss 연산 로직과 tensor shape, reduction 방식을 적으십시오.
* **Data Pipeline & Batch Structure:** dataset loader, sampler, collator, augmentation, batch dict 구조를 분석하십시오.
* **Training / Evaluation Flow:** 학습 스크립트, evaluation 스크립트, checkpoint 흐름, 주요 config 인자를 정리하십시오.
* **Hidden Engineering Tricks:** 논문에 기재되지 않았으나 성능 향상을 위해 적용된 augmentation, preprocessing, masking, normalization, caching, mixed precision, distributed training trick 등을 찾으십시오.
* **Paper Consistency Check:** 구현이 논문과 정확히 일치하는지, 또는 논문에는 없지만 코드에만 있는 디테일이 무엇인지 적으십시오.
* **Promotion Recommendation:** 이 논문이 `main scope representative`, `recent frontier representative`, `adjacent branch supplementary`, `blocked` 중 어디에 가까운지 적으십시오.
  최소한 다음을 포함하십시오.
  * `scope relevance`: main scope / adjacent branch / out-of-scope
  * `recent frontier signal`: yes / no
  * `code readiness`: clone complete / partial / blocked
  * `recommended action`: full report / supplementary note / hold
* **Synthesis Handoff:** 최종 paper writer가 바로 가져다 쓸 수 있도록 다음을 함께 남기십시오.
  * `module -> target bottleneck -> core operator -> input/output/shape -> code path -> why it matters` 형태의 압축 메모
  * `전체 구조 overview -> forward flow -> module deep dive`를 바로 쓸 수 있는 call chain 요약
  * `1~3`개의 실제 코드 발췌 후보: path, line range, 왜 중요한지, 변수/shape 설명, 추천 inline comment 또는 줄단위 설명 포인트. init/config보다 핵심 메커니즘 block를 우선하십시오.
  * 필요한 경우에만 보조용 pseudocode 후보
  * 핵심 수식 `1~3`개와 equation-to-code mapping 메모, notation 설명, 각 수식의 한두 문장 의미 해설
  * `Experimental / Evaluation Setup`에 들어갈 config 요약: dataset/split, protocol, num_frames/input length, resolution/hardware, optimizer, schedule, batch size, augmentation, inference/deployment setting
  * code에서 실제로 확인한 값과 `Not found in code` 값을 분리한 setup evidence
  * paper writer가 조심해야 할 불확실성 / paper-code mismatch

## 3. Paper 리포트와의 연동
* 공식 코드가 있는 논문에 대해서는 Sub 3의 결과가 Sub 2의 `papers/*.md`에도 반영되어야 합니다.
* 특히 `Methodology & Implementation Walkthrough`와 `Experimental / Evaluation Setup`은 코드 분석 결과를 바탕으로 실제 구현 수준까지 설명해야 합니다.
* multi-agent 모드에서는 clone/코드 분석이 paper writing보다 느려질 수 있으므로, director는 code repo 수를 보고 code engineer 수를 동적으로 늘릴 수 있어야 합니다.
* Sub 2는 가능하면 Sub 3가 넘긴 `모듈 목적`, `입출력 shape`, `call chain`, `equation-to-code`, `config/실험 setting` 메모를 그대로 method 및 experimental/evaluation setup 설명의 골격으로 사용하십시오.
* Sub 2와 Sub 3는 병렬로 움직일 수 있지만, 최종 `paper.md`는 synthesis 단계에서 두 결과를 합친 뒤에만 완료 처리하십시오.
* `codes/*_analysis.md`가 있더라도, 그 내용이 `papers/*.md`의 Methodology와 Experimental / Evaluation Setup 이해를 실질적으로 깊게 만들지 못했다면 integration이 실패한 것으로 보고 재작업하십시오.
* 공식 코드가 있는 논문은 `어느 줄에 있다` 수준의 handoff로 끝내지 말고, 실제 코드 발췌와 식별 가능한 equation-to-code 근거까지 넘기십시오.
* 특히 recent frontier paper에 대해 code analysis가 완료되었다면, `overview-only`로 둘지 `full report`로 승격할지에 대한 판단 근거를 `Promotion Recommendation`에 남기십시오.
