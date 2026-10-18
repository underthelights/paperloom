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

## 실행 구성: 한 보고서는 하나의 profile

`walkthrough.execution_profile`을 반드시 작성한다. 아래는 형식 예시이며 실제 값·URL이 아니다. `code-status.json`의 저장소·commit과 수집된 코드 manifest가 있으면 먼저 대조한다. manifest는 파일의 존재·내용 식별 근거이며 그 파일을 읽었다거나 실행했다는 증명은 아니다.

```json
{"execution_profile":{"repository":"https://github.com/OWNER/REPO","commit":"실제로 수집한 40자리 commit","config":"저장소 기준 main config 파일 경로","mode":"training","scope":"선택한 진입점과 파일, config 합성 순서, 확인한 CLI override, 실행하지 않은 경계","unknowns":["미해결 interpolation 또는 외부 config의 정확한 이름"],"dimensions":[{"symbol":"D","value":"실제 확인값 또는 확인 불가","source":"https://github.com/OWNER/REPO/blob/COMMIT/config.yaml#L10-L14","meaning":"어떤 tensor의 어느 축인지, 적용 variant와 가정"}]}}
```

- `mode`는 `training`, `inference`, `shared` 중 하나다. 실제로 어느 경로인지 알 수 없으면 `unknowns`와 `scope`에 적고 구성 검증 완료를 주장하지 않는다.
- 이 버전은 단일 profile만 지원한다. 학습 스크립트·데이터셋·모델 variant 중 하나의 근거 있는 조합을 고르고, 다른 구성의 숫자를 합치지 않는다. 다른 inference 경로의 차이는 기호와 조건으로 설명한다. 두 구성이 달라 수치 trace를 공유할 수 없다면 구체적 수치는 선택 profile에만 사용한다.
- README의 실행 예제 → 진입점 → config defaults/include → 모델·데이터 config → 명시된 CLI override 순서로 실제 파일을 읽는다. 클래스 기본 인수는 최종 resolved config가 아니다. 구성 시스템을 실행하거나 Python config를 import하여 resolver를 호출하지 않는다.
- Hydra/OmegaConf interpolation, Python으로 계산되는 설정, 환경변수, checkpoint metadata, 데이터에서 결정되는 축이 해소되지 않으면 정확한 표현을 `unknowns`에 남긴다. 실행하지 않고 정적으로 확인 가능한 부분만 확정한다. `config`가 파일 하나라고 해서 합성 전체가 확인된 것은 아니다.
- 각 dimension의 `source`는 실제 읽은 고정 commit/행 HTTPS URL이며 report `sources`에도 포함한다. `value`를 숫자로 적으려면 해당 profile에서 그 값이 적용된다는 근거까지 확인한다. 근거 없는 B, horizon, 이미지 크기, head 수, dtype를 편의상 채우지 않는다.
- 입력 shape가 데이터 의존적이면 기호를 유지하고 의미와 제약을 쓴다. `D=H·dh`, `N=F·h′·w′`처럼 유도 가능한 관계와 실제 측정값을 구분한다. 숫자 교육 예시는 profile dimensions에 넣지 않는다.
- shallow clone에 없는 과거 논문 시점 코드, submodule 미수집, LFS pointer, external package 구현, 다운로드로만 제공되는 config는 수집 공백이다. 다른 branch 최신 코드로 몰래 대체하지 말고 그 경계의 trace를 `unknown`으로 표시한다.

## 실제 입력에서 출력까지의 shape_trace

각 step에 `shape_trace` 배열을 작성한다. 설명용 `mechanics`와 별도로, 선택 profile의 실제 tensor 경로를 기계적으로 점검할 수 있는 순서다. 존재하지 않는 층을 관습적으로 추가하지 않는다.

```json
{"shape_trace":[{"title":"조건 채널 결합","operation":"concat","input_shape":"x:[B,C,F,h,w], y:[B,Ccond,F,h,w]","output_shape":"[B,C+Ccond,F,h,w]","basis":"code","assumptions":"dim=1; B,F,h,w가 일치해야 함. 각 기호는 선택 profile 기준.","evidence":[{"label":"파일·함수·행","url":"https://github.com/OWNER/REPO/blob/COMMIT/model.py#L100-L108"}]}]}
```

- `title`, `operation`, `input_shape`, `output_shape`, `assumptions`는 문자열이다. `basis`는 `code`, `mathematical`, `illustrative`, `unknown`이다. `code`에는 실제 읽은 고정 commit 행 근거가 필요하다. `mathematical`은 적용 조건을, `illustrative`는 가상값임을, `unknown`은 빠진 정보와 이유를 명시한다.
- 입력 → 전처리 → 인코더 → latent/patch → 조건 → 핵심 모듈 → head → loss 또는 sampler → decode/반환 중 실제 구현된 경로를 연결한다. shape_trace의 앞 출력과 다음 입력이 다르면 생략된 변환을 복원하거나 어디서 달라지는지 명시한다. fork·skip·조건 경로는 별도 입력 이름으로 추적한다.
- 숨겨진 `reshape/view/flatten/unflatten/permute`, 토큰·채널 concat, Q/K/V projection과 head 분할, matmul 합산 축, attention mask/broadcast, normalization 축, residual·gating, head decode를 실제 호출 순서대로 확인한다. 해당 모델에 없는 연산은 요구하지 않는다.
- 한 덩어리의 “Transformer 실행”만으로 shape_trace를 끝내지 않는다. 핵심 신규 모듈과 shape·정보 흐름이 달라지는 각 지점은 독립 항목으로 작성한다. 반복 동일 block은 반복 횟수의 출처와 동일 shape 불변 조건을 적고 불필요하게 복제하지 않는다.
- 학습은 clean/noise 정의와 시간 방향, target, teacher forcing과 attention 접근 범위, mask 적용 위치, loss의 합산·평균·분모, `detach/no_grad` 경계를 추적한다. 추론은 초기 sample, 각 update의 shape, scheduler 좌표·부호, cache 내용·수명·갱신, 반환값과 물리적 명령 사이를 추적한다.
- 논문 식과 코드 기호가 반대 방향이면 대응식을 명시한다. 예를 들어 `t=1−sigma`라면 속도 부호가 반대다. 이 관계를 모든 논문에 일괄 적용하지 말고 해당 식과 scheduler에서 확인한다.
- encoder latent를 RGB, padded action 차원을 로봇 DoF, 학습 반복을 추론 solver step이라고 바꾸어 설명하지 않는다. 연산의 의미와 단위까지 일치해야 한다.

## 저장 전 근거·커버리지 확인

1. profile의 저장소·commit·config가 실제 수집 결과와 일치하는지 확인한다. source URL과 commit이 존재해도 논문의 실험 구성을 재현했다는 뜻은 아니다.
2. 모든 `basis: code`의 파일·행이 수집된 commit의 범위 안에 있는지 확인하고, 해당 행이 서술한 연산·값을 직접 뒷받침하는지 읽는다. 단지 report `sources`에 있는 URL이라는 이유만으로 `code` 또는 `source`로 승격하지 않는다.
3. 입력부터 loss/반환까지 빠진 경로를 `scope`와 `unknowns`에 남긴다. 공식 코드 미공개, 구성 미해결, 외부 구현 미수집은 정상적인 부분 분석 결과이며 임의의 일반 모델 단계로 채우지 않는다.
4. 수학적 설명, 숫자 교육 예제, 정적 코드 사실, 실제 실행 측정의 경계를 유지한다. 이 작업은 정적 분석이므로 실행·학습 성공이나 실험 재현을 주장하지 않는다.
5. 서버가 근거 검증·커버리지 검사를 수행하더라도 모델은 검증 verdict나 실행 측정 결과를 직접 만들어 넣지 않는다. 근거가 충분한 데이터와 확인 불가 사유를 반환하고, 판정은 파이프라인에 맡긴다.
