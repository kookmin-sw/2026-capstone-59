"""ai/clients/llm.py 단위 테스트 — Anthropic Direct API 기반 (이슈 #232)."""

import json
import logging
from unittest.mock import AsyncMock, MagicMock

import pytest
from anthropic import APIStatusError
from pydantic import BaseModel

from ai.clients.llm import LLMClient
from ai.exceptions import AIErrorCode, AIGenerationFailedError, BedrockAPIError

MODEL_ID = "claude-haiku-4-5-20251001"


class _Schema(BaseModel):
    """테스트용 단순 스키마."""

    answer: str
    score: int


def _make_message(text_payload: str) -> MagicMock:
    """Anthropic messages.create 응답 형태를 모방."""
    msg = MagicMock()
    msg.content = [MagicMock(text=text_payload)]
    return msg


def _valid_response() -> MagicMock:
    return _make_message(json.dumps({"answer": "ok", "score": 42}))


def _malformed_json_response() -> MagicMock:
    return _make_message("{not valid json")


def _schema_violation_response() -> MagicMock:
    # answer가 누락 → ValidationError 발생
    return _make_message(json.dumps({"score": 1}))


def _make_api_status_error(message: str = "rate limited", status: int = 429) -> APIStatusError:
    """anthropic.APIStatusError 인스턴스를 생성."""
    response = MagicMock()
    response.status_code = status
    return APIStatusError(message=message, response=response, body={"error": {"message": message}})


@pytest.fixture
def anthropic_mock() -> MagicMock:
    """AsyncAnthropic mock — messages.create를 AsyncMock으로 노출."""
    mock = MagicMock()
    mock.messages = MagicMock()
    mock.messages.create = AsyncMock()
    return mock


@pytest.fixture
def client(anthropic_mock: MagicMock) -> LLMClient:
    return LLMClient(
        anthropic_client=anthropic_mock,
        model_id=MODEL_ID,
        max_tokens=128,
        temperature=0.5,
    )


class TestInvokeSuccess:
    @pytest.mark.asyncio
    async def test_invoke_returns_validated_instance(
        self, client: LLMClient, anthropic_mock: MagicMock
    ):
        anthropic_mock.messages.create.return_value = _valid_response()

        result = await client.invoke("hello", _Schema)

        assert isinstance(result, _Schema)
        assert result.answer == "ok"
        assert result.score == 42

    @pytest.mark.asyncio
    async def test_invoke_passes_correct_request_body(
        self, client: LLMClient, anthropic_mock: MagicMock
    ):
        anthropic_mock.messages.create.return_value = _valid_response()

        await client.invoke("질문 내용", _Schema)

        call_kwargs = anthropic_mock.messages.create.call_args.kwargs
        assert call_kwargs["model"] == MODEL_ID
        assert call_kwargs["max_tokens"] == 128
        assert call_kwargs["temperature"] == 0.5
        assert call_kwargs["messages"] == [{"role": "user", "content": "질문 내용"}]


class TestInvokeRetryOnRetryableErrors:
    @pytest.mark.asyncio
    async def test_json_decode_error_then_success(
        self, client: LLMClient, anthropic_mock: MagicMock
    ):
        anthropic_mock.messages.create.side_effect = [
            _malformed_json_response(),
            _valid_response(),
        ]

        result = await client.invoke("p", _Schema, max_retries=2)

        assert result.answer == "ok"
        assert anthropic_mock.messages.create.call_count == 2

    @pytest.mark.asyncio
    async def test_validation_error_then_success(
        self, client: LLMClient, anthropic_mock: MagicMock
    ):
        anthropic_mock.messages.create.side_effect = [
            _schema_violation_response(),
            _valid_response(),
        ]

        result = await client.invoke("p", _Schema, max_retries=2)

        assert result.answer == "ok"
        assert anthropic_mock.messages.create.call_count == 2


class TestInvokeRetryExhaustion:
    @pytest.mark.asyncio
    async def test_schema_mismatch_three_attempts_then_fails(
        self, client: LLMClient, anthropic_mock: MagicMock
    ):
        anthropic_mock.messages.create.side_effect = [
            _schema_violation_response(),
            _schema_violation_response(),
            _schema_violation_response(),
        ]

        with pytest.raises(AIGenerationFailedError) as exc_info:
            await client.invoke("p", _Schema, max_retries=2)

        # max_retries=2 → 1 + 2 = 3회 호출
        assert anthropic_mock.messages.create.call_count == 3
        err = exc_info.value
        assert err.code == AIErrorCode.AI_GENERATION_FAILED
        assert err.details["max_retries"] == 2
        assert err.details["last_error"]["type"] == "schema_validation_error"
        # 불일치 필드 상세 — 'answer' 누락이 errors에 포함되어야 함
        errors = err.details["last_error"]["errors"]
        assert any("answer" in str(e.get("loc", "")) for e in errors)

    @pytest.mark.asyncio
    async def test_json_decode_error_exhausts_retries(
        self, client: LLMClient, anthropic_mock: MagicMock
    ):
        anthropic_mock.messages.create.side_effect = [
            _malformed_json_response(),
            _malformed_json_response(),
            _malformed_json_response(),
        ]

        with pytest.raises(AIGenerationFailedError) as exc_info:
            await client.invoke("p", _Schema, max_retries=2)

        assert anthropic_mock.messages.create.call_count == 3
        assert exc_info.value.details["last_error"]["type"] == "json_decode_error"


class TestBedrockApiErrorImmediate:
    @pytest.mark.asyncio
    async def test_api_error_raises_immediately_without_retry(
        self, client: LLMClient, anthropic_mock: MagicMock
    ):
        api_error = _make_api_status_error("Rate exceeded", status=429)
        anthropic_mock.messages.create.side_effect = api_error

        with pytest.raises(BedrockAPIError) as exc_info:
            await client.invoke("p", _Schema, max_retries=2)

        # 재시도 없음 — 정확히 1회만 호출
        assert anthropic_mock.messages.create.call_count == 1
        err = exc_info.value
        assert err.code == AIErrorCode.BEDROCK_API_ERROR
        assert err.details["error_type"] == "APIStatusError"
        assert "correlation_id" in err.details


class TestCorrelationIdLogging:
    @pytest.mark.asyncio
    async def test_correlation_id_present_in_start_and_success_logs(
        self,
        client: LLMClient,
        anthropic_mock: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ):
        anthropic_mock.messages.create.return_value = _valid_response()

        with caplog.at_level(logging.INFO, logger="ai.clients.llm"):
            await client.invoke("p", _Schema)

        assert len(caplog.records) >= 2
        events = []
        correlation_ids = set()
        for rec in caplog.records:
            data = json.loads(rec.message)
            events.append(data["event"])
            if "correlation_id" in data:
                correlation_ids.add(data["correlation_id"])

        assert "llm_invoke_start" in events
        assert "llm_invoke_success" in events
        # 호출당 정확히 1개의 correlation_id가 모든 로그에 공유되어야 함
        assert len(correlation_ids) == 1

    @pytest.mark.asyncio
    async def test_correlation_id_in_error_logs(
        self,
        client: LLMClient,
        anthropic_mock: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ):
        anthropic_mock.messages.create.side_effect = _make_api_status_error(
            "no", status=403
        )

        with caplog.at_level(logging.INFO, logger="ai.clients.llm"):
            with pytest.raises(BedrockAPIError):
                await client.invoke("p", _Schema)

        error_records = [
            json.loads(r.message)
            for r in caplog.records
            if r.levelno >= logging.ERROR
        ]
        assert any(
            r.get("event") == "llm_bedrock_api_error" and "correlation_id" in r
            for r in error_records
        )

    @pytest.mark.asyncio
    async def test_correlation_id_unique_per_invocation(
        self, client: LLMClient, anthropic_mock: MagicMock, caplog: pytest.LogCaptureFixture
    ):
        anthropic_mock.messages.create.side_effect = lambda **_: _valid_response()

        with caplog.at_level(logging.INFO, logger="ai.clients.llm"):
            await client.invoke("p1", _Schema)
            await client.invoke("p2", _Schema)

        ids = set()
        for rec in caplog.records:
            data = json.loads(rec.message)
            if data.get("event") == "llm_invoke_start":
                ids.add(data["correlation_id"])

        assert len(ids) == 2

    @pytest.mark.asyncio
    async def test_retry_logs_include_attempt_and_correlation_id(
        self,
        client: LLMClient,
        anthropic_mock: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ):
        anthropic_mock.messages.create.side_effect = [
            _schema_violation_response(),
            _valid_response(),
        ]

        with caplog.at_level(logging.WARNING, logger="ai.clients.llm"):
            await client.invoke("p", _Schema, max_retries=2)

        retry_records = [
            json.loads(r.message)
            for r in caplog.records
            if r.levelno == logging.WARNING
        ]
        assert len(retry_records) == 1
        retry = retry_records[0]
        assert retry["event"] == "llm_invoke_retry"
        assert retry["reason"] == "schema_validation_error"
        assert retry["attempt"] == 0
        assert "correlation_id" in retry
