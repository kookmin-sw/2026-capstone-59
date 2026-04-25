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
    required_step: list[RequiredStepItem]
