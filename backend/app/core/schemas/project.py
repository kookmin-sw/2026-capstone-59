from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ProjectCreateRequest(BaseModel):
    name: str
    duration_months: int
    member_count: int
    description: Optional[str] = None
    constraint: Optional[str] = None
    prompt: Optional[str] = None


class ProjectUpdateRequest(BaseModel):
    name: Optional[str] = None
    duration_months: Optional[int] = None
    member_count: Optional[int] = None
    description: Optional[str] = None
    constraint: Optional[str] = None
    prompt: Optional[str] = None


class ProjectResponse(BaseModel):
    project_id: UUID
    name: str
    current_stage_number: int
    is_completed: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime