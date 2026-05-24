"""LLMClient.invoke(max_tokens=...) 우선순위 단위 테스트.

3단 우선순위를 검증한다:
    1) invoke(max_tokens=X) 명시값
    2) LLMClient(max_tokens=Y) 생성자 값
    3) LLMClient 생성자 기본값 (4096)

anthropic_client.messages.create을 mock하여 호출 kwargs의 max_tokens
필드를 직접 assert한다 (이슈 #232).
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel

from ai.clients.llm import LLMClient


MODEL_ID = "claude-haiku-4-5-20251001"


class _Schema(BaseModel):
    """테스트용 최소 스키마."""

    answer: str


def _valid_response() -> MagicMock:
    msg = MagicMock()
    msg.content = [MagicMock(text=json.dumps({"answer": "ok"}))]
    return msg


def _make_anthropic_mock() -> MagicMock:
    mock = MagicMock()
    mock.messages = MagicMock()
    mock.messages.create = AsyncMock(return_value=_valid_response())
    return mock


def _captured_max_tokens(anthropic_mock: MagicMock) -> int:
    """messages.create 호출의 max_tokens kwarg 값을 꺼낸다."""
    return anthropic_mock.messages.create.call_args.kwargs["max_tokens"]


class TestInvokeMaxTokensPriority:
    @pytest.mark.asyncio
    async def test_explicit_invoke_max_tokens_wins_over_constructor(self) -> None:
        """invoke(max_tokens=X)를 명시하면 생성자 값을 무시하고 X가 들어간다."""
        anthropic = _make_anthropic_mock()
        client = LLMClient(anthropic_client=anthropic, model_id=MODEL_ID, max_tokens=4096)

        await client.invoke("p", _Schema, max_tokens=512)

        assert _captured_max_tokens(anthropic) == 512

    @pytest.mark.asyncio
    async def test_omitted_invoke_max_tokens_uses_constructor_value(self) -> None:
        """invoke(max_tokens=None) 기본 생략 시 생성자에서 받은 값이 들어간다."""
        anthropic = _make_anthropic_mock()
        client = LLMClient(anthropic_client=anthropic, model_id=MODEL_ID, max_tokens=2048)

        await client.invoke("p", _Schema)

        assert _captured_max_tokens(anthropic) == 2048

    @pytest.mark.asyncio
    async def test_constructor_default_4096_fallback(self) -> None:
        """LLMClient(..., max_tokens=4096) 기본값이 생성자 생략 시 들어간다."""
        anthropic = _make_anthropic_mock()
        # max_tokens 인자를 생략하면 생성자 기본값 4096이 self.max_tokens가 된다.
        client = LLMClient(anthropic_client=anthropic, model_id=MODEL_ID)

        await client.invoke("p", _Schema)

        assert _captured_max_tokens(anthropic) == 4096

    @pytest.mark.asyncio
    async def test_invoke_max_tokens_overrides_even_non_default_constructor(self) -> None:
        """생성자가 1024여도 invoke(max_tokens=256) 명시값이 이긴다."""
        anthropic = _make_anthropic_mock()
        client = LLMClient(anthropic_client=anthropic, model_id=MODEL_ID, max_tokens=1024)

        await client.invoke("p", _Schema, max_tokens=256)

        assert _captured_max_tokens(anthropic) == 256
