from app.core.aws.bedrock import bedrock_agent_runtime
from app.core.config import settings


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """Bedrock Knowledge Base 검색."""
    if not settings.BEDROCK_KB_ID:
        return []

    client = bedrock_agent_runtime()
    resp = client.retrieve(
        knowledgeBaseId=settings.BEDROCK_KB_ID,
        retrievalQuery={"text": query},
        retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": top_k}},
    )
    return resp.get("retrievalResults", [])
