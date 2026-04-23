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
