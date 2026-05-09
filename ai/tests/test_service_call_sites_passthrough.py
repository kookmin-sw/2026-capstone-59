"""서비스 호출부가 Task 2 완료 시점에서 `llm.invoke(prompt, Schema)` 3-인자
positional 호출만 수행한다는 것을 증명한다 (하위 호환성).

Task 5에서 이 테스트는 `max_tokens=1024/2048/256` 검증으로 업데이트된다.
현재 목적: Task 2가 기존 호출부를 한 줄도 고치지 않았음을 회귀적으로 증명.
"""

from __future__ import annotations

from typing import Any, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest

from ai.schemas.accept import AcceptInput, AcceptOutput
from ai.schemas.common import (
    CommonMistake,
    DecisionHistoryItem,
    DictionaryItem,
    GeneratedStep,
    MentoringContent,
    ProjectInfo,
    RecommendedMethod,
    RequiredStepInfo,
    RequiredStepStatus,
    StageInfo,
    StepInfo,
)
from ai.schemas.generate import GenerateInput, GenerateOutput
from ai.schemas.side_panel import SidePanelInput, SidePanelOutput
from ai.services.required_step_judge import RequiredStepJudge
from ai.services.side_panel_generator import SidePanelGenerator
from ai.services.step_generator import StepGenerator


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _project() -> ProjectInfo:
    return ProjectInfo(
        project_id="proj",
        duration_months=3,
        member_count=4,
        initial_prompt="배달 라이더 경로 최적화 아이디어",
    )


def _stage() -> StageInfo:
    return StageInfo(stage_id="stage-1", stage_sequence=1, name="아이디어 구체화")


def _required_step() -> RequiredStepInfo:
    return RequiredStepInfo(
        step_id="rs",
        name="문제/기회 정의",
        is_completed=False,
        goal="goal",
        entry_criteria="entry",
        fulfillment_criteria=["a", "b", "c", "d"],
        minimum_fulfillment_count=2,
    )


def _make_llm_mock(return_value: Any) -> MagicMock:
    llm = MagicMock()
    llm.invoke = AsyncMock(return_value=return_value)
    return llm


def _make_rag_mock() -> MagicMock:
    rag = MagicMock()
    rag.search_doj = AsyncMock(return_value=[])
    rag.search_custom = AsyncMock(return_value=[])
    return rag


def _assert_positional_only_invoke(
    llm: MagicMock,
    expected_schema: type,
    extra_allowed_kwargs: Optional[set] = None,
) -> None:
    """llm.invoke가 3-인자 positional 호출만 사용했는지 검증.

    허용: llm.invoke(prompt, Schema) 또는 llm.invoke(prompt, Schema, max_retries=N).
    금지: max_tokens keyword 전달 (Task 5에서 비로소 추가될 예정).
    """
    llm.invoke.assert_awaited_once()
    call = llm.invoke.await_args
    args = call.args
    kwargs = call.kwargs

    assert len(args) >= 2, "invoke는 최소 2개 positional 인자(prompt, Schema)로 호출되어야 한다"
    assert isinstance(args[0], str), "첫 번째 인자는 prompt (str)"
    assert args[1] is expected_schema, (
        f"두 번째 인자는 {expected_schema.__name__} 스키마여야 한다"
    )
    # Task 2 시점: max_tokens keyword는 전달되면 안 된다
    assert "max_tokens" not in kwargs, (
        "Task 2 단계에서는 서비스 호출부에 max_tokens keyword가 전달되지 않아야 한다"
    )


# ---------------------------------------------------------------------------
# 테스트
# ---------------------------------------------------------------------------


class TestServiceCallSitesPassthrough:
    @pytest.mark.asyncio
    async def test_step_generator_does_not_pass_max_tokens(self) -> None:
        valid = GenerateOutput(
            generated_steps=[
                GeneratedStep(name="a", description="1"),
                GeneratedStep(name="b", description="2"),
                GeneratedStep(name="c", description="3"),
            ]
        )
        llm = _make_llm_mock(valid)
        rag = _make_rag_mock()
        service = StepGenerator(llm=llm, rag=rag)

        input_data = GenerateInput(
            project_info=_project(),
            current_stage=_stage(),
            decision_history=[
                DecisionHistoryItem(step_id="s0", name="문제 정의", status="ACCEPTED"),
            ],
            current_step=StepInfo(step_id="s1", name="start"),
            current_required_step=_required_step(),
        )

        await service.generate_steps(input_data)

        _assert_positional_only_invoke(llm, GenerateOutput)

    @pytest.mark.asyncio
    async def test_side_panel_generator_does_not_pass_max_tokens(self) -> None:
        valid = SidePanelOutput(
            mentoring=MentoringContent(
                description="d",
                recommended_methods=[
                    RecommendedMethod(title="t1", content="c1"),
                    RecommendedMethod(title="t2", content="c2"),
                ],
                common_mistakes=[
                    CommonMistake(mistake="m", bad_example="b", good_example="g"),
                ],
                one_line_tip="tip",
            ),
            dictionary=[
                DictionaryItem(term="x", definition="y"),
                DictionaryItem(term="z", definition="w"),
            ],
        )
        llm = _make_llm_mock(valid)
        rag = _make_rag_mock()
        service = SidePanelGenerator(llm=llm, rag=rag)

        input_data = SidePanelInput(
            project_info=_project(),
            current_stage=_stage(),
            target_step=StepInfo(step_id="ts", name="target"),
            decision_history=[],
            current_required_step=_required_step(),
        )

        await service.generate_side_panel(input_data)

        _assert_positional_only_invoke(llm, SidePanelOutput)

    @pytest.mark.asyncio
    async def test_required_step_judge_does_not_pass_max_tokens(self) -> None:
        valid = AcceptOutput(is_current_required_step_completed=True)
        llm = _make_llm_mock(valid)
        service = RequiredStepJudge(llm=llm)

        accept_input = AcceptInput(
            project_info=_project(),
            current_stage=_stage(),
            required_steps_status=[
                RequiredStepStatus(name="문제/기회 정의", order=1, is_completed=False),
                RequiredStepStatus(name="대상 사용자 파악", order=2, is_completed=False),
                RequiredStepStatus(name="핵심 컨셉 정의", order=3, is_completed=False),
                RequiredStepStatus(name="실현 가능성 검토", order=4, is_completed=False),
            ],
            current_required_step=_required_step(),
            accepted_steps_in_required=[StepInfo(step_id="s1", name="aa")],
            accepted_step=StepInfo(step_id="s1", name="aa"),
        )

        await service.judge_required_step(accept_input)

        _assert_positional_only_invoke(llm, AcceptOutput)
