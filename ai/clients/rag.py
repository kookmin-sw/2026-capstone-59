"""Bedrock Knowledge Base RAG 클라이언트.

boto3 bedrock-agent-runtime 클라이언트를 의존성 주입받아 KB를 검색하고
RetrievedChunk 리스트를 반환한다. 검색 실패는 비치명적으로 처리한다.

DOJ / Custom Data Source 분리:
    단일 KB 안의 두 Data Source를 `dataSourceId` filter로 분리해 검색한다.
    Bedrock KB가 각 청크에 자동으로 붙이는 시스템 metadata 키
    `x-amz-bedrock-kb-data-source-id`를 이용하므로, 별도 `.metadata.json`
    사이드카 파일을 추가할 필요는 없다.
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any, Optional

from ai.schemas.common import RetrievedChunk

logger = logging.getLogger(__name__)

_DATA_SOURCE_METADATA_KEY = "x-amz-bedrock-kb-data-source-id"


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


def _build_retrieval_configuration(
    num_results: int, data_source_id: Optional[str]
) -> dict:
    """retrievalConfiguration 딕셔너리 조립.

    data_source_id가 주어지면 Bedrock KB 시스템 metadata 키로 filter를
    추가해 해당 Data Source 청크만 검색한다. None이면 필터 없이 KB 전체에서
    검색한다.
    """
    vector_config: dict[str, Any] = {"numberOfResults": num_results}
    if data_source_id is not None:
        vector_config["filter"] = {
            "equals": {"key": _DATA_SOURCE_METADATA_KEY, "value": data_source_id}
        }
    return {"vectorSearchConfiguration": vector_config}


class RAGClient:
    """Bedrock Knowledge Base 검색 래퍼."""

    def __init__(self, bedrock_agent_client: Any, kb_id: str) -> None:
        self.bedrock_agent_client = bedrock_agent_client
        self.kb_id = kb_id

    async def search_doj(
        self,
        query: str,
        num_results: int = 5,
        data_source_id: Optional[str] = None,
    ) -> list[RetrievedChunk]:
        """DOJ Data Source를 검색하여 RetrievedChunk 리스트를 반환.

        data_source_id가 주어지면 해당 DOJ Data Source 청크로 검색이
        제한된다. None이면 KB 전체에서 검색한다(하위 호환).

        검색 실패 시 빈 리스트를 반환한다 (비치명적).
        """
        correlation_id = str(uuid.uuid4())
        _log(
            logging.INFO,
            "rag_search_doj_start",
            correlation_id=correlation_id,
            kb_id=self.kb_id,
            data_source_id=data_source_id,
            query_len=len(query),
            num_results=num_results,
        )
        try:
            response = self.bedrock_agent_client.retrieve(
                knowledgeBaseId=self.kb_id,
                retrievalQuery={"text": query},
                retrievalConfiguration=_build_retrieval_configuration(
                    num_results, data_source_id
                ),
            )
            chunks = _parse_chunks(response.get("retrievalResults", []))
            _log(
                logging.INFO,
                "rag_search_doj_success",
                correlation_id=correlation_id,
                kb_id=self.kb_id,
                data_source_id=data_source_id,
                num_chunks=len(chunks),
            )
            return chunks
        except Exception as exc:
            _log(
                logging.WARNING,
                "rag_search_doj_failed",
                correlation_id=correlation_id,
                kb_id=self.kb_id,
                data_source_id=data_source_id,
                error_type=type(exc).__name__,
                error=str(exc),
            )
            return []

    async def search_custom(
        self,
        query: str,
        num_results: int = 3,
        data_source_id: Optional[str] = None,
    ) -> list[RetrievedChunk]:
        """Custom Data Source를 검색하여 RetrievedChunk 리스트를 반환.

        data_source_id가 주어지면 해당 Custom Data Source 청크로 검색이
        제한된다. None이면 KB 전체에서 검색한다(하위 호환).

        검색 실패 시 빈 리스트를 반환한다 (비치명적).
        """
        correlation_id = str(uuid.uuid4())
        _log(
            logging.INFO,
            "rag_search_custom_start",
            correlation_id=correlation_id,
            kb_id=self.kb_id,
            data_source_id=data_source_id,
            query_len=len(query),
            num_results=num_results,
        )
        try:
            response = self.bedrock_agent_client.retrieve(
                knowledgeBaseId=self.kb_id,
                retrievalQuery={"text": query},
                retrievalConfiguration=_build_retrieval_configuration(
                    num_results, data_source_id
                ),
            )
            chunks = _parse_chunks(response.get("retrievalResults", []))
            _log(
                logging.INFO,
                "rag_search_custom_success",
                correlation_id=correlation_id,
                kb_id=self.kb_id,
                data_source_id=data_source_id,
                num_chunks=len(chunks),
            )
            return chunks
        except Exception as exc:
            _log(
                logging.WARNING,
                "rag_search_custom_failed",
                correlation_id=correlation_id,
                kb_id=self.kb_id,
                data_source_id=data_source_id,
                error_type=type(exc).__name__,
                error=str(exc),
            )
            return []
