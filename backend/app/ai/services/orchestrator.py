import boto3
from ai import generate_steps, judge_required_step, generate_side_panel

# boto3 클라이언트 생성 (Lambda에서는 IAM Role로 자동 인증)
bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")
bedrock_agent = boto3.client("bedrock-agent-runtime", region_name="us-east-1")

MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
KB_ID = "ZAEWSDQVP1"  # 환경변수로 관리 권장

import boto3
from app.core.config import settings
from ai import generate_steps, judge_required_step, generate_side_panel

bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")
bedrock_agent = boto3.client("bedrock-agent-runtime", region_name="us-east-1")


async def call_accept(input_data):
    return await judge_required_step(input_data, bedrock_runtime, settings.BEDROCK_MODEL_ID)


async def call_generate(input_data):
    return await generate_steps(input_data, bedrock_runtime, bedrock_agent, settings.BEDROCK_MODEL_ID, settings.BEDROCK_KB_ID)


async def call_side_panel(input_data):
    return await generate_side_panel(input_data, bedrock_runtime, bedrock_agent, settings.BEDROCK_MODEL_ID, settings.BEDROCK_KB_ID)