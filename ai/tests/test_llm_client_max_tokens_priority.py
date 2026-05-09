"""LLMClient.invoke(max_tokens=...) 우선순위 단위 테스트.

3단 우선순위를 검증한다:
    1) invoke(max_tokens=X) 명시값
    2) LLMClient(max_tokens=Y) 생성자 값
    3) LLMClient 생성자 기본값 (4096)

bedrock_client.invoke_model을 mock하여 request body의 max_tokens 필드를
JSON 파싱 후 assert한다.
"""

import io
import json
from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel

from ai.clients.llm import LLMClient


MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"


class _Schema(BaseModel):
    """테스트용 최소 스키마."""

    answer: str


def _valid_response() -> dict:
    envelope = {"content": [{"type": "text", "text": json.dumps({"answer": "ok"})}]}
    return {"body": io.BytesIO(json.dumps(envelope).encode("utf-8"))}


def _captured_max_tokens(bedrock_mock: MagicMock) -> int:
    """invoke_model 호출의 body에서 max_tokens 값을 꺼낸다."""
    body_str = bedrock_mock.invoke_model.call_args.kwargs["body"]
    payload = json.loads(body_str)
    return payload["max_tokens"]


class TestInvokeMaxTokensPriority:
    @pytest.mark.asyncio
    async def test_explicit_invoke_max_tokens_wins_over_constructor(self) -> None:
        """invoke(max_tokens=X)를 명시하면 생성자 값을 무시하고 X가 body에 들어간다."""
        bedrock = MagicMock()
        bedrock.invoke_model.return_value = _valid_response()
        client = LLMClient(bedrock_client=bedrock, model_id=MODEL_ID, max_tokens=4096)

        await client.invoke("p", _Schema, max_tokens=512)

        assert _captured_max_tokens(bedrock) == 512

    @pytest.mark.asyncio
    async def test_omitted_invoke_max_tokens_uses_constructor_value(self) -> None:
        """invoke(max_tokens=None) 기본 생략 시 생성자에서 받은 값이 body에 들어간다."""
        bedrock = MagicMock()
        bedrock.invoke_model.return_value = _valid_response()
        client = LLMClient(bedrock_client=bedrock, model_id=MODEL_ID, max_tokens=2048)

        await client.invoke("p", _Schema)

        assert _captured_max_tokens(bedrock) == 2048

    @pytest.mark.asyncio
    async def test_constructor_default_4096_fallback(self) -> None:
        """LLMClient(..., max_tokens=4096) 기본값이 생성자 생략 시 body에 들어간다."""
        bedrock = MagicMock()
        bedrock.invoke_model.return_value = _valid_response()
        # max_tokens 인자를 생략하면 생성자 기본값 4096이 self.max_tokens가 된다.
        client = LLMClient(bedrock_client=bedrock, model_id=MODEL_ID)

        await client.invoke("p", _Schema)

        assert _captured_max_tokens(bedrock) == 4096

    @pytest.mark.asyncio
    async def test_invoke_max_tokens_overrides_even_non_default_constructor(self) -> None:
        """생성자가 1024여도 invoke(max_tokens=256) 명시값이 이긴다."""
        bedrock = MagicMock()
        bedrock.invoke_model.return_value = _valid_response()
        client = LLMClient(bedrock_client=bedrock, model_id=MODEL_ID, max_tokens=1024)

        await client.invoke("p", _Schema, max_tokens=256)

        assert _captured_max_tokens(bedrock) == 256
