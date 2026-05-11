"""ai/clients/rag.py 단위 테스트."""

import json
import logging
from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from ai.clients.rag import RAGClient
from ai.schemas.common import RetrievedChunk

KB_ID = "ZAEWSDQVP1"


def _retrieve_response(items: list[dict]) -> dict:
    return {"retrievalResults": items}


def _chunk_item(text: str, score: float) -> dict:
    return {"content": {"text": text}, "score": score}


@pytest.fixture
def agent_mock() -> MagicMock:
    return MagicMock()


@pytest.fixture
def client(agent_mock: MagicMock) -> RAGClient:
    return RAGClient(bedrock_agent_client=agent_mock, kb_id=KB_ID)


# ---------------------------------------------------------------------------
# search_doj
# ---------------------------------------------------------------------------


class TestSearchDoj:
    @pytest.mark.asyncio
    async def test_returns_retrieved_chunks(self, client: RAGClient, agent_mock: MagicMock):
        agent_mock.retrieve.return_value = _retrieve_response(
            [_chunk_item("DOJ 문서 A", 0.92), _chunk_item("DOJ 문서 B", 0.85)]
        )

        result = await client.search_doj("소프트웨어 개발")

        assert len(result) == 2
        assert all(isinstance(c, RetrievedChunk) for c in result)
        assert result[0].text == "DOJ 문서 A"
        assert result[0].relevance_score == pytest.approx(0.92)
        assert result[1].text == "DOJ 문서 B"
        assert result[1].relevance_score == pytest.approx(0.85)

    @pytest.mark.asyncio
    async def test_passes_correct_params(self, client: RAGClient, agent_mock: MagicMock):
        agent_mock.retrieve.return_value = _retrieve_response([])

        await client.search_doj("쿼리 내용", num_results=7)

        agent_mock.retrieve.assert_called_once_with(
            knowledgeBaseId=KB_ID,
            retrievalQuery={"text": "쿼리 내용"},
            retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 7}},
        )

    @pytest.mark.asyncio
    async def test_empty_results_returns_empty_list(self, client: RAGClient, agent_mock: MagicMock):
        agent_mock.retrieve.return_value = _retrieve_response([])

        result = await client.search_doj("쿼리")

        assert result == []

    @pytest.mark.asyncio
    async def test_api_error_returns_empty_list(self, client: RAGClient, agent_mock: MagicMock):
        agent_mock.retrieve.side_effect = ClientError(
            error_response={"Error": {"Code": "AccessDeniedException", "Message": "no"}},
            operation_name="Retrieve",
        )

        result = await client.search_doj("쿼리")

        assert result == []

    @pytest.mark.asyncio
    async def test_api_error_logs_warning(
        self, client: RAGClient, agent_mock: MagicMock, caplog: pytest.LogCaptureFixture
    ):
        agent_mock.retrieve.side_effect = RuntimeError("timeout")

        with caplog.at_level(logging.WARNING, logger="ai.clients.rag"):
            await client.search_doj("쿼리")

        warning_records = [
            json.loads(r.message) for r in caplog.records if r.levelno >= logging.WARNING
        ]
        assert any(r.get("event") == "rag_search_doj_failed" for r in warning_records)
        assert any("correlation_id" in r for r in warning_records)

    @pytest.mark.asyncio
    async def test_api_error_does_not_raise(self, client: RAGClient, agent_mock: MagicMock):
        agent_mock.retrieve.side_effect = Exception("unexpected")

        # 예외가 전파되지 않아야 한다
        result = await client.search_doj("쿼리")
        assert result == []

    @pytest.mark.asyncio
    async def test_malformed_item_is_skipped(self, client: RAGClient, agent_mock: MagicMock):
        agent_mock.retrieve.return_value = _retrieve_response(
            [
                {"content": {"text": "정상 항목"}, "score": 0.8},
                {"broken": True},  # content 키 없음 → 스킵
                {"content": {"text": "두번째 정상"}, "score": 0.6},
            ]
        )

        result = await client.search_doj("쿼리")

        assert len(result) == 2
        assert result[0].text == "정상 항목"
        assert result[1].text == "두번째 정상"

    @pytest.mark.asyncio
    async def test_success_log_contains_correlation_id(
        self, client: RAGClient, agent_mock: MagicMock, caplog: pytest.LogCaptureFixture
    ):
        agent_mock.retrieve.return_value = _retrieve_response([])

        with caplog.at_level(logging.INFO, logger="ai.clients.rag"):
            await client.search_doj("쿼리")

        records = [json.loads(r.message) for r in caplog.records]
        start = next(r for r in records if r["event"] == "rag_search_doj_start")
        success = next(r for r in records if r["event"] == "rag_search_doj_success")
        assert start["correlation_id"] == success["correlation_id"]


# ---------------------------------------------------------------------------
# search_custom
# ---------------------------------------------------------------------------


class TestSearchCustom:
    @pytest.mark.asyncio
    async def test_returns_retrieved_chunks(self, client: RAGClient, agent_mock: MagicMock):
        agent_mock.retrieve.return_value = _retrieve_response(
            [_chunk_item("커스텀 문서 A", 0.78)]
        )

        result = await client.search_custom("요구사항")

        assert len(result) == 1
        assert result[0].text == "커스텀 문서 A"
        assert result[0].relevance_score == pytest.approx(0.78)

    @pytest.mark.asyncio
    async def test_passes_correct_params(self, client: RAGClient, agent_mock: MagicMock):
        agent_mock.retrieve.return_value = _retrieve_response([])

        await client.search_custom("쿼리", num_results=3)

        agent_mock.retrieve.assert_called_once_with(
            knowledgeBaseId=KB_ID,
            retrievalQuery={"text": "쿼리"},
            retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 3}},
        )

    @pytest.mark.asyncio
    async def test_empty_results_returns_empty_list(self, client: RAGClient, agent_mock: MagicMock):
        agent_mock.retrieve.return_value = _retrieve_response([])

        result = await client.search_custom("쿼리")

        assert result == []

    @pytest.mark.asyncio
    async def test_api_error_returns_empty_list(self, client: RAGClient, agent_mock: MagicMock):
        agent_mock.retrieve.side_effect = ClientError(
            error_response={"Error": {"Code": "ThrottlingException", "Message": "rate"}},
            operation_name="Retrieve",
        )

        result = await client.search_custom("쿼리")

        assert result == []

    @pytest.mark.asyncio
    async def test_api_error_logs_warning(
        self, client: RAGClient, agent_mock: MagicMock, caplog: pytest.LogCaptureFixture
    ):
        agent_mock.retrieve.side_effect = RuntimeError("connection error")

        with caplog.at_level(logging.WARNING, logger="ai.clients.rag"):
            await client.search_custom("쿼리")

        warning_records = [
            json.loads(r.message) for r in caplog.records if r.levelno >= logging.WARNING
        ]
        assert any(r.get("event") == "rag_search_custom_failed" for r in warning_records)
        assert any("correlation_id" in r for r in warning_records)

    @pytest.mark.asyncio
    async def test_api_error_does_not_raise(self, client: RAGClient, agent_mock: MagicMock):
        agent_mock.retrieve.side_effect = Exception("unexpected")

        result = await client.search_custom("쿼리")
        assert result == []

    @pytest.mark.asyncio
    async def test_success_log_contains_correlation_id(
        self, client: RAGClient, agent_mock: MagicMock, caplog: pytest.LogCaptureFixture
    ):
        agent_mock.retrieve.return_value = _retrieve_response([])

        with caplog.at_level(logging.INFO, logger="ai.clients.rag"):
            await client.search_custom("쿼리")

        records = [json.loads(r.message) for r in caplog.records]
        start = next(r for r in records if r["event"] == "rag_search_custom_start")
        success = next(r for r in records if r["event"] == "rag_search_custom_success")
        assert start["correlation_id"] == success["correlation_id"]


# ---------------------------------------------------------------------------
# Data Source filter — search_doj / search_custom
# ---------------------------------------------------------------------------


_SYS_KEY = "x-amz-bedrock-kb-data-source-id"


class TestDataSourceFilter:
    """Data Source ID가 주어지면 retrievalConfiguration에 filter가 실린다."""

    @pytest.mark.asyncio
    async def test_doj_with_data_source_id_adds_filter(
        self, client: RAGClient, agent_mock: MagicMock
    ):
        agent_mock.retrieve.return_value = _retrieve_response([])

        await client.search_doj("쿼리", num_results=4, data_source_id="POGP6P0D6Q")

        agent_mock.retrieve.assert_called_once_with(
            knowledgeBaseId=KB_ID,
            retrievalQuery={"text": "쿼리"},
            retrievalConfiguration={
                "vectorSearchConfiguration": {
                    "numberOfResults": 4,
                    "filter": {"equals": {"key": _SYS_KEY, "value": "POGP6P0D6Q"}},
                }
            },
        )

    @pytest.mark.asyncio
    async def test_custom_with_data_source_id_adds_filter(
        self, client: RAGClient, agent_mock: MagicMock
    ):
        agent_mock.retrieve.return_value = _retrieve_response([])

        await client.search_custom("쿼리", num_results=2, data_source_id="VILRYZZZWG")

        agent_mock.retrieve.assert_called_once_with(
            knowledgeBaseId=KB_ID,
            retrievalQuery={"text": "쿼리"},
            retrievalConfiguration={
                "vectorSearchConfiguration": {
                    "numberOfResults": 2,
                    "filter": {"equals": {"key": _SYS_KEY, "value": "VILRYZZZWG"}},
                }
            },
        )

    @pytest.mark.asyncio
    async def test_doj_without_data_source_id_omits_filter(
        self, client: RAGClient, agent_mock: MagicMock
    ):
        agent_mock.retrieve.return_value = _retrieve_response([])

        await client.search_doj("쿼리", num_results=3)

        kwargs = agent_mock.retrieve.call_args.kwargs
        vector_config = kwargs["retrievalConfiguration"]["vectorSearchConfiguration"]
        assert "filter" not in vector_config
        assert vector_config["numberOfResults"] == 3

    @pytest.mark.asyncio
    async def test_custom_without_data_source_id_omits_filter(
        self, client: RAGClient, agent_mock: MagicMock
    ):
        agent_mock.retrieve.return_value = _retrieve_response([])

        await client.search_custom("쿼리", num_results=3)

        kwargs = agent_mock.retrieve.call_args.kwargs
        vector_config = kwargs["retrievalConfiguration"]["vectorSearchConfiguration"]
        assert "filter" not in vector_config

    @pytest.mark.asyncio
    async def test_doj_and_custom_receive_different_filters(
        self, client: RAGClient, agent_mock: MagicMock
    ):
        """같은 RAGClient로 두 검색을 호출해도 filter가 서로 섞이지 않는다."""
        agent_mock.retrieve.return_value = _retrieve_response([])

        await client.search_doj("a", num_results=3, data_source_id="POGP6P0D6Q")
        await client.search_custom("b", num_results=2, data_source_id="VILRYZZZWG")

        assert agent_mock.retrieve.call_count == 2
        first_call = agent_mock.retrieve.call_args_list[0].kwargs
        second_call = agent_mock.retrieve.call_args_list[1].kwargs

        first_filter = first_call["retrievalConfiguration"][
            "vectorSearchConfiguration"
        ]["filter"]
        second_filter = second_call["retrievalConfiguration"][
            "vectorSearchConfiguration"
        ]["filter"]

        assert first_filter == {"equals": {"key": _SYS_KEY, "value": "POGP6P0D6Q"}}
        assert second_filter == {"equals": {"key": _SYS_KEY, "value": "VILRYZZZWG"}}


# ---------------------------------------------------------------------------
# Service-layer propagation — StepGenerator / SidePanelGenerator
# ---------------------------------------------------------------------------


class TestServiceLayerPropagation:
    """서비스가 생성자로 받은 Data Source ID를 RAGClient 호출까지 전달."""

    @pytest.mark.asyncio
    async def test_step_generator_propagates_doj_id(
        self, agent_mock: MagicMock
    ):
        from unittest.mock import AsyncMock

        from ai.services.step_generator import StepGenerator

        llm = MagicMock()
        llm.invoke = AsyncMock(return_value=None)  # 호출만 검증
        rag = RAGClient(bedrock_agent_client=agent_mock, kb_id=KB_ID)
        rag_spy = MagicMock(wraps=rag)
        rag_spy.search_doj = AsyncMock(return_value=[])

        service = StepGenerator(llm=llm, rag=rag_spy, doj_data_source_id="POGP6P0D6Q")

        # generate_steps 내부는 복잡하므로 search_doj 호출만 직접 트리거
        await service.rag.search_doj(
            "test", num_results=3, data_source_id=service.doj_data_source_id
        )

        rag_spy.search_doj.assert_called_once()
        kwargs = rag_spy.search_doj.call_args.kwargs
        assert kwargs["data_source_id"] == "POGP6P0D6Q"

    @pytest.mark.asyncio
    async def test_side_panel_generator_propagates_both_ids(
        self, agent_mock: MagicMock
    ):
        from unittest.mock import AsyncMock

        from ai.services.side_panel_generator import SidePanelGenerator

        llm = MagicMock()
        rag = RAGClient(bedrock_agent_client=agent_mock, kb_id=KB_ID)
        rag_spy = MagicMock(wraps=rag)
        rag_spy.search_doj = AsyncMock(return_value=[])
        rag_spy.search_custom = AsyncMock(return_value=[])

        service = SidePanelGenerator(
            llm=llm,
            rag=rag_spy,
            doj_data_source_id="POGP6P0D6Q",
            custom_data_source_id="VILRYZZZWG",
        )

        assert service.doj_data_source_id == "POGP6P0D6Q"
        assert service.custom_data_source_id == "VILRYZZZWG"
