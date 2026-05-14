"""SidePanelGenerator.generate_stream 단위 테스트."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

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
# Fixtures (기존 test_side_panel_generator.py와 동일 구조, 독립 정의)
# ---------------------------------------------------------------------------


def _project() -> ProjectInfo:
    return ProjectInfo(
        project_id="proj-1",
        name="배달 라이더 경로 최적화 앱",
        duration_months=3,
        member_count=4,
        description="배달 라이더 경로 비효율 문제 해결",
        constraints=["React + FastAPI"],
        initial_prompt="배달 라이더 경로 최적화 서비스를 만들고 싶음",
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _async_gen(chunks: list):
    for c in chunks:
        yield c


def _make_stream_service(
    chunks: list,
    doj_return=None,
    custom_return=None,
):
    llm = MagicMock()
    llm.invoke_stream = MagicMock(return_value=_async_gen(chunks))

    rag = MagicMock()
    rag.search_doj = AsyncMock(return_value=doj_return if doj_return is not None else [])
    rag.search_custom = AsyncMock(return_value=custom_return if custom_return is not None else [])

    return SidePanelGenerator(llm=llm, rag=rag), llm, rag


def _make_service(
    llm_return=None,
    doj_return=None,
    custom_return=None,
):
    llm = MagicMock()
    llm.invoke = AsyncMock(return_value=llm_return if llm_return is not None else _valid_output())

    rag = MagicMock()
    rag.search_doj = AsyncMock(return_value=doj_return if doj_return is not None else [])
    rag.search_custom = AsyncMock(return_value=custom_return if custom_return is not None else [])

    return SidePanelGenerator(llm=llm, rag=rag), llm, rag


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestGenerateStream:
    @pytest.mark.asyncio
    async def test_calls_rag_with_reduced_num_results(self) -> None:
        """RAG 호출 시 num_results=3(doj), num_results=2(custom)."""
        service, _, rag = _make_stream_service(chunks=["x"])

        async for _ in service.generate_stream(_input_full()):
            pass

        assert rag.search_doj.await_args.kwargs.get("num_results") == 3
        assert rag.search_custom.await_args.kwargs.get("num_results") == 2

    @pytest.mark.asyncio
    async def test_calls_invoke_stream_with_max_tokens_2048(self) -> None:
        """invoke_stream 호출 시 max_tokens=2048이 전달되는지 검증."""
        service, llm, _ = _make_stream_service(chunks=["x"])

        async for _ in service.generate_stream(_input_full()):
            pass

        assert llm.invoke_stream.call_args.kwargs["max_tokens"] == 2048

    @pytest.mark.asyncio
    async def test_yields_chunks_unchanged(self) -> None:
        """invoke_stream 청크가 변형 없이 그대로 yield되는지 검증."""
        service, _, _ = _make_stream_service(chunks=["A", "B", "C"])

        collected = []
        async for chunk in service.generate_stream(_input_full()):
            collected.append(chunk)

        assert collected == ["A", "B", "C"]

    @pytest.mark.asyncio
    async def test_prompt_identical_to_non_stream(self) -> None:
        """sync/stream 경로가 같은 입력·RAG 결과에 대해 byte-identical 프롬프트를 생성."""
        doj = [RetrievedChunk(text="DOJ chunk", relevance_score=0.9)]
        custom = [RetrievedChunk(text="Custom chunk", relevance_score=0.8)]
        inp = _input_full()

        # Sync path
        sync_service, sync_llm, _ = _make_service(
            llm_return=_valid_output(), doj_return=doj, custom_return=custom,
        )
        await sync_service.generate_side_panel(inp)
        sync_prompt = sync_llm.invoke.await_args.args[0]

        # Stream path — 같은 RAG 결과
        stream_service, stream_llm, _ = _make_stream_service(
            chunks=["x"], doj_return=doj, custom_return=custom,
        )
        async for _ in stream_service.generate_stream(inp):
            pass
        stream_prompt = stream_llm.invoke_stream.call_args.args[0]

        assert sync_prompt == stream_prompt, "sync/stream 프롬프트가 불일치"


# ---------------------------------------------------------------------------
# Data Source ID propagation — streaming path
# ---------------------------------------------------------------------------


class TestStreamDataSourceIdPropagation:
    """generate_side_panel_stream도 doj/custom data source ID를
    retrieve filter까지 전달해야 한다."""

    @pytest.mark.asyncio
    async def test_stream_passes_both_ids_to_retrieve(self):
        from ai.clients.llm import LLMClient
        from ai.clients.rag import RAGClient
        from ai.services import generate_side_panel_stream

        # RAG mock (retrieve call 검증 대상)
        agent = MagicMock()
        agent.retrieve.return_value = {"retrievalResults": []}

        # LLM mock: invoke_stream은 빈 async generator
        llm_client = MagicMock(spec=LLMClient)

        async def _empty_stream(*_args, **_kwargs):
            if False:
                yield ""  # generator 문법 유지
            return

        llm_client.invoke_stream = _empty_stream
        rag_client = RAGClient(bedrock_agent_client=agent, kb_id="test-kb")

        # 입력 fixture는 같은 파일의 기존 _input_full() 활용
        chunks = []
        async for c in generate_side_panel_stream(
            input_data=_input_full(),
            llm_client=llm_client,
            rag_client=rag_client,
            doj_data_source_id="POGP6P0D6Q",
            custom_data_source_id="VILRYZZZWG",
        ):
            chunks.append(c)

        # streaming은 sync 경로와 동일하게 retrieve 2회 (DOJ + Custom)
        assert agent.retrieve.call_count == 2
        values = {
            call.kwargs["retrievalConfiguration"]["vectorSearchConfiguration"][
                "filter"
            ]["equals"]["value"]
            for call in agent.retrieve.call_args_list
        }
        assert values == {"POGP6P0D6Q", "VILRYZZZWG"}

    @pytest.mark.asyncio
    async def test_stream_without_ids_omits_filters(self):
        from ai.clients.llm import LLMClient
        from ai.clients.rag import RAGClient
        from ai.services import generate_side_panel_stream

        agent = MagicMock()
        agent.retrieve.return_value = {"retrievalResults": []}

        llm_client = MagicMock(spec=LLMClient)

        async def _empty_stream(*_args, **_kwargs):
            if False:
                yield ""
            return

        llm_client.invoke_stream = _empty_stream
        rag_client = RAGClient(bedrock_agent_client=agent, kb_id="test-kb")

        chunks = []
        async for c in generate_side_panel_stream(
            input_data=_input_full(),
            llm_client=llm_client,
            rag_client=rag_client,
        ):
            chunks.append(c)

        assert agent.retrieve.call_count == 2
        for call in agent.retrieve.call_args_list:
            vector_config = call.kwargs["retrievalConfiguration"][
                "vectorSearchConfiguration"
            ]
            assert "filter" not in vector_config
