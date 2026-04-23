from uuid import UUID
from pydantic import BaseModel

from app.core.enums import ProjectStageStatus


class StageListItem(BaseModel):
    stage_id: UUID
    stage_sequence: int
    stage_name: str
    status: ProjectStageStatus
    is_completed: bool


class StageListResponse(BaseModel):
    stages: list[StageListItem]
