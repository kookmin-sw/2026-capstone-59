from app.core.aws.bedrock import bedrock_agent_runtime
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """Bedrock Knowledge Base 검색."""
    if not settings.BEDROCK_KB_ID:
        logger.debug("rag: skipped — no knowledge base configured")
        return []

    client = bedrock_agent_runtime()
    try:
        resp = client.retrieve(
            knowledgeBaseId=settings.BEDROCK_KB_ID,
            retrievalQuery={"text": query},
            retrievalConfiguration={
                "vectorSearchConfiguration": {"numberOfResults": top_k}
            },
        )
    except Exception:
        logger.error(
            "rag: retrieve failed",
            extra={"query_len": len(query), "top_k": top_k},
            exc_info=True,
        )
        raise

    results = resp.get("retrievalResults", [])
    logger.debug(
        "rag: retrieve completed",
        extra={"query_len": len(query), "result_count": len(results)},
    )
    return results
