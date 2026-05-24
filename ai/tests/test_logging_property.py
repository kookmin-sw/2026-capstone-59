"""hypothesis 기반 LLMClient 로깅 property 테스트 (이슈 #232).

Property 8: 요청별 correlation_id 일관성
"""

import asyncio
import json
import logging
from unittest.mock import AsyncMock, MagicMock

from hypothesis import given, settings
from hypothesis import strategies as st

from ai.clients.llm import LLMClient
from ai.schemas.accept import AcceptOutput


def _make_anthropic_mock(payload: dict) -> MagicMock:
    """주어진 payload를 Anthropic 응답 형식으로 반환하는 mock (호출마다 새 메시지)."""

    def _response(**_):
        msg = MagicMock()
        msg.content = [MagicMock(text=json.dumps(payload))]
        return msg

    mock = MagicMock()
    mock.messages = MagicMock()
    mock.messages.create = AsyncMock(side_effect=_response)
    return mock


def _capture_logs(client: LLMClient) -> tuple[list[dict], list[dict]]:
    """두 번 invoke를 실행하고 각 호출에서 캡처된 로그 레코드 목록을 반환."""
    log_records_1: list[str] = []
    log_records_2: list[str] = []

    class _Collector(logging.Handler):
        def __init__(self, target: list[str]) -> None:
            super().__init__()
            self._target = target

        def emit(self, record: logging.LogRecord) -> None:
            self._target.append(record.getMessage())

    llm_logger = logging.getLogger("ai.clients.llm")
    llm_logger.setLevel(logging.DEBUG)

    handler1 = _Collector(log_records_1)
    llm_logger.addHandler(handler1)
    asyncio.run(client.invoke("{}", AcceptOutput))
    llm_logger.removeHandler(handler1)

    handler2 = _Collector(log_records_2)
    llm_logger.addHandler(handler2)
    asyncio.run(client.invoke("{}", AcceptOutput))
    llm_logger.removeHandler(handler2)

    def _parse(records: list[str]) -> list[dict]:
        result = []
        for msg in records:
            try:
                result.append(json.loads(msg))
            except json.JSONDecodeError:
                pass
        return result

    return _parse(log_records_1), _parse(log_records_2)


# Property 8: 요청별 correlation_id 일관성
@settings(max_examples=100)
@given(st.data())
def test_correlation_id_consistency(_data):
    valid_payload = {"is_current_required_step_completed": True}
    anthropic_mock = _make_anthropic_mock(valid_payload)
    client = LLMClient(anthropic_client=anthropic_mock, model_id="test-model")

    logs1, logs2 = _capture_logs(client)

    # 각 호출에 로그가 존재해야 함
    assert len(logs1) >= 2  # at least llm_invoke_start + llm_invoke_success
    assert len(logs2) >= 2

    # 단일 요청 내 모든 로그 엔트리에 동일한 correlation_id가 있어야 함
    ids1 = {entry["correlation_id"] for entry in logs1 if "correlation_id" in entry}
    ids2 = {entry["correlation_id"] for entry in logs2 if "correlation_id" in entry}

    assert len(ids1) == 1, f"1회 invoke에서 correlation_id가 여러 개: {ids1}"
    assert len(ids2) == 1, f"2회 invoke에서 correlation_id가 여러 개: {ids2}"

    # 서로 다른 호출의 correlation_id는 달라야 함
    cid1 = ids1.pop()
    cid2 = ids2.pop()
    assert cid1 != cid2, "서로 다른 invoke 호출이 동일한 correlation_id를 공유함"
