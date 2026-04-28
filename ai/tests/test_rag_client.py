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
