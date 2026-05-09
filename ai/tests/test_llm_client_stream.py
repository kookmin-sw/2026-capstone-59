"""ai/clients/llm.py LLMClient.invoke_stream 단위 테스트."""

import json
import logging
from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from ai.clients.llm import LLMClient
from ai.exceptions import BedrockAPIError

MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _delta_event(text: str) -> dict:
    payload = {"type": "content_block_delta", "delta": {"text": text}}
    return {"chunk": {"bytes": json.dumps(payload).encode("utf-8")}}


def _non_delta_event() -> dict:
    payload = {"type": "message_start"}
    return {"chunk": {"bytes": json.dumps(payload).encode("utf-8")}}


def _invalid_chunk_event() -> dict:
    return {"chunk": {"bytes": b"{not valid json"}}


def _stream_response(events: list) -> dict:
    return {"body": iter(events)}


async def _collect(agen) -> list:
    result = []
    async for chunk in agen:
        result.append(chunk)
    return result


def _make_bedrock_mock(events: list) -> MagicMock:
    bedrock = MagicMock()
    bedrock.invoke_model_with_response_stream.return_value = _stream_response(events)
    return bedrock


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestInvokeStream:
    @pytest.mark.asyncio
    async def test_invoke_stream_yields_chunks(self) -> None:
        """delta event → 텍스트 yield, non-delta event는 건너뜀."""
        events = [
            _non_delta_event(),
            _delta_event("A"),
            _delta_event("B"),
            _delta_event("C"),
        ]
        bedrock = _make_bedrock_mock(events)
        client = LLMClient(bedrock_client=bedrock, model_id=MODEL_ID)

        chunks = await _collect(client.invoke_stream("prompt"))

        assert chunks == ["A", "B", "C"]

    @pytest.mark.asyncio
    async def test_invoke_stream_max_tokens_priority(self) -> None:
        """invoke_stream max_tokens 3단 우선순위 검증."""

        def _captured_max_tokens(bedrock: MagicMock) -> int:
            body_str = bedrock.invoke_model_with_response_stream.call_args.kwargs["body"]
            return json.loads(body_str)["max_tokens"]

        # Case 1: 명시값 > 생성자 값
        bedrock1 = _make_bedrock_mock([])
        client1 = LLMClient(bedrock_client=bedrock1, model_id=MODEL_ID, max_tokens=4096)
        await _collect(client1.invoke_stream("p", max_tokens=512))
        assert _captured_max_tokens(bedrock1) == 512

        # Case 2: 생성자 값 사용 (invoke_stream max_tokens 생략)
        bedrock2 = _make_bedrock_mock([])
        client2 = LLMClient(bedrock_client=bedrock2, model_id=MODEL_ID, max_tokens=2048)
        await _collect(client2.invoke_stream("p"))
        assert _captured_max_tokens(bedrock2) == 2048

        # Case 3: 생성자 기본값 4096 폴백
        bedrock3 = _make_bedrock_mock([])
        client3 = LLMClient(bedrock_client=bedrock3, model_id=MODEL_ID)
        await _collect(client3.invoke_stream("p"))
        assert _captured_max_tokens(bedrock3) == 4096

    @pytest.mark.asyncio
    async def test_invoke_stream_raises_bedrock_api_error_on_client_error(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """invoke_model_with_response_stream ClientError → BedrockAPIError."""
        bedrock = MagicMock()
        bedrock.invoke_model_with_response_stream.side_effect = ClientError(
            {"Error": {"Code": "ThrottlingException", "Message": "Rate exceeded"}},
            "InvokeModelWithResponseStream",
        )
        client = LLMClient(bedrock_client=bedrock, model_id=MODEL_ID)

        with caplog.at_level(logging.ERROR):
            with pytest.raises(BedrockAPIError):
                await _collect(client.invoke_stream("prompt"))

        assert any("llm_invoke_stream_failed" in r.message for r in caplog.records)

    @pytest.mark.asyncio
    async def test_invoke_stream_skips_invalid_chunks(self) -> None:
        """invalid JSON 청크는 skip하고 스트림 계속."""
        events = [
            _delta_event("A"),
            _invalid_chunk_event(),
            _delta_event("B"),
        ]
        bedrock = _make_bedrock_mock(events)
        client = LLMClient(bedrock_client=bedrock, model_id=MODEL_ID)

        chunks = await _collect(client.invoke_stream("prompt"))

        assert chunks == ["A", "B"]

    @pytest.mark.asyncio
    async def test_invoke_stream_does_not_block_event_loop(self) -> None:
        """두 stream을 gather로 돌렸을 때 직렬화되지 않는다."""
        import asyncio
        import time as _time

        class _SlowIterable:
            def __init__(self, events, delay=0.05):
                self._events = events
                self._delay = delay
                self._i = 0

            def __iter__(self):
                return self

            def __next__(self):
                if self._i >= len(self._events):
                    raise StopIteration
                _time.sleep(self._delay)
                e = self._events[self._i]
                self._i += 1
                return e

        events = [_delta_event(f"c{i}") for i in range(5)]

        bedrock = MagicMock()
        bedrock.invoke_model_with_response_stream.side_effect = [
            {"body": _SlowIterable(events)},
            {"body": _SlowIterable(events)},
        ]
        client = LLMClient(bedrock_client=bedrock, model_id=MODEL_ID, max_tokens=256)

        async def _first_chunk_time(agen):
            start = asyncio.get_event_loop().time()
            async for _ in agen:
                return asyncio.get_event_loop().time() - start
            return float("inf")

        gen1 = client.invoke_stream("p1")
        gen2 = client.invoke_stream("p2")
        t1, t2 = await asyncio.gather(_first_chunk_time(gen1), _first_chunk_time(gen2))

        # 직렬화되면 t2 >= 5 * 0.05 = 0.25s. async면 t2 < 0.2s.
        assert t2 < 0.2, f"두 번째 stream이 직렬화됨: t1={t1:.3f}s, t2={t2:.3f}s"
