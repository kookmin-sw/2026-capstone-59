# ai/data/custom/

팀 자체 제작 가이드 문서 모음. Bedrock Knowledge Base의 **KB-B** Data Source로 인덱싱됩니다.

## 두 유형으로 분리

### 1. `glossary/` — 용어 사전

**1 파일 = 1 개념.** 한 문서에 여러 용어를 섞지 않음.

**작성 구조 (권장):**
```markdown
---
type: glossary
related_stages: [3, 4]
---

# 기능 요구사항 (Functional Requirement)

## 한 줄 정의
시스템이 **무엇을** 해야 하는지를 기술한 요구사항.

## 쉬운 설명
...

## 관련 용어
- 비기능 요구사항
- 유스케이스
```

**예시 문서 파일명:**
- `functional-requirement.md`
- `non-functional-requirement.md`
- `use-case.md`
- `erd.md`

### 2. `technique/` — 기법 가이드

**1 파일 = 1 기법.** "언제 쓰나 + 어떻게 하나 + 초보자 실수" 구조.

**작성 구조 (권장):**
```markdown
---
type: technique
related_stages: [3]
related_steps: []
---

# 인터뷰 (Interview)

## 언제 쓰나
사용자 요구사항을 직접 들어야 할 때.

## 프로젝트 규모별 추천
- 1~3인 팀: 3~5명 대상 30분 단위
- 4~6인 팀: 10명 이상 권장

## 진행 방법
1. ...

## 초보자가 자주 하는 실수
- ...
```

**예시 문서 파일명:**
- `interview.md`
- `brainstorming.md`
- `prototyping.md`
- `three-tier-architecture.md`

## 작성 우선순위

자체 문서 제작 순서 (`.kiro/steering/Poco_AI_Design_Guide_v1.md` §6.3 참조):

| 순위 | 기준 | 시점 |
|---|---|---|
| 1순위 | 24개 필수 Step의 주제 (Stage 3~4 먼저) | Phase 2 직후 |
| 2순위 | 범용 반복 주제 (우선순위 정하기, 프로토타이핑 등) | Phase 3 중 |
| 3순위 | RAG 검색 미스 보강 (실제 운영 데이터 기반) | 데모 전 튜닝 |
