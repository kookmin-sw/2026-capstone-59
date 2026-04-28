"""ai/services/step_generator.py 단위 테스트."""

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from ai.exceptions import AIGenerationFailedError
from ai.schemas.common import (
    DecisionHistoryItem,
    GeneratedStep,
    ProjectInfo,
    RequiredStepInfo,
    RetrievedChunk,
    StageInfo,
    StepInfo,
)
from ai.schemas.generate import GenerateInput, GenerateOutput
from ai.services.step_generator import StepGenerator


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
        constraints="React + FastAPI",
        initial_prompt="스터디 메이트 매칭 서비스를 만들고 싶음",
    )


def _project_minimal() -> ProjectInfo:
    """Optional 필드가 None인 프로젝트."""
    return ProjectInfo(
        project_id="proj-2",
        duration_months=2,
        member_count=1,
        initial_prompt="개인 프로젝트",
    )


def _stage() -> StageInfo:
    return StageInfo(stage_id="stage-1", stage_number=1, name="아이디어 구체화")


def _required_step() -> RequiredStepInfo:
    return RequiredStepInfo(
        step_id="rs-1",
        name="대상 사용자 파악",
        is_completed=False,
        goal="사용자 정의",
        entry_criteria="문제/기회 맥락 존재",
        fulfillment_aspects=[
            "1차 타겟 사용자군의 특성 정의",
            "사용자의 행동·습관·맥락 파악",
            "페르소나 정리",
            "사용자 검증 활동",
        ],
        fulfillment_threshold=2,
    )


def _input_with_required() -> GenerateInput:
    return GenerateInput(
        project_info=_project(),
        current_stage=_stage(),
        decision_history=[
            DecisionHistoryItem(step_id="s0", name="문제 정의", status="ACCEPTED"),
        ],
        current_step=StepInfo(step_id="s1", name="문제 정의 정리"),
        current_required_step=_required_step(),
    )


def _input_without_required() -> GenerateInput:
    return GenerateInput(
        project_info=_project_minimal(),
        current_stage=_stage(),
        decision_history=[],
        current_step=StepInfo(step_id="s1", name="시작"),
        current_required_step=None,
    )


def _valid_output() -> GenerateOutput:
    return GenerateOutput(
        generated_steps=[
            GeneratedStep(name="경쟁 서비스 조사", description="유사 서비스를 조사하는 활동"),
            GeneratedStep(name="사용자 인터뷰 계획", description="타겟 사용자 인터뷰 설계"),
            GeneratedStep(name="기술 스택 비교", description="후보 기술 스택을 비교 분석"),
        ]
    )


def _make_service(
    llm_return: Any = None,
    llm_side_effect: Any = None,
    rag_return: Any = None,
    rag_side_effect: Any = None,
) -> tuple[StepGenerator, MagicMock, MagicMock]:
    llm = MagicMock()
    llm.invoke = AsyncMock()
    if llm_side_effect is not None:
        llm.invoke.side_effect = llm_side_effect
    else:
        llm.invoke.return_value = llm_return if llm_return is not None else _valid_output()

    rag = MagicMock()
    rag.search_doj = AsyncMock()
    if rag_side_effect is not None:
        rag.search_doj.side_effect = rag_side_effect
    else:
        rag.search_doj.return_value = rag_return if rag_return is not None else []

    return StepGenerator(llm=llm, rag=rag), llm, rag


# ---------------------------------------------------------------------------
# 정상 흐름
# ---------------------------------------------------------------------------


class TestGenerateStepsHappyPath:
    @pytest.mark.asyncio
    async def test_returns_generate_output(self):
        service, _, _ = _make_service(
            llm_return=_valid_output(),
            rag_return=[RetrievedChunk(text="DOJ chunk A", relevance_score=0.9)],
        )

        result = await service.generate_steps(_input_with_required())

        assert isinstance(result, GenerateOutput)
        assert len(result.generated_steps) == 3

    @pytest.mark.asyncio
    async def test_rag_query_uses_stage_number_and_name(self):
        service, _, rag = _make_service()

        await service.generate_steps(_input_with_required())

        rag.search_doj.assert_awaited_once()
        query = rag.search_doj.await_args.args[0]
        assert "Stage 1" in query
        assert "아이디어 구체화" in query
        assert "activities" in query

    @pytest.mark.asyncio
    async def test_prompt_contains_project_and_stage_context(self):
        service, llm, _ = _make_service(
            rag_return=[RetrievedChunk(text="DOJ Ch3 Initiation 청크", relevance_score=0.88)]
        )

        await service.generate_steps(_input_with_required())

        prompt = llm.invoke.await_args.args[0]
        # 프로젝트
        assert "스터디 매칭 앱" in prompt
        assert "3개월" in prompt
        assert "4명" in prompt
        assert "React + FastAPI" in prompt
        # Stage
        assert "Stage 1" in prompt
        assert "아이디어 구체화" in prompt
        # current_step
        assert "문제 정의 정리" in prompt
        # required step JSON 직렬화
        assert "대상 사용자 파악" in prompt
        assert "fulfillment_aspects" in prompt
        # rag chunk
        assert "DOJ Ch3 Initiation 청크" in prompt

    @pytest.mark.asyncio
    async def test_prompt_includes_decision_history_as_json(self):
        service, llm, _ = _make_service()

        await service.generate_steps(_input_with_required())

        prompt = llm.invoke.await_args.args[0]
        assert "문제 정의" in prompt
        assert "ACCEPTED" in prompt

    @pytest.mark.asyncio
    async def test_passes_generate_output_schema_to_llm(self):
        service, llm, _ = _make_service()

        await service.generate_steps(_input_with_required())

        schema_arg = llm.invoke.await_args.args[1]
        assert schema_arg is GenerateOutput


# ---------------------------------------------------------------------------
# current_required_step 분기
# ---------------------------------------------------------------------------


class TestCurrentRequiredStepBranch:
    @pytest.mark.asyncio
    async def test_required_step_none_renders_label(self):
        service, llm, _ = _make_service()

        await service.generate_steps(_input_without_required())

        prompt = llm.invoke.await_args.args[0]
        # "현재 진행 중인 필수 Step" 섹션에 "없음"이 들어가야 한다
        assert "없음" in prompt
        # required step 정보가 없으므로 그 안의 값들이 prompt에 들어가면 안 됨
        # (fulfillment_aspects 키 자체는 템플릿 본문에 등장하므로 값으로 검증)
        assert "1차 타겟 사용자군의 특성 정의" not in prompt
        assert "대상 사용자 파악" not in prompt
        # JSON 직렬화 결과의 특징적 패턴도 없어야 함
        assert "fulfillment_threshold" not in prompt

    @pytest.mark.asyncio
    async def test_required_step_present_serialized_to_json(self):
        service, llm, _ = _make_service()

        await service.generate_steps(_input_with_required())

        prompt = llm.invoke.await_args.args[0]
        assert "fulfillment_aspects" in prompt
        assert "fulfillment_threshold" in prompt
        assert "1차 타겟 사용자군의 특성 정의" in prompt


# ---------------------------------------------------------------------------
# RAG 실패 fallback
# ---------------------------------------------------------------------------


class TestRagFailureFallback:
    @pytest.mark.asyncio
    async def test_rag_returns_empty_list_proceeds_with_empty_context(self):
        # RAGClient 본 구현이 검색 실패 시 [] 반환하도록 설계됨
        service, llm, _ = _make_service(rag_return=[])

        result = await service.generate_steps(_input_with_required())

        assert isinstance(result, GenerateOutput)
        prompt = llm.invoke.await_args.args[0]
        # RAG context가 없을 때 "없음" 라벨이 들어가야 한다
        assert prompt.count("없음") >= 1

    @pytest.mark.asyncio
    async def test_rag_with_multiple_chunks_joined_by_newline(self):
        service, llm, _ = _make_service(
            rag_return=[
                RetrievedChunk(text="청크 1", relevance_score=0.9),
                RetrievedChunk(text="청크 2", relevance_score=0.8),
                RetrievedChunk(text="청크 3", relevance_score=0.7),
            ]
        )

        await service.generate_steps(_input_with_required())

        prompt = llm.invoke.await_args.args[0]
        assert "청크 1\n청크 2\n청크 3" in prompt


# ---------------------------------------------------------------------------
# LLM 실패 케이스
# ---------------------------------------------------------------------------


class TestLLMFailure:
    @pytest.mark.asyncio
    async def test_llm_validation_retry_failure_propagates(self):
        # LLMClient 자체 retry 후 발생하는 예외가 그대로 전파되어야 함
        err = AIGenerationFailedError(
            message="재시도 초과",
            details={"last_error": {"type": "schema_validation_error"}},
        )
        service, _, _ = _make_service(llm_side_effect=err)

        with pytest.raises(AIGenerationFailedError):
            await service.generate_steps(_input_with_required())

    @pytest.mark.asyncio
    async def test_llm_eventual_success_returned(self):
        # LLMClient가 내부 재시도 후 성공한 결과를 반환하면 서비스도 그대로 반환
        ok = _valid_output()
        service, _, _ = _make_service(llm_return=ok)

        result = await service.generate_steps(_input_with_required())

        assert result is ok


# ---------------------------------------------------------------------------
# Optional 필드 처리
# ---------------------------------------------------------------------------


class TestOptionalProjectFields:
    @pytest.mark.asyncio
    async def test_none_optional_fields_render_as_label(self):
        service, llm, _ = _make_service()

        await service.generate_steps(_input_without_required())

        prompt = llm.invoke.await_args.args[0]
        # name=None, description=None, constraints=None → "없음" 으로 렌더링되어야 한다
        # "이름: 없음" 처럼 단어가 그대로 노출되어야 함
        # 정확히 prompt에 미치환 placeholder가 없는지만 확인
        assert "{project_name}" not in prompt
        assert "{description}" not in prompt
        assert "{constraints}" not in prompt
        # 빈 문자열이 아니라 "없음" 라벨이 들어가야 함
        assert "이름: 없음" in prompt


# ---------------------------------------------------------------------------
# 의사결정 히스토리 직렬화
# ---------------------------------------------------------------------------


class TestDecisionHistorySerialization:
    @pytest.mark.asyncio
    async def test_empty_history_renders_empty_array(self):
        service, llm, _ = _make_service()

        await service.generate_steps(_input_without_required())

        prompt = llm.invoke.await_args.args[0]
        # 빈 배열 "[]" 이 prompt에 포함되어야 함
        assert "[]" in prompt

    @pytest.mark.asyncio
    async def test_history_items_serialized_with_status(self):
        inp = GenerateInput(
            project_info=_project(),
            current_stage=_stage(),
            decision_history=[
                DecisionHistoryItem(step_id="a", name="문제 정의", status="ACCEPTED"),
                DecisionHistoryItem(step_id="b", name="사용자 조사", status="ACCEPTED"),
            ],
            current_step=StepInfo(step_id="c", name="다음"),
        )
        service, llm, _ = _make_service()

        await service.generate_steps(inp)

        prompt = llm.invoke.await_args.args[0]
        # JSON 배열로 직렬화되어 status 키 포함
        assert '"status"' in prompt or "status" in prompt
        assert "사용자 조사" in prompt
