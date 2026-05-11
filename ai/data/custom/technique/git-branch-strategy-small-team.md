---
type: technique
related_stages: [5]
related_required_steps: [5-R1, 5-R2]
---

# 소규모 팀 Git 브랜치 전략

## 한 줄 정의

**브랜치 전략**은 팀이 변경을 어떻게 분리하고 합칠지 정하는 약속이다. 형상 관리가 통제되지 않으면 코드가 분기·병합 중에 손실되거나 일관성을 잃는다. 팀 규모와 릴리스 빈도에 맞는 **가장 단순한** 전략을 택하는 게 원칙이다.

## 대표 전략 3가지

- **Trunk-based** — main 한 줄, feature 브랜치는 하루 안에 끝낼 만큼 아주 짧게. 빠른 통합에 유리하다.
- **GitHub Flow** — main + 짧은 feature 브랜치 + PR 리뷰 후 머지. 단순한 릴리스 흐름에 적합하며 소규모 팀 디폴트.
- **Git Flow** — main + develop + feature + release + hotfix. 정형화된 릴리스 주기에 맞춰 쓰지만 소규모 팀에는 무겁다.

## 팀 규모별 권장 전략

- **1명** — Trunk-based(main 한 줄)로 충분. 작은 단위 커밋, 의미 있는 메시지, 매일 push. PR 리뷰·브랜치 보호 규칙은 생략 가능하지만, 의미 있는 커밋 메시지(3개월 뒤 본인이 봐도 이해될 수준)는 절대 생략 금지다.
- **2~3명** — Trunk-based + 짧은 feature 브랜치(1~3일). PR 형식 도입, 1명 승인, 짧은 PR 단위. develop·release·hotfix 브랜치는 생략 가능하지만, main 보호(직접 push 금지)는 절대 생략 금지다.
- **4~6명** — **GitHub Flow**(main + 짧은 feature 브랜치)가 디폴트. PR 리뷰 1~2명, 브랜치 보호 + CI 통과 필수. feature 브랜치는 1주 이내로 유지. 커밋 메시지 컨벤션 합의(Conventional Commits 권장)는 절대 생략 금지다.
- **7~10명** — GitHub Flow로도 충분하고, 정기 릴리스가 있으면 단순화된 Git Flow. PR 리뷰 2명 + CI/리뷰 자동 머지 차단 + 모듈 소유자 자동 할당. 릴리스 태깅과 변경 로그 자동화를 더하면 좋다. PR 템플릿 + 브랜치 명명 규칙은 꼭 정해둔다.

## 기본 운영 규칙

- **main은 항상 동작** — 깨진 상태를 main에 남기지 않는다. CI 통과한 코드만 머지.
- **PR은 짧게** — 200~400줄 단위로 쪼갠다. 1000줄 PR은 리뷰어가 포기한다.
- **feature 브랜치는 1주 이내** — 더 길어지면 main과 멀어져 머지 충돌 폭발.
- **커밋 메시지 컨벤션** — `feat:`, `fix:`, `refactor:` 등 prefix로 종류 구분.

## 흔한 실수

- **Git Flow를 소규모 팀에 무리하게 도입** — develop·release·hotfix까지 풀세트로 운영하면 머지 충돌이 매주 터진다. Git Flow는 정기 릴리스가 있는 제품 모델이지 소규모 팀에 맞지 않는다. GitHub Flow로 단순하게 main + 짧은 feature 브랜치만 쓴다.
  - bad: develop·release·hotfix까지 Git Flow 풀세트를 썼다.
  - good: main과 짧은 feature 브랜치만 쓰는 GitHub Flow로 갔다.
- **main에 직접 commit** — "급한 수정이라서"로 main 직커밋을 하면 리뷰 누락·추적성 손실·다른 작업과의 충돌 가능성을 한 번에 만든다. 급한 수정도 짧은 hotfix 브랜치 + PR로 처리한다.
  - bad: 급한 수정을 main에 바로 커밋했다.
  - good: 급한 수정도 짧은 hotfix 브랜치 PR로 올렸다.
- **너무 긴 feature 브랜치** — 2주 동안 머지 안 한 브랜치는 main과 격리되어 머지 충돌이 폭발하고, 다른 팀원 작업과 통합 비용이 커진다. 1주 이내 머지를 규칙으로 둔다.
  - bad: feature 브랜치를 2주 넘게 머지하지 않고 뒀다.
  - good: feature 브랜치는 1주 안에 꼭 머지하도록 정했다.

## 핵심 요약

**소규모 팀 디폴트는 GitHub Flow.** main + 짧은 feature 브랜치 + PR 리뷰. 전략을 무겁게 잡을수록 머지 비용이 늘고, 가벼울수록 팀이 실제로 규칙을 지킨다.
