import boto3
from typing import AsyncIterator

from app.core.config import settings
from ai import generate_steps, judge_required_step, generate_side_panel, generate_side_panel_stream
from ai.clients.llm import LLMClient
from ai.clients.rag import RAGClient

bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")
bedrock_agent = boto3.client("bedrock-agent-runtime", region_name="us-east-1")


async def call_accept(input_data):
    return await judge_required_step(
        input_data, bedrock_runtime, settings.BEDROCK_MODEL_ID
    )


async def call_generate(input_data):
    return await generate_steps(
        input_data,
        bedrock_runtime,
        bedrock_agent,
        settings.BEDROCK_MODEL_ID,
        settings.BEDROCK_KB_ID,
        doj_data_source_id=settings.BEDROCK_DOJ_DATA_SOURCE_ID or None,
    )


async def call_side_panel(input_data):
    return await generate_side_panel(
        input_data,
        bedrock_runtime,
        bedrock_agent,
        settings.BEDROCK_MODEL_ID,
        settings.BEDROCK_KB_ID,
        doj_data_source_id=settings.BEDROCK_DOJ_DATA_SOURCE_ID or None,
        custom_data_source_id=settings.BEDROCK_CUSTOM_DATA_SOURCE_ID or None,
    )


async def call_side_panel_stream(input_data) -> AsyncIterator[str]:
    llm = LLMClient(bedrock_client=bedrock_runtime, model_id=settings.BEDROCK_MODEL_ID)
    rag = RAGClient(bedrock_agent_client=bedrock_agent, kb_id=settings.BEDROCK_KB_ID)
    async for chunk in generate_side_panel_stream(
        input_data,
        llm,
        rag,
        doj_data_source_id=settings.BEDROCK_DOJ_DATA_SOURCE_ID or None,
        custom_data_source_id=settings.BEDROCK_CUSTOM_DATA_SOURCE_ID or None,
    ):
        yield chunk
