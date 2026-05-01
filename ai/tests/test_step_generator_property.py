"""hypothesis 기반 StepGenerator property 테스트."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from ai.schemas.common import (
    DecisionHistoryItem,
    ProjectInfo,
    RequiredStepInfo,
    StageInfo,
    StepInfo,
)
from ai.schemas.generate import GenerateInput, GenerateOutput, GeneratedStep
from ai.services.step_generator import StepGenerator

_nonempty = st.text(
    # 제어 문자(C), 큰따옴표, 역슬래시, 중괄호 제외
    # — json.dumps 이스케이프 시 원본과 달라지는 문자들을 막아 프롬프트 포함성 검증을 단순화
    alphabet=st.characters(
        blacklist_categories=("C",),
        blacklist_characters='"\\{}',
    ),
    min_size=1,
    max_size=40,
)
_step_id = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=8)

_project_st = st.builds(
    ProjectInfo,
    project_id=_step_id,
    duration_months=st.integers(min_value=1, max_value=24),
    member_count=st.integers(min_value=1, max_value=10),
    initial_prompt=_nonempty,
    name=st.just(None),
    description=st.just(None),
    constraints=st.just(None),
)

_stage_st = st.builds(
    StageInfo,
    stage_id=_step_id,
    stage_number=st.integers(min_value=1, max_value=6),
    name=_nonempty,
)

_history_item_st = st.builds(
    DecisionHistoryItem,
    step_id=_step_id,
    name=_nonempty,
    status=st.just("ACCEPTED"),
)

_required_step_st = st.builds(
    RequiredStepInfo,
    step_id=_step_id,
    name=_nonempty,
    is_completed=st.booleans(),
    goal=_nonempty,
    entry_criteria=_nonempty,
    fulfillment_criteria=st.lists(_nonempty, min_size=1, max_size=5),
    minimum_fulfillment_count=st.integers(min_value=1, max_value=3),
)

_current_step_st = st.builds(StepInfo, step_id=_step_id, name=_nonempty)

_generate_input_st = st.builds(
    GenerateInput,
    project_info=_project_st,
    current_stage=_stage_st,
    decision_history=st.lists(_history_item_st, min_size=1, max_size=5),
    current_step=_current_step_st,
    current_required_step=_required_step_st,
    rag_context=st.just(None),
)

_dummy_output = GenerateOutput(
    generated_steps=[
        GeneratedStep(name="Step A", description="A 활동"),
        GeneratedStep(name="Step B", description="B 활동"),
        GeneratedStep(name="Step C", description="C 활동"),
    ]
)


def _make_service() -> tuple[StepGenerator, MagicMock, MagicMock]:
    llm = MagicMock()
    llm.invoke = AsyncMock(return_value=_dummy_output)

    rag = MagicMock()
    rag.search_doj = AsyncMock(return_value=[])

    return StepGenerator(llm=llm, rag=rag), llm, rag


@settings(max_examples=100)
@given(input_data=_generate_input_st)
def test_generate_prompt_contains_all_context(input_data: GenerateInput):
    import asyncio

    service, llm, _ = _make_service()
    asyncio.run(service.generate_steps(input_data))

    prompt: str = llm.invoke.await_args.args[0]

    assert input_data.project_info.initial_prompt in prompt

    for item in input_data.decision_history:
        assert item.name in prompt

    for aspect in input_data.current_required_step.fulfillment_criteria:
        assert aspect in prompt
