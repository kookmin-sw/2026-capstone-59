"""ai/clients/llm.py LLMClient.invoke_stream 단위 테스트 — Anthropic Direct API (이슈 #232)."""

import asyncio
from unittest.mock import MagicMock

import pytest
from anthropic import APIStatusError

from ai.clients.llm import LLMClient
from ai.exceptions import BedrockAPIError

MODEL_ID = "claude-haiku-4-5-20251001"


# ---------------------------------------------------------------------------
# Helpers — anthropic.messages.stream context manager mock
# ---------------------------------------------------------------------------


class _FakeTextStream:
    """anthropic stream.text_stream 모방 — async iterator로 청크를 yield."""

    def __init__(self, chunks: list, delay: float = 0.0) -> None:
        self._chunks = list(chunks)
        self._delay = delay

    def __aiter__(self):
        return self

    async def __anext__(self) -> str:
        if not self._chunks:
            raise StopAsyncIteration
        if self._delay > 0:
            await asyncio.sleep(self._delay)
        return self._chunks.pop(0)


class _FakeStreamContext:
    """anthropic.messages.stream(...) 반환값 모방 — async context manager."""

    def __init__(self, chunks: list, delay: float = 0.0) -> None:
        self.text_stream = _FakeTextStream(chunks, delay=delay)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None


def _make_anthropic_mock(chunks_list_or_factory) -> MagicMock:
    """chunks_list_or_factory가 list면 단일 스트림, callable이면 매 호출마다 새 컨텍스트."""
    mock = MagicMock()
    mock.messages = MagicMock()
    if callable(chunks_list_or_factory):
        mock.messages.stream = MagicMock(side_effect=chunks_list_or_factory)
    else:
        mock.messages.stream = MagicMock(return_value=_FakeStreamContext(chunks_list_or_factory))
    return mock


async def _collect(agen) -> list:
    result = []
    async for chunk in agen:
        result.append(chunk)
    return result


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestInvokeStream:
    @pytest.mark.asyncio
    async def test_invoke_stream_yields_chunks(self) -> None:
        """text_stream의 청크가 (tail-buffer batching 후) 그대로 yield된다."""
        anthropic = _make_anthropic_mock(["A", "B", "C"])
        client = LLMClient(anthropic_client=anthropic, model_id=MODEL_ID)

        chunks = await _collect(client.invoke_stream("prompt"))

        # Tail-buffer batches final chars; check content, not exact chunk split.
        assert "".join(chunks) == "ABC"

    @pytest.mark.asyncio
    async def test_invoke_stream_max_tokens_priority(self) -> None:
        """invoke_stream max_tokens 3단 우선순위 검증."""

        def _captured_max_tokens(anthropic: MagicMock) -> int:
            return anthropic.messages.stream.call_args.kwargs["max_tokens"]

        # Case 1: 명시값 > 생성자 값
        anthropic1 = _make_anthropic_mock([])
        client1 = LLMClient(anthropic_client=anthropic1, model_id=MODEL_ID, max_tokens=4096)
        await _collect(client1.invoke_stream("p", max_tokens=512))
        assert _captured_max_tokens(anthropic1) == 512

        # Case 2: 생성자 값 사용 (invoke_stream max_tokens 생략)
        anthropic2 = _make_anthropic_mock([])
        client2 = LLMClient(anthropic_client=anthropic2, model_id=MODEL_ID, max_tokens=2048)
        await _collect(client2.invoke_stream("p"))
        assert _captured_max_tokens(anthropic2) == 2048

        # Case 3: 생성자 기본값 4096 폴백
        anthropic3 = _make_anthropic_mock([])
        client3 = LLMClient(anthropic_client=anthropic3, model_id=MODEL_ID)
        await _collect(client3.invoke_stream("p"))
        assert _captured_max_tokens(anthropic3) == 4096

    @pytest.mark.asyncio
    async def test_invoke_stream_raises_bedrock_api_error_on_api_error(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """messages.stream APIStatusError → BedrockAPIError."""
        response = MagicMock()
        response.status_code = 429
        api_error = APIStatusError(
            message="Rate exceeded",
            response=response,
            body={"error": {"message": "Rate exceeded"}},
        )
        anthropic = MagicMock()
        anthropic.messages = MagicMock()
        anthropic.messages.stream = MagicMock(side_effect=api_error)
        client = LLMClient(anthropic_client=anthropic, model_id=MODEL_ID)

        import logging
        with caplog.at_level(logging.ERROR):
            with pytest.raises(BedrockAPIError):
                await _collect(client.invoke_stream("prompt"))

        assert any("llm_invoke_stream_failed" in r.message for r in caplog.records)

    @pytest.mark.asyncio
    async def test_invoke_stream_does_not_block_event_loop(self) -> None:
        """두 stream을 gather로 돌렸을 때 직렬화되지 않는다."""
        # 매 호출마다 새 스트림 컨텍스트를 만들어야 한다 (text_stream이 일회용 iterator라서).
        def _factory(**_kwargs):
            return _FakeStreamContext([f"c{i}" for i in range(5)], delay=0.05)

        anthropic = _make_anthropic_mock(_factory)
        client = LLMClient(anthropic_client=anthropic, model_id=MODEL_ID, max_tokens=256)

        async def _first_chunk_time(agen):
            start = asyncio.get_event_loop().time()
            async for _ in agen:
                return asyncio.get_event_loop().time() - start
            return float("inf")

        gen1 = client.invoke_stream("p1")
        gen2 = client.invoke_stream("p2")
        t1, t2 = await asyncio.gather(_first_chunk_time(gen1), _first_chunk_time(gen2))

        # Tail-buffer delays first yield by ~3 events (3 * 0.05 = 0.15s).
        # Serialized: t2 >= 5 * 0.05 + 3 * 0.05 = 0.40s. Async: t2 ~= 0.15s.
        assert t2 < 0.25, f"두 번째 stream이 직렬화됨: t1={t1:.3f}s, t2={t2:.3f}s"

    @pytest.mark.asyncio
    async def test_invoke_stream_strips_json_fence(self) -> None:
        """```json ... ``` 코드 펜스를 벗겨내고 내용만 yield."""
        chunks = ["```json\n", '{"a": ', "1}", "\n```"]
        anthropic = _make_anthropic_mock(chunks)
        client = LLMClient(anthropic_client=anthropic, model_id=MODEL_ID)

        result = await _collect(client.invoke_stream("prompt"))

        assert "".join(result) == '{"a": 1}'

    @pytest.mark.asyncio
    async def test_invoke_stream_strips_plain_fence(self) -> None:
        """``` ... ``` (언어 없는) 코드 펜스를 벗겨내고 내용만 yield."""
        chunks = ["```\n", '{"a": 1}', "\n```"]
        anthropic = _make_anthropic_mock(chunks)
        client = LLMClient(anthropic_client=anthropic, model_id=MODEL_ID)

        result = await _collect(client.invoke_stream("prompt"))

        assert "".join(result) == '{"a": 1}'

    @pytest.mark.asyncio
    async def test_invoke_stream_no_fence_passthrough(self) -> None:
        """펜스 없는 응답은 내용이 변형 없이 yield된다."""
        chunks = ['{"a"', ": 1}"]
        anthropic = _make_anthropic_mock(chunks)
        client = LLMClient(anthropic_client=anthropic, model_id=MODEL_ID)

        result = await _collect(client.invoke_stream("prompt"))

        assert "".join(result) == '{"a": 1}'
