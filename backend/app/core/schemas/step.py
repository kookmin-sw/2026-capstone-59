from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel

from app.core.enums import StepStatus


class GeneratedStep(BaseModel):
    step_id: UUID
    name: str
    status: StepStatus
    is_required: bool
    parent_step_id: UUID | None


class StepTreeNode(BaseModel):
    step_id: UUID
    name: str
    status: StepStatus
    is_required: bool
    is_keep: bool = False
    parent_step_id: UUID | None
    children: list[StepTreeNode] = []


StepTreeNode.model_rebuild()


class StepTreeResponse(BaseModel):
    current_path: list[UUID]
    steps: list[StepTreeNode]


class RequiredStepItem(BaseModel):
    step_id: UUID
    name: str
    stage_id: UUID
    sequence: int


class RequiredStepListResponse(BaseModel):
    required_steps: list[RequiredStepItem]


class StepAcceptResponse(BaseModel):
    is_current_required_step_completed: bool
    is_current_stage_completed: bool
    generated_steps: list[GeneratedStep]


class StepDetailResponse(BaseModel):
    is_required: bool
    step_id: UUID
    name: str
    mentoring: list | dict | None = None
    dictionary: list | dict | None = None
    template_url: str | None = None
    is_keep: bool = False


class StepKeepUpdateRequest(BaseModel):
    is_keep: bool


class StepKeepResponse(BaseModel):
    id: UUID
    is_keep: bool


class NotionTemplateResponse(BaseModel):
    notion_page_id: str
    notion_page_url: str


class SidePanelStartResponse(BaseModel):
    """POST /steps/{step_id}/sidepanel-start 응답."""
    step_id: UUID
    status: str  # pending / streaming / done


class SidePanelContentResponse(BaseModel):
    """GET /steps/{step_id}/sidepanel-content 폴링 응답."""
    status: str  # idle / pending / streaming / done / error
    content: str  # 누적 raw text (생성 중에도 부분 노출)
    is_complete: bool


class ProjectInfo(BaseModel):
    project_id: UUID
    name: str
    duration_months: int | None
    member_count: int | None
    description: str | None
    constraints: list[str] | None = None
    initial_prompt: str


class CurrentStage(BaseModel):
    stage_id: UUID
    stage_sequence: int
    name: str


class RequiredStepStatusItem(BaseModel):
    name: str
    order: int
    is_completed: bool


class CurrentRequiredStep(BaseModel):
    step_id: UUID
    name: str
    is_completed: bool
    goal: str
    entry_criteria: str
    fulfillment_criteria: list[str]
    minimum_fulfillment_count: int


class AcceptedStepItem(BaseModel):
    step_id: UUID
    name: str


class DecisionHistoryItem(BaseModel):
    step_id: UUID
    name: str
    status: str
    stage_sequence: int


class TargetStep(BaseModel):
    step_id: UUID
    name: str


class SidePanelDecisionHistoryItem(BaseModel):
    step_id: UUID
    name: str
    status: str
    stage_sequence: int


class AcceptRequest(BaseModel):
    project_info: ProjectInfo
    current_stage: CurrentStage
    required_steps_status: list[RequiredStepStatusItem]
    current_required_step: CurrentRequiredStep | None
    accepted_steps_in_required: list[AcceptedStepItem]
    accepted_step: AcceptedStepItem
    rag_context: dict = {}


class GenerateRequest(BaseModel):
    project_info: ProjectInfo
    current_stage: CurrentStage
    current_required_step: CurrentRequiredStep | None
    decision_history: list[DecisionHistoryItem]
    current_step: AcceptedStepItem
    rag_context: dict = {}


class SidePanelRequest(BaseModel):
    project_info: ProjectInfo
    current_stage: CurrentStage
    target_step: TargetStep
    decision_history: list[SidePanelDecisionHistoryItem]
    current_required_step: CurrentRequiredStep | None
    rag_context: dict = {}


class AcceptedRequiredStepItem(BaseModel):
    step_id: UUID
    name: str
    stage_sequence: int


class AcceptedRequiredStepListResponse(BaseModel):
    required_steps: list[AcceptedRequiredStepItem]