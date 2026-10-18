# 영·한 원문 읽기와 주장 구조 하이라이트

HTML 원문을 열면 Codex가 문단·제목·그림 설명을 순서대로 번역하고 원문에서 선택한 구절을 분류한다. 영어 원본은 유지하고 한국어를 오른쪽에 표시한다. 좁은 창에서는 아래로 배치한다. 수식은 번역 입력에서 placeholder로 보호하고 한국어에서는 원문 수식 표기를 복원한다. PDF 자체의 번역은 이 기능 범위에 포함하지 않는다.

분류는 기존 연구/baseline, 본 논문 주장, 논리·근거, 실험·결과의 네 종류이며 범례에서 개별 표시를 끌 수 있다. 분류 이유와 주장 주체를 펼쳐 볼 수 있다. 자동 분류는 사용자 하이라이트와 별개로 저장된다. 근거 없는 구절·원문과 불일치하는 인용·동일 문단의 위치가 모호한 반복 인용은 거부한다. AI의 분류 자체가 연구 결과의 독립 검증을 의미하지 않는다.

`GET /api/reader/document/:id`는 문서 hash와 블록 ID를 제공한다. `POST /api/reader/auto`는 paper_id 및 선택적인 retry를 받으며 중복 실행을 방지한다. `GET /api/reader/auto/:id`는 완료 문단과 상태를 반환한다. 결과는 reader_auto 테이블에 저장되며 문서 hash·스킬 hash가 달라지면 다시 처리한다. 실패/앱 재시작 시 완료된 문단은 유지하고 재시도 버튼으로 이어간다. 초기 번역에는 Codex 사용량과 시간이 필요하다. 문서에 삽입된 한국어는 원문 UTF-16 주석 좌표 계산에서 제외된다.

실행 규칙: [bilingual-evidence-reader](../../research-skills/bilingual-evidence-reader/SKILL.md). 동일 스킬을 사용자의 Codex skills 디렉터리에도 설치했다.

## 참고한 공개 구현

- [Immersive Translate 구 공개 코드](https://github.com/immersive-translate/old-immersive-translate): 문단 단위 병렬 표시 설계 참고. 2023년에 보관된 저장소이며 최신 제품 코드로 간주하지 않는다.
- [PDFMathTranslate](https://github.com/PDFMathTranslate/PDFMathTranslate): 수학 기호·문서 구조 보존을 고려하는 번역 설계 참고. Paperloom에 이 프로젝트의 코드나 PDF 엔진을 복사하거나 의존성으로 추가하지 않았다.

## 검증

- Python runner 69 tests: 원문 hash 보존, UTF-16 인용 검증, 수식 토큰 누락 거부, 완료 문단 재사용, 지침 변경 무효화, 재시작 복구 포함.
- 합성 API 브라우저 검사: 병렬 번역 후 두 번째 문단의 선택 좌표 유지, 원문 전용 전환, 분류별 강조 토글, 밝게/어둡게 화면.
- 실제 Codex 호출: 합성 연구 문단의 한국어 번역, 40%/60% 조건 보존, JSON 파싱, 정확한 원문 구절의 분류를 확인했다. 전체 논문 번역 품질을 완전히 검증한 것은 아니다.
