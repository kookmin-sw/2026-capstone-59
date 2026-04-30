from uuid import UUID
from pydantic import BaseModel


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
    stage_number: int
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


class AcceptPayload(BaseModel):
    project_info: ProjectInfo
    current_stage: CurrentStage
    required_steps_status: list[RequiredStepStatusItem]
    current_required_step: CurrentRequiredStep | None
    accepted_steps_in_required: list[AcceptedStepItem]
    accepted_step: AcceptedStepItem
    rag_context: dict = {}

class DecisionHistoryItem(BaseModel):
    step_id: UUID
    name: str
    status: str 


class GeneratePayload(BaseModel):
    project_info: ProjectInfo
    current_stage: CurrentStage
    current_required_step: CurrentRequiredStep | None
    decision_history: list[DecisionHistoryItem]
    current_step: AcceptedStepItem               # 방금 accept된 부모 step
    rag_context: dict = {}

class TargetStep(BaseModel):
    step_id: UUID
    name: str


class SidePanelDecisionHistoryItem(BaseModel):
    step_id: UUID
    name: str
    status: str
    stage_number: int


class SidePanelPayload(BaseModel):
    project_info: ProjectInfo
    current_stage: CurrentStage
    target_step: TargetStep
    decision_history: list[SidePanelDecisionHistoryItem]
    current_required_step: CurrentRequiredStep | None
    rag_context: dict = {}