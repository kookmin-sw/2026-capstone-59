# Poco AI

Bedrock Claude + Bedrock Knowledge Base 기반의 **독립 AI 모듈**.
백엔드(FastAPI) 의존성 없이 `ai/` 폴더 단독으로 개발·검증 가능하며, 검증 완료 후 `backend/app/ai/services/`에 납품되는 구조.

---

## 1. CLI 실행

```bash
# 파이프라인 전체 실측 (Stage 1 R1 고정 fixture, 5회 반복)
python -m ai.latency_simulator --runs 5

# 스트리밍 모드 (Stage B side_panel × 3을 SSE 스트리밍으로 실행, TTFT·TTLT 측정)
python -m ai.latency_simulator --streaming --runs 5

# 대화형 시뮬레이션 (사용자가 직접 Step을 선택하며 흐름 재현)
python -m ai.cli_simulator
```

실행 전 `AWS_REGION`, `MODEL_ID`, `KB_ID`(+ data source ID) 환경 변수가 설정돼 있어야 합니다. 아래 [4. 환경 변수](#4-환경-변수-env) 참조.

---

## 2. 디렉토리 구조

```
ai/
├── pyproject.toml              # 의존성 정의 (uv / pip-tools 호환)
├── config.py                   # 환경 변수 로딩 (pydantic-settings)
├── exceptions.py               # 도메인 예외 (BedrockAPIError, AIGenerationFailedError ...)
├── cli_simulator.py            # 대화형 파이프라인 시뮬레이터
├── latency_simulator.py        # 레이턴시 실측 CLI (sync / streaming)
│
├── clients/                    # AWS 호출 공통 클라이언트
│   ├── llm.py                  #   LLMClient (invoke / invoke_stream)
│   └── rag.py                  #   RAGClient (Bedrock Knowledge Base retrieve)
│
├── services/                   # 시나리오별 오케스트레이터 (public interface)
│   ├── __init__.py             #   generate_steps / judge_required_step /
│   │                           #   generate_side_panel / generate_side_panel_stream /
│   │                           #   generate_design_export
│   ├── step_generator.py       #   generate 시나리오
│   ├── required_step_judge.py  #   accept 시나리오
│   ├── side_panel_generator.py #   side_panel 시나리오 (sync + stream)
│   ├── design_export_generator.py #   design_export 시나리오 (.md 다운로드)
│   └── position_label.py       #   사이드패널 위치감 라벨 deterministic 결정
│
├── schemas/                    # Pydantic 입출력 스키마
│   ├── common.py               #   ProjectInfo, StageInfo, DecisionHistoryItem ...
│   ├── generate.py             #   GenerateInput / GenerateOutput
│   ├── accept.py               #   AcceptInput / AcceptOutput
│   ├── side_panel.py           #   SidePanelInput / SidePanelOutput
│   └── design_export.py        #   DesignExportInput / DesignExportOutput
│
├── prompts/                    # LLM 프롬프트 템플릿 (.txt, 별도 모듈화)
│   ├── generate.txt
│   ├── accept.txt
│   ├── side_panel.txt
│   ├── design_export.txt
│   ├── template.py             #   PromptTemplate.load_and_render
│   └── activity_guides.py      #   24개 R 활동 가이드 + 나쁜 예 기반 R-blocklist
│
├── data/                       # RAG 인덱싱 원본 (Bedrock Knowledge Base 업로드용)
│   ├── doj/                    #   DOJ Data Source: DOJ SDLC Guidance Document 마크다운 변환본
│   └── custom/                 #   Custom Data Source: 팀 자체 제작 가이드 문서
│       ├── glossary/           #     용어 사전
│       └── technique/          #     기법 가이드
│
├── fixtures/                   # 테스트·시뮬레이터 공용 고정 데이터
│   └── required_steps.py       #   Stage별 24개 필수 Step 정의
│
└── tests/                      # 단위 테스트 + Property-Based Tests
    ├── test_llm_client*.py
    ├── test_rag_client*.py
    ├── test_step_generator*.py
    ├── test_required_step_judge*.py
    ├── test_side_panel_generator*.py
    └── test_latency_simulator*.py
```

**레이어 규칙:** `service` → `client` → `AWS`
- `service`(오케스트레이터)는 입력 조립 + 프롬프트 렌더 + 결과 검증만 담당
- `client`(`LLMClient`, `RAGClient`)는 boto3 호출과 재시도·에러 래핑만 담당
- Pydantic 스키마 검증은 `LLMClient.invoke()` 내부에서 수행

---

## 3. 개발 환경 세팅

### 사전 요구사항
- Python 3.13+
- AWS CLI 또는 IAM 자격증명 (Bedrock / Bedrock Knowledge Base 호출 권한)
- Bedrock Claude 모델 액세스 승인 (Haiku 4.5, Sonnet 4 등)
- Bedrock Knowledge Base 생성 완료 + Data Source 인덱싱 완료

### 설치

```bash
cd ai
# 런타임 의존성
pip install -e .

# 개발·테스트 의존성
pip install -e ".[dev]"
```

> CloudShell 등 가상환경 내부에서는 `--user` 옵션을 빼고 실행합니다. uv를 쓴다면 `uv pip install -e .` 로 대체 가능.

### 환경 변수 파일

프로젝트 루트에 `.env` 파일을 만들거나 셸 환경 변수로 직접 설정합니다 (셋 중 아무 방식이나 가능):

```env
AWS_REGION=us-east-1
MODEL_ID=us.anthropic.claude-haiku-4-5-20251001-v1:0
KB_ID=<your-knowledge-base-id>
DOJ_DATA_SOURCE_ID=<your-doj-data-source-id>
CUSTOM_DATA_SOURCE_ID=<your-custom-data-source-id>
MAX_TOKENS=4096        # 선택
TEMPERATURE=0.7        # 선택
```

---

## 4. 환경 변수 (.env)

| 카테고리 | 변수 | 설명 |
|---|---|---|
| **AWS** | `AWS_REGION` | Bedrock 호출 리전 (us-east-1 권장) |
| **모델** | `MODEL_ID` | Claude inference profile ID. 운영: `us.anthropic.claude-haiku-4-5-20251001-v1:0` |
| | `MAX_TOKENS` | LLM 응답 최대 토큰 (기본 4096, 시나리오별 override 가능) |
| | `TEMPERATURE` | LLM temperature (기본 0.7) |
| **RAG** | `KB_ID` | Bedrock Knowledge Base ID |
| | `DOJ_DATA_SOURCE_ID` | DOJ SDLC 문서가 인덱싱된 data source ID |
| | `CUSTOM_DATA_SOURCE_ID` | 팀 자체 제작 가이드가 인덱싱된 data source ID |

모든 변수는 Optional이며 생략 시 `ai/config.py`의 기본값이 적용됩니다. 단, `KB_ID`가 비어 있으면 RAG 호출은 빈 결과를 반환합니다.

---

## 5. 테스트

### 전체 실행

```bash
pytest ai/tests/ -q
```

### 주요 테스트 그룹

| 그룹 | 목적 |
|---|---|
| `test_llm_client*` | Bedrock 호출 wrapper — invoke/invoke_stream의 max_tokens 우선순위, 코드 펜스 방어, 이벤트 루프 블로킹 회귀 방지 |
| `test_rag_client*` | Bedrock Knowledge Base retrieve wrapper — data source 필터링, 빈 결과 처리 |
| `test_step_generator*` | generate 시나리오 — 프롬프트 조립, 필수 Step 측면 기반 생성, 중복 금지 |
| `test_required_step_judge*` | accept 시나리오 — 측면 커버리지 기반 boolean 판단 |
| `test_side_panel_generator*` | side_panel 시나리오 — sync/stream 파리티, Dictionary↔Mentoring 정합성 |
| `test_latency_simulator*` | 레이턴시 시뮬레이터 — CLI 인자, summary 집계, streaming 스키마 |
| `*_property.py` | Hypothesis 기반 Property-Based Tests — 스키마 불변식, 프롬프트 조립 멱등성 |

> AWS 실호출 없이 모두 boto3 mock 으로 동작합니다. 실호출 검증은 `latency_simulator` 또는 `cli_simulator`로 진행.

### 특정 시나리오만

```bash
pytest ai/tests/test_side_panel_generator.py -q
pytest ai/tests/test_llm_client_stream.py -q
```

---

## 6. 파이프라인 시뮬레이터

### 6-1. latency_simulator — 실제 Bedrock 호출 기반 레이턴시 측정

```bash
# 기본 실행 (Stage 1 R1 고정 입력, 1회)
python -m ai.latency_simulator

# 5회 반복하여 p50/p100 통계 수집
python -m ai.latency_simulator --runs 5

# 결과를 JSON으로 저장
python -m ai.latency_simulator --runs 5 --output results.json

# 스트리밍 모드 (side_panel × 3 SSE, TTFT/TTLT 측정)
python -m ai.latency_simulator --streaming --runs 5

# baseline 기록 모드 (기존 파일 보호)
python -m ai.latency_simulator --baseline --output baseline.json
```

Exit code: 0 성공 / 1 stage 실패 / 2 baseline 파일 중복 / 130 사용자 중단(SIGINT).

### 6-2. cli_simulator — 대화형 파이프라인

사용자가 Step을 직접 고르며 프로젝트 진행을 재현합니다. 프롬프트 튜닝이나 콘텐츠 품질 확인에 유용.

```bash
python -m ai.cli_simulator
```

---

## 7. AI 모듈 공개 함수 (5개)

`ai/services/__init__.py`에서 re-export. 백엔드가 이 5개 함수만 import해서 사용합니다.

| 함수 | 시나리오 | 반환 타입 |
|---|---|---|
| `generate_steps` | 일반 Step 3개 동적 생성 | `GenerateOutput` |
| `judge_required_step` | 필수 Step 충족 판단 (`fulfillment_criteria` 커버리지 기반) | `AcceptOutput` (boolean) |
| `generate_side_panel` | 일반 Step 사이드패널 콘텐츠 생성 (sync) | `SidePanelOutput` |
| `generate_side_panel_stream` | 일반 Step 사이드패널 콘텐츠 생성 (stream) | `AsyncIterator[str]` |
| `generate_design_export` | 사고 궤적 .md 다운로드 — RS별 What·Why 질문 + 영역 전체 핵심 정리 생성 | `DesignExportOutput` |

**병렬 호출(judge ∥ generate, side_panel × 3 등) 및 SSE 응답 layer 구성은 백엔드 오케스트레이션 영역**입니다. AI 모듈은 위 5개 단독 호출만 public interface로 노출하며, 합성·멀티플렉싱·SSE 엔드포인트 구성·.md 골격 렌더 등은 백엔드 PR에서 처리합니다.

design-export 시나리오의 `.md` 골격(자기소개 블록쿼터·프로젝트 컨텍스트·RS 헤더·진행한 결정·푸터)은 백엔드 `Design_Export_Renderer`가 직접 렌더하며, AI 모듈은 변환·합성이 필요한 두 부분(`questions_per_rs`, `core_summary`) 만 JSON으로 반환합니다.

---

## 8. 프롬프트 튜닝

프롬프트 템플릿은 Python 코드와 완전히 분리되어 `ai/prompts/*.txt`에 저장됩니다. 톤·제약·RAG 지시어 변경 시 `.txt`만 수정하면 되며, 서비스 로직 코드를 건드릴 필요가 없습니다.

### 주요 원칙
- **출력 형식 엄격** — 모든 프롬프트가 JSON 한 덩어리만 반환하도록 지시 + 서버 측에서 코드 펜스 자동 제거
- **한국어 순도** — 일본어/중국어 어휘 혼입 금지. 영문 고유명사·약어·괄호 병기는 예외로 허용
- **톤 일관성** — 사이드패널 AI 생성본은 사람이 작성한 24개 필수 Step 사이드패널 콘텐츠(`content/required-steps/*`)와 동일 톤 유지
- **Dictionary ↔ Mentoring 정합성** — Dictionary의 각 term은 mentoring 본문에 실제 등장한 단어·구절만 사용 (발명 금지, 축약·영문 병기 금지)

### 튜닝 후 검증 절차
1. `pytest ai/tests/ -q` — 회귀 확인
2. `python -m ai.latency_simulator --streaming --runs 3` — 실제 Bedrock 호출 품질 확인
3. 프롬프트 크기 증가분 × TTFT 영향 측정

---

## 9. 디버깅

### 로거 사용

```python
import logging
logger = logging.getLogger(__name__)
logger.info(json.dumps({"event": "step_generator_invoke", "step": "..."}))
```

`LLMClient`와 `RAGClient`는 모든 호출에 **correlation_id** (UUID)를 발급하고 `event` 기반 구조화 JSON 로그를 남깁니다. 로그 검색 시 correlation_id로 단일 호출 궤적 전체를 추적할 수 있습니다.

### 주요 로그 이벤트

| event | 의미 |
|---|---|
| `llm_invoke_start` / `llm_invoke_success` / `llm_invoke_retry` / `llm_invoke_failed` | sync 호출 lifecycle |
| `llm_invoke_stream_start` / `llm_invoke_stream_end` / `llm_invoke_stream_failed` | stream 호출 lifecycle |
| `llm_bedrock_api_error` | Bedrock API 에러 (즉시 BedrockAPIError로 래핑) |
| `rag_search_start` / `rag_search_success` / `rag_search_failed` | Knowledge Base retrieve lifecycle |
| `step_generator_invoke` / `required_step_judge_invoke` / `side_panel_generator_invoke` | 시나리오별 진입점 |
| `side_panel_stream_start` | side_panel 스트리밍 시작 |

### 로컬 실행 시 JSON 대신 읽기 편한 포맷
```python
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s | %(name)s | %(message)s")
```

---

## 10. 백엔드 납품 (현재 상태)

AI 모듈은 `backend/app/ai/services/`에 **import 경로 그대로 사용** 중입니다. AI 모듈 코드는 `ai/` 폴더 하나만 유지되며, 백엔드는 `from ai import ...` 형태로 직접 import합니다 (sys.path를 통해 둘 다 참조 가능).

백엔드에서 사용하는 형태:

```python
from ai import (
    generate_steps,
    judge_required_step,
    generate_side_panel,
    generate_side_panel_stream,
    generate_design_export,
)

# 예시: Accept API 핸들러
async def accept_step(step_id: str):
    result = await judge_required_step(input_data, bedrock_client, model_id)
    if result.is_current_required_step_completed:
        ...
    generated = await generate_steps(input_data, bedrock_client, bedrock_agent_client, model_id, kb_id)
    ...

# 예시: design-export SSE 엔드포인트 (backend/app/ai/routers/projects.py)
ai_output = await generate_design_export(input_data, bedrock_client, model_id)
md = design_export_renderer.render(input_data, ai_output)
yield f"event: complete\ndata: {json.dumps({'markdown': md, 'filename': filename})}\n\n"
```

백엔드는 위 5개 함수를 직접 호출하고, **병렬 실행 / SSE 엔드포인트 구성 / `.md` 골격 렌더 / DB 저장 / 에러 응답 변환은 모두 백엔드 레이어에서 처리**합니다. design-export의 경우 AI는 동기 1회 호출이고, 백엔드가 결과를 받아 SSE `event: complete` 청크로 전송하는 *"whole-response SSE"* 패턴을 사용합니다 (API Gateway 29초 동기 한도 우회용).

---

## 11. 참고 문서

- [`ai/data/README.md`](./data/README.md) — RAG 인덱싱 원본 가이드
- [`backend/README.md`](../backend/README.md) — 백엔드 실행 방법
- [`index.md`](../index.md) — 프로젝트 전체 소개 페이지

