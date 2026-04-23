from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ProjectCreateRequest(BaseModel):
    name: Optional[str] = None
    duration_months: int
    member_count: int
    description: Optional[str] = None
    constraint: Optional[str] = None
    prompt: str 


class ProjectUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    project_id: UUID
    name: str
    current_stage_number: int
    is_completed: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class ProjectListItemResponse(BaseModel):
    project_id: UUID
    name: str
    current_stage_number: int
    is_completed: bool
    is_deleted: bool
    member_count: int
    duration_month: int
    description: str | None
    constraint: str | None
    prompt: str
    created_at: datetime
    updated_at: datetime