# Logging Convention

서비스 레이어에서 사용하는 로깅 규칙. CloudWatch에서 검색/필터/집계가 쉽도록
**구조화 로그(JSON)** 를 전제로 한다.

---

## 1. 기본 사용법

```python
from app.core.logging import get_logger

logger = get_logger(__name__)

logger.info(
    "project: created",
    extra={"project_id": str(project.id), "user_id": str(user.id)},
)
```

- **모듈마다** `logger = get_logger(__name__)` 한 줄로 인스턴스 획득
- 메시지는 **고정 문자열**, 데이터는 **`extra`** 로 분리

---

## 2. 로그 레벨

| 레벨 | 사용 시점 | 예시 |
|---|---|---|
| `DEBUG` | 내부 분기/계산 결과, 디버깅용 상세 상태 | 캐시 hit/miss, 후보군 산출 결과 |
| `INFO` | **비즈니스 이벤트 성공** (상태 변경, 의미 있는 도착점) | 프로젝트 생성, 스텝 Accept, 롤백 완료 |
| `WARNING` | 정상 흐름이지만 주의 필요 (복구 가능) | OAuth 토큰 갱신 실패 후 재발급, 폴백 동작 |
| `ERROR` | 처리 실패/예외 발생 (사용자 영향) | DB 제약 위반, 외부 API 4xx/5xx, 도메인 예외 |
| `CRITICAL` | 서비스 자체 위협 | 거의 사용 X (인프라 알람으로 대체) |

> **원칙:** 운영 환경 기본 `LOG_LEVEL=INFO`. DEBUG는 일시적 디버깅 외에는 끔.

---

## 3. 메시지 형식

```
"<도메인>: <동사형 이벤트>"
```

- 모두 **소문자**, 짧고 고정된 문자열 (변수 보간 금지)
- 도메인 prefix는 모듈/기능 단위로 통일
- 동사는 과거형(완료) 또는 진행형(진행 중)

### 도메인 prefix 예시
| prefix | 영역 |
|---|---|
| `project:` | 프로젝트 생성/수정/삭제/복원 |
| `stage:` | Stage 전환/완료 |
| `step:` | Step accept/reject/rollback |
| `required_step:` | Required Step fulfillment |
| `auth:` | 로그인/로그아웃/토큰 갱신 |
| `oauth:` | OAuth 콜백/Provider 호출 |
| `ai:` | LLM/Bedrock 호출 |
| `rag:` | Knowledge Base 검색 |
| `notion:` | Notion API 호출 |

### 메시지 예시
```python
"project: created"
"project: name updated"
"step: accepted"
"step: rollback completed"
"oauth: callback received"
"ai: generation failed"
```

❌ 나쁜 예 — 변수 보간/장황한 문장
```python
f"Project {project_id} was successfully created by user {user_id}"
```

---

## 4. `extra` 필드 규칙

### 4-1. 명명 규칙
| 종류 | 접미사/접두사 | 예 |
|---|---|---|
| ID | `_id` | `project_id`, `step_id`, `user_id`, `stage_id` |
| 개수 | `_count` | `canceled_count`, `step_count` |
| 시간(ms) | `_ms` | `duration_ms`, `latency_ms` |
| 시퀀스 번호 | `_sequence` | `stage_sequence` |
| Boolean | `is_` 접두사 | `is_required`, `is_stage_completed` |
| 외부 ID | `external_<name>_id` | `external_oauth_user_id` |

### 4-2. 타입 변환
- **UUID는 반드시 `str(...)` 변환** — JSON 직렬화 안전
- datetime은 ISO 문자열로 변환
- 모델 객체 자체는 넣지 않음 (ID/이름만 추출)

### 4-3. 도메인 컨텍스트 ID는 가능한 한 포함
같은 이벤트 안에서 추적이 쉽도록:
- 프로젝트 관련 이벤트 → `project_id` 포함
- Step 관련 → `project_id` + `stage_id` + `step_id`
- 사용자 행위 → `user_id` 포함

```python
logger.info(
    "step: accepted",
    extra={
        "project_id": str(step.project_id),
        "stage_id": str(step.stage_id),
        "step_id": str(step.id),
        "is_required": step.required_step_id is not None,
    },
)
```

---

## 5. 예외 로깅

도메인 예외(`PocoError` 하위)는 보통 `exception_handlers`가 응답으로 처리하므로
**서비스 레이어에서는 발생 직전 사유**를 ERROR로 남긴다.

```python
if step_repo.has_children(db, step_id):
    logger.warning(
        "step: rollback rejected — has children",
        extra={"step_id": str(step_id), "project_id": str(step.project_id)},
    )
    raise InvalidRollbackError()
```

외부 호출 실패 등 unexpected 예외는 `exc_info=True`로 스택 트레이스 보존:

```python
try:
    response = await llm.invoke(...)
except Exception:
    logger.error(
        "ai: bedrock invocation failed",
        extra={"project_id": str(project_id)},
        exc_info=True,
    )
    raise AIGenerationFailedError()
```

---

## 6. 어디에 남기는가

| 레이어 | 로깅 여부 | 이유 |
|---|---|---|
| **Router** | ❌ | FastAPI 액세스 로그로 충분 |
| **Service** | ✅ | 비즈니스 이벤트의 본거지 |
| **Repository** | ❌ | 너무 노이즈 많음. 호출자(service)가 결과로 로깅 |
| **외부 클라이언트** (ai/, boto3 래퍼) | ✅ (DEBUG/ERROR) | 호출 시점/실패만 |

---

## 7. 서비스 함수당 기본 로그 패턴

### 7-1. 상태 변경 (Create/Update/Delete)
**완료 시점**에 INFO 한 줄.

```python
def create_project(...):
    project = project_repo.add_project(...)
    db.commit()
    logger.info(
        "project: created",
        extra={"project_id": str(project.id), "user_id": str(user_id)},
    )
    return project
```

### 7-2. 다단계 작업 (Rollback, Stage 전환 등)
**진입(DEBUG)** + **중간 분기(DEBUG)** + **완료(INFO)** + **거부 시(WARNING/ERROR)**

```python
def rollback_step(db, step_id):
    logger.debug("step: rollback start", extra={"step_id": str(step_id)})
    ...
    if step_repo.has_children(...):
        logger.warning("step: rollback rejected — has children", extra={...})
        raise InvalidRollbackError()
    ...
    logger.info(
        "step: rollback completed",
        extra={"step_id": str(step_id), "canceled_count": len(canceled)},
    )
```

### 7-3. 외부 시스템 호출
**호출 직전(DEBUG)** + **실패(ERROR with `exc_info=True`)**. 성공 시 별도 로그 불필요(상위 비즈니스 이벤트로 충분).

```python
logger.debug("ai: invoking bedrock", extra={"prompt_len": len(prompt)})
try:
    result = await llm.invoke(...)
except Exception:
    logger.error("ai: bedrock invocation failed", extra={...}, exc_info=True)
    raise
```

### 7-4. 조회 (Query)
**기본적으로 로깅하지 않음.** 비즈니스 의미 있는 조회만(권한 위반, 예상치 못한 not-found 등) WARNING/ERROR로 남김.

---

## 8. 금지 사항

다음은 **절대 로그에 남기지 않는다**.

- JWT access/refresh token 원문
- OAuth client secret, code, state 원문
- 비밀번호, API key
- 사용자 email, 전화번호 등 PII (마스킹 시에는 OK)
- 외부 API 요청/응답 본문 전체 (필요 시 status code, length, 일부만)

```python
# ❌
logger.info("auth: token issued", extra={"access_token": token})

# ✅
logger.info("auth: token issued", extra={"user_id": str(user.id), "expires_in": 3600})
```

---

## 9. 표준 필드 (자동 포함되는 것)

`JsonFormatter`가 자동으로 추가:
- `timestamp` (ISO 8601, UTC)
- `level`
- `logger` (모듈 경로)
- `message`
- `exception` (스택 트레이스, `exc_info=True`일 때)

→ `extra`에는 **도메인 데이터만** 넣으면 됨.

---

## 10. 체크리스트 (코드 리뷰용)

- [ ] 메시지가 `"도메인: 동사"` 형식인가
- [ ] 변수가 메시지에 보간되지 않고 `extra`에 분리되어 있는가
- [ ] UUID/datetime이 `str()` 변환되었는가
- [ ] 비즈니스 이벤트 = INFO, 단순 분기 디버깅 = DEBUG 인가
- [ ] 도메인 예외 발생 직전에 WARNING/ERROR가 있는가
- [ ] 토큰/비밀번호/이메일 등 민감 정보가 없는가
- [ ] 같은 이벤트 안에서 추적할 ID(project_id 등)가 포함되어 있는가
