from functools import lru_cache

import boto3

from app.core.config import settings


@lru_cache(maxsize=1)
def bedrock_runtime():
    return boto3.client("bedrock-runtime", region_name=settings.AWS_REGION)


@lru_cache(maxsize=1)
def bedrock_agent_runtime():
    """Used for Knowledge Base retrieve / retrieve_and_generate."""
    return boto3.client("bedrock-agent-runtime", region_name=settings.AWS_REGION)
