"""hypothesis 기반 LLMClient property 테스트 — Anthropic Direct API 기반 (이슈 #232)."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from ai.clients.llm import LLMClient
from ai.exceptions import AIGenerationFailedError
from ai.schemas.accept import AcceptOutput
from ai.schemas.common import (
    CommonMistake,
    DictionaryItem,
    GeneratedStep,
    MentoringContent,
    RecommendedMethod,
)
from ai.schemas.generate import GenerateOutput
from ai.schemas.side_panel import SidePanelOutput

_nonempty = st.text(min_size=1)

_generated_step_st = st.builds(GeneratedStep, name=_nonempty, description=_nonempty)
_recommended_method_st = st.builds(RecommendedMethod, title=_nonempty, content=_nonempty)
_common_mistake_st = st.builds(
    CommonMistake, mistake=_nonempty, bad_example=_nonempty, good_example=_nonempty
)

_generate_output_st = st.builds(
    GenerateOutput,
    generated_steps=st.lists(_generated_step_st, min_size=3, max_size=3),
)
_accept_output_st = st.builds(AcceptOutput, is_current_required_step_completed=st.booleans())
_dictionary_item_st = st.builds(DictionaryItem, term=_nonempty, definition=_nonempty)
_mentoring_content_st = st.builds(
    MentoringContent,
    description=_nonempty,
    recommended_methods=st.lists(_recommended_method_st, min_size=0, max_size=5),
    common_mistakes=st.lists(_common_mistake_st, min_size=0, max_size=5),
    one_line_tip=_nonempty,
)
_side_panel_output_st = st.builds(
    SidePanelOutput,
    mentoring=_mentoring_content_st,
    dictionary=st.lists(_dictionary_item_st, min_size=0, max_size=5),
)


# ---------------------------------------------------------------------------
# Property 1: 직렬화 → 파싱 라운드트립
# ---------------------------------------------------------------------------


@settings(max_examples=100)
@given(output=_generate_output_st)
def test_generate_output_roundtrip(output: GenerateOutput):
    payload = json.loads(output.model_dump_json())
    restored = GenerateOutput.model_validate(payload)
    assert restored == output


@settings(max_examples=100)
@given(output=_accept_output_st)
def test_accept_output_roundtrip(output: AcceptOutput):
    payload = json.loads(output.model_dump_json())
    restored = AcceptOutput.model_validate(payload)
    assert restored == output


@settings(max_examples=100)
@given(output=_side_panel_output_st)
def test_side_panel_output_roundtrip(output: SidePanelOutput):
    payload = json.loads(output.model_dump_json())
    restored = SidePanelOutput.model_validate(payload)
    assert restored == output


# ---------------------------------------------------------------------------
# Property 2: 스키마 불일치 시 재시도 일관성
# ---------------------------------------------------------------------------


def _schema_mismatch_anthropic_mock() -> MagicMock:
    """messages.create가 항상 빈 dict {}를 content[0].text로 반환하는 mock."""

    def _response(**_):
        msg = MagicMock()
        msg.content = [MagicMock(text=json.dumps({}))]
        return msg

    mock = MagicMock()
    mock.messages = MagicMock()
    mock.messages.create = AsyncMock(side_effect=_response)
    return mock


@settings(max_examples=100)
@given(st.data())
def test_schema_mismatch_retry_count_and_failure(data):
    anthropic_mock = _schema_mismatch_anthropic_mock()
    client = LLMClient(anthropic_client=anthropic_mock, model_id="test-model")

    import asyncio

    with pytest.raises(AIGenerationFailedError):
        asyncio.run(client.invoke("{}", GenerateOutput, max_retries=2))

    assert anthropic_mock.messages.create.call_count == 3
