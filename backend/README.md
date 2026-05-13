# Poco Backend

FastAPI + SQLAlchemy + Alembic 기반의 Lambda 백엔드.
`business` (REST API) 와 `ai` (AI Orchestrator) 두 개의 서비스로 구성됨.

---

## 1. CLI 실행

```bash
# Business API (포트 8000)
python main.py business

# AI Orchestrator (포트 8001)
python main.py ai
```

`--reload` 모드로 동작하므로 코드 변경 시 자동 재시작.

---

## 2. 디렉토리 구조

```
backend/
├── main.py                 # 로컬 서버 진입점 (uvicorn)
├── seed.py                 # 시드 데이터 삽입 스크립트
├── pyproject.toml          # Poetry 의존성 정의
├── alembic.ini             # Alembic 설정
├── Dockerfile              # business Lambda 이미지
├── Dockerfile.ai           # ai Lambda 이미지
│
├── alembic/                # DB 마이그레이션
│   ├── env.py
│   └── versions/           # 마이그레이션 리비전 파일
│
└── app/
    ├── business/           # Business 서비스 (REST API)
    │   ├── main.py         # FastAPI 앱 + Mangum 핸들러
    │   ├── routers/        # API 라우터
    │   ├── services/       # 비즈니스 로직
    │   ├── dependencies.py # 공통 의존성 (소유권 검증 등)
    │   └── auth/           # OAuth Provider 구현체
    │
    ├── ai/                 # AI 서비스 (LLM Orchestrator)
    │   ├── main.py
    │   ├── routers/
    │   └── services/
    │
    └── core/               # 공통 모듈 (양 서비스에서 import)
        ├── config.py       # 환경 변수 (pydantic-settings)
        ├── database.py     # SessionLocal, Base
        ├── logging.py      # 로거 세팅 (get_logger)
        ├── exceptions.py   # 도메인 예외
        ├── models/         # SQLAlchemy ORM 모델
        ├── schemas/        # Pydantic DTO
        ├── repositories/   # DB 접근 레이어
        ├── auth/           # JWT, 쿠키, CSRF
        ├── api/            # EnvelopeRouter (응답 래퍼)
        ├── aws/            # boto3 클라이언트
        └── seeds/          # 시드 데이터
```

**레이어 규칙:** `router` → `service` (commit) → `repository` (flush)
Repository는 도메인 예외를 raise하지 않고 모델만 반환.

---

## 3. 개발 환경 세팅 (Poetry)

### 사전 요구사항
- Python 3.13+
- Poetry 2.0+
- PostgreSQL 14+ (로컬 또는 Docker)

### 설치

```bash
# Poetry 설치 (없으면)
curl -sSL https://install.python-poetry.org | python3 -

# 의존성 설치
cd backend
poetry install

# 가상환경 활성화
poetry env activate
# 또는: source $(poetry env info --path)/bin/activate

# 환경 변수 파일 생성
cp .env.example .env
# .env 편집 후 DB / OAuth 등 채우기
```

### 의존성 추가
```bash
poetry add <package>
poetry add --group dev <package>   # dev only
```

---

## 4. 환경 변수 (.env)

| 카테고리 | 변수 | 설명 |
|---|---|---|
| **DB** | `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT` | PostgreSQL 접속 정보 |
| | `DB_SSL` | RDS 등 SSL 필요 시 `true` |
| **AWS** | `AWS_REGION` | Bedrock 호출 리전 |
| | `BEDROCK_MODEL_ID` | Claude 모델 ID |
| | `BEDROCK_KB_ID` | Knowledge Base ID (RAG) |
| | `BEDROCK_DOJ_DATA_SOURCE_ID` | DOJ 데이터 소스 ID |
| | `BEDROCK_CUSTOM_DATA_SOURCE_ID` | 커스텀 데이터 소스 ID |
| **JWT** | `JWT_SECRET_KEY` | 토큰 서명 키 (랜덤 32+ chars) |
| | `JWT_ALGORITHM` | `HS256` 권장 |
| | `ACCESS_TOKEN_EXPIRE_MINUTES` | Access Token 만료 (분) |
| | `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh Token 만료 (일) |
| **OAuth** | `GOOGLE_CLIENT_ID/SECRET/REDIRECT_URI` | Google OAuth |
| | `NAVER_CLIENT_ID/SECRET/REDIRECT_URI` | Naver OAuth |
| | `FRONTEND_REDIRECT_URL` | OAuth 콜백 완료 후 프론트로 redirect할 URL |
| **CORS** | `CORS_ALLOWED_ORIGINS` | JSON 배열 `["https://app.com"]` |
| **Cookie** | `COOKIE_SECURE` | HTTPS 환경 `true`, 로컬 HTTP `false` |
| | `COOKIE_SAMESITE` | `lax` / `strict` / `none` |
| | `COOKIE_DOMAIN` | 비우면 현재 호스트, 서브도메인 공유 시 `.poco.com` |
| **Logging** | `LOG_LEVEL` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| | `LOG_FORMAT` | `json` (운영) / `text` (로컬) |

---

## 5. Alembic (DB 마이그레이션)

### 현재 스키마 적용
```bash
alembic upgrade head
```

### 새 마이그레이션 생성
```bash
# 모델 변경 후 autogenerate
alembic revision --autogenerate -m "add user table"

# 빈 마이그레이션
alembic revision -m "manual change"
```

> **주의:** autogenerate 결과는 항상 검토 후 커밋.
> 로컬 DB에 수동으로 추가된 컬럼이 있으면 잘못된 `drop_column`이 생길 수 있음.

### 자주 쓰는 명령
```bash
alembic current              # 현재 리비전 확인
alembic history              # 전체 히스토리
alembic downgrade -1         # 한 단계 롤백
alembic downgrade <rev>      # 특정 리비전으로
```

### Multiple Heads 발생 시
같은 `down_revision`을 가진 마이그레이션이 두 개 생기면 발생.
한쪽의 `down_revision`을 상대방의 revision id로 변경해서 직렬화.

---

## 6. Seed Data

`alembic upgrade head` 이후 실행. Stage / RequiredStep 등 기준 데이터를 삽입.

```bash
# 전체 seed
python seed.py

# 특정 seed만
python seed.py stage
python seed.py required_step
```

seed 정의 위치: `app/core/seeds/`

> 이미 삽입된 데이터는 멱등 처리되므로 여러 번 실행해도 안전.

---

## 7. 디버깅

### 로그 레벨 변경
```bash
# .env
LOG_LEVEL=DEBUG
LOG_FORMAT=text    # 로컬 가독성
```

### 코드에서 로거 사용
```python
from app.core.logging import get_logger

logger = get_logger(__name__)
logger.debug("event", extra={"step_id": str(step_id), "count": 3})
```

### VS Code 디버거 (launch.json)
```json
{
  "name": "Business API",
  "type": "python",
  "request": "launch",
  "program": "${workspaceFolder}/backend/main.py",
  "args": ["business"],
  "console": "integratedTerminal",
  "envFile": "${workspaceFolder}/backend/.env"
}
```

### API 문서 (Swagger)
- Business: http://localhost:8000/docs
- AI: http://localhost:8001/docs

### DB 직접 접속
```bash
psql -h localhost -U postgres -d pocodb
```

---

## 8. OAuth 세팅 가이드

### Google
1. [Google Cloud Console](https://console.cloud.google.com) → API 및 서비스 → 사용자 인증 정보
2. **OAuth 2.0 클라이언트 ID** 생성 (애플리케이션 유형: 웹 애플리케이션)
3. **승인된 리디렉션 URI** 등록:
   ```
   http://localhost:8000/auth/google/callback         # 로컬
   https://api.your-domain.com/auth/google/callback   # 운영
   ```
4. 발급된 `Client ID` / `Client Secret`을 `.env`에 입력
   ```
   GOOGLE_CLIENT_ID=...
   GOOGLE_CLIENT_SECRET=...
   GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
   ```

### Naver
1. [Naver Developers](https://developers.naver.com/apps) → 애플리케이션 등록
2. **사용 API**: 네이버 로그인
3. **서비스 URL** 및 **Callback URL** 등록:
   ```
   http://localhost:8000/auth/naver/callback
   ```
4. `.env` 입력
   ```
   NAVER_CLIENT_ID=...
   NAVER_CLIENT_SECRET=...
   NAVER_REDIRECT_URI=http://localhost:8000/auth/naver/callback
   ```

### 프론트 연동
- 로그인 시작: `GET /auth/{provider}/login` 으로 redirect
- 콜백 완료 후 백엔드는 `FRONTEND_REDIRECT_URL`로 redirect (HttpOnly 쿠키에 토큰 set)
- 이후 API 호출은 쿠키 자동 전송 + `X-CSRF-Token` 헤더 필요

> **도메인 다를 때 쿠키 이슈:** 프론트(CloudFront)와 API(API Gateway) 도메인이 다르면 쿠키가 전송되지 않음.
> 해결: ① 커스텀 도메인으로 같은 루트 도메인 사용, ② CloudFront에 `/api/*` behavior 추가해 단일 도메인화.