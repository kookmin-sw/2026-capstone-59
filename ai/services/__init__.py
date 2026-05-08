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

import asyncio
from typing import Any, List, Tuple

from ai.clients.llm import LLMClient
from ai.clients.rag import RAGClient
from ai.schemas.accept import AcceptInput, AcceptOutput
from ai.schemas.common import StepInfo
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


async def accept_and_generate(
    accept_input: AcceptInput,
    generate_input: GenerateInput,
    bedrock_runtime_client: Any,
    bedrock_agent_client: Any,
    model_id: str,
    kb_id: str,
) -> Tuple[AcceptOutput, GenerateOutput]:
    """accept 판단과 generate를 병렬 실행하여 응답 시간 단축."""
    accept_result, generate_result = await asyncio.gather(
        judge_required_step(accept_input, bedrock_runtime_client, model_id),
        generate_steps(generate_input, bedrock_runtime_client, bedrock_agent_client, model_id, kb_id),
    )
    return accept_result, generate_result


async def accept_and_generate_with_side_panels(
    accept_input: AcceptInput,
    generate_input: GenerateInput,
    bedrock_runtime_client: Any,
    bedrock_agent_client: Any,
    model_id: str,
    kb_id: str,
) -> Tuple[AcceptOutput, GenerateOutput, List[SidePanelOutput]]:
    """accept + generate를 병렬 실행(Stage A) 후 Step별 side_panel 3개를 병렬 실행(Stage B)."""
    # Stage A: accept 판단과 Step 생성을 병렬 실행
    accept_result, generate_result = await asyncio.gather(
        judge_required_step(accept_input, bedrock_runtime_client, model_id),
        generate_steps(generate_input, bedrock_runtime_client, bedrock_agent_client, model_id, kb_id),
    )

    # Stage B: 생성된 Step 3개의 side_panel을 병렬 실행
    sp_inputs = [
        SidePanelInput(
            project_info=generate_input.project_info,
            current_stage=generate_input.current_stage,
            target_step=StepInfo(step_id="temp", name=step.name),
            decision_history=generate_input.decision_history,
            current_required_step=generate_input.current_required_step,
        )
        for step in generate_result.generated_steps
    ]
    side_panel_results: List[SidePanelOutput] = list(
        await asyncio.gather(
            *[
                generate_side_panel(sp_input, bedrock_runtime_client, bedrock_agent_client, model_id, kb_id)
                for sp_input in sp_inputs
            ]
        )
    )

    return accept_result, generate_result, side_panel_results


__all__ = [
    "generate_steps",
    "judge_required_step",
    "generate_side_panel",
    "accept_and_generate",
    "accept_and_generate_with_side_panels",
]
