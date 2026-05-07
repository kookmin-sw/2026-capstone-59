"""ai/services/side_panel_generator.py 단위 테스트."""

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from ai.exceptions import AIGenerationFailedError
from ai.schemas.common import (
    CommonMistake,
    DecisionHistoryItem,
    DictionaryItem,
    MentoringContent,
    ProjectInfo,
    RecommendedMethod,
    RequiredStepInfo,
    RetrievedChunk,
    StageInfo,
    StepInfo,
)
from ai.schemas.side_panel import SidePanelInput, SidePanelOutput
from ai.services.side_panel_generator import SidePanelGenerator


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _project() -> ProjectInfo:
    return ProjectInfo(
        project_id="proj-1",
        name="배달 라이더 경로 최적화 앱",
        duration_months=3,
        member_count=4,
        description="배달 라이더 경로 비효율 문제 해결",
        constraints="React + FastAPI",
        initial_prompt="배달 라이더 경로 최적화 서비스를 만들고 싶음",
    )


def _project_minimal() -> ProjectInfo:
    return ProjectInfo(
        project_id="proj-2",
        duration_months=2,
        member_count=1,
        initial_prompt="개인 프로젝트",
    )


def _stage() -> StageInfo:
    return StageInfo(stage_id="stage-1", stage_sequence=1, name="아이디어 구체화")


def _required_step() -> RequiredStepInfo:
    return RequiredStepInfo(
        step_id="rs-1",
        name="핵심 컨셉 정의",
        is_completed=False,
        goal="문제를 어떤 해결책으로 풀지 정리",
        entry_criteria="문제와 사용자에 대한 맥락이 존재",
        fulfillment_criteria=["해결 접근", "경쟁 비교", "차별점", "주요 기능"],
        minimum_fulfillment_count=2,
    )


def _input_full() -> SidePanelInput:
    return SidePanelInput(
        project_info=_project(),
        current_stage=_stage(),
        target_step=StepInfo(step_id="ts-1", name="경쟁 서비스 조사"),
        decision_history=[
            DecisionHistoryItem(step_id="s0", name="문제/기회 정의", status="ACCEPTED"),
        ],
        current_required_step=_required_step(),
    )


def _input_minimal() -> SidePanelInput:
    return SidePanelInput(
        project_info=_project_minimal(),
        current_stage=_stage(),
        target_step=StepInfo(step_id="ts-1", name="시작"),
        decision_history=[],
        current_required_step=None,
    )


def _valid_output() -> SidePanelOutput:
    return SidePanelOutput(
        mentoring=MentoringContent(
            description="이 Step에서는 ...",
            recommended_methods=[
                RecommendedMethod(title="경쟁 서비스 찾기", content="3~5개 후보를 모은다."),
                RecommendedMethod(title="사용자 리뷰 모으기", content="앱스토어 리뷰를 모은다."),
            ],
            common_mistakes=[
                CommonMistake(
                    mistake="이름만 모으고 끝내기",
                    bad_example="A사, B사가 있다",
                    good_example="A사는 ~를 잘하지만 ~가 부족하다",
                ),
            ],
            one_line_tip="기존 대안이 놓친 틈을 찾자.",
        ),
        dictionary=[
            DictionaryItem(term="페르소나", definition="타겟 사용자를 대표하는 가상 인물"),
            DictionaryItem(term="MVP", definition="최소 기능만 갖춘 초기 제품"),
        ],
    )


def _make_service(
    llm_return: Any = None,
    llm_side_effect: Any = None,
    doj_return: Any = None,
    doj_side_effect: Any = None,
    custom_return: Any = None,
    custom_side_effect: Any = None,
) -> tuple[SidePanelGenerator, MagicMock, MagicMock]:
    llm = MagicMock()
    llm.invoke = AsyncMock()
    if llm_side_effect is not None:
        llm.invoke.side_effect = llm_side_effect
    else:
        llm.invoke.return_value = llm_return if llm_return is not None else _valid_output()

    rag = MagicMock()
    rag.search_doj = AsyncMock()
    rag.search_custom = AsyncMock()

    if doj_side_effect is not None:
        rag.search_doj.side_effect = doj_side_effect
    else:
        rag.search_doj.return_value = doj_return if doj_return is not None else []

    if custom_side_effect is not None:
        rag.search_custom.side_effect = custom_side_effect
    else:
        rag.search_custom.return_value = (
            custom_return if custom_return is not None else []
        )

    return SidePanelGenerator(llm=llm, rag=rag), llm, rag


# ---------------------------------------------------------------------------
# 정상 흐름
# ---------------------------------------------------------------------------


class TestHappyPath:
    @pytest.mark.asyncio
    async def test_returns_side_panel_output(self):
        service, _, _ = _make_service(
            llm_return=_valid_output(),
            doj_return=[RetrievedChunk(text="DOJ 청크", relevance_score=0.9)],
            custom_return=[RetrievedChunk(text="Custom 청크", relevance_score=0.8)],
        )

        result = await service.generate_side_panel(_input_full())

        assert isinstance(result, SidePanelOutput)
        assert len(result.mentoring.recommended_methods) == 2
        assert len(result.mentoring.common_mistakes) == 1
        assert result.mentoring.one_line_tip == "기존 대안이 놓친 틈을 찾자."
        assert len(result.dictionary) == 2

    @pytest.mark.asyncio
    async def test_passes_side_panel_output_schema_to_llm(self):
        service, llm, _ = _make_service()

        await service.generate_side_panel(_input_full())

        schema_arg = llm.invoke.await_args.args[1]
        assert schema_arg is SidePanelOutput

    @pytest.mark.asyncio
    async def test_doj_query_uses_stage_and_target_step(self):
        service, _, rag = _make_service()

        await service.generate_side_panel(_input_full())

        rag.search_doj.assert_awaited_once()
        query = rag.search_doj.await_args.args[0]
        assert "Stage 1" in query
        assert "아이디어 구체화" in query
        assert "경쟁 서비스 조사" in query

    @pytest.mark.asyncio
    async def test_custom_query_is_target_step_name(self):
        service, _, rag = _make_service()

        await service.generate_side_panel(_input_full())

        rag.search_custom.assert_awaited_once()
        query = rag.search_custom.await_args.args[0]
        assert query == "경쟁 서비스 조사"


# ---------------------------------------------------------------------------
# RAG 결과 결합
# ---------------------------------------------------------------------------


class TestRagCombination:
    @pytest.mark.asyncio
    async def test_doj_and_custom_chunks_both_in_prompt(self):
        service, llm, _ = _make_service(
            doj_return=[
                RetrievedChunk(text="DOJ Ch4 System Concept", relevance_score=0.92),
                RetrievedChunk(text="DOJ 대안 분석", relevance_score=0.85),
            ],
            custom_return=[
                RetrievedChunk(text="자체 문서: 경쟁 분석 기법", relevance_score=0.88),
            ],
        )

        await service.generate_side_panel(_input_full())

        prompt = llm.invoke.await_args.args[0]
        assert "DOJ Ch4 System Concept" in prompt
        assert "DOJ 대안 분석" in prompt
        assert "자체 문서: 경쟁 분석 기법" in prompt
        # 섹션 라벨도 들어가야 함
        assert "[DOJ SDLC]" in prompt
        assert "[자체 문서]" in prompt

    @pytest.mark.asyncio
    async def test_rag_chunks_separated_by_newlines(self):
        service, llm, _ = _make_service(
            doj_return=[
                RetrievedChunk(text="청크1", relevance_score=0.9),
                RetrievedChunk(text="청크2", relevance_score=0.8),
            ],
            custom_return=[RetrievedChunk(text="청크3", relevance_score=0.7)],
        )

        await service.generate_side_panel(_input_full())

        prompt = llm.invoke.await_args.args[0]
        # 각 청크가 줄바꿈으로 연결
        assert "청크1\n청크2" in prompt
        assert "청크3" in prompt


# ---------------------------------------------------------------------------
# Custom 폴백
# ---------------------------------------------------------------------------


class TestCustomFallback:
    @pytest.mark.asyncio
    async def test_custom_empty_proceeds_with_doj_only(self):
        service, llm, _ = _make_service(
            doj_return=[RetrievedChunk(text="DOJ 청크만", relevance_score=0.9)],
            custom_return=[],
        )

        result = await service.generate_side_panel(_input_full())

        assert isinstance(result, SidePanelOutput)
        prompt = llm.invoke.await_args.args[0]
        assert "DOJ 청크만" in prompt
        assert "[DOJ SDLC]" in prompt
        # Custom 섹션은 빈 결과이므로 라벨이 없어야 함
        assert "[자체 문서]" not in prompt

    @pytest.mark.asyncio
    async def test_custom_failure_returns_empty_proceeds(self):
        # RAGClient 본 구현은 검색 실패 시 [] 반환 — 그 동작을 그대로 재현
        service, llm, _ = _make_service(
            doj_return=[RetrievedChunk(text="DOJ 청크", relevance_score=0.9)],
            custom_return=[],  # Custom 실패 시 빈 리스트 반환
        )

        result = await service.generate_side_panel(_input_full())

        assert isinstance(result, SidePanelOutput)
        prompt = llm.invoke.await_args.args[0]
        assert "DOJ 청크" in prompt
        assert "[자체 문서]" not in prompt

    @pytest.mark.asyncio
    async def test_both_empty_renders_none_label(self):
        service, llm, _ = _make_service(doj_return=[], custom_return=[])

        result = await service.generate_side_panel(_input_full())

        assert isinstance(result, SidePanelOutput)
        prompt = llm.invoke.await_args.args[0]
        # rag_context 영역에 "없음"이 들어가야 함
        assert "없음" in prompt
        assert "[DOJ SDLC]" not in prompt
        assert "[자체 문서]" not in prompt


# ---------------------------------------------------------------------------
# LLM 실패 전파
# ---------------------------------------------------------------------------


class TestLLMFailure:
    @pytest.mark.asyncio
    async def test_validation_failure_propagates(self):
        err = AIGenerationFailedError(
            message="재시도 초과",
            details={"last_error": {"type": "schema_validation_error", "attempt": 2}},
        )
        service, _, _ = _make_service(llm_side_effect=err)

        with pytest.raises(AIGenerationFailedError):
            await service.generate_side_panel(_input_full())


# ---------------------------------------------------------------------------
# 프롬프트 조립
# ---------------------------------------------------------------------------


class TestPromptAssembly:
    @pytest.mark.asyncio
    async def test_prompt_contains_project_and_stage_context(self):
        service, llm, _ = _make_service()

        await service.generate_side_panel(_input_full())

        prompt = llm.invoke.await_args.args[0]
        assert "배달 라이더 경로 최적화 앱" in prompt
        assert "3개월" in prompt
        assert "4명" in prompt
        assert "React + FastAPI" in prompt
        assert "Stage 1" in prompt
        assert "아이디어 구체화" in prompt
        assert "경쟁 서비스 조사" in prompt

    @pytest.mark.asyncio
    async def test_required_step_present_serialized(self):
        service, llm, _ = _make_service()

        await service.generate_side_panel(_input_full())

        prompt = llm.invoke.await_args.args[0]
        assert "핵심 컨셉 정의" in prompt
        assert "minimum_fulfillment_count" in prompt

    @pytest.mark.asyncio
    async def test_required_step_none_renders_label(self):
        service, llm, _ = _make_service()

        await service.generate_side_panel(_input_minimal())

        prompt = llm.invoke.await_args.args[0]
        assert "없음" in prompt
        # required_step 직렬화 결과가 들어가면 안 됨
        assert "minimum_fulfillment_count" not in prompt
        assert "핵심 컨셉 정의" not in prompt

    @pytest.mark.asyncio
    async def test_decision_history_serialized(self):
        service, llm, _ = _make_service()

        await service.generate_side_panel(_input_full())

        prompt = llm.invoke.await_args.args[0]
        assert "문제/기회 정의" in prompt
        assert "ACCEPTED" in prompt

    @pytest.mark.asyncio
    async def test_no_unresolved_placeholders(self):
        service, llm, _ = _make_service()

        await service.generate_side_panel(_input_full())

        prompt = llm.invoke.await_args.args[0]
        for placeholder in [
            "{project_name}",
            "{duration_months}",
            "{member_count}",
            "{description}",
            "{constraints}",
            "{initial_prompt}",
            "{stage_sequence}",
            "{stage_name}",
            "{target_step_name}",
            "{decision_history}",
            "{current_required_step_info}",
            "{rag_context}",
        ]:
            assert placeholder not in prompt, f"미치환: {placeholder}"

    @pytest.mark.asyncio
    async def test_optional_project_fields_render_label(self):
        service, llm, _ = _make_service()

        await service.generate_side_panel(_input_minimal())

        prompt = llm.invoke.await_args.args[0]
        # name, description, constraints 모두 None → "없음" 라벨
        assert "이름: 없음" in prompt


# ---------------------------------------------------------------------------
# 통합 테스트
# ---------------------------------------------------------------------------


class TestIntegration:
    @pytest.mark.asyncio
    async def test_happy_path_doj_and_custom_chunks(self):
        service, _, _ = _make_service(
            llm_return=_valid_output(),
            doj_return=[
                RetrievedChunk(text="DOJ 청크 A", relevance_score=0.92),
                RetrievedChunk(text="DOJ 청크 B", relevance_score=0.85),
            ],
            custom_return=[
                RetrievedChunk(text="Custom 청크 A", relevance_score=0.88),
            ],
        )

        result = await service.generate_side_panel(_input_full())

        assert isinstance(result, SidePanelOutput)

    @pytest.mark.asyncio
    async def test_custom_empty_no_custom_label_in_prompt(self):
        service, llm, _ = _make_service(
            doj_return=[RetrievedChunk(text="DOJ 청크만", relevance_score=0.9)],
            custom_return=[],
        )

        await service.generate_side_panel(_input_full())

        prompt = llm.invoke.await_args.args[0]
        assert "[자체 문서]" not in prompt

    @pytest.mark.asyncio
    async def test_custom_failure_returns_side_panel_output(self):
        service, _, _ = _make_service(
            doj_return=[RetrievedChunk(text="DOJ 청크", relevance_score=0.9)],
            custom_return=[],
        )

        result = await service.generate_side_panel(_input_full())

        assert isinstance(result, SidePanelOutput)

    @pytest.mark.asyncio
    async def test_llm_schema_mismatch_propagates(self):
        err = AIGenerationFailedError(
            message="재시도 초과",
            details={"last_error": {"type": "schema_validation_error", "attempt": 2}},
        )
        service, _, _ = _make_service(llm_side_effect=err)

        with pytest.raises(AIGenerationFailedError):
            await service.generate_side_panel(_input_full())
