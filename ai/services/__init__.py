"""ai/services — generate, accept, side_panel, design_export 오케스트레이터.

백엔드(Lambda)가 호출하는 5개 public async 함수를 노출한다.
백엔드는 IAM Role 기반으로 boto3 클라이언트를 미리 만들어 주입하며,
이 모듈은 LLMClient/RAGClient를 wrapping해 실제 시나리오 서비스를 구동한다.

설계 원칙:
- backend 의존성(FastAPI, SQLAlchemy 등) 없음
- AI Dataset Spec v3 입출력 계약 준수
- pre-configured boto3 클라이언트를 받아 그대로 사용 (재생성 금지)

Data Source 필터링:
- 단일 KB 안에 DOJ와 Custom Data Source가 함께 있으므로, 각 검색에 해당
  Data Source ID를 지정해 소스 분리를 강제한다. 환경변수 주입 예시:
    BEDROCK_KB_ID=ZAEWSDQVP1
    BEDROCK_DOJ_DATA_SOURCE_ID=POGP6P0D6Q
    BEDROCK_CUSTOM_DATA_SOURCE_ID=VILRYZZZWG
- 하위 호환: doj/custom_data_source_id 인자를 생략하면 KB 전체에서 검색.
"""

from __future__ import annotations

from typing import Any, AsyncIterator, Optional

from ai.clients.llm import LLMClient
from ai.clients.rag import RAGClient
from ai.schemas.accept import AcceptInput, AcceptOutput
from ai.schemas.design_export import DesignExportInput, DesignExportOutput
from ai.schemas.generate import GenerateInput, GenerateOutput
from ai.schemas.side_panel import SidePanelInput, SidePanelOutput
from ai.services.design_export_generator import DesignExportGenerator
from ai.services.required_step_judge import RequiredStepJudge
from ai.services.side_panel_generator import SidePanelGenerator
from ai.services.step_generator import StepGenerator


async def generate_steps(
    input_data: GenerateInput,
    bedrock_runtime_client: Any,
    bedrock_agent_client: Any,
    model_id: str,
    kb_id: str,
    doj_data_source_id: Optional[str] = None,
) -> GenerateOutput:
    """generate 시나리오 — 일반 Step 3개 동적 생성.

    doj_data_source_id가 주어지면 DOJ Data Source로 검색을 제한한다.
    None이면 KB 전체에서 검색한다(하위 호환).
    """
    llm = LLMClient(bedrock_client=bedrock_runtime_client, model_id=model_id)
    rag = RAGClient(bedrock_agent_client=bedrock_agent_client, kb_id=kb_id)
    service = StepGenerator(
        llm=llm, rag=rag, doj_data_source_id=doj_data_source_id
    )
    return await service.generate_steps(input_data)


async def judge_required_step(
    input_data: AcceptInput,
    bedrock_runtime_client: Any,
    model_id: str,
) -> AcceptOutput:
    """accept 시나리오 — 필수 Step 충족 여부 판단.

    RAG를 사용하지 않으므로 Data Source ID 인자가 없다.
    """
    llm = LLMClient(bedrock_client=bedrock_runtime_client, model_id=model_id)
    service = RequiredStepJudge(llm=llm)
    return await service.judge_required_step(input_data)


async def generate_side_panel(
    input_data: SidePanelInput,
    bedrock_runtime_client: Any,
    bedrock_agent_client: Any,
    model_id: str,
    kb_id: str,
    doj_data_source_id: Optional[str] = None,
    custom_data_source_id: Optional[str] = None,
) -> SidePanelOutput:
    """side_panel 시나리오 — 일반 Step 사이드패널 콘텐츠 생성.

    doj/custom_data_source_id가 주어지면 각 Data Source로 검색을 분리한다.
    None이면 KB 전체에서 검색한다(하위 호환).
    """
    llm = LLMClient(bedrock_client=bedrock_runtime_client, model_id=model_id)
    rag = RAGClient(bedrock_agent_client=bedrock_agent_client, kb_id=kb_id)
    service = SidePanelGenerator(
        llm=llm,
        rag=rag,
        doj_data_source_id=doj_data_source_id,
        custom_data_source_id=custom_data_source_id,
    )
    return await service.generate_side_panel(input_data)


async def generate_side_panel_stream(
    input_data: SidePanelInput,
    llm_client: LLMClient,
    rag_client: RAGClient,
    doj_data_source_id: Optional[str] = None,
    custom_data_source_id: Optional[str] = None,
) -> AsyncIterator[str]:
    """side_panel 시나리오 — 스트리밍 경로.

    기존 generate_side_panel과 달리, 백엔드가 LLMClient/RAGClient를 미리
    만들어 주입하는 형태. SSE 엔드포인트 당 연결을 유지하며 청크를 즉시
    yield한다. Pydantic 검증은 수행하지 않으며, 순수 텍스트 청크를 그대로
    전달한다.
    """
    service = SidePanelGenerator(
        llm=llm_client,
        rag=rag_client,
        doj_data_source_id=doj_data_source_id,
        custom_data_source_id=custom_data_source_id,
    )
    async for chunk in service.generate_stream(input_data):
        yield chunk


async def generate_design_export(
    input_data: DesignExportInput,
    bedrock_runtime_client: Any,
    model_id: str,
) -> DesignExportOutput:
    """design-export 시나리오 — Poco 사고 궤적 .md 본문 생성.

    백엔드가 RDS에서 모은 Project_Info + 선택된 Required_Step 영역의
    진행 데이터를 받아, Bedrock Claude Haiku 4.5 동기 호출로 .md 본문을
    생성한다. RAG 미사용 (Req 15.5).
    """
    llm = LLMClient(bedrock_client=bedrock_runtime_client, model_id=model_id)
    service = DesignExportGenerator(llm=llm)
    return await service.generate_design_export(input_data)


__all__ = [
    "generate_steps",
    "judge_required_step",
    "generate_side_panel",
    "generate_side_panel_stream",
    "generate_design_export",
]
