from uuid import UUID
from pydantic import BaseModel


class StageListItem(BaseModel):
    stage_id: UUID
    stage_sequence: int
    stage_name: str
    is_active: bool
    is_completed: bool


class StageListResponse(BaseModel):
    stages: list[StageListItem]
