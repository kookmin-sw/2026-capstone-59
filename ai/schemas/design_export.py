"""design_export 시나리오 입출력 스키마.

박제: Poco_Design_Export_Spec_v1.md v1.3 §7 (AI 입력 스키마).
백엔드가 RDS에서 모은 데이터를 그대로 담아 AI에 전달하는 형태이며,
AI 출력은 마크다운 문자열을 Pydantic으로 wrap한 형태다.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from ai.schemas.common import MentoringContent, ProjectInfo

# SidePanelMentoring 은 MentoringContent 를 그대로 재사용한다 (Req 6.7).
# dictionary 필드는 본 시나리오에서 입력에 포함되지 않으므로 (Req 6.8),
# 별도 Optional 필드로 추가하지 않는다.
SidePanelMentoring = MentoringContent


class AcceptedStepData(BaseModel):
    """필수 Step 영역 안 Accept된 일반 Step의 데이터 (Req 6.6)."""

    step_id: str
    name: str
    description: str
    accepted_at: datetime
    sidepanel_mentoring: Optional[SidePanelMentoring] = None


class RequiredStepExportData(BaseModel):
    """선택된 Required_Step 1개의 DB 정의 + 진행 데이터 (Req 6.5)."""

    required_step_id: str
    required_step_name: str
    goal: str
    entry_criteria: str
    fulfillment_criteria: list[str]
    accepted_general_steps: list[AcceptedStepData]


class StageExportData(BaseModel):
    """선택된 Required_Step 들이 속한 Stage 단위 묶음 (Req 6.4)."""

    stage_sequence: int
    stage_name: str
    required_steps: list[RequiredStepExportData]


class ProjectStateForExport(BaseModel):
    """선택된 영역 전체 진행 데이터 (Req 6.3)."""

    stages: list[StageExportData]


class DesignExportInput(BaseModel):
    """generate_design_export 입력 (Req 6.1, 6.2, 6.10)."""

    project_info: ProjectInfo
    project_state: ProjectStateForExport
    generated_at: datetime = Field(
        ...,
        description=(
            "백엔드가 다운로드 요청을 처리한 시점의 KST(Asia/Seoul) 시각. "
            "분 단위까지 채워 전달하며, AI는 푸터에 그대로 사용하고 "
            "임의로 변경하지 않는다."
        ),
    )


class DesignExportOutput(BaseModel):
    """generate_design_export 출력.

    Bedrock 응답이 LLMClient.invoke 의 Pydantic 검증을 통과하도록,
    .md 본문 전체를 단일 문자열 필드로 감싼다. AI는 이 필드 안에
    고정 템플릿 + 자연어 요약 + 변환된 What·Why 질문을 채워 넣는다.
    """

    markdown: str = Field(
        ...,
        description=".md 본문 전체. 자기소개 블록쿼터부터 푸터까지 포함.",
    )
