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

## 단계 내부: 논문이 생략한 기초부터 연산까지

각 step에 `mechanics` 배열을 최대 12개 추가한다. 해당 연산을 이해하는 데 필요한 생략된 기초를 복원하되, 모든 논문에 같은 Transformer 강의를 붙이지 않는다. 실제 입력에서 출력까지 필요한 전제만 선택한다.

```json
{"mechanics":[{"title":"축별 행렬곱","explanation":"A의 열 축과 W의 행 축을 같은 k로 합산한다. B는 배치, N은 토큰, Din과 Dout은 입출력 특성 수다.","input_shape":"A:[B,N,Din], W:[Din,Dout]","output_shape":"Y:[B,N,Dout]","equation":"Y_{b,n,j}=\\sum_{k=1}^{D_{in}} A_{b,n,k}W_{k,j}","basis":"mathematical","assumptions":"실수 텐서의 일반적인 행렬곱 정의. 이 논문이 이 연산을 실제 사용하는지는 상위 step의 코드 근거로 별도 확인.","evidence":[]}]}
```

- `basis: code`는 해당 논문 공식 구현에서 직접 확인한 연산이다. 실제 열람한 commit/행 HTTPS URL을 `evidence`와 보고서 `sources`에 모두 기록한다.
- `basis: mathematical`은 명시한 전제로부터 유도한 수학적 설명이다. 출처가 없어도 허용하되, 논문의 주장·실험 결과나 실제 코드의 동작이라고 바꾸어 말하지 않는다. 적용에 필요한 축, 함수, 미분 가능성, 정규화 등의 전제를 `assumptions`에 쓴다.
- `basis: illustrative`는 이해를 위한 작은 수치 예제이며 실제 config나 실행 결과가 아니다. 작은 입력과 중간값·출력을 보여 주는 것이 유익할 때만 추가한다. `unknown`은 확인 불가능한 경계와 이유를 표시한다.
- `title`, `explanation`, `input_shape`, `output_shape`, `equation`, `assumptions`는 문자열이다. 확인되지 않은 shape을 만들지 않는다. 입력/출력이 텐서가 아닌 단계는 그 자료형과 적용 범위를 명시한다.
- matmul/축 축약은 가능하면 인덱스 수식으로 합산 축과 남는 축을 보여 준다. broadcasting은 어떤 singleton 축이 확장되는지, normalization은 어느 축의 평균·분산 또는 norm인지와 epsilon·scale 의미를 적는다.
- reshape는 원소 순서와 원소 수 보존, permute는 축 순서 변경을 구분한다. stride/contiguity와 copy/view 동작은 실제 프레임워크 코드에서 확인했거나 수학적 설명의 한계로 명시한다.
- mask 적용 위치와 방향, loss 분모, detach/no_grad/teacher forcing 등의 gradient 경로를 설명한다. code 근거 없이 optimizer나 gradient 동작을 검증했다고 쓰지 않는다.
- 모델 variant, 실제 resolved config, dtype, padding과 batch 가정의 경계를 유지한다. 논문에 생략된 기초 설명과 논문의 새로운 기여를 분리한다.
