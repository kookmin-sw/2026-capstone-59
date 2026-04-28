"""Bedrock Knowledge Base RAG 클라이언트.

boto3 bedrock-agent-runtime 클라이언트를 의존성 주입받아 KB를 검색하고
RetrievedChunk 리스트를 반환한다. 검색 실패는 비치명적으로 처리한다.
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from ai.schemas.common import RetrievedChunk

logger = logging.getLogger(__name__)


def _log(level: int, event: str, **fields: Any) -> None:
    payload = {"event": event, **fields}
    logger.log(level, json.dumps(payload, ensure_ascii=False, default=str))


def _parse_chunks(retrieval_results: list[dict]) -> list[RetrievedChunk]:
    chunks: list[RetrievedChunk] = []
    for item in retrieval_results:
        try:
            text = item["content"]["text"]
            score = item.get("score", 0.0)
            chunks.append(RetrievedChunk(text=text, relevance_score=score))
        except (KeyError, TypeError):
            continue
    return chunks


class RAGClient:
    """Bedrock Knowledge Base 검색 래퍼."""

    def __init__(self, bedrock_agent_client: Any, kb_id: str) -> None:
        self.bedrock_agent_client = bedrock_agent_client
        self.kb_id = kb_id

    async def search_doj(self, query: str, num_results: int = 5) -> list[RetrievedChunk]:
        """DOJ 문서 KB를 검색하여 RetrievedChunk 리스트를 반환.

        검색 실패 시 빈 리스트를 반환한다 (비치명적).
        """
        correlation_id = str(uuid.uuid4())
        _log(
            logging.INFO,
            "rag_search_doj_start",
            correlation_id=correlation_id,
            kb_id=self.kb_id,
            query_len=len(query),
            num_results=num_results,
        )
        try:
            response = self.bedrock_agent_client.retrieve(
                knowledgeBaseId=self.kb_id,
                retrievalQuery={"text": query},
                retrievalConfiguration={
                    "vectorSearchConfiguration": {"numberOfResults": num_results}
                },
            )
            chunks = _parse_chunks(response.get("retrievalResults", []))
            _log(
                logging.INFO,
                "rag_search_doj_success",
                correlation_id=correlation_id,
                kb_id=self.kb_id,
                num_chunks=len(chunks),
            )
            return chunks
        except Exception as exc:
            _log(
                logging.WARNING,
                "rag_search_doj_failed",
                correlation_id=correlation_id,
                kb_id=self.kb_id,
                error_type=type(exc).__name__,
                error=str(exc),
            )
            return []

    async def search_custom(self, query: str, num_results: int = 3) -> list[RetrievedChunk]:
        """커스텀 문서 KB를 검색하여 RetrievedChunk 리스트를 반환.

        검색 실패 시 빈 리스트를 반환한다 (비치명적).

        TODO: Data Source 필터링 추가 예정
              retrievalConfiguration에 filter 조건을 추가하여
              DOJ Data Source와 Custom Data Source를 분리한다.
        """
        correlation_id = str(uuid.uuid4())
        _log(
            logging.INFO,
            "rag_search_custom_start",
            correlation_id=correlation_id,
            kb_id=self.kb_id,
            query_len=len(query),
            num_results=num_results,
        )
        try:
            response = self.bedrock_agent_client.retrieve(
                knowledgeBaseId=self.kb_id,
                retrievalQuery={"text": query},
                retrievalConfiguration={
                    "vectorSearchConfiguration": {"numberOfResults": num_results}
                },
            )
            chunks = _parse_chunks(response.get("retrievalResults", []))
            _log(
                logging.INFO,
                "rag_search_custom_success",
                correlation_id=correlation_id,
                kb_id=self.kb_id,
                num_chunks=len(chunks),
            )
            return chunks
        except Exception as exc:
            _log(
                logging.WARNING,
                "rag_search_custom_failed",
                correlation_id=correlation_id,
                kb_id=self.kb_id,
                error_type=type(exc).__name__,
                error=str(exc),
            )
            return []
