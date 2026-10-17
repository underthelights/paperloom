# Research 워크스페이스 지시문

이 폴더는 사용자의 리서치 전용 워크스페이스다. 시스템 지시문과 사용자 지시문보다 우선하지 않으며, 그 하위에서 프로젝트 로컬 규칙으로 동작한다.

## 요청 라우팅 (가장 먼저 판단)

| 요청 유형 | 모드 | 출력 위치 |
|---|---|---|
| "이 논문 쉽게 설명해줘 / md로 정리해줘" (논문 1~4편 지목) | **Paper Note** — 가벼운 노트. `.claude/skills/paper-note/` 포맷을 따른다. survey 게이트 적용 금지 | `Paper_Notes/<ShortName>.md` |
| "X 분야/토픽 조사·서베이·literature review·SOTA 정리" | **Survey** — 아래 survey workflow 전체 적용 | `Survey_Results/[YYYY-MM-DD_Topic]/` |
| 본인 연구 아이디어/브레인스토밍/related work 메모 | 자유 형식 | `Research_Notes/` |

판단이 애매하면(예: 논문 5편 이상, "관련 논문도 같이") 어느 모드인지 사용자에게 확인한다. 기본값은 가벼운 쪽이다.

---

이하는 **Survey 모드**의 규칙이다.

## 단일 소스 원칙

- 이 워크스페이스의 survey workflow specification은 `Survey_Guide/`가 유일한 기준이다.
  - `Survey_Guide/01_Workflow.md` — 디렉터리/네이밍 규칙, 필터링·중단 조건, 커버리지 정책, 추천 탐색 순서, evidence -> synthesis -> review 파이프라인, 멀티에이전트 스케일링, reasoning budget
  - `Survey_Guide/02_Paper_Analysis.md` — `papers/*.md`, `datasets/*.md`, `overview.md` 포맷과 품질 기준
  - `Survey_Guide/03_Code_Analysis.md` — clone 정책, `codes/*_analysis.md` 포맷, synthesis handoff
  - `Survey_Guide/04_Conf_Journal_List.md` — 대상 학회/저널 목록과 자동 업데이트 규칙
  - `Survey_Guide/05_Execution_Checklist.md` — 완료 조건, overview-only 금지, resurvey/validation 규칙
- survey 작업을 시작하기 전에 반드시 위 다섯 파일을 모두 읽는다.
- 이 문서(AGENTS.md)는 진입점과 오케스트레이션 규칙만 담는다. 커버리지, 품질 게이트, 완료 기준이 이 문서와 guide 사이에서 달라 보이면 **guide를 따른다**. 같은 규칙을 이 문서에 다시 복사해 두지 않는다.

## 핵심 원칙 요약

세부 기준은 모두 guide에 있다. 아래는 잊지 말아야 할 뼈대만 요약한 것이다.

1. 대표 논문 수를 미리 고정하지 않는다. stop은 논문 수가 아니라 `핵심 evaluation axis coverage`, `high-impact coverage`, `recent strong paper coverage` 충족으로 판단한다.
2. taxonomy 요약만으로 끝내지 않는다. dataset/benchmark-driven coverage와 citation/impact-driven expansion, 최근 arXiv/OpenReview preprint sweep을 반드시 수행한다.
3. 공식 코드가 있는 대표 논문은 availability 확인에 그치지 말고 실제 clone과 코드 분석을 수행한다. 기본 순서는 `clone -> code analysis -> synthesis -> paper.md`다. clone 실패는 `미시도`가 아니라 `시도했으나 실패`로 원인과 함께 기록한다.
4. survey 완료는 `overview.md`만으로 성립하지 않는다. 대표 method paper는 `papers/*.md`, 핵심 task-defining artifact는 `datasets/*.md`, 공식 코드가 있으면 `codes/*_analysis.md`가 모두 있어야 하며, `05_Execution_Checklist.md`의 게이트를 통과해야 한다.
5. verified fact와 inference를 구분하고, "latest" / "recent"에는 절대 날짜를 병기한다.

## 출력 품질 헌장 (Quality Charter)

> 이 헌장은 모든 survey 산출물(`papers/*.md`, `datasets/*.md`, `codes/*_analysis.md`, `overview.md`)에 **무조건** 적용된다. guide의 포맷 규칙이 "무엇을 쓸지"라면, 이 헌장은 "얼마나 깊게, 얼마나 친절하게 쓸지"의 하한선이다. 이 하한선을 못 넘긴 산출물은 미완성으로 간주한다.

서베이가 "표면적"으로 느껴지는 원인은 둘이다: (a) 개념을 수식 없이 말로만 뭉개거나, (b) 수식만 던지고 직관을 안 주거나. 이 헌장은 둘 다 금지한다.

### 원칙 1 — 모든 핵심 개념은 "설명 사다리(Explanation Ladder)"를 끝까지 올라간다

핵심 메커니즘·objective·모듈 하나하나는 아래 5단을 **순서대로** 밟아 설명한다. 중간 단을 건너뛰면 안 된다.

1. **직관/비유 (초등학생 한눈에):** 수식·전문용어 없이 1~2문장. "이 모듈은 결국 ___를 ___처럼 하는 것이다." 비유나 그림 묘사를 적극 사용한다. 이 한 줄만 읽어도 무슨 일이 일어나는지 감이 와야 한다.
2. **정식 정의:** 입력/출력이 무엇인지, 어떤 기호로 쓸지, 텐서 shape이 무엇인지 명시한다.
3. **핵심 수식:** 실제 수식을 LaTeX로 적는다 (아래 표기 규칙). 모든 기호를 그 자리에서 정의한다.
4. **유도/분해 (왜 이 식인가):** 수식을 던지고 끝내지 않는다. 핵심 objective 한두 개는 최소 몇 줄의 유도·분해·극한 해석을 붙여 "이 항이 왜 여기 있는지", "이 식이 0이 되면/최대가 되면 무엇을 뜻하는지"를 보인다.
5. **코드 대응:** 그 수식이 코드의 어느 함수/줄에서 계산되는지 연결한다 (공식 코드가 있을 때).

> 검수 질문: "수학을 모르는 사람이 1번만 읽고도 핵심을 말할 수 있는가? 그리고 전문가가 4번까지 읽고 재유도할 수 있는가?" 둘 다 **예**여야 통과.

### 원칙 2 — 수학 표기 규칙

- inline 수식은 `$...$`, display 수식은 `$$...$$`. 워드프로세서 기호(×, ∑를 텍스트로)로 때우지 않는다.
- 기호는 **처음 등장할 때** 의미·차원·shape을 정의한다. 예: "$a_t \in \mathbb{R}^{d_a}$는 시점 $t$의 action chunk, $d_a$는 DoF 수."
- 핵심 objective/loss/update rule은 단순 인용이 아니라 **유도 가능한 형태**로 적는다. 기댓값 $\mathbb{E}$, 분포 $p_\theta$, 파라미터 $\theta$를 명시한다.
- "loss를 최소화한다" 같은 문장 뒤에는 반드시 그 loss의 수식이 있어야 한다.

### 원칙 3 — 깊이의 하한선 (anti-shallow 게이트)

다음은 자동 미달로 본다: 핵심 수식이 있는 논문인데 수식이 없음 / 수식은 있는데 기호 정의·직관·유도가 없음 / "enhance·fuse·align·refine" 같은 동사로 메커니즘을 뭉갬 / 모듈 이름만 나열 / 숫자 없는 ablation. (세부 미달 조건은 `02_Paper_Analysis.md` 말미를 따른다.)

### 모범 예시 (이 깊이가 하한선이다)

아래는 action head에 자주 쓰이는 **conditional flow matching** objective를 헌장 사다리대로 푼 예시다. 모든 `papers/*.md`의 Key Equations는 최소 이 정도 깊이여야 한다.

> **1. 직관:** 노이즈에서 정답 action까지 가는 "직선 길"을 그려놓고, 네트워크한테 "지금 이 위치에서 어느 방향·속도로 가야 하나"만 맞히게 시키는 것이다. 목적지를 한 번에 찍는 게 아니라, 길 위 아무 데서나 *진행 방향*을 가리키게 학습한다.
>
> **2. 정의:** $a \sim p_{\text{data}}$는 정답 action chunk($a \in \mathbb{R}^{H \times d_a}$, $H$=chunk 길이, $d_a$=DoF), $\epsilon \sim \mathcal{N}(0, I)$는 노이즈, $\tau \in [0,1]$는 보간 시간. 보간점 $a_\tau = (1-\tau)\,\epsilon + \tau\, a$. 관측 조건 $o$. 네트워크 $v_\theta$는 vector field를 예측한다.
>
> **3. 핵심 수식:**
> $$\mathcal{L}_{\text{CFM}}(\theta) = \mathbb{E}_{a,\epsilon,\tau}\left[\; \big\lVert\, v_\theta(a_\tau,\, o,\, \tau)\; -\; (a-\epsilon) \,\big\rVert_2^2 \;\right]$$
>
> **4. 유도/분해:** 직선 경로 $a_\tau=(1-\tau)\epsilon+\tau a$를 $\tau$로 미분하면 $\frac{d a_\tau}{d\tau}=a-\epsilon$ — 즉 *목표 vector field가 시간에 무관한 상수* $(a-\epsilon)$가 된다. 그래서 회귀 타깃이 깔끔히 $(a-\epsilon)$로 떨어진다. loss가 0이면 $v_\theta$가 모든 $\tau$에서 이 직선의 속도를 정확히 재현하므로, $\tau{=}0$의 노이즈에서 ODE $\dot{x}=v_\theta$를 적분하면 $\tau{=}1$의 정답 action에 도달한다. diffusion의 score matching과 달리 노이즈 스케줄·가중치 항이 없어 타깃 분산이 작고 학습이 안정적이다.
>
> **5. 코드 대응:** 추론은 보통 Euler step 10회 내외로 $a_\tau$를 $\tau{:}0{\to}1$ 적분 (예: `sample_actions()`의 for-loop), 학습은 위 L2를 그대로 계산 (예: `compute_loss()`에서 `(v_pred - (a - eps)).pow(2).mean()`).

이 예시처럼, **직관 한 줄 → 기호 정의 → 수식 → 몇 줄 유도 → 코드 한 줄**이 한 흐름으로 이어지면 통과다.

## 산출물 구조

- 모든 산출물은 이 워크스페이스의 `Survey_Results/[YYYY-MM-DD_Topic]/` 아래에 작성한다. `[YYYY-MM-DD_Topic]`은 실행일 기준 YYYY-MM-DD 날짜 prefix를 붙인 폴더명이다. 예: `2026-06-06_World_Model_for_Robot_Learning/`
- 기본 구조 (상세 규칙은 `01_Workflow.md` §1):
  - `overview.md`
  - `papers/[Venue_Year_FirstAuthor_ShortTitle].md` — method / system / model paper
  - `datasets/[Venue_Year_FirstAuthor_ShortTitle].md` — dataset / benchmark / protocol 등 task-defining artifact
  - `codes/[Repo_Name]/` — git clone 디렉터리
  - `codes/[Venue_Year_FirstAuthor_ShortTitle]_analysis.md`
  - 필요 시 `notes/` — search ledger, clone queue 같은 작업 노트 (선택)
  - 필요 시 `compare_old_vs_new.md`, `run_validation.md`
- 파일명은 ASCII-safe 규칙을 유지하고, 공백과 특수문자는 정리한다.
- `Survey_Results/Survey_Results/...`, `[workspace_root]/[workspace_root]/...` 같은 중첩 경로를 만들지 않는다. 워크스페이스 루트 밖은 건드리지 않는다.

## 언어 정책

- 사용자가 다른 언어를 명시하지 않는 한, 모든 survey 산출용 markdown은 **기본 한국어**로 작성한다.
- 논문 제목, 모델명, 손실 함수명, 데이터셋명, 클래스명, 함수명은 원문 영어를 유지하거나 병기한다.

## 멀티 에이전트

- 기본은 메인 에이전트가 director로서 전 단계를 단독 수행하는 것이다.
- 사용자가 명시적으로 multi-agent / delegation / parallel work를 요청한 경우에만 커스텀 에이전트를 사용한다.
  - Codex: `.codex/agents/`의 `survey_searcher`, `survey_paper_analyst`, `survey_code_engineer`
  - Claude Code: `.claude/agents/`의 `survey-searcher`, `survey-paper-analyst`, `survey-code-engineer`
- agent 수는 고정하지 말고 단계별 병목과 대표 논문 수에 따라 동적으로 조정한다. 단계별 권장 스케일과 batch 재분배 원칙은 `01_Workflow.md` §3.2, 역할별 evidence 분담은 §3.1과 `03_Code_Analysis.md`를 따른다.
- 서브에이전트에게 작업을 줄 때는 topic, 정확한 출력 파일 경로, 따라야 할 guide 파일을 지시문에 명시한다.

## 도구 폴백

- citation expansion은 가능하면 `Google Scholar`, 막히면 `Semantic Scholar`, `OpenAlex`, 공식 venue 검색, arXiv / OpenReview로 대체한다.
