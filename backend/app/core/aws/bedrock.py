"""AWS Bedrock 클라이언트 팩토리."""

import boto3

from app.core.config import settings


def bedrock_runtime():
    """Bedrock Runtime 클라이언트 (모델 호출용)."""
    return boto3.client("bedrock-runtime", region_name=settings.AWS_REGION)


def bedrock_agent_runtime():
    """Bedrock Agent Runtime 클라이언트 (Knowledge Base 검색용)."""
    return boto3.client("bedrock-agent-runtime", region_name=settings.AWS_REGION)
