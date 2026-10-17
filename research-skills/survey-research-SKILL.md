---
name: survey-research
description: 사용자가 특정 연구 주제나 기술 분야에 대해 조사, 서베이, 문헌 정리, SOTA 정리, benchmark 비교를 요청할 때 활성화한다. 예시는 "X 분야 조사해줘", "Y 토픽 서베이", "literature review on Z", "state of the art for A"이다. 이 skill은 주제 조사, taxonomy 정리, 벤치마크 비교, 논문 선별, 필요 시 공식 코드 점검에 사용한다. 단순 사실 조회나 구현 작업에는 사용하지 않는다.
---

# Survey Research 스킬 (Codex)

이 skill은 topic-driven research survey를 위한 것이다. 워크플로의 유일한 스펙은 `Survey_Guide/`이고, 이 문서는 시작 절차만 정의한다. 규칙을 여기에 복사해 두지 않는다.

## 시작 절차

1. Read `AGENTS.md`.
2. Read `Survey_Guide/`의 다섯 파일을 모두 읽는다.
   - `01_Workflow.md` — 디렉터리 규칙, 커버리지 정책, 탐색 순서, evidence -> synthesis -> review 파이프라인, 멀티에이전트 스케일링
   - `02_Paper_Analysis.md` — `papers/*.md`, `datasets/*.md`, `overview.md` 포맷
   - `03_Code_Analysis.md` — clone 정책과 `codes/*_analysis.md` 포맷
   - `04_Conf_Journal_List.md` — 대상 venue 목록
   - `05_Execution_Checklist.md` — 완료 조건과 validation
3. 사용자 요청에서 target topic을 추론하고, filesystem-safe 이름으로 정규화해 `Survey_Results/[YYYY-MM-DD_Topic]/`(실행일 기준 YYYY-MM-DD 날짜 prefix)을 출력 루트로 정한다.

## 실행 원칙

- 짧은 답변보다 comprehensive survey가 기본값이다. 최종 응답에는 high-level synthesis, taxonomy, benchmark 비교, open problems를 포함한다.
- 커버리지, stop 판단, 품질 게이트, 완료 조건은 전부 guide를 따른다. 특히 `05_Execution_Checklist.md`를 통과하기 전에는 완료라고 보고하지 않는다.
- 시간에 민감한 정보(현재 benchmark, active repo, venue/year)는 웹 검색과 primary source로 최근 상태를 우선 확인한다.
- 사용자가 명시적으로 multi-agent / parallel work를 요청한 경우에만 `.codex/agents/`의 `survey_searcher`, `survey_paper_analyst`, `survey_code_engineer`를 사용한다. 스케일링은 `01_Workflow.md` §3.2를 따른다.
- 서브에이전트에게 작업을 줄 때 topic, 정확한 출력 경로, 따라야 할 guide 파일을 지시문에 명시한다.
