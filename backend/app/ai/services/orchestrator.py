import boto3
from typing import AsyncIterator

from anthropic import AsyncAnthropic

from app.core.config import settings
from app.core.logging import get_logger
from ai import generate_steps, judge_required_step, generate_side_panel, generate_side_panel_stream, generate_design_export
from ai.clients.llm import LLMClient
from ai.clients.rag import RAGClient

logger = get_logger(__name__)

# Anthropic Direct API client (LLM 호출 전용 — 이슈 #232).
anthropic_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
# RAG는 여전히 Bedrock KB (bedrock-agent-runtime) 그대로 유지.
bedrock_agent = boto3.client("bedrock-agent-runtime", region_name="us-east-1")


async def call_accept(input_data):
    logger.debug("ai: invoking accept (judge_required_step)")
    try:
        return await judge_required_step(
            input_data, anthropic_client, settings.BEDROCK_MODEL_ID
        )
    except Exception:
        logger.error("ai: accept invocation failed", exc_info=True)
        raise


async def call_generate(input_data):
    logger.debug("ai: invoking generate_steps")
    try:
        return await generate_steps(
            input_data,
            anthropic_client,
            bedrock_agent,
            settings.BEDROCK_MODEL_ID,
            settings.BEDROCK_KB_ID,
            doj_data_source_id=settings.BEDROCK_DOJ_DATA_SOURCE_ID or None,
        )
    except Exception:
        logger.error("ai: generate_steps invocation failed", exc_info=True)
        raise


async def call_side_panel(input_data):
    logger.debug("ai: invoking side_panel")
    try:
        return await generate_side_panel(
            input_data,
            anthropic_client,
            bedrock_agent,
            settings.BEDROCK_MODEL_ID,
            settings.BEDROCK_KB_ID,
            doj_data_source_id=settings.BEDROCK_DOJ_DATA_SOURCE_ID or None,
            custom_data_source_id=settings.BEDROCK_CUSTOM_DATA_SOURCE_ID or None,
        )
    except Exception:
        logger.error("ai: side_panel invocation failed", exc_info=True)
        raise


async def call_side_panel_stream(input_data) -> AsyncIterator[str]:
    llm = LLMClient(anthropic_client=anthropic_client, model_id=settings.BEDROCK_MODEL_ID)
    rag = RAGClient(bedrock_agent_client=bedrock_agent, kb_id=settings.BEDROCK_KB_ID)
    async for chunk in generate_side_panel_stream(
        input_data,
        llm,
        rag,
        doj_data_source_id=settings.BEDROCK_DOJ_DATA_SOURCE_ID or None,
        custom_data_source_id=settings.BEDROCK_CUSTOM_DATA_SOURCE_ID or None,
    ):
        yield chunk



async def call_design_export(input_data):
    logger.debug("ai: invoking generate_design_export")
    try:
        return await generate_design_export(
            input_data,
            anthropic_client,
            settings.BEDROCK_MODEL_ID,
        )
    except Exception:
        logger.error("ai: design_export invocation failed", exc_info=True)
        raise
