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


class StepGenerateResponse(BaseModel):
    generated_steps: list[GeneratedStep]


class StepTreeNode(BaseModel):
    step_id: UUID
    name: str
    status: StepStatus
    is_required: bool
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
    step_id: UUID
    status: StepStatus
    is_current_required_step_completed: bool


class StepDetailResponse(BaseModel):
    is_required: bool
    step_id: UUID
    name: str
    mentoring: list | dict | None = None
    dictionary: list | dict | None = None
    template_url: str | None = None


class NotionTemplateResponse(BaseModel):
    notion_page_id: str
    notion_page_url: str


class ProjectInfo(BaseModel):
    project_id: UUID
    name: str
    duration_months: int | None
    member_count: int | None
    description: str | None
    constraints: str | None
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
    fulfillment_aspects: list[str]
    fulfillment_threshold: int


class AcceptedStepItem(BaseModel):
    step_id: UUID
    name: str


class DecisionHistoryItem(BaseModel):
    step_id: UUID
    name: str
    status: str


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
