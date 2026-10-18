## 영상 생성 모델에서 로봇 정책까지

확인일: 2026-10-18. 모델 이름이 같아도 버전·체크포인트·용도를 분리합니다. 아래 ‘비교 대상’은 DreamZero가 사용한 모델이라는 뜻이 아닙니다.

### 모델 계열과 공개 범위

| 계열 | 개발·공개 주체 | 무엇을 학습하는가 | 코드·가중치 | 로봇과의 관계 |
|---|---|---|---|---|
| Wan2.1 | [Alibaba Group / Wan Team](https://arxiv.org/html/2503.20314v2) | 시공간 VAE와 diffusion transformer를 이용한 영상 생성. 1.3B와 14B 계열을 구분 | [공식 코드·모델](https://github.com/Wan-Video/Wan2.1), Apache-2.0 공개 안내 | **채택 확인**: DreamZero 기본 백본은 Wan2.1-I2V-14B. 모든 Wan 변형을 사용한 것은 아님 |
| Wan2.2-TI2V-5B | Wan-Video | 텍스트·이미지 조건 영상 생성. DreamZero 안내에서는 다른 VAE와 transformer 설정 사용 | [저장소](https://github.com/Wan-Video/Wan2.2), 선택 체크포인트의 모델 카드 확인 | **구현 안내 확인**: 현재 DreamZero 저장소의 DROID 학습 대안. 원 논문의 14B 실험 결과와 구분 |
| LTX-Video | Lightricks | Video-VAE와 denoising transformer를 함께 설계하여 압축 잠재공간에서 영상 생성 | [코드](https://github.com/Lightricks/LTX-Video)는 Apache-2.0. [가중치](https://huggingface.co/Lightricks/LTX-Video/blob/main/README.md)는 버전별 별도 라이선스 | **비교 대상**: 속도·압축 설계가 제어 지연 연구에 관련. 이 노트에서 실제 로봇 정책 채택은 확인 불가 |
| LTX-2 | Lightricks | 후속 오디오·비디오 생성 계열 | [별도 코드·학습 안내](https://github.com/Lightricks/LTX-2). LTX-Video의 라이선스·벤치마크를 그대로 적용하지 않음 | **비교 대상**: 오디오·영상 생성 능력이 로봇 행동 출력 능력을 의미하지 않음 |
| SANA 원형 | NVlabs, NVIDIA·MIT·Tsinghua 연구 협력 | 선형 attention과 고압축 autoencoder를 이용한 **이미지** 생성 | [공식 프로젝트](https://nvlabs.github.io/Sana/), [코드](https://github.com/NVlabs/Sana)는 Apache-2.0. 가중치는 개별 모델 카드 확인 | **설계 비교**: 효율적인 표현·attention. 원형을 video policy로 분류하지 않음 |
| SANA-Video / Video 2.0 | NVlabs SANA 프로젝트 | 영상 생성으로 확장된 별도 계열. Video 2.0은 hybrid linear/softmax attention 사용 | [계열별 문서·체크포인트](https://github.com/NVlabs/Sana). 원형 이미지 체크포인트와 구분 | **비교 대상**: 긴 시공간 문맥의 비용을 줄이는 설계. DreamZero 채택 근거는 확인 불가 |
| SANA-WM | SANA-WM 저자팀 / NVlabs 공개 | 6-DoF **카메라 궤적** 조건의 분 단위 영상 world model | [논문](https://arxiv.org/abs/2605.15178), [프로젝트](https://nvlabs.github.io/Sana/WM/), SANA 저장소의 학습 안내 | **조건부 세계 모델**: 카메라 pose 제어를 로봇 관절·그리퍼 정책으로 동일시하면 안 됨 |

SANA의 이미지 → 영상 → world model은 같은 연구 계열 안의 확장입니다. Wan → DreamZero는 백본을 실제 로봇 정책으로 전환한 관계입니다. LTX ↔ SANA ↔ Wan은 이 노트에서 **비교 관계**이며, 서로의 가중치를 계승했다는 관계가 아닙니다. 개발 주체를 개별 저자의 현재 소속·학위로 확장해서 추정하지 않습니다.

### 연결 지도 — 간선이 뜻하는 것

| 출발 | 관계 | 도착 | 근거 |
|---|---|---|---|
| Wan2.1-I2V-14B | 기본 백본 | DreamZero | [공식 백본 안내](https://github.com/dreamzero0/dreamzero/blob/main/docs/WAN22_BACKBONE.md) |
| Wan2.2-TI2V-5B | 별도 학습 구성 | DreamZero / DROID | 같은 안내의 Quick Start·Configuration Details. 원 논문 성능 재현 확인을 뜻하지 않음 |
| DreamZero | 영상·행동 공동 모델링 | World Action Models | [원 논문](https://arxiv.org/abs/2602.15922) |
| LTX-Video | 압축·추론 비용 비교 | Video Diffusion Models | [LTX 논문](https://arxiv.org/abs/2501.00103) |
| SANA | 이미지 생성 설계 | Linear Attention | [SANA 원 논문](https://arxiv.org/abs/2410.10629) |
| SANA-WM | 카메라 조건부 생성 | World Models | [SANA-WM 논문](https://arxiv.org/abs/2605.15178) |

### 왜 영상 모델을 로봇에 가져오는가

물체가 이동하고 손이 물체를 가리는 영상에는 시간에 따른 상태 변화가 들어 있습니다. 이런 표현을 사전학습하면 로봇 데이터만으로 시각적 변화까지 처음부터 학습할 부담을 줄일 수 있습니다. 그러나 그럴듯한 영상을 생성하는 것만으로 힘·접촉·관절 제한을 만족하는 행동을 얻지는 못합니다.

아래는 모델 간 차이를 설명하기 위한 **분석용 확률 표기**이며 각 논문의 목적함수를 그대로 옮긴 식이 아닙니다. $o_t$는 현재 관측, $s_t$는 로봇 상태, $c$는 지시, $V$는 미래 영상, $A$는 미래 행동 묶음입니다.

$$p_\theta(V\mid o_t,c)\quad\longrightarrow\quad p_\phi(V,A\mid o_t,s_t,c).$$

왼쪽은 장면의 미래를 생성합니다. 오른쪽은 그 미래와 함께 실행할 행동도 모델링합니다. $A\in\mathbb R^{H\times d_a}$에서 $H$는 제어 horizon, $d_a$는 선택한 로봇의 행동 차원입니다. 단위와 정규화는 로봇별로 명시해야 합니다. 영상 토큰의 좌표를 관절각으로 바로 읽을 수는 없습니다.

DreamZero는 사전학습 영상 백본을 바탕으로 영상과 행동을 공동 모델링합니다. 공식 구현 안내의 `CausalWanModel`은 action/state register와 행동 decoder를 사용합니다. 따라서 **가중치 다운로드 → 로봇에 바로 실행**이 아니라, 로봇 관측·상태·행동을 연결하는 학습과 실행 구성이 필요합니다. [논문](https://arxiv.org/abs/2602.15922), [구현 안내](https://github.com/dreamzero0/dreamzero/blob/main/docs/WAN22_BACKBONE.md).

로봇 적용 경로도 구분해야 합니다. 다음은 기술 비교를 위한 분류이며 위 모델 모두가 세 경로를 구현했다는 뜻은 아닙니다.

| 경로 | 추가로 필요한 것 | 주요 실패 조건 |
|---|---|---|
| 미래 영상 → inverse dynamics → 행동 | 영상 전이와 실제 행동을 짝지은 데이터, embodiment별 행동 모델 | 영상은 비슷하지만 필요한 힘·행동이 다른 경우 |
| 행동 후보 → 미래 예측 → 계획 | action-conditioned dynamics, 목적함수, 후보 탐색 | 모델 오류를 이용하는 계획, 접촉·충돌 예측 오류 |
| 영상·행동 공동 생성 | 행동 표현, 로봇 학습 데이터, 인과적 문맥, 재관측 | 행동 지연, 관측 분포 이동, 긴 rollout의 누적 오차 |

### 압축과 제어 지연을 함께 읽기

LTX-Video 원 논문은 시공간 축소와 VAE/transformer 역할 분담을 통해 영상 생성 비용을 줄입니다. 이는 로봇에서 중요할 수 있지만, **영상 생성 처리량과 폐루프 제어 주기는 다른 측정값**입니다. 원 논문의 영상 생성 속도를 로봇 제어 Hz로 변환해서 적으면 안 됩니다. [LTX 논문](https://arxiv.org/abs/2501.00103).

다음 식은 일반적인 비용 분석입니다. 토큰 수를 $N$, hidden dimension을 $d$라 두면 dense attention의 주된 연산은 $O(N^2d)$입니다. 압축으로 $N$을 절반으로 줄이면 이 항은 약 1/4이 됩니다. 전체 실행 시간은 VAE·메모리 이동·다른 층의 비용도 포함하므로 4배 빨라진다는 보장은 없습니다. 고압축은 작은 물체·접촉 지점 같은 세부 정보를 잃을 수 있어 제어 정확도와 함께 평가해야 합니다.

교육용 지연 예: 20 Hz 제어의 예산은 $1/20=0.05$초입니다. 추론이 0.20초라면 결과가 도착할 때까지 4개 제어 시점이 지납니다. 비동기 추론이나 action chunk가 필요한 이유가 여기에 있습니다. 이 숫자는 Wan·LTX·SANA의 측정 결과가 아닙니다.

### 함께 연결해서 읽을 개념

- **Joint Video-Action Modeling**: 영상과 행동이 공유하는 문맥, 서로 다른 출력 차원과 손실.
- **Flow Matching**: 노이즈와 데이터 사이의 경로·시간 방향·예측 대상. 모든 diffusion 구현의 수식을 동일시하지 않기.
- **Asynchronous Inference**: 오래 걸리는 예측과 빠른 제어를 겹치되 관측의 오래됨을 관리하기.
- **Closed-loop Control**: 생성한 미래를 계속 믿지 않고 실제 관측으로 다시 조건화하기.
- **Cross-embodiment Transfer**: 영상에서 공유할 수 있는 변화와 로봇마다 다른 행동 공간을 나누기.

### 다음 검증과 시각화

LTX·SANA의 실제 로봇 적용 사례는 이 노트의 근거만으로 확인할 수 없습니다. 추가 논문을 연결할 때 정확한 체크포인트, 학습 코드, 로봇 종류, 실험 조건을 확인한 뒤 ‘채택 확인’ 간선을 추가합니다. SANA-WM의 카메라 제어 결과를 조작 성공률로 옮기지 않습니다. 코드 공개, 가중치 공개, 학습 데이터 공개는 각각 다른 항목입니다.

시각화 설계: (1) 영상 프레임을 잠재 토큰으로 압축, (2) 노이즈에서 미래 영상으로 이동, (3) 행동 토큰을 추가해 공동 예측, (4) 예측과 실제 관측이 어긋나면 재관측으로 수정. 이 장면의 Manim 구현은 아직 없습니다. 시간 앙상블 영상을 영상 확산의 설명으로 대신 표시하지 않습니다.
