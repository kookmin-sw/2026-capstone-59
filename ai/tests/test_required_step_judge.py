"""ai/services/required_step_judge.py 단위 테스트."""

import json
from typing import Any, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest

from ai.exceptions import AIGenerationFailedError
from ai.schemas.accept import AcceptInput, AcceptOutput
from ai.schemas.common import (
    ProjectInfo,
    RequiredStepInfo,
    RequiredStepStatus,
    StageInfo,
    StepInfo,
)
from ai.services.required_step_judge import RequiredStepJudge


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _project() -> ProjectInfo:
    return ProjectInfo(
        project_id="proj-1",
        name="스터디 매칭 앱",
        duration_months=3,
        member_count=4,
        description="대학생용 스터디 매칭",
        constraints=["React + FastAPI"],
        initial_prompt="스터디 메이트 매칭 서비스를 만들고 싶음",
    )


def _stage() -> StageInfo:
    return StageInfo(stage_id="stage-1", stage_sequence=1, name="아이디어 구체화")


def _required_step() -> RequiredStepInfo:
    return RequiredStepInfo(
        step_id="rs-1",
        name="대상 사용자 파악",
        is_completed=False,
        goal="정의된 문제로 불편을 겪는 구체적 사용자군을 식별하고 특성을 그린다.",
        entry_criteria="문제/기회에 관한 맥락이 존재한다.",
        fulfillment_criteria=[
            "1차 타겟 사용자군의 특성 정의 (연령·상황·역할 등)",
            "사용자의 현재 행동·습관·맥락 파악",
            "사용자 페르소나 또는 시나리오 정리",
            "사용자 검증 활동 (인터뷰·관찰·설문 등)",
        ],
        minimum_fulfillment_count=2,
    )


def _required_steps_status() -> list[RequiredStepStatus]:
    return [
        RequiredStepStatus(name="문제/기회 정의", order=1, is_completed=True),
        RequiredStepStatus(name="대상 사용자 파악", order=2, is_completed=False),
        RequiredStepStatus(name="핵심 컨셉 정의", order=3, is_completed=False),
        RequiredStepStatus(name="실현 가능성 검토", order=4, is_completed=False),
    ]


def _input_with_required(
    accepted_steps: Optional[list[StepInfo]] = None,
    accepted_step: Optional[StepInfo] = None,
) -> AcceptInput:
    return AcceptInput(
        project_info=_project(),
        current_stage=_stage(),
        required_steps_status=_required_steps_status(),
        current_required_step=_required_step(),
        accepted_steps_in_required=accepted_steps
        if accepted_steps is not None
        else [
            StepInfo(step_id="s1", name="타겟 사용자 정의"),
            StepInfo(step_id="s2", name="사용자 인터뷰 계획"),
        ],
        accepted_step=accepted_step
        if accepted_step is not None
        else StepInfo(step_id="s2", name="사용자 인터뷰 계획"),
    )


def _input_without_required() -> AcceptInput:
    return AcceptInput(
        project_info=_project(),
        current_stage=_stage(),
        required_steps_status=_required_steps_status(),
        current_required_step=None,
        accepted_steps_in_required=[],
        accepted_step=StepInfo(step_id="s0", name="아무거나"),
    )


def _make_service(
    llm_return: Any = None,
    llm_side_effect: Any = None,
) -> tuple[RequiredStepJudge, MagicMock]:
    llm = MagicMock()
    llm.invoke = AsyncMock()
    if llm_side_effect is not None:
        llm.invoke.side_effect = llm_side_effect
    else:
        llm.invoke.return_value = (
            llm_return
            if llm_return is not None
            else AcceptOutput(is_current_required_step_completed=True)
        )
    return RequiredStepJudge(llm=llm), llm


# ---------------------------------------------------------------------------
# 조기 반환 (LLM 호출 없음)
# ---------------------------------------------------------------------------


class TestSkipWhenNoRequiredStep:
    @pytest.mark.asyncio
    async def test_returns_false_when_current_required_step_is_none(self):
        service, llm = _make_service()

        result = await service.judge_required_step(_input_without_required())

        assert isinstance(result, AcceptOutput)
        assert result.is_current_required_step_completed is False

    @pytest.mark.asyncio
    async def test_llm_not_called_when_current_required_step_is_none(self):
        service, llm = _make_service()

        await service.judge_required_step(_input_without_required())

        llm.invoke.assert_not_called()


# ---------------------------------------------------------------------------
# 정상 판단 흐름
# ---------------------------------------------------------------------------


class TestJudgeHappyPath:
    @pytest.mark.asyncio
    async def test_llm_returns_true_propagated(self):
        service, llm = _make_service(
            llm_return=AcceptOutput(is_current_required_step_completed=True)
        )

        result = await service.judge_required_step(_input_with_required())

        assert isinstance(result, AcceptOutput)
        assert result.is_current_required_step_completed is True
        llm.invoke.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_llm_returns_false_propagated(self):
        service, llm = _make_service(
            llm_return=AcceptOutput(is_current_required_step_completed=False)
        )

        result = await service.judge_required_step(_input_with_required())

        assert isinstance(result, AcceptOutput)
        assert result.is_current_required_step_completed is False
        llm.invoke.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_passes_accept_output_schema_to_llm(self):
        service, llm = _make_service()

        await service.judge_required_step(_input_with_required())

        schema_arg = llm.invoke.await_args.args[1]
        assert schema_arg is AcceptOutput


# ---------------------------------------------------------------------------
# LLM 실패 전파
# ---------------------------------------------------------------------------


class TestLLMFailurePropagates:
    @pytest.mark.asyncio
    async def test_validation_failure_propagates(self):
        err = AIGenerationFailedError(
            message="재시도 초과",
            details={"last_error": {"type": "schema_validation_error", "attempt": 2}},
        )
        service, _ = _make_service(llm_side_effect=err)

        with pytest.raises(AIGenerationFailedError):
            await service.judge_required_step(_input_with_required())


# ---------------------------------------------------------------------------
# 프롬프트 조립 검증
# ---------------------------------------------------------------------------


class TestPromptAssembly:
    @pytest.mark.asyncio
    async def test_prompt_contains_required_step_name_and_goal(self):
        service, llm = _make_service()

        await service.judge_required_step(_input_with_required())

        prompt = llm.invoke.await_args.args[0]
        assert "대상 사용자 파악" in prompt
        assert "정의된 문제로 불편을 겪는" in prompt

    @pytest.mark.asyncio
    async def test_prompt_contains_all_fulfillment_criteria(self):
        service, llm = _make_service()

        await service.judge_required_step(_input_with_required())

        prompt = llm.invoke.await_args.args[0]
        for aspect in _required_step().fulfillment_criteria:
            assert aspect in prompt, f"측면이 누락됨: {aspect}"

    @pytest.mark.asyncio
    async def test_prompt_contains_threshold(self):
        service, llm = _make_service()

        await service.judge_required_step(_input_with_required())

        prompt = llm.invoke.await_args.args[0]
        # threshold=2 → "2개 이상의 측면" 표현이 템플릿에 들어있고
        # placeholder가 정상 치환되어야 함
        assert "2개 이상의 측면" in prompt

    @pytest.mark.asyncio
    async def test_prompt_contains_accepted_steps_in_required(self):
        service, llm = _make_service()

        await service.judge_required_step(_input_with_required())

        prompt = llm.invoke.await_args.args[0]
        assert "타겟 사용자 정의" in prompt
        assert "사용자 인터뷰 계획" in prompt

    @pytest.mark.asyncio
    async def test_prompt_contains_accepted_step_name(self):
        service, llm = _make_service(
            llm_return=AcceptOutput(is_current_required_step_completed=False)
        )
        inp = _input_with_required(
            accepted_step=StepInfo(step_id="s99", name="설문 조사 진행")
        )

        await service.judge_required_step(inp)

        prompt = llm.invoke.await_args.args[0]
        assert "설문 조사 진행" in prompt

    @pytest.mark.asyncio
    async def test_prompt_serializes_aspects_as_json_array(self):
        service, llm = _make_service()

        await service.judge_required_step(_input_with_required())

        prompt = llm.invoke.await_args.args[0]
        # JSON 배열 직렬화 결과가 그대로 prompt에 들어가야 함
        expected = json.dumps(
            _required_step().fulfillment_criteria, ensure_ascii=False
        )
        assert expected in prompt

    @pytest.mark.asyncio
    async def test_prompt_serializes_accepted_steps_as_json_with_names(self):
        service, llm = _make_service()

        await service.judge_required_step(_input_with_required())

        prompt = llm.invoke.await_args.args[0]
        # 각 Step의 step_id + name이 JSON 직렬화로 들어가야 함
        assert '"step_id"' in prompt
        assert '"name"' in prompt
        assert '"s1"' in prompt or "s1" in prompt
        assert '"s2"' in prompt or "s2" in prompt

    @pytest.mark.asyncio
    async def test_empty_accepted_steps_renders_empty_array(self):
        service, llm = _make_service()
        inp = _input_with_required(accepted_steps=[])

        await service.judge_required_step(inp)

        prompt = llm.invoke.await_args.args[0]
        assert "[]" in prompt

    @pytest.mark.asyncio
    async def test_no_unresolved_placeholders_in_prompt(self):
        service, llm = _make_service()

        await service.judge_required_step(_input_with_required())

        prompt = llm.invoke.await_args.args[0]
        # 미치환 placeholder 패턴이 없어야 한다
        for placeholder in [
            "{required_step_name}",
            "{required_step_goal}",
            "{fulfillment_criteria}",
            "{minimum_fulfillment_count}",
            "{accepted_steps_in_required}",
            "{accepted_step_name}",
        ]:
            assert placeholder not in prompt, f"미치환: {placeholder}"


# ---------------------------------------------------------------------------
# 통합 테스트
# ---------------------------------------------------------------------------


class TestIntegration:
    @pytest.mark.asyncio
    async def test_none_required_step_returns_false_llm_not_called(self):
        service, llm = _make_service()

        result = await service.judge_required_step(_input_without_required())

        assert result.is_current_required_step_completed is False
        llm.invoke.assert_not_called()

    @pytest.mark.asyncio
    async def test_llm_returns_true_judge_returns_true(self):
        service, llm = _make_service(
            llm_return=AcceptOutput(is_current_required_step_completed=True)
        )

        result = await service.judge_required_step(_input_with_required())

        assert result.is_current_required_step_completed is True
        llm.invoke.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_schema_mismatch_error_propagates(self):
        err = AIGenerationFailedError(
            message="재시도 초과",
            details={"last_error": {"type": "schema_validation_error"}},
        )
        service, _ = _make_service(llm_side_effect=err)

        with pytest.raises(AIGenerationFailedError):
            await service.judge_required_step(_input_with_required())
