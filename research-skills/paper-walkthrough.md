# Paper walkthrough: 근거가 있는 연산 단계

새 단일 논문 JSON 보고서에 `walkthrough` 객체를 작성한다. 근거가 없으면 빈 steps와 scope에 구체적인 이유를 기록한다. 논문·공식 코드에서 확인한 실제 연산을 단계별로 읽는 UI의 데이터이며 실행 가능한 프로그램이나 학습 재현 결과가 아니다. 기존 보고서에 이 필드가 없어도 유효하다.

```json
{"walkthrough":{"title":"논문명 · 연산 흐름","scope":"검토한 구현 commit, 구성과 확인하지 못한 경계","steps":[{"id":"stable-ascii-id","title":"구체적 모듈/연산명","explanation":"입력의 의미, 이 연산이 필요한 이유, 출력의 사용처와 모든 축의 정의","operation":"코드에서 확인한 reshape / permute / matmul 등","input_shape":"[B,T,H,W,C]; B=batch, ...","output_shape":"[B,C,T,H,W]","equation":"실제 수식 또는 빈 문자열","mode":"shared","evidence":[{"label":"파일·함수·행 또는 논문 절/표","url":"https://..."}],"verification":"source","concepts":["실제로 대응하는 개념명"]}]}}
```

- 최대 40단계. 입력 → 전처리 → 인코더 → latent/patch → 조건 결합 → 핵심 연산 → head → loss 또는 sampler → decode → 출력 순서 중 실제 존재하는 단계만 기록한다. 서로 다른 학습·추론 경로는 `mode: training | inference | shared`로 분리한다.
- 각 step의 title, explanation, input_shape, output_shape는 문자열이어야 한다. shape은 확인된 기호와 축 정의를 사용한다. 수치를 알 수 없으면 `확인 불가: 누락된 설정/코드`를 적는다. 서로 다른 모델 variant나 미해결 config 기본값을 합쳐 숫자를 만들지 않는다.
- `verification: source`는 실제 열람한 출처 URL이 해당 보고서 `sources`에도 있고 해당 단계의 주장을 뒷받침할 때만 사용한다. 코드가 실행되었다는 뜻이 아니다. HTTPS commit permalink와 행 범위, 원문 절·표를 우선한다. 단순히 URL이 있다는 사실은 검증 완료의 근거가 아니다.
- 교육용으로 임의 정한 숫자 예시는 `illustrative`로 명시하고 실제 모델 shape으로 제시하지 않는다. 출처·연산·축을 확인할 수 없으면 `unknown`과 구체적인 누락 이유를 적는다. 제목만 있는 일반적인 pipeline으로 채우지 않는다.
- 학습은 target 정의, noise/time convention, mask, loss 축 축약을 설명한다. 추론은 초기 상태, 반복 update, cache 갱신, decoder와 실제 출력 경계를 구분한다. forward만 읽고 optimizer 또는 로봇 실행을 검증했다고 주장하지 않는다.
- `concepts`는 단계와 직접 관련 있는 개념의 정확한 이름을 최대 8개 기록한다. 다른 모델의 채택 여부나 수학적 동등성을 이름 유사성만으로 주장하지 않는다.
- 원문이나 공식 구현을 확보하지 못했다면 빈 steps와 scope의 정확한 이유를 반환한다. 임의의 표준 Transformer 단계로 대체하지 않는다.
