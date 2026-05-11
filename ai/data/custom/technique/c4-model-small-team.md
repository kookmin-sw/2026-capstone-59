---
type: technique
related_stages: [4]
related_required_steps: [4-R2]
---

# C4 모델 — 소규모 팀 적용 가이드

## 한 줄 정의

**C4 모델**은 시스템 아키텍처를 4단계 줌으로 기록하는 시각화 기법이다.

- **Level 1 — Context** — 시스템 1개 + 외부 사용자·외부 시스템. "이 시스템이 외부와 어떻게 닿는가."
- **Level 2 — Container** — 시스템 내부의 배포 가능한 단위(웹앱·API·DB·모바일). "이 시스템은 무엇으로 구성되는가."
- **Level 3 — Component** — 컨테이너 내부의 주요 모듈·기능 그룹. "이 API는 어떤 기능 블록으로 나뉘는가."
- **Level 4 — Code** — 클래스 다이어그램. "이 모듈의 클래스는 어떻게 짜였는가."

## 왜 다층 뷰가 필요한가

설계는 다른 사람에게 전달돼야 의미가 있다. 이해관계자마다 필요한 추상화 수준이 다르다. 외부 검토자는 Context로도 충분하고, 팀 내부 개발자는 Container·Component까지 보고 싶다. 각 계층에서 같은 시스템을 일관된 표기로 보여주는 게 C4의 장점이다.

## 팀 규모별 권장 분량

- **1명** — Context 1장 + Container 1장 = 총 2장. 도구는 draw.io, Excalidraw, 또는 손그림 사진으로 충분하다. Component와 Code 다이어그램은 생략 가능하지만, Container 1장은 절대 생략 금지다. 외부 사용자가 봐도 시스템을 이해할 수 있는 수준으로 그린다.
- **2~3명** — Context 1장 + Container 1장 + 핵심 Component 1~2장. 도구는 draw.io 또는 Mermaid(마크다운에 박을 수 있어 편리). Code 다이어그램과 모든 Component를 그리는 건 생략 가능하지만, Container 다이어그램과 핵심 데이터 흐름 1개는 꼭 남긴다.
- **4~6명** — Context + Container + Component 2~3장. 도구는 draw.io 또는 Structurizr(코드 기반 다이어그램). Code Level 다이어그램은 외부 설명·보고 자리에서는 거의 쓰이지 않으므로 생략 가능하다. Container 다이어그램은 README 또는 외부 설명 자료에 꼭 포함한다.
- **7~10명** — Context + Container + Component 3~5장(서브팀별). 도구는 Structurizr DSL 또는 PlantUML(버전 관리 가능). 주요 시나리오 2~3개에 대해 시퀀스 다이어그램을 추가하면 좋다. 다이어그램 갱신 책임자 1명 지정은 절대 생략 금지다.

## 도구 비교

| 도구 | 장점 | 적합 규모 |
|---|---|---|
| draw.io / Excalidraw | 무료, 30분 안에 한 장 그리기 쉬움 | 1~6명 |
| Mermaid | 마크다운·README에 그대로 박기 좋음 | 1~6명 |
| Structurizr DSL / PlantUML | 코드 기반, 버전 관리 가능 | 4~10명 |

## 흔한 실수

- **Level 4까지 다 그리려 시도** — 모든 클래스 다이어그램을 그리면 한 주가 사라진다. Code 레벨은 코드가 바뀔 때마다 갱신 부담이 크므로 소규모 팀에서는 가치 대비 비용이 가장 크다. Container까지만 그리고 Component는 핵심 2개만 그리는 게 실용적이다.
  - bad: 모든 클래스 다이어그램을 그리느라 한 주를 썼다.
  - good: Container까지 그리고 Component는 핵심 2개만 그렸다.
- **한 번 그리고 갱신 안 하기** — Stage 4 시작 때 그린 다이어그램이 프로젝트 후반까지 그대로면 거짓 정보가 되고 신뢰를 깬다. 주요 구조 변경 때마다 Container 다이어그램 1장만이라도 갱신한다.
  - bad: 처음 그린 다이어그램을 프로젝트 후반까지 안 고쳤다.
  - good: 구조 변경 때마다 Container 그림을 한 번씩 갱신했다.
- **도구를 너무 무겁게 잡기** — 유료 도구 라이선스 알아보느라 3일을 보내면 본업이 사라진다. draw.io나 Mermaid로 30분 안에 1장 그리는 쪽이 훨씬 낫다.
  - bad: 유료 도구 라이선스를 알아보느라 3일을 썼다.
  - good: draw.io로 30분 안에 첫 다이어그램을 그렸다.

## 핵심 요약

**Container까지가 소규모 팀 표준이다.** Context + Container 2장이면 외부 설명용으로 충분하고, Component는 핵심 모듈만 추가한다. Code 레벨은 소규모 팀에서 대부분 불필요하다.
