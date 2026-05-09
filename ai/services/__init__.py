"""ai/services — generate, accept, side_panel 오케스트레이터.

백엔드(Lambda)가 호출하는 3개 public async 함수를 노출한다.
백엔드는 IAM Role 기반으로 boto3 클라이언트를 미리 만들어 주입하며,
이 모듈은 LLMClient/RAGClient를 wrapping해 실제 시나리오 서비스를 구동한다.

설계 원칙:
- backend 의존성(FastAPI, SQLAlchemy 등) 없음
- AI Dataset Spec v3 입출력 계약 준수
- pre-configured boto3 클라이언트를 받아 그대로 사용 (재생성 금지)
"""

from __future__ import annotations

from typing import Any, AsyncIterator

from ai.clients.llm import LLMClient
from ai.clients.rag import RAGClient
from ai.schemas.accept import AcceptInput, AcceptOutput
from ai.schemas.generate import GenerateInput, GenerateOutput
from ai.schemas.side_panel import SidePanelInput, SidePanelOutput
from ai.services.required_step_judge import RequiredStepJudge
from ai.services.side_panel_generator import SidePanelGenerator
from ai.services.step_generator import StepGenerator


async def generate_steps(
    input_data: GenerateInput,
    bedrock_runtime_client: Any,
    bedrock_agent_client: Any,
    model_id: str,
    kb_id: str,
) -> GenerateOutput:
    """generate 시나리오 — 일반 Step 3개 동적 생성."""
    llm = LLMClient(bedrock_client=bedrock_runtime_client, model_id=model_id)
    rag = RAGClient(bedrock_agent_client=bedrock_agent_client, kb_id=kb_id)
    service = StepGenerator(llm=llm, rag=rag)
    return await service.generate_steps(input_data)


async def judge_required_step(
    input_data: AcceptInput,
    bedrock_runtime_client: Any,
    model_id: str,
) -> AcceptOutput:
    """accept 시나리오 — 필수 Step 충족 여부 판단."""
    llm = LLMClient(bedrock_client=bedrock_runtime_client, model_id=model_id)
    service = RequiredStepJudge(llm=llm)
    return await service.judge_required_step(input_data)


async def generate_side_panel(
    input_data: SidePanelInput,
    bedrock_runtime_client: Any,
    bedrock_agent_client: Any,
    model_id: str,
    kb_id: str,
) -> SidePanelOutput:
    """side_panel 시나리오 — 일반 Step 사이드패널 콘텐츠 생성."""
    llm = LLMClient(bedrock_client=bedrock_runtime_client, model_id=model_id)
    rag = RAGClient(bedrock_agent_client=bedrock_agent_client, kb_id=kb_id)
    service = SidePanelGenerator(llm=llm, rag=rag)
    return await service.generate_side_panel(input_data)


async def generate_side_panel_stream(
    input_data: SidePanelInput,
    llm_client: LLMClient,
    rag_client: RAGClient,
) -> AsyncIterator[str]:
    """side_panel 시나리오 — 스트리밍 경로.

    기존 generate_side_panel과 달리, 백엔드가 LLMClient/RAGClient를 미리
    만들어 주입하는 형태. SSE 엔드포인트 당 연결을 유지하며 청크를 즉시
    yield한다. Pydantic 검증은 수행하지 않으며, 순수 텍스트 청크를 그대로
    전달한다.
    """
    service = SidePanelGenerator(llm=llm_client, rag=rag_client)
    async for chunk in service.generate_stream(input_data):
        yield chunk


__all__ = [
    "generate_steps",
    "judge_required_step",
    "generate_side_panel",
    "generate_side_panel_stream",
]
