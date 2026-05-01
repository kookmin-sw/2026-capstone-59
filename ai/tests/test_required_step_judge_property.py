"""hypothesis 기반 RequiredStepJudge property 테스트."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

from hypothesis import given, settings
from hypothesis import strategies as st

from ai.schemas.accept import AcceptInput, AcceptOutput
from ai.schemas.common import (
    ProjectInfo,
    RequiredStepInfo,
    RequiredStepStatus,
    StageInfo,
    StepInfo,
)
from ai.services.required_step_judge import RequiredStepJudge

_safe_text = st.text(
    alphabet=st.characters(
        blacklist_categories=("C",),
        blacklist_characters='"\\{}',
    ),
    min_size=1,
    max_size=40,
)

_step_id = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789",
    min_size=1,
    max_size=8,
)

_project_st = st.builds(
    ProjectInfo,
    project_id=_step_id,
    duration_months=st.integers(min_value=1, max_value=24),
    member_count=st.integers(min_value=1, max_value=10),
    initial_prompt=_safe_text,
    name=st.just(None),
    description=st.just(None),
    constraints=st.just(None),
)

_stage_st = st.builds(
    StageInfo,
    stage_id=_step_id,
    stage_number=st.integers(min_value=1, max_value=6),
    name=_safe_text,
)

_required_step_st = st.builds(
    RequiredStepInfo,
    step_id=_step_id,
    name=_safe_text,
    is_completed=st.booleans(),
    goal=_safe_text,
    entry_criteria=_safe_text,
    fulfillment_criteria=st.lists(_safe_text, min_size=1, max_size=5),
    minimum_fulfillment_count=st.integers(min_value=1, max_value=3),
)

_step_info_st = st.builds(StepInfo, step_id=_step_id, name=_safe_text)

_required_step_status_st = st.builds(
    RequiredStepStatus,
    name=_safe_text,
    order=st.integers(min_value=1, max_value=4),
    is_completed=st.booleans(),
)

_accept_input_st = st.builds(
    AcceptInput,
    project_info=_project_st,
    current_stage=_stage_st,
    required_steps_status=st.lists(_required_step_status_st, min_size=0, max_size=4),
    current_required_step=_required_step_st,
    accepted_steps_in_required=st.lists(_step_info_st, min_size=1, max_size=5),
    accepted_step=_step_info_st,
    rag_context=st.just(None),
)


def _make_service(result: bool) -> tuple[RequiredStepJudge, MagicMock]:
    llm = MagicMock()
    llm.invoke = AsyncMock(return_value=AcceptOutput(is_current_required_step_completed=result))
    return RequiredStepJudge(llm=llm), llm


@settings(max_examples=100)
@given(input_data=_accept_input_st, llm_result=st.booleans())
def test_accept_prompt_completeness_and_output_type(
    input_data: AcceptInput, llm_result: bool
):
    service, llm = _make_service(llm_result)

    result = asyncio.run(service.judge_required_step(input_data))

    # 반환값이 AcceptOutput boolean 타입인지 확인
    assert isinstance(result, AcceptOutput)
    assert isinstance(result.is_current_required_step_completed, bool)

    prompt: str = llm.invoke.await_args.args[0]

    # 1) fulfillment_criteria 각 항목이 프롬프트에 포함되는지
    for aspect in input_data.current_required_step.fulfillment_criteria:
        assert aspect in prompt, f"aspect 누락: {aspect!r}"

    # 2) minimum_fulfillment_count 값이 프롬프트에 포함되는지
    threshold = input_data.current_required_step.minimum_fulfillment_count
    assert str(threshold) in prompt, f"threshold {threshold} 누락"

    # 3) accepted_steps_in_required의 모든 Step name이 포함되는지
    for step in input_data.accepted_steps_in_required:
        assert step.name in prompt, f"step name 누락: {step.name!r}"
